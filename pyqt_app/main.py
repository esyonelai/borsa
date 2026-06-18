#!/usr/bin/env python3
"""
Bloomberg Terminal — BIST & Global Makro
PyQt6 Desktop Uygulaması

Kullanım:
    python main.py
"""

import sys
import os
import traceback

# Core paket yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """Uygulamayı başlat."""
    try:
        # Yüksek DPI desteği
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        # Global font
        font = QFont("Segoe UI", 10)
        app.setFont(font)

        # Pencere
        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception:
        with open("terminal_error.log", "w") as f:
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
