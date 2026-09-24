"""Homeメニュー。Android版 ui/HomeScreen.kt の homeMenuButtons 相当。"""
from __future__ import annotations

import http.client
import subprocess
import urllib.error
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from backend import PTT_CHANNEL_POWER, _send_ptt_channel_state
from version import __version__
from widgets import NavButton, error_dialog


def is_english(settings) -> bool:
    return getattr(settings, "language", "JAPANESE") == "ENGLISH"

# ホーム画面カードの文字サイズ(背景画像に元々焼き込まれていた比率に合わせる:
# 日本語は大きく、英語(2行目)は約6割の小さめサイズ、英語UIのみの1行表示は
# 中間サイズ)。座標は1600x1024基準(このファイルの他の_mock_rectと同じ)。
_CARD_JA_PX = 26
_CARD_EN_SUB_PX = 15
_CARD_EN_ONLY_PX = 22

_BUTTONS = [
    ("送信", "Transmit", "tx"),
    ("受信", "Receive", "rx"),
    ("周波数", "Frequency", "frequency"),
    ("RSSI測定", "RSSI Measurement", "rssi"),
    ("シンボルレート", "Symbol Rate", "symbolrate"),
    ("誤り訂正", "FEC", "fec"),
    ("変調方式", "Modulation", "modulation"),
    ("映像ソース", "Video Source", "videosource"),
    ("出力設定", "Stream Output", "streamoutput"),
    ("RXゲイン", "RX Gain", "rxgain"),
    ("TX出力", "TX Power", "txpower"),
    ("設定", "Config", "settings"),
    ("機器試験", "Diagnostic", "testequipment"),
    ("ヘルプ", "Help", "manual"),
    ("アプリ再起動", "App Restart", "pluto_reboot"),
    ("電源オフ", "Power Off", "shutdown"),
    ("Langstone", "SDR Transceiver", "langstone"),
    ("プリセット", "Presets", "presets"),
    ("Pluto電源", "Pluto Power", "pluto_power_cycle"),
]

# Pluto+のdatvplutofrmファームウェアの既定rootクレデンシャル(Dropbear SSH)。
_PLUTO_SSH_USER = "root"
_PLUTO_SSH_PASSWORD = "analog"

# ★Langstone V3(pi5/third_party/Langstone-V3、g4eml氏のSDRトランシーバー)は
# Qt eglfsとは別に/dev/fb0を直接描画する独立アプリのため、同時稼働はできない。
# shonan-gui.service/langstone.service/shonan-boot-menu.serviceの3つは
# systemdのConflicts=で互いに排他制御されるため、切替はsystemctl startを
# 直接呼ぶだけでよくPi5自体のrebootは不要(pi5/scripts/install.sh 9/9参照)。
# マーカーファイルはConditionPathExistsとの整合のため引き続き作成/削除する
# (Langstone側の「GOTO SHONAN_LITE」ボタンはこのファイルを削除する。
# pi5/third_party/Langstone-V3/LangstoneGUI_Pluto.c参照)。
_LANGSTONE_BOOT_MARKER = Path.home() / ".pi5_boot_mode_langstone"


