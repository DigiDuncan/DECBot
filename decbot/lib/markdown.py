from dataclasses import dataclass
import re
from typing import Literal, TypedDict

import mistletoe
from mistletoe.token import Token
from mistletoe.ast_renderer import AstRenderer
from mistletoe.span_token import SpanToken, RawText, Emphasis, Strikethrough, Strong, InlineCode, AutoLink, Link
from mistletoe.block_token import Heading

HeaderLevel = Literal[0, 1, 2, 3, 4, 5, 6, -1]

class Underline(SpanToken):
    """Adds support for the `__underline__` style Discord supports.

    It looks like Strikethrough is already supported.
    """
    # pattern = re.compile(r"(?<!\\)(?:\\\\)*\_\_(.+?)\_\_", re.DOTALL)
    pattern = re.compile(
        r"""
        (?<!\\)   # Escaped _ doesn't count
        (?:\\\\)* # But escaped backslashes before are okay? (?:this is a non-capturing group)

        # And now for the part you can replace with copy and paste
        __     # The opener characters
        (.+?)  # The insides
        __     # The closer characters
        """,
        re.X  # Allow nice commented regex
        | re.DOTALL  # Alters the . character's behvior (see python re docs)
    )

class Insert(SpanToken):
    """Adds support for the `[[insert]]` style I just made up.
    """
    # pattern = re.compile(r"(?<!\\)(?:\\\\)*\_\_(.+?)\_\_", re.DOTALL)
    pattern = re.compile(
        r"""
        (?<!\\)   # Escaped _ doesn't count
        (?:\\\\)* # But escaped backslashes before are okay? (?:this is a non-capturing group)

        # And now for the part you can replace with copy and paste
        \[\[     # The opener characters
        (.+?)  # The insides
        \]\]     # The closer characters
        """,
        re.X  # Allow nice commented regex
        | re.DOTALL  # Alters the . character's behvior (see python re docs)
    )

class Spoiler(SpanToken):
    """Adds support for the `||spoiler||` style Discord supports."""

    # pattern = re.compile(r"(?<!\\)(?:\\\\)*\_\_(.+?)\_\_", re.DOTALL)
    pattern = re.compile(
        r"""
        (?<!\\)   # Escaped _ doesn't count
        (?:\\\\)* # But escaped backslashes before are okay? (?:this is a non-capturing group)

        # And now for the part you can replace with copy and paste
        \|\|     # The opener characters
        (.+?)  # The insides
        \|\|     # The closer characters
        """,
        re.X  # Allow nice commented regex
        | re.DOTALL  # Alters the . character's behvior (see python re docs)
    )

class Subtext(SpanToken):
    """Adds support for the `-# subtext` style Discord supports."""

    # pattern = re.compile(r"(?<!\\)(?:\\\\)*\_\_(.+?)\_\_", re.DOTALL)
    pattern = re.compile(
        r"""
        (?<!\\)   # Escaped _ doesn't count
        (?:\\\\)* # But escaped backslashes before are okay? (?:this is a non-capturing group)

        # And now for the part you can replace with copy and paste
        -\#\s      # The opener characters
        (.+?)  # The insides
        $     # The closer characters
        """,
        re.X  # Allow nice commented regex
        | re.DOTALL  # Alters the . character's behvior (see python re docs)
    )

