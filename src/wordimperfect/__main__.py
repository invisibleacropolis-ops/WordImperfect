"""Executable entrypoint for running the WordImperfect application."""

from __future__ import annotations

from wordimperfect.app import Application


def main() -> None:
    """Launch the Tkinter application."""

    app = Application()
    app.run()


if __name__ == "__main__":
    main()
