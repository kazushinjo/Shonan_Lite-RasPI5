"""Help画面。モック準拠の章一覧+本文レイアウト。"""
from __future__ import annotations

from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from manual_content import (
    MANUAL_SCREENSHOTS, MANUAL_SCREENSHOTS_EN, MANUAL_SECTIONS, MANUAL_SECTIONS_EN,
)
from i18n import is_english, tr
from widgets import SettingsSubScreen


class ManualScreen(SettingsSubScreen):
    def __init__(self, main_window):
        super().__init__("ヘルプ / Help", lambda: main_window.navigate_to("home"))
        self.sections = MANUAL_SECTIONS_EN if is_english() else MANUAL_SECTIONS
        self.screenshots = MANUAL_SCREENSHOTS_EN if is_english() else MANUAL_SCREENSHOTS
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.body_layout.setContentsMargins(14, 10, 14, 10)

        columns = QtWidgets.QHBoxLayout()
        columns.setSpacing(12)
        self.body_layout.addLayout(columns, 1)

        nav_card = QtWidgets.QFrame()
        nav_card.setFixedWidth(190)
        nav_card.setStyleSheet("QFrame { background: #191d1f; border-radius: 12px; } QListWidget { background: #191d1f; color: white; border: none; } QListWidget::item { padding: 8px 6px; border-radius: 5px; } QListWidget::item:selected { background: #0c9bc0; }")
        nav_layout = QtWidgets.QVBoxLayout(nav_card)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(6)
        nav_layout.addWidget(QtWidgets.QLabel(tr("ヘルプ項目", "Help Items")))
        self.section_list = QtWidgets.QListWidget()
        self.section_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        for title, _items in self.sections:
            self.section_list.addItem(title)
        self.section_list.currentRowChanged.connect(self._show_section)
        nav_layout.addWidget(self.section_list, 1)
        columns.addWidget(nav_card)

        content_card = QtWidgets.QFrame()
        content_card.setStyleSheet("QFrame { background: #191d1f; border-radius: 12px; } QLabel { color: white; background: transparent; }")
        content_layout = QtWidgets.QVBoxLayout(content_card)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(8)
        self.content_title = QtWidgets.QLabel()
        self.content_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        content_layout.addWidget(self.content_title)
        self.content_text = QtWidgets.QTextBrowser()
        self.content_text.setOpenExternalLinks(True)
        self.content_text.setStyleSheet("QTextBrowser { background: #101416; color: #d9e1e4; border: 1px solid #30383c; border-radius: 6px; padding: 8px; }")
        content_layout.addWidget(self.content_text, 1)
        columns.addWidget(content_card, 1)
        self.section_list.setCurrentRow(0)

    def _show_section(self, index: int) -> None:
        if not 0 <= index < len(self.sections):
            return
        title, items = self.sections[index]
        self.content_title.setText(title)
        html = []
        image_name = self.screenshots.get(title)
        if image_name:
            # 一部の章は複数スクリーンショット(リスト)を持つため、単一パス名と
            # どちらでも扱えるようにする。
            image_names = image_name if isinstance(image_name, list) else [image_name]
            image_dir = Path(__file__).resolve().parents[2] / "docs" / "images"
            if any((image_dir / name).exists() for name in image_names):
                html.append(f'<p style="color:#8fb3ff;">{tr(f"実機画面：{title}", f"Actual screen: {title}")}</p>')
        for subtitle, text in items:
            html.append(f'<p style="color:#8fb3ff; font-weight:bold;">{subtitle}</p>')
            html.append(f'<p>{text}</p>')
        self.content_text.setHtml("".join(html))


def create(main_window) -> QtWidgets.QWidget:
    return ManualScreen(main_window)