class DigiRenderer(AstRenderer):

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: additional parameters to be passed to the ancestor's
                      constructor.
        """
        super().__init__(
            # 2. Pass your classes like *args items
            Underline, Spoiler, Subtext, Insert, **kwargs)

    # For each ClassName, define a render_class_name(self, token) like this
    def render_underline(self, token) -> str:
        return self.render_inner(token)


def parse_string_to_json(string: str) -> str:
    """A function for tired Digis.

    Args:
        string: the string to parse.
    Returns:
        Some json to `json.loads`.
    """
    return mistletoe.markdown(string, DigiRenderer)


def print_token(token: SpanToken, level = 0):
    print(f"{' ' * 2 * level}{token}")
    if token.children:
        for child in token.children:
            print_token(child, level + 1)

@dataclass
class Span:
    text: str
    bold: bool = False
    underline: bool = False
    italics: bool = False
    spoiler: bool = False
    strikethrough: bool = False
    code: bool = False
    link: bool = False
    insert: bool = False
    header_level: HeaderLevel = 0

class LevelState(TypedDict):
    bold: bool
    underline: bool
    italics: bool
    spoiler: bool
    strikethrough: bool
    code: bool
    link: bool
    insert: bool
    header_level: HeaderLevel

def parse_string_to_spans(string: str) -> list[Span]:
    spans: list[Span] = []
    level_states: dict[int, LevelState] = {-1: {"bold": False, "header_level": 0, "italics": False, "spoiler": False, "underline": False, "strikethrough": False, "link": False, "code": False, "insert": False}}

    def _parse(token: Token, level = 0):
        nonlocal level_states, spans

        # Clear old styles
        old_levels = []
        for l in level_states:
            if l >= level:
                old_levels.append(l)
        for old in old_levels:
            level_states.pop(old)

        # Create default style
        if level not in level_states:
            level_states[level] = level_states[level - 1].copy()

        # Build up this level
        if type(token) is Strong:
            level_states[level]["bold"] = True
        elif type(token) is Emphasis:
            level_states[level]["italics"] = True
        elif type(token) is Underline:
            level_states[level]["underline"] = True
        elif type(token) is Strikethrough:
            level_states[level]["strikethrough"] = True
        elif type(token) is Subtext:
            level_states[level]["header_level"] = -1
        elif type(token) is Heading:
            level_states[level]["header_level"] = token.level
        elif type(token) is InlineCode:
            level_states[level]["code"] = True
        elif type(token) is AutoLink:
            level_states[level]["link"] = True
        elif type(token) is Insert:
            level_states[level]["insert"] = True
        elif type(token) is Link:
            level_states[level]["link"] = True
            cs = level_states[level]
            spans.append(Span(token.title if token.title else "link", cs['bold'], cs['underline'], cs['italics'], cs['spoiler'], cs['strikethrough'], cs['code'], cs['link'], cs['insert'], cs['header_level']))
        elif type(token) is RawText:
            cs = level_states[level]
            spans.append(Span(token.content, cs['bold'], cs['underline'], cs['italics'], cs['spoiler'], cs['strikethrough'], cs['code'], cs['link'], cs['insert'], cs['header_level']))

        # Deeper!
        if token.children:
            for child in token.children:
                _parse(child, level + 1)

    with DigiRenderer() as renderer:
        doc = mistletoe.Document(string)
        _parse(doc)

    return spans


if __name__ == "__main__":
    messages = [
        "**This is a test.** I'm not bold anymore, but I am *italic~*",
        "__What__ the __||fuck|| did you say to me you little ||bleep||?!**__ *Is* ~~this~~ library? D:__ -# (uwu~)",
        "### Wow!"
    ]

    for message in messages:
        spans = parse_string_to_spans(message)
        print(spans)

async def debug(self, s: str) -> str:
    """A recreation of the <parse command used in the bot."""
    spans = parse_string_to_spans(s)
    message = ""
    for span in spans:
        message += f"**{span.text}** "
        if span.bold or span.italics or span.spoiler or span.strikethrough or span.underline or span.header_level:
            message += "*("
            if span.bold:
                message += "bold, "
            if span.italics:
                message += "italics, "
            if span.spoiler:
                message += "spoiler, "
            if span.strikethrough:
                message += "strikethrough, "
            if span.underline:
                message += "underline, "
            if span.link:
                message += "link, "
            if span.header_level:
                message += "header " + str(span.header_level)
            message = message.rstrip()
            message = message.removesuffix(",")
            message += ")*"
        message += "\n"
    return message
