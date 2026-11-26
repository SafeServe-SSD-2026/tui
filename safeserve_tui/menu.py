"""Reusable menus independent of terminal I/O and backend services."""

from collections.abc import Callable
from dataclasses import dataclass, field


def _validate_text(value: str, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")


@dataclass(frozen=True)
class MenuHeader:
    """A nonblank heading, preserved exactly as supplied."""

    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text, "Header")


@dataclass(frozen=True)
class MenuEntry:
    """A nonblank label associated with a zero-argument action."""

    label: str
    action: Callable[[], None] = field(repr=False)

    def __post_init__(self) -> None:
        _validate_text(self.label, "Entry label")
        if not callable(self.action):
            raise TypeError("Entry action must be callable")


@dataclass(frozen=True)
class Menu:
    """An immutable menu configuration with zero-based choices.

    Actions may have effects when selected. Constructing or rendering a menu
    never invokes them. Action failures propagate to the application caller.
    """

    header: MenuHeader
    entries: tuple[MenuEntry, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.header, MenuHeader):
            raise TypeError("Menu header must be a MenuHeader")
        if not isinstance(self.entries, (list, tuple)):
            raise TypeError("Menu entries must be a list or tuple")
        entries = tuple(self.entries)
        if not entries:
            raise ValueError("Menu must contain at least one entry")
        if any(not isinstance(entry, MenuEntry) for entry in entries):
            raise TypeError("Every menu entry must be a MenuEntry")
        object.__setattr__(self, "entries", entries)

    def render(self) -> str:
        """Return the heading and numbered choices, ending with a newline."""
        lines = [self.header.text]
        lines.extend(
            f"{index}) {entry.label}"
            for index, entry in enumerate(self.entries)
        )
        return "\n".join(lines) + "\n"

    def select(self, index: int) -> None:
        """Validate the choice and execute one action without reading input."""
        if type(index) is not int:
            raise TypeError("Menu choice must be an integer")
        if not 0 <= index < len(self.entries):
            raise ValueError("Menu choice is out of range")
        self.entries[index].action()


class MenuBuilder:
    """Build independent menu snapshots through a fluent interface.

    Building does not consume entries. Further additions only affect future
    menus, and failed additions leave the builder unchanged.
    """

    def __init__(self, header: MenuHeader) -> None:
        if not isinstance(header, MenuHeader):
            raise TypeError("Menu header must be a MenuHeader")
        self._header = header
        self._entries: list[MenuEntry] = []

    def with_entry(
        self, label: str, action: Callable[[], None]
    ) -> MenuBuilder:
        """Append a validated entry and return this builder."""
        self._entries.append(MenuEntry(label, action))
        return self

    def build(self) -> Menu:
        """Return a validated menu containing a snapshot of the entries."""
        return Menu(self._header, tuple(self._entries))