class PowerSymbolIcon(QtWidgets.QWidget):
    """電源オフ確認ダイアログ用の電源記号(丸に縦棒)アイコン。

    ★以前はUnicodeの電源記号"⏻"(U+23FB)をQLabelのテキストとして描画して
    いたが、この実機のフォント環境ではグリフが用意されておらず表示されない
    (ユーザー指摘により判明)。PlutoPowerCardの電源アイコンと同じ、円弧+
    縦線の自前描画に置き換え、フォント依存を無くす。
    """

    def __init__(self, color: str = "#e53935", parent=None) -> None:
        super().__init__(parent)
        self._color = color

    def paintEvent(self, _event) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        side = min(self.width(), self.height())
        margin = side * 0.15
        pen = QtGui.QPen(QtGui.QColor(self._color), max(2.0, side * 0.09),
                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        arc_rect = QtCore.QRectF(margin, margin, side - margin * 2, side - margin * 2)
        # ★一般的な電源記号(IEC 60417-5009相当)は、円の上部の切れ目がもう少し
        # 広く、縦線が円の上端と揃う(円からはみ出さない)。以前は切れ目20°・
        # 円の上端よりわずかに上まで線が飛び出しており、実物のイラストと
        # 微妙に異なっていた(ユーザー指摘)。切れ目を30°に広げ、線の上端を
        # 円の上端(margin)にちょうど揃え、下端は円の中心(50%)までにする。
        painter.drawArc(arc_rect, 105 * 16, 330 * 16)
        cx = self.width() / 2
        painter.drawLine(QtCore.QPointF(cx, margin),
                          QtCore.QPointF(cx, side * 0.5))
        painter.end()


class FecCheckIcon(QtWidgets.QWidget):
    """iPad版FECカードの円囲みチェックアイコン。"""

    def paintEvent(self, _event) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        margin = max(1, min(self.width(), self.height()) * 0.08)
        circle = QtCore.QRectF(
            margin, margin, self.width() - margin * 2, self.height() - margin * 2)
        pen = QtGui.QPen(QtGui.QColor("white"), max(1.5, self.width() * 0.07))
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(circle)
        check = QtGui.QPainterPath()
        check.moveTo(self.width() * 0.28, self.height() * 0.52)
        check.lineTo(self.width() * 0.45, self.height() * 0.68)
        check.lineTo(self.width() * 0.74, self.height() * 0.34)
        painter.drawPath(check)
        painter.end()


class PresetCard(QtWidgets.QWidget):
    def __init__(self, parent=None, english: bool = False) -> None:
        super().__init__(parent)
        self._english = english

    def paintEvent(self, _event) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.scale(self.width() / 322.0, self.height() / 107.0)
        inner = QtCore.QRectF(4, 4, 314, 99)
        fill = QtGui.QLinearGradient(inner.topLeft(), inner.bottomLeft())
        fill.setColorAt(0.0, QtGui.QColor("#071a2c"))
        fill.setColorAt(1.0, QtGui.QColor("#030b16"))
        painter.setBrush(QtGui.QBrush(fill))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(inner, 12, 12)

        icon_center = QtCore.QPointF(52, 52)
        painter.setPen(QtGui.QPen(QtGui.QColor("white"), 3, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        for y, x in ((icon_center.y() - 12, 45), (icon_center.y(), 58), (icon_center.y() + 12, 49)):
            painter.drawLine(QtCore.QPointF(30, y), QtCore.QPointF(73, y))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))
            painter.drawEllipse(QtCore.QPointF(x, y), 3.5, 3.5)

        # 通常カードの日本語タイトルと同じ見かけの大きさに合わせる。
        painter.setPen(QtGui.QColor("white"))
        # ★要望により、他カードより一回り大きく(26→30、16→18)する。
        if self._english:
            font = QtGui.QFont("Noto Sans CJK JP")
            font.setPixelSize(30)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(font)
            painter.drawText(QtCore.QRectF(108, 27, 205, 55),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "Presets")
        else:
            font = QtGui.QFont("Noto Sans CJK JP")
            font.setPixelSize(30)
            font.setWeight(QtGui.QFont.Thin)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(font)
            painter.drawText(QtCore.QRectF(108, 27, 205, 30),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "プリセット")
            small_font = QtGui.QFont("Noto Sans CJK JP")
            small_font.setPixelSize(18)
            small_font.setWeight(QtGui.QFont.Thin)
            small_font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(small_font)
            painter.drawText(QtCore.QRectF(108, 56, 205, 25),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "Presets")
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor("#247f9f"), 2))
        painter.drawRoundedRect(QtCore.QRectF(1, 1, 320, 105), 15, 15)
        painter.end()


