import json
from os import PathLike
from typing import Any


class FileList:
    def __init__(self, file: PathLike):
        self.file = file
        self._items: list[str] = []

        with open(file, "r+") as f:
            self._items = f.readlines()

        for item in self._items:
            item = item.strip()

        self._items = [item.strip() for item in self._items if item != ""]

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self):
        pass

    def _save(self):
        with open(self.file, "w+") as f:
            f.writelines([item + "\n" for item in self._items])

    def append(self, i: str):
        self._items.append(i.strip())
        self._save()

    def remove(self, i: str):
        self._items.remove(i.strip())
        self._save()

    def pop(self, i: int):
        self._items.pop(i)
        self._save()

    def clear(self):
        self._items.clear()
        self._save()

    def sort(self):
        self._items.sort()
        self._save()

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __setitem__(self, i, o):
        self._items.__setitem__(i, o)
        self._save()


class UniqueFileList(FileList):
    def append(self, i: str):
        icf = i.casefold().strip()
        if icf in self._items:
            raise ValueError(f"{i} is already in this list!")
        super().append(i)

    def remove(self, i: str):
        icf = i.casefold().strip()
        for item in self._items:
            if item == icf:
                super().remove(i)
                return
        raise ValueError(f"No item {i} in list!")


class FileDict:
    def __init__(self, file: PathLike):
        self.file = file
        self._dict: dict[str, Any] = {}

        with open(file, "r+") as f:
            self._dict = json.load(f)

    def _save(self):
        with open(self.file, "w+") as f:
            json.dump(self._dict, f)

    def clear(self):
        self._dict.clear()
        self._save()

    def get(self, k: str):
        return self._dict.get(k)

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def pop(self, k: str):
        v = self._dict.pop(k)
        self._save()
        return v

    def setdefault(self, k: str, v):
        r = self._dict.setdefault(k, v)
        self._save()
        return r

    def __len__(self):
        return self._dict.__len__()

    def __getitem__(self, k):
        return self._dict[k]

    def __setitem__(self, k, v):
        self._dict[k] = v
        self._save()
