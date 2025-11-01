"""Pluggable object insertion hooks for the editor."""

from __future__ import annotations

from collections.abc import Callable, Iterable

Handler = Callable[..., object]


class ObjectInsertionController:
    """Registry for functions that can embed rich objects in the document."""

    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register_handler(self, name: str, handler: Handler) -> None:
        """Associate ``name`` with ``handler`` replacing previous entries."""

        self._handlers[name] = handler

    def unregister_handler(self, name: str) -> None:
        """Remove a previously registered handler when present."""

        self._handlers.pop(name, None)

    def available_objects(self) -> Iterable[str]:
        """Return the registered object identifiers in registration order."""

        return tuple(self._handlers.keys())

    def insert(self, name: str, *args: object, **kwargs: object) -> object:
        """Execute the handler associated with ``name`` and return its result."""

        if name not in self._handlers:
            msg = f"No handler registered for object '{name}'."
            raise KeyError(msg)
        return self._handlers[name](*args, **kwargs)


__all__ = ["ObjectInsertionController"]