class PlutoPowerCard(QtWidgets.QWidget):
    """PresetCardと同様、モック画像上の空きスロットに描画する電源サイクルカード。"""

    def __init__(self, parent=None, english: bool = False) -> None:
        super().__init__(parent)
        self._english = english

    def paintEvent(self, _event) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.scale(self.width() / 298.0, self.height() / 111.0)
        inner = QtCore.QRectF(4, 4, 290, 103)
        fill = QtGui.QLinearGradient(inner.topLeft(), inner.bottomLeft())
        fill.setColorAt(0.0, QtGui.QColor("#071a2c"))
        fill.setColorAt(1.0, QtGui.QColor("#030b16"))
        painter.setBrush(QtGui.QBrush(fill))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(inner, 12, 12)

        # 電源アイコン(上部を開けた円弧+縦線。他画面の電源オフダイアログと同系統)。
        icon_center = QtCore.QPointF(48, 55)
        radius = 20.0
        pen = QtGui.QPen(QtGui.QColor("white"), 3, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        arc_rect = QtCore.QRectF(icon_center.x() - radius, icon_center.y() - radius,
                                  radius * 2, radius * 2)
        painter.drawArc(arc_rect, 100 * 16, 340 * 16)
        painter.drawLine(QtCore.QPointF(icon_center.x(), icon_center.y() - radius - 4),
                          QtCore.QPointF(icon_center.x(), icon_center.y() - 2))

        # ★文字サイズはPresetCard(同じ量産カードパターンの兄弟カード、要望により
        # 30px/18pxへ拡大済み)と揃える。
        painter.setPen(QtGui.QColor("white"))
        if self._english:
            font = QtGui.QFont("Noto Sans CJK JP")
            font.setPixelSize(30)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(font)
            painter.drawText(QtCore.QRectF(108, 22, 185, 34),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "Pluto Power")
            small_font = QtGui.QFont("Noto Sans CJK JP")
            small_font.setPixelSize(18)
            small_font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(small_font)
            painter.drawText(QtCore.QRectF(108, 58, 185, 26),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "Power Cycle")
        else:
            font = QtGui.QFont("Noto Sans CJK JP")
            font.setPixelSize(30)
            font.setWeight(QtGui.QFont.Thin)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(font)
            # ★"Pluto電源"を1つのdrawText()にまとめると、Latin("Pluto")と
            # CJK("電源")とでQtのフォールバックフォントの実際の文字送り幅が
            # ずれ、"電源"が"Pluto"の末尾に重なって描画される不具合が実機で
            # 確認された(このカード独自の不具合で、他カードはLatin/CJKが
            # 別行のため影響なし)。"Pluto"の実測幅を使って"電源"の開始位置を
            # 個別に計算し、確実に重ならないようにする。
            pluto_text = "Pluto"
            # ★QFontMetricsF(font)による幅計算は、この実機のフォールバック
            # フォント選択とずれるらしく、依然として重なりが解消しなかった
            # (実機screenshotで確認)。painter自身に実際に描画させた直後の
            # boundingRect()(同じデバイスコンテキストでの実測)に切り替え、
            # 更に安全マージンを追加する。
            pluto_rect = painter.boundingRect(
                QtCore.QRectF(108, 22, 300, 34),
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, pluto_text)
            pluto_width = pluto_rect.width() + 10
            painter.drawText(QtCore.QRectF(108, 22, pluto_width, 34),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, pluto_text)
            painter.drawText(QtCore.QRectF(108 + pluto_width, 22, 185 - pluto_width, 34),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "電源")
            small_font = QtGui.QFont("Noto Sans CJK JP")
            small_font.setPixelSize(18)
            small_font.setWeight(QtGui.QFont.Thin)
            small_font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            painter.setFont(small_font)
            painter.drawText(QtCore.QRectF(108, 58, 185, 26),
                             QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, "OFF→ON")
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor("#247f9f"), 2))
        painter.drawRoundedRect(QtCore.QRectF(1, 1, 296, 109), 15, 15)
        painter.end()


