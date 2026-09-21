#!/usr/bin/env python3
"""
Alias script so that `python3 bot_ui.py` works identically to `python3 bot_tui.py`.
"""
from bot_tui import main

if __name__ == '__main__':
    main()