class HomeScreen(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("background-color: black;")
        self._mock_mode = False
        self._mock_canvas = None

        if self._build_illustrated_home():
            return

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 10)
        outer.setSpacing(6)

        title_row = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel(
            "Shonan_Lite <span style='font-size:9pt;'>for</span> RasPI5"
        )
        title.setStyleSheet(
            "color: white; font-size: 17pt; font-weight: bold; font-style: italic; "
            "font-family: 'DejaVu Serif', 'Times New Roman', serif;")
        title.setAlignment(QtCore.Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addStretch(1)
        version_label = QtWidgets.QLabel(f"Version {__version__}")
        version_label.setStyleSheet("color: white; font-size: 12px;")
        version_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        title_row.addWidget(version_label)
        outer.addLayout(title_row)

        subtitle = QtWidgets.QLabel("DVB-S2 DATV TRANSCEIVER")
        subtitle.setStyleSheet(
            "color: #8f9aaa; font-size: 9px; letter-spacing: 1px; "
            "font-weight: bold; padding-left: 2px;")
        outer.addWidget(subtitle)

        menu_panel = QtWidgets.QFrame()
        menu_panel.setObjectName("homeMenuPanel")
        menu_panel.setStyleSheet(
            "QFrame#homeMenuPanel { background-color: #11161d; "
            "border: 1px solid #293442; border-radius: 18px; }")
        panel_layout = QtWidgets.QVBoxLayout(menu_panel)
        panel_layout.setContentsMargins(14, 10, 14, 14)
        panel_layout.setSpacing(8)
        main_menu_label = QtWidgets.QLabel("Main Menu")
        main_menu_label.setStyleSheet(
            "color: #e9edf3; font-size: 13pt; font-weight: bold; "
            "padding-left: 3px;")
        panel_layout.addWidget(main_menu_label)

        grid_widget = QtWidgets.QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self._buttons = {}
        for i, (ja, en, route) in enumerate(_BUTTONS):
            btn = NavButton(ja, en)
            if route == "shutdown":
                btn.clicked.connect(self._on_shutdown_clicked)
            elif route == "pluto_reboot":
                btn.clicked.connect(self._on_app_restart_clicked)
            elif route == "langstone":
                btn.clicked.connect(self._on_langstone_clicked)
            elif route == "tx":
                # ホームの「送信」は送信画面を開くだけにする。
                # 実際の送信開始はTxScreenの「送信開始」ボタンでのみ行う。
                btn.clicked.connect(self._on_transmit_clicked)
            elif route == "pluto_power_cycle":
                btn.clicked.connect(self._on_pluto_power_cycle_clicked)
            else:
                btn.clicked.connect(lambda _, r=route: self.main_window.navigate_to(r))
            self._buttons[route] = btn
            grid.addWidget(btn, i // 4, i % 4, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        panel_layout.addWidget(grid_widget, 1)
        outer.addWidget(menu_panel, 1)

        datv_label = QtWidgets.QLabel("Digital Amateur TV System (DATV)")
        datv_label.setStyleSheet("color: white; font-size: 8pt;")
        datv_label.setAlignment(QtCore.Qt.AlignRight)
        outer.addWidget(datv_label)

    def _add_card_label(self, canvas, japanese: str, english_text: str, rect,
                         english_only: bool) -> QtWidgets.QLabel:
        """背景画像に焼き込まれたカード文字を隠し、Qtで描画し直す。

        日本語UIでは「日本語(大)+英語(小)」の2行、英語UIでは英語1行のみを表示し、
        全カードで同じフォントサイズ比になるようにする(_position_mock_home()で
        キャンバスサイズに応じてpxを再計算する)。
        """
        label = QtWidgets.QLabel(canvas)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel { background-color: rgba(3, 16, 34, 255); padding-left: 4px; }")
        label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        label._mock_rect = rect
        label._card_japanese = japanese
        label._card_english = english_text
        label._card_english_only = english_only
        self._mock_overlays.append(label)
        self._card_labels.append(label)
        return label

    def _build_illustrated_home(self) -> bool:
        """モック画像を表示し、その上に透明な実ボタンを重ねる。

        画像が配備されていない開発環境では従来のカードUIへフォールバックする。
        モックのカード文字・アイコンを背景として使うため、見た目を一致させながら
        タッチ領域だけをQtの実ボタンとして維持できる。
        """
        english = is_english(self.main_window.settings)
        images_dir = Path(__file__).resolve().parents[2] / "docs" / "images"
        image_path = images_dir / "home_illustrated_mockup_en.png" if english \
            else images_dir / "home_illustrated_mockup.png"
        if not image_path.exists():
            image_path = images_dir / "home_illustrated_mockup.png"
        if not image_path.exists():
            return False

        self._mock_mode = True
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        canvas = QtWidgets.QWidget(self)
        canvas.setStyleSheet("background-color: black;")
        self._mock_canvas = canvas
        background = QtWidgets.QLabel(canvas)
        background.setPixmap(QtGui.QPixmap(str(image_path)))
        background.setScaledContents(True)
        background.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self._mock_background = background

        # 背景画像に埋め込まれた旧FEC表示を一度隠し、iPad版のアイコンと文字を描く。
        # フォントサイズは背景画像に焼き込んだタイトル文字と見かけの大きさを
        # 揃えるため、_position_mock_home()でキャンバスの実サイズに応じて
        # 都度設定し直す(self._scaled_font_labelsに登録)。
        self._mock_overlays = []
        self._scaled_font_labels = []
        self._card_labels = []

        version_label = QtWidgets.QLabel(f"Version {__version__}", canvas)
        version_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        version_label.setStyleSheet(
            "QLabel { background: transparent; color: white; font-size: 14px; }"
        )
        version_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        version_label._mock_rect = (1300, 15, 280, 30)
        self._mock_overlays.append(version_label)

        restart_label = QtWidgets.QLabel("App Restart" if english else "アプリ再起動\nApp Restart", canvas)
        restart_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        restart_label.setStyleSheet(
            "QLabel { background-color: rgba(3, 16, 34, 255); color: white; padding-left: 4px; }"
        )
        restart_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        restart_label._mock_rect = (852, 593, 190, 96) if english else (850, 608, 205, 72)
        self._mock_overlays.append(restart_label)
        self._scaled_font_labels.append((restart_label, 22 if english else 26))

        fec_clear = QtWidgets.QLabel(canvas)
        fec_clear.setStyleSheet("background-color: rgba(3, 16, 34, 255);")
        fec_clear.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        fec_clear._mock_rect = (420, 322, 300, 108)
        self._mock_overlays.append(fec_clear)

        fec_icon = FecCheckIcon(canvas)
        fec_icon.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        # 上下のカードと同じ左寄せ基準へ合わせる。
        fec_icon._mock_rect = (450, 349, 44, 44)
        self._mock_overlays.append(fec_icon)

        self._add_card_label(canvas, "誤り訂正", "FEC", (505, 337, 160, 72), english)

        # ★JA版の背景画像には「437000 kHz」というプレースホルダー値が"Frequency"
        # サブタイトルごと焼き込まれているだけで、on_show()で実際の設定値に更新
        # する仕組みが無かった(通常レイアウトのNavButton.set_subtitle()相当が
        # mockモードには存在しなかった)。プレースホルダーをサブタイトルごと
        # 覆い隠し、"Frequency"+実際の周波数を都度描画し直す(値だけを部分的に
        # 覆うと焼き込み済みサブタイトルとの境界がずれて透けて見えるため)。
        # EN版の背景画像はタイトル直下が空きスロットのままなので、値のみを
        # 透明背景で追加描画すればよい。
        self._freq_value_label = QtWidgets.QLabel(canvas)
        self._freq_value_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # ★main.pyのアプリ全体スタイルシート(QWidget { ... font-size: 14px; })が
        # 全QWidgetに適用されるため、このラベル自身のスタイルシートに
        # font-sizeを書かない限りsetPixelSize()の指定は無視され、常に14pxで
        # 描画される(実機ログでfont().pixelSize()が常に14固定になることを
        # 確認済み)。他の重ね書きラベル(restart_label/fec_label)も同じ理由で
        # 実際は常に14px描画のため、タイトル行はここでも明示的に14pxを指定して
        # 揃える。kHz値の行だけは要望によりさらに一回り小さく(12px)する
        # ため、QLabelの<span>で行ごとに別サイズを指定する(setHtml不要、
        # QLabelはリッチテキストを自動判定して描画する)。
        if english:
            self._freq_value_label.setStyleSheet(
                "QLabel { background: transparent; color: white; padding-left: 4px; font-size: 14px; }"
            )
            # ★x=1075だと「周波数」カード(752-1050)の外、隣の「RSSI測定」カードの
            # 上に値が描画されてしまっていた(実機screenshotで発覚、本セッションの
            # 変更とは無関係の既存バグ)。「周波数」カード内に収まるx=850に修正。
            self._freq_value_label._mock_rect = (850, 236, 180, 40)
        else:
            self._freq_value_label.setStyleSheet(
                "QLabel { background-color: rgba(3, 16, 34, 255); color: white; padding-left: 4px; font-size: 14px; }"
            )
            # ★以前はx=776でアイコン(サイン波、実測で背景画像上のx≈788-841に
            # 相当)と文字が重なっていた(実機screenshotで確認)。同じ列幅の
            # 「アプリ再起動」カード(restart_label、x=850)に揃え、アイコンの
            # 右側に十分な余白を確保する。
            # ★幅210・高さ70だと、カード右端(x=1050)・下端(y=297)を超えて
            # このラベルの背景矩形がカードの角丸ボーダーの内側にまで
            # かかり、ボーダー線が矩形の分だけ欠けて見える不具合が実機で
            # 確認された。角丸の半径(15px相当)を避けられるよう、右端・
            # 下端ともカード境界より内側に収まる幅180・高さ58にする。
            self._freq_value_label._mock_rect = (850, 225, 180, 58)
        self._freq_value_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self._mock_overlays.append(self._freq_value_label)

        # ★背景画像に焼き込まれた「Langstone」タイトル(実測でx≈174-274,
        # y≈763-786相当、1600空間)を覆い隠し、要望により大きめの文字で
        # 再描画する。角丸コーナー(半径15px相当)を避けるため、カード
        # (68,728,322,111)の右端・下端より内側に収める。
        langstone_title_label = QtWidgets.QLabel("Langstone", canvas)
        langstone_title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        langstone_title_label.setStyleSheet(
            "QLabel { background-color: rgba(3, 16, 34, 255); color: white;"
            " padding-left: 4px; font-size: 17px; }"
        )
        langstone_title_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        # ★20px/18pxだと"Langstone"9文字がラベル幅に収まらず末尾が見切れた
        # (実機screenshotで確認)。17pxに落とし、アイコンとの余白も詰めて
        # カード右端の角丸コーナー(半径15px相当、右端390-15=375が安全域)
        # ぎりぎりまで幅を広げる。
        langstone_title_label._mock_rect = (150, 748, 225, 40)
        self._mock_overlays.append(langstone_title_label)

        preset_card = PresetCard(canvas, english=english)
        preset_card.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        preset_card._mock_rect = (414, 728, 322, 111)
        self._mock_overlays.append(preset_card)

        # 「Langstone」「プリセット」の右側(752,728)はモック画像上まだ空きスロットの
        # ため、PresetCardと同じ要領でPlutoPowerCardを描画する。
        pluto_power_card = PlutoPowerCard(canvas, english=english)
        pluto_power_card.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        pluto_power_card._mock_rect = (752, 728, 298, 111)
        self._mock_overlays.append(pluto_power_card)

        # 背景画像に焼き込まれた旧「相手局検索/Find Station」表示を隠し、
        # 「RSSI測定/RSSI」に差し替える。アイコン(虫眼鏡)は焼き込みのまま流用し、
        # 文字部分だけを覆う。他カードとフォントサイズを揃えるため、カードが
        # 狭く"RSSI Measurement"は収まらないので"RSSI"に短縮する(正式名称は
        # 遷移先画面のタイトル・マニュアルに表示される。Windows版と同じ理由)。
        self._add_card_label(canvas, "RSSI測定", "RSSI", (1168, 198, 171, 87), english)

        # 背景画像に焼き込まれた他のカード文字も同じ手法でQt描画へ統一し、
        # 全カードでフォント・サイズ比(日本語大・英語小)を揃える(Windows版で
        # 実機確認済みの座標をこのモック画像の1600x1024基準に変換して流用)。
        for route, rect in {
            "tx": (165, 198, 210, 87),
            "rx": (509, 198, 208, 87),
            "symbolrate": (165, 331, 210, 87),
            "modulation": (857, 331, 187, 87),
            "videosource": (1168, 331, 171, 87),
            "streamoutput": (165, 466, 210, 87),
            "rxgain": (509, 466, 208, 87),
            "txpower": (857, 466, 187, 87),
            "settings": (1167, 466, 172, 87),
            "testequipment": (165, 600, 210, 86),
            "manual": (509, 600, 208, 86),
        }.items():
            ja, en = next((b[0], b[1]) for b in _BUTTONS if b[2] == route)
            self._add_card_label(canvas, ja, en, rect, english)

        # 座標は1600x1024のモック画像上。実画面サイズに応じてresizeEventで縮放する。
        card_rects = [
            (68, 186, 322, 111), (414, 186, 315, 111), (752, 186, 298, 111), (1075, 186, 267, 111),
            (68, 320, 322, 111), (414, 320, 315, 111), (752, 320, 298, 111), (1075, 320, 267, 111),
            (68, 454, 322, 111), (414, 454, 315, 111), (752, 454, 298, 111), (1075, 454, 267, 111),
            (68, 587, 322, 111), (414, 587, 315, 111), (752, 587, 298, 111), (1075, 587, 267, 111),
            (68, 728, 322, 111), (414, 728, 322, 111), (752, 728, 298, 111),
        ]
        self._buttons = {}
        for (ja, en, route), rect in zip(_BUTTONS, card_rects):
            btn = QtWidgets.QPushButton(canvas)
            btn.setFocusPolicy(QtCore.Qt.NoFocus)
            btn.setToolTip(f"{ja} / {en}")
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; }"
                "QPushButton:pressed { background: rgba(50, 110, 220, 45); border: 2px solid #4d8dff; }"
            )
            self._connect_home_action(btn, route)
            self._buttons[route] = btn
            btn._mock_rect = rect
        outer.addWidget(canvas, 1)
        self._position_mock_home()
        return True

    def _connect_home_action(self, btn: QtWidgets.QPushButton, route: str) -> None:
        if route == "shutdown":
            btn.clicked.connect(self._on_shutdown_clicked)
        elif route == "pluto_reboot":
            btn.clicked.connect(self._on_app_restart_clicked)
        elif route == "langstone":
            btn.clicked.connect(self._on_langstone_clicked)
        elif route == "tx":
            btn.clicked.connect(self._on_transmit_clicked)
        elif route == "pluto_power_cycle":
            btn.clicked.connect(self._on_pluto_power_cycle_clicked)
        else:
            btn.clicked.connect(lambda _, r=route: self.main_window.navigate_to(r))

    def _position_mock_home(self) -> None:
        if self._mock_canvas is None:
            return
        width = max(1, self._mock_canvas.width())
        height = max(1, self._mock_canvas.height())
        self._mock_background.setGeometry(0, 0, width, height)
        for overlay in self._mock_overlays:
            x, y, w, h = overlay._mock_rect
            overlay.setGeometry(round(x * width / 1600), round(y * height / 1024),
                                round(w * width / 1600), round(h * height / 1024))
        for btn in self._buttons.values():
            x, y, w, h = btn._mock_rect
            btn.setGeometry(round(x * width / 1600), round(y * height / 1024),
                            round(w * width / 1600), round(h * height / 1024))
        # 背景画像に焼き込んだタイトル文字も画面サイズに応じて拡大縮小されるため、
        # このオーバーレイの文字サイズもキャンバス幅に比例させて見かけを揃える。
        for entry in getattr(self, "_scaled_font_labels", []):
            # ★以前はどのラベルも一律max(10, ...)でフロアしていたため、周波数
            # カードの数字だけ小さくしようとしてもbase_pxを下げた効果が
            # フロアに吸収され、実機で見た目がまったく変わらない不具合が
            # あった。ラベルごとに最小サイズを指定できるようにする。
            label, base_px, min_px = entry if len(entry) == 3 else (*entry, 10)
            font = label.font()
            font.setPixelSize(max(min_px, round(base_px * width / 1600)))
            label.setFont(font)

        # ホームカードの文字(_add_card_label): 日本語UIは「日本語(大)+英語(小)」の
        # 2行、英語UIは英語1行のみをリッチテキストで描画し、全カードで同じ
        # フォントサイズ比になるようにする。
        for label in getattr(self, "_card_labels", []):
            if label._card_english_only:
                px = max(10, round(_CARD_EN_ONLY_PX * width / 1600))
                label.setTextFormat(QtCore.Qt.RichText)
                label.setText(f'<span style="color:white; font-size:{px}px;">'
                              f'{label._card_english}</span>')
            else:
                px_ja = max(10, round(_CARD_JA_PX * width / 1600))
                px_en = max(8, round(_CARD_EN_SUB_PX * width / 1600))
                label.setTextFormat(QtCore.Qt.RichText)
                label.setText(f'<span style="color:white; font-size:{px_ja}px;">'
                              f'{label._card_japanese}</span><br>'
                              f'<span style="color:white; font-size:{px_en}px;">'
                              f'{label._card_english}</span>')

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_mock_home()

    def _on_transmit_clicked(self) -> None:
        """送信画面へ移動するだけで、TXプロセスは起動しない。"""
        self.main_window.navigate_to("tx")

    def _on_shutdown_clicked(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("電源オフ")
        dialog.setModal(True)
        dialog.setFixedSize(560, 320)
        dialog.setStyleSheet("QDialog { background: #101416; color: white; } QLabel { color: white; }")
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        icon = PowerSymbolIcon("#e53935")
        icon.setFixedSize(72, 72)
        icon_row = QtWidgets.QHBoxLayout()
        icon_row.addStretch(1)
        icon_row.addWidget(icon)
        icon_row.addStretch(1)
        layout.addLayout(icon_row)
        message = QtWidgets.QLabel("システムの電源をオフにします。\nよろしいですか？")
        message.setAlignment(QtCore.Qt.AlignCenter)
        message.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(message)
        buttons = QtWidgets.QHBoxLayout()
        shutdown = QtWidgets.QPushButton("電源をオフにする")
        cancel = QtWidgets.QPushButton("キャンセル")
        shutdown.setMinimumHeight(44)
        cancel.setMinimumHeight(44)
        shutdown.setStyleSheet("QPushButton { background: #e53935; color: white; border: none; border-radius: 6px; padding: 6px 18px; font-weight: bold; }")
        cancel.setStyleSheet("QPushButton { background-color: #14235c; color: white; border: 1px solid #3b5159; border-radius: 6px; padding: 6px 18px; font-weight: bold; } QPushButton:pressed { background-color: #0c1638; }")
        shutdown.clicked.connect(dialog.accept)
        cancel.clicked.connect(dialog.reject)
        buttons.addWidget(shutdown)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        try:
            subprocess.Popen(["sudo", "shutdown", "-h", "now"])
        except OSError as exc:
            error_dialog(self, "シャットダウン失敗", str(exc))

    def _on_pluto_reboot_clicked(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Pluto再起動")
        dialog.setModal(True)
        dialog.setFixedSize(560, 320)
        dialog.setStyleSheet("QDialog { background: #101416; color: white; } QLabel { color: white; }")
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        icon = QtWidgets.QLabel("⟳")
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setStyleSheet("color: #0c9bc0; font-size: 72px; font-weight: bold;")
        layout.addWidget(icon)
        message = QtWidgets.QLabel("Pluto SDRを再起動します。\nよろしいですか？")
        message.setAlignment(QtCore.Qt.AlignCenter)
        message.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(message)
        buttons = QtWidgets.QHBoxLayout()
        reboot = QtWidgets.QPushButton("再起動する")
        cancel = QtWidgets.QPushButton("キャンセル")
        for button in (reboot, cancel):
            button.setMinimumHeight(44)
            button.setStyleSheet("QPushButton { border: 1px solid #3b5159; border-radius: 6px; padding: 6px 18px; font-weight: bold; } QPushButton:pressed { background: #0c9bc0; }")
            buttons.addWidget(button)
        reboot.setStyleSheet("QPushButton { background: #0c9bc0; color: white; border: none; border-radius: 6px; padding: 6px 18px; font-weight: bold; }")
        reboot.clicked.connect(dialog.accept)
        cancel.clicked.connect(dialog.reject)
        layout.addLayout(buttons)
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        try:
            self._reboot_pluto()
        except OSError as exc:
            error_dialog(self, "Pluto再起動失敗", str(exc))

    def _on_pluto_power_cycle_clicked(self) -> None:
        """PA_Power/PTTコントローラ(ESP32)のGPIO26(12V電源)をOFF→3秒待ち→ONする
        (Pluto+含む12V系統全体の電源サイクル)。"""
        host = self.main_window.settings.ptt_controller_host
        if not host:
            error_dialog(
                self, "PTTコントローラ未設定",
                "設定画面でPA_Power/PTTコントローラ(ESP32)のIPアドレスを設定してください。")
            return
        try:
            _send_ptt_channel_state(host, PTT_CHANNEL_POWER, "off")
        except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
            error_dialog(self, "Pluto電源OFF失敗", str(exc))
            return
        QtCore.QTimer.singleShot(3000, lambda: self._pluto_power_on(host))

    def _pluto_power_on(self, host: str) -> None:
        try:
            _send_ptt_channel_state(host, PTT_CHANNEL_POWER, "on")
        except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
            error_dialog(self, "Pluto電源ON失敗", str(exc))

    def _on_app_restart_clicked(self) -> None:
        """iPad版と同じソフトリスタートをMainWindowへ依頼する。"""
        self.main_window.restart_app()

    def _on_langstone_clicked(self) -> None:
        try:
            # ★以前はPi5自体もrebootしていたが、shonan-boot-menu.service導入後は
            # shonan-gui.service/langstone.service/shonan-boot-menu.serviceが
            # systemdのConflicts=で互いに排他制御されるため、systemctl startを
            # 直接呼ぶだけで切り替わる(Pi5自体はrebootしない。呼び出すと現在
            # 稼働中のこのプロセス自体はsystemdに自動停止される)。Pluto+側だけは
            # 切替のたびに必ずreboot して、IIOコンテキストが詰まった状態のまま
            # Langstone側のGNU Radioフローグラフが起動しない不具合(実機で確認)を
            # 避ける。
            try:
                self._reboot_pluto(wait=True)
            except subprocess.TimeoutExpired:
                pass  # 届いていなくても切替は進める
            # ★Langstone V3自身は12V電源(GPIO26)に触れないため、切替時に
            # ここで明示的にONを送っておく(Langstone側の送信でPA電源が
            # 入っていない、という事態を避ける)。
            host = self.main_window.settings.ptt_controller_host
            if host:
                try:
                    _send_ptt_channel_state(host, PTT_CHANNEL_POWER, "on")
                except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
                    print(f"[MCU1] GPIO26 ON通知に失敗しました(Langstone切替): {exc}", flush=True)
            _LANGSTONE_BOOT_MARKER.touch()
            subprocess.Popen(["sudo", "/bin/systemctl", "start", "--no-block", "langstone.service"])
        except OSError as exc:
            error_dialog(self, "Langstone起動失敗", str(exc))

    def _reboot_pluto(self, wait: bool = False) -> None:
        # ★アプリ切替時にPluto+を毎回rebootして必ずクリーンな状態にする。
        # Pluto+はTX/RXを繰り返した後、IIOコンテキストが詰まったような状態
        # (fmcomms2_source: Unable to refill buffer: Connection timed out)
        # になることがあり、その状態のままLangstone側のGNU Radioフローグラフを
        # 起動すると永久に「Restarting GNU Radio」を繰り返し動作しない
        # (実機で確認・Pluto+ rebootで解消)。
        pluto_uri = self.main_window.settings.pluto_uri
        prefix = "ip:"
        host = pluto_uri[len(prefix):] if pluto_uri.startswith(prefix) else pluto_uri
        cmd = [
            "sshpass", "-p", _PLUTO_SSH_PASSWORD,
            "ssh",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=6",
            "-o", "PreferredAuthentications=password",
            "-o", "PubkeyAuthentication=no",
            f"{_PLUTO_SSH_USER}@{host}",
            "reboot",
        ]
        if wait:
            # Langstone起動直後、Conflicts=によりこのshonan-gui.serviceプロセス
            # 自体がsystemdに停止させられる(Pi5自体はrebootしない)。停止される
            # 前にSSHコマンドの送信が完了する(=実際にPluto+へ届く)ことを保証する
            # ためここで待つ。接続失敗時も(最大ConnectTimeout=6秒程度で)
            # 戻ってきてから先へ進む。
            subprocess.run(cmd, timeout=10)
        else:
            subprocess.Popen(cmd)

    def on_show(self) -> None:
        settings = self.main_window.settings
        lo_hz = settings.effective_lo_hz()
        if lo_hz is not None:
            value_text = f"{lo_hz / 1000:.0f} kHz"
        else:
            value_text = "Not Set" if is_english(settings) else "未設定"
        if self._mock_mode:
            if is_english(settings):
                self._freq_value_label.setText(
                    f"<span style='font-size:12px;'>{value_text}</span>")
            else:
                self._freq_value_label.setText(
                    f"<span style='font-size:12px;'>Frequency</span><br>"
                    f"<span style='font-size:12px;'>{value_text}</span>")
        else:
            self._buttons["frequency"].set_subtitle(value_text)


def create(main_window) -> QtWidgets.QWidget:
    return HomeScreen(main_window)
