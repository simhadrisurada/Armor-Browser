import sys
import os
from urllib.parse import quote
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QTabWidget,
                             QToolBar, QFileDialog, QMessageBox, QGraphicsOpacityEffect,
                             QComboBox, QProgressBar, QWidget, QHBoxLayout,
                             QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy,
                             QScrollArea)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (QWebEngineSettings, QWebEngineProfile,
                                   QWebEnginePage)
from PyQt6.QtCore import (QUrl, Qt, QPropertyAnimation, QEasingCurve,
                          QTimer, pyqtSignal, QPoint, QThread, pyqtSlot,
                          QObject)
from PyQt6.QtGui import QAction, QFont, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import requests
import hashlib
import random
import string
# ============================================================
#  LOGIN CREDENTIALS + UID
# ============================================================
UID = ""
INTERCEPT_API_BASE = "http://127.0.0.1:8888/"

DOWNLOAD_EXTENSIONS = (
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".mp3", ".mp4", ".wav", ".avi", ".mkv", ".mov",
    ".iso", ".img", ".apk", ".ipa",
)
def randomise(str):
    salt = ''.join(random.choices(string.digits, k=5))
    str = str + salt
    return encode(str)
def is_download_link(url: str) -> bool:
    path = QUrl(url).path().lower()
    return any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS)
def get_the_response(code) :
    url = "http://127.0.0.1:8000/?text=" + code
    return requests.get(url).text
def encode(data):
    return hashlib.sha256(data.encode()).hexdigest()
# ============================================================
#  ASYNC API FETCHER
# ============================================================
class ApiFetcher(QObject):
    image_ready = pyqtSignal(bytes)
    fetch_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)

    def fetch(self, target_url: str):
        encoded = quote(target_url, safe="")
        api_url = QUrl(INTERCEPT_API_BASE + encoded)
        request = QNetworkRequest(api_url)
        reply = self._nam.get(request)
        reply.finished.connect(lambda: self._on_reply(reply))

    def _on_reply(self, reply: QNetworkReply):
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.fetch_error.emit(reply.errorString())
        else:
            data = bytes(reply.readAll())
            self.image_ready.emit(data)
        reply.deleteLater()


# ============================================================
#  INTERCEPT SIDE PANEL
# ============================================================
class InterceptSidePanel(QFrame):
    decision = pyqtSignal(bool)

    _PANEL_WIDTH = 340

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("interceptPanel")
        self.setFixedWidth(self._PANEL_WIDTH)
        self.hide()

        self._fetcher = ApiFetcher(self)
        self._fetcher.image_ready.connect(self._show_image)
        self._fetcher.fetch_error.connect(self._show_error)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        hdr = QHBoxLayout()
        shield = QLabel("🛡️")
        shield.setObjectName("panelShield")
        title = QLabel("INTERCEPT ACTIVE")
        title.setObjectName("panelTitle")
        hdr.addWidget(shield)
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("panelDivider")
        root.addWidget(divider)

        url_lbl = QLabel("INTERCEPTED URL")
        url_lbl.setObjectName("panelFieldLbl")
        root.addWidget(url_lbl)

        self.url_display = QLabel()
        self.url_display.setObjectName("panelUrlDisplay")
        self.url_display.setWordWrap(True)
        self.url_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.url_display)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setObjectName("panelDivider")
        root.addWidget(divider2)

        api_lbl = QLabel("API SCAN RESULT")
        api_lbl.setObjectName("panelFieldLbl")
        root.addWidget(api_lbl)

        scroll = QScrollArea()
        scroll.setObjectName("panelScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(260)

        self._image_container = QWidget()
        self._image_container.setObjectName("panelImgContainer")
        img_layout = QVBoxLayout(self._image_container)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_lbl = QLabel("Fetching scan result...")
        self._status_lbl.setObjectName("panelStatus")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setWordWrap(True)

        self._image_lbl = QLabel()
        self._image_lbl.setObjectName("panelImage")
        self._image_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_lbl.hide()

        img_layout.addWidget(self._status_lbl)
        img_layout.addWidget(self._image_lbl)
        scroll.setWidget(self._image_container)
        root.addWidget(scroll)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.allow_btn = QPushButton("ALLOW")
        self.allow_btn.setObjectName("panelAllowBtn")
        self.allow_btn.setFixedHeight(46)
        self.allow_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.allow_btn.clicked.connect(self._allow)

        self.block_btn = QPushButton("BLOCK")
        self.block_btn.setObjectName("panelBlockBtn")
        self.block_btn.setFixedHeight(46)
        self.block_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.block_btn.clicked.connect(self._block)

        btn_row.addWidget(self.allow_btn)
        btn_row.addWidget(self.block_btn)
        root.addLayout(btn_row)

        self.setStyleSheet("""
            QFrame#interceptPanel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0b1023, stop:1 #07091a);
                border-left: 3px solid #8b5cf6;
                border-top: 1px solid #1e2a4a;
            }
            QLabel#panelShield { font-size: 20px; }
            QLabel#panelTitle {
                font-family: 'Courier New'; font-size: 11px; font-weight: 900;
                letter-spacing: 4px; color: #a78bfa;
            }
            QFrame#panelDivider {
                color: #1e2a4a; background: #1e2a4a; max-height: 1px;
            }
            QLabel#panelFieldLbl {
                font-family: 'Courier New'; font-size: 9px; letter-spacing: 3px;
                color: #3b82f6; font-weight: 700;
            }
            QLabel#panelUrlDisplay {
                font-family: 'Courier New'; font-size: 10px; color: #c4d4f0;
                background: #040d18; border: 1px solid #1e2a4a;
                border-left: 3px solid #3b82f6; border-radius: 3px; padding: 8px 10px;
            }
            QScrollArea#panelScroll {
                background: transparent; border: 1px solid #1e2a4a; border-radius: 6px;
            }
            QWidget#panelImgContainer { background: #040d18; }
            QLabel#panelStatus {
                font-family: 'Courier New'; font-size: 11px; color: #64748b; padding: 20px;
            }
            QLabel#panelImage { padding: 6px; }
            QPushButton#panelAllowBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #064e3b, stop:1 #065f46);
                color: #6ee7b7; border: 1px solid #059669; border-radius: 4px;
                font-family: 'Courier New'; font-size: 11px; font-weight: 900;
                letter-spacing: 2px;
            }
            QPushButton#panelAllowBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #065f46, stop:1 #047857);
                color: #a7f3d0; border-color: #34d399;
            }
            QPushButton#panelAllowBtn:pressed { background: #022c22; }
            QPushButton#panelBlockBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #450a0a, stop:1 #7f1d1d);
                color: #fca5a5; border: 1px solid #ef4444; border-radius: 4px;
                font-family: 'Courier New'; font-size: 11px; font-weight: 900;
                letter-spacing: 2px;
            }
            QPushButton#panelBlockBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7f1d1d, stop:1 #991b1b);
                color: #fecaca; border-color: #f87171;
            }
            QPushButton#panelBlockBtn:pressed { background: #300505; }
        """)

    def show_for_url(self, url: str, parent_rect):
        self._image_lbl.hide()
        self._image_lbl.clear()
        self._status_lbl.setText("Fetching scan result...")
        self._status_lbl.show()
        self.allow_btn.setEnabled(True)
        self.block_btn.setEnabled(True)

        self.url_display.setText(randomise(url))

        toolbar_h = 75
        panel_h = parent_rect.height() - toolbar_h
        self.setFixedHeight(panel_h)
        self.move(parent_rect.width() - self._PANEL_WIDTH, toolbar_h)
        self.raise_()
        self.show()

        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(280)
        anim.setStartValue(QPoint(parent_rect.width(), toolbar_h))
        anim.setEndValue(QPoint(parent_rect.width() - self._PANEL_WIDTH, toolbar_h))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._slide_anim = anim

        self._fetcher.fetch(url)

    def _show_image(self, data: bytes):
        pixmap = QPixmap()
        loaded = pixmap.loadFromData(data)
        if loaded and not pixmap.isNull():
            max_w = self._PANEL_WIDTH - 36
            if pixmap.width() > max_w:
                pixmap = pixmap.scaledToWidth(max_w, Qt.TransformationMode.SmoothTransformation)
            self._status_lbl.hide()
            self._image_lbl.setPixmap(pixmap)
            self._image_lbl.show()
        else:
            self._status_lbl.setText("API returned data that could not be rendered as an image.")

    def _show_error(self, msg: str):
        self._status_lbl.setText(f"API Error:\n{msg}")

    def _allow(self):
        self._emit_decision(True)

    def _block(self):
        self._emit_decision(False)

    def _emit_decision(self, allow: bool):
        start_x = self.x()
        end_x = start_x + self._PANEL_WIDTH
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(220)
        anim.setStartValue(QPoint(start_x, self.y()))
        anim.setEndValue(QPoint(end_x, self.y()))
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.hide)
        anim.finished.connect(lambda: self.decision.emit(allow))
        anim.start()
        self._close_anim = anim
        self.allow_btn.setEnabled(False)
        self.block_btn.setEnabled(False)


# ============================================================
#  LOGIN SCREEN
# ============================================================
class LoginScreen(QWidget):
    login_success = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyArmor Browser — Login")
        self.setFixedSize(1500, 950)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        bg = QWidget()
        bg.setObjectName("bg")
        bg_layout = QVBoxLayout(bg)
        bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(bg)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(480, 570)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 48, 48, 48)
        card_layout.setSpacing(16)
        bg_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("🛡️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setObjectName("shieldIcon")

        title = QLabel("ARMOR VIEW")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("titleLabel")

        subtitle = QLabel("Secure Browser Login")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitleLabel")

        user_label = QLabel("Username")
        user_label.setObjectName("fieldLabel")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setObjectName("inputField")
        self.username_input.setFixedHeight(48)

        pass_label = QLabel("Password")
        pass_label.setObjectName("fieldLabel")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("inputField")
        self.password_input.setFixedHeight(48)
        self.password_input.returnPressed.connect(self.attempt_login)

        self.uid_label = QLabel("")
        self.uid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uid_label.setObjectName("uidLabel")
        self.uid_label.hide()

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setObjectName("errorLabel")
        self.error_label.hide()

        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFixedHeight(52)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.attempt_login)

        card_layout.addWidget(icon_label)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(user_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(pass_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.uid_label)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.login_btn)

        self.setStyleSheet("""
            QWidget#bg {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #05050a, stop:0.4 #0d0022, stop:0.6 #001133, stop:1 #05050a);
            }
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0b1023, stop:0.5 #0a0d1f, stop:1 #07091a);
                border: 0px; border-top: 4px solid #8b5cf6;
                border-right: 1px solid #1e2a4a; border-bottom: 1px solid #1e2a4a;
                border-left: 6px solid #3b82f6; border-radius: 4px;
            }
            QLabel#shieldIcon { font-size: 52px; padding-bottom: 2px; }
            QLabel#titleLabel {
                font-family: 'Courier New'; font-size: 26px; font-weight: 900;
                letter-spacing: 10px; color: #a78bfa;
            }
            QLabel#subtitleLabel {
                font-family: 'Courier New'; font-size: 11px; letter-spacing: 4px;
                color: #334155; margin-bottom: 4px; padding: 6px 0px;
                border-bottom: 1px solid #1e293b;
            }
            QLabel#fieldLabel {
                font-family: 'Courier New'; font-size: 10px; letter-spacing: 3px;
                color: #3b82f6; font-weight: 700; padding-left: 2px;
            }
            QLineEdit#inputField {
                background-color: #080d1c; color: #c4d4f0;
                border: 1px solid #1e2a4a; border-left: 3px solid #1e3a6e;
                border-radius: 3px; padding: 8px 14px;
                font-family: 'Courier New'; font-size: 13px; letter-spacing: 1px;
                selection-background-color: #3b82f6;
            }
            QLineEdit#inputField:focus {
                border: 1px solid #3b82f6; border-left: 3px solid #a78bfa;
                background-color: #0c1428; color: #e8f0ff;
            }
            QLabel#uidLabel {
                color: #00bfff; font-family: 'Courier New'; font-size: 11px;
                letter-spacing: 2px; padding: 8px 14px; background: #040d18;
                border: 1px solid #003a55; border-left: 3px solid #00bfff; border-radius: 3px;
            }
            QLabel#errorLabel {
                color: #f87171; font-family: 'Courier New'; font-size: 11px;
                letter-spacing: 2px; padding: 6px 10px; background: #1a0a0a;
                border: 1px solid #3a1010; border-left: 3px solid #f87171; border-radius: 3px;
            }
            QPushButton#loginBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b0d8c, stop:0.5 #1d4ed8, stop:1 #3b0d8c);
                color: #c4d4ff; border: 0px;
                border-top: 1px solid #8b5cf6; border-bottom: 1px solid #3b82f6;
                border-radius: 3px; font-family: 'Courier New';
                font-size: 13px; font-weight: 900; letter-spacing: 6px;
            }
            QPushButton#loginBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5b21b6, stop:0.5 #2563eb, stop:1 #5b21b6);
                color: #ffffff;
                border-top: 1px solid #a78bfa; border-bottom: 1px solid #60a5fa;
            }
            QPushButton#loginBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e0870, stop:0.5 #1d40af, stop:1 #1e0870);
                color: #a0b4e8; border-top: 1px solid #6d28d9;
            }
        """)

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text() 
        code = encode(encode(username + password))
        #print(code)
        u1,u2 = get_the_response(code).split(":")
        #print(encode(code + u2))
        #print(u2)
        if u1 == encode(code + u2):
            self.error_label.hide()
            self.uid_label.setText(f"Account UID: {u2}")
            self.uid_label.show()
            self.login_btn.setEnabled(False)
            QTimer.singleShot(1000, lambda: self.login_success.emit(username, u2))
        else:
            self.uid_label.hide()
            self.error_label.setText("Invalid username or password.")
            self.error_label.show()
            self.password_input.clear()
            self.password_input.setFocus()
            self._shake()

    def _shake(self):
        card = self.findChild(QFrame, "card")
        if not card:
            return
        anim = QPropertyAnimation(card, b"pos")
        anim.setDuration(300)
        orig = card.pos()
        anim.setKeyValueAt(0,    orig)
        anim.setKeyValueAt(0.15, orig.__class__(orig.x() - 10, orig.y()))
        anim.setKeyValueAt(0.30, orig.__class__(orig.x() + 10, orig.y()))
        anim.setKeyValueAt(0.45, orig.__class__(orig.x() - 8,  orig.y()))
        anim.setKeyValueAt(0.60, orig.__class__(orig.x() + 8,  orig.y()))
        anim.setKeyValueAt(0.75, orig.__class__(orig.x() - 4,  orig.y()))
        anim.setKeyValueAt(1.0,  orig)
        anim.start()
        self._shake_anim = anim


# ============================================================
#  SHARE PANEL
# ============================================================
class SharePanel(QFrame):
    navigate_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sharePanel")
        self.setFixedWidth(540)
        self.setFixedHeight(172)
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        lbl1 = QLabel("Current URL")
        lbl1.setObjectName("shareLbl")
        lbl1.setFixedWidth(95)
        self.current_url_field = QLineEdit()
        self.current_url_field.setObjectName("shareReadField")
        self.current_url_field.setReadOnly(True)
        self.current_url_field.setPlaceholderText("No URL — home page active")
        self.current_url_field.setFixedHeight(38)
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setObjectName("shareCopyBtn")
        self.copy_btn.setFixedSize(72, 38)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_url)
        row1.addWidget(lbl1)
        row1.addWidget(self.current_url_field)
        row1.addWidget(self.copy_btn)

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        lbl2 = QLabel("Paste URL")
        lbl2.setObjectName("shareLbl")
        lbl2.setFixedWidth(95)
        self.paste_field = QLineEdit()
        self.paste_field.setObjectName("sharePasteField")
        self.paste_field.setPlaceholderText("Paste a URL here and press Go...")
        self.paste_field.setFixedHeight(38)
        self.paste_field.returnPressed.connect(self._go)
        self.go_btn = QPushButton("Go")
        self.go_btn.setObjectName("shareGoBtn")
        self.go_btn.setFixedSize(72, 38)
        self.go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.go_btn.clicked.connect(self._go)
        row2.addWidget(lbl2)
        row2.addWidget(self.paste_field)
        row2.addWidget(self.go_btn)

        layout.addLayout(row1)
        layout.addLayout(row2)

        self.setStyleSheet("""
            QFrame#sharePanel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1428, stop:1 #080d1c);
                border: 1px solid #2d3a5a; border-top: 3px solid #8b5cf6;
                border-radius: 0px 0px 10px 10px;
            }
            QLabel#shareLbl {
                color: #3b82f6; font-family: 'Courier New';
                font-size: 10px; letter-spacing: 2px; font-weight: 700;
            }
            QLineEdit#shareReadField {
                background: #050a14; color: #a78bfa;
                border: 1px solid #1e2a4a; border-left: 3px solid #8b5cf6;
                border-radius: 4px; padding: 4px 10px;
                font-family: 'Courier New'; font-size: 12px; letter-spacing: 1px;
            }
            QLineEdit#sharePasteField {
                background: #050a14; color: #e2e8f0;
                border: 1px solid #1e2a4a; border-left: 3px solid #3b82f6;
                border-radius: 4px; padding: 4px 10px;
                font-family: 'Courier New'; font-size: 12px;
            }
            QLineEdit#sharePasteField:focus {
                border: 1px solid #3b82f6; border-left: 3px solid #a78bfa;
                background: #0a1020;
            }
            QPushButton#shareCopyBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b0d8c, stop:1 #5b21b6);
                color: #e0d4ff; border: 1px solid #6d28d9; border-radius: 4px;
                font-family: 'Courier New'; font-size: 11px; font-weight: 700; letter-spacing: 1px;
            }
            QPushButton#shareCopyBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5b21b6, stop:1 #7c3aed); color: #ffffff;
            }
            QPushButton#shareCopyBtn:pressed { background: #2e0a6e; }
            QPushButton#shareGoBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8, stop:1 #2563eb);
                color: #dbeafe; border: 1px solid #3b82f6; border-radius: 4px;
                font-family: 'Courier New'; font-size: 11px; font-weight: 700; letter-spacing: 1px;
            }
            QPushButton#shareGoBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #3b82f6); color: #ffffff;
            }
            QPushButton#shareGoBtn:pressed { background: #1e40af; }
        """)

    def set_current_url(self, url: str):
        self.current_url_field.setText(randomise(url))
        self.paste_field.clear()

    def _copy_url(self):
        url = self.current_url_field.text().strip()
        if url:
            QApplication.clipboard().setText(url)
            self.copy_btn.setText("Copied")
            QTimer.singleShot(1500, lambda: self.copy_btn.setText("Copy"))

    def _go(self):
        url = self.paste_field.text().strip()
        if url:
            self.navigate_requested.emit(url)
            self.hide()


# ============================================================
#  WEB VIEW
# ============================================================
class SmoothWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_smooth_rendering()

    def _setup_smooth_rendering(self):
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

    def inject_smooth_scroll(self):
        js = """
        (function() {
            if (document.documentElement) {
                document.documentElement.style.scrollBehavior = 'smooth';
            }
        })();
        """
        self.page().runJavaScript(js)


class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(3)
        self.setTextVisible(False)
        self.setRange(0, 100)
        self.setValue(0)
        self.hide()
        self.setStyleSheet("""
            QProgressBar { background: transparent; border: none; border-radius: 0px; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:0.5 #3b82f6, stop:1 #00bfff);
                border-radius: 0px;
            }
        """)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._target = 0
        self._current = 0.0

    def start_loading(self):
        self._current = 0.0
        self._target = 30
        self.setValue(0)
        self.show()
        self._anim_timer.start(16)

    def set_progress(self, percent):
        self._target = percent

    def finish_loading(self):
        self._target = 100
        QTimer.singleShot(350, self.hide)
        QTimer.singleShot(350, lambda: self.setValue(0))

    def _tick(self):
        if self._current < self._target:
            diff = self._target - self._current
            step = max(0.5, diff * 0.08)
            self._current = min(self._current + step, self._target)
            self.setValue(int(self._current))
        if self._current >= 100:
            self._anim_timer.stop()


# ============================================================
#  MAIN BROWSER WINDOW
# ============================================================
class Browser(QMainWindow):
    def __init__(self, username: str = "", uid: str = ""):
        super().__init__()
        self.setWindowTitle("MyArmor Browser")
        self.setGeometry(100, 100, 1500, 950)

        self.profile = QWebEngineProfile("MyArmorStorage", self)
        self.profile.setPersistentStoragePath(os.path.join(os.getcwd(), "web_profile"))
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.setHttpCacheMaximumSize(100 * 1024 * 1024)
        self.profile.downloadRequested.connect(self.handle_download)

        self.setStyleSheet("""
            QMainWindow { background-color: #05050a; }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a0033, stop:1 #001a33);
                border-bottom: 1px solid #3b82f6; padding: 10px; spacing: 15px;
            }
            QToolButton {
                color: #ffffff; background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px; padding: 8px; font-weight: bold;
            }
            QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8a2be2, stop:1 #0077ff);
                border: 1px solid #00bfff;
            }
            QLineEdit {
                background-color: #0f172a; color: #e2e8f0;
                border: 2px solid #1e293b; border-radius: 15px; padding: 8px 15px;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: #1a1a2e; }
            QTabWidget::pane { border: none; background: #05050a; }
            QTabBar::tab {
                background: #1a1a2e; color: #94a3b8;
                padding: 12px 25px; margin-right: 5px;
                border-top-left-radius: 12px; border-top-right-radius: 12px;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5f00ff, stop:1 #1a0033);
                color: white; border-bottom: 2px solid #00bfff;
            }
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:1 #0f172a);
                color: #ffffff; border: 2px solid #334155;
                border-radius: 15px; padding: 8px 15px; min-width: 160px;
            }
            QComboBox:hover {
                border: 2px solid #8b5cf6;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #312e81, stop:1 #1e293b);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 35px; border-left: 1px solid #334155;
                border-top-right-radius: 15px; border-bottom-right-radius: 15px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none; border-left: 6px solid transparent;
                border-right: 6px solid transparent; border-top: 8px solid #8b5cf6;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a; border: 2px solid #8b5cf6;
                border-radius: 12px; padding: 6px;
                selection-background-color: #5f00ff;
                selection-color: white; color: #e2e8f0;
            }
            QLineEdit#navUidBadge {
                color: #00bfff; background: rgba(0,191,255,0.08);
                border: none; border-radius: 10px; padding: 5px 12px;
                font-family: 'Consolas'; font-size: 11px; letter-spacing: 1px;
            }
        """)

        self.home_identifier = "myarmor://home"
        self.intercept_enabled = False

        # Pending intercept state
        self._pending_intercept: dict | None = None

        # ── FIX: one-shot passthrough token ───────────────────
        # After the user clicks ALLOW in the side panel, we store
        # the approved URL here.  intercept_url() will pass it through
        # exactly ONCE (then clears it), so we never need to toggle
        # intercept_enabled on/off — which caused a race condition
        # that prevented navigation even when intercept was OFF.
        self._allowed_url: str | None = None

        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.setCentralWidget(central)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_url_on_tab_change)
        self.tabs.currentChanged.connect(self.animate_tab_change)
        central_layout.addWidget(self.tabs)

        self.progress_bar = AnimatedProgressBar(self)
        self.progress_bar.setFixedWidth(self.width())

        navbar = QToolBar()
        navbar.setFixedHeight(75)
        self.addToolBar(navbar)
        self._navbar = navbar

        font = QFont("Segoe UI", 12)

        for text, slot in [("◀", lambda: self.current_browser().back()),
                           ("▶", lambda: self.current_browser().forward()),
                           ("⟳", self.reload_page),
                           ("🏠", self.go_home),
                           ("➕", self.add_new_tab)]:
            action = QAction(text, self)
            action.setFont(font)
            action.triggered.connect(slot)
            navbar.addAction(action)

        self.intercept_action = QAction("🛡️ Intercept: OFF", self)
        self.intercept_action.setFont(font)
        self.intercept_action.setCheckable(True)
        self.intercept_action.triggered.connect(self.toggle_intercept)
        navbar.addAction(self.intercept_action)

        self.search_engine = QComboBox()
        self.search_engine.setFont(QFont("Segoe UI", 11))
        self.search_engine.setFixedHeight(45)
        self.search_engines = {
            "Google":     "https://www.google.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Bing":       "https://www.bing.com/search?q=",
            "Yahoo":      "https://search.yahoo.com/search?p=",
            "Brave":      "https://search.brave.com/search?q="
        }
        self.search_engine.addItems(self.search_engines.keys())
        navbar.addWidget(self.search_engine)

        self.url_bar = QLineEdit()
        self.url_bar.setFont(QFont("Consolas", 12))
        self.url_bar.setFixedHeight(45)
        self.url_bar.setPlaceholderText("Enter URL or Secure Search...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.share_action = QAction("📤 Share", self)
        self.share_action.setFont(font)
        self.share_action.triggered.connect(self._toggle_share_panel)
        navbar.addAction(self.share_action)

        if uid:
            uid_badge = QLineEdit(f"🔑 {username}  ·  {uid}")
            uid_badge.setObjectName("navUidBadge")
            uid_badge.setFont(QFont("Consolas", 10))
            uid_badge.setFixedHeight(38)
            uid_badge.setReadOnly(True)
            uid_badge.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            uid_badge.setCursor(Qt.CursorShape.ArrowCursor)
            navbar.addWidget(uid_badge)

        self.share_panel = SharePanel(self)
        self.share_panel.navigate_requested.connect(self._navigate_from_share)

        self.intercept_panel = InterceptSidePanel(self)
        self.intercept_panel.decision.connect(self._on_intercept_decision)

        self._tab_animations = {}
        self._fullscreen_view = None

        self.add_new_tab()

    # ──────────────────────────────────────────────────────────
    #  INTERCEPT LOGIC
    # ──────────────────────────────────────────────────────────

    def toggle_intercept(self, checked):
        self.intercept_enabled = checked
        self.intercept_action.setText(
            f"🛡️ Intercept: {'ON' if checked else 'OFF'}"
        )
        if not checked and self.intercept_panel.isVisible():
            self.intercept_panel.hide()
            self._pending_intercept = None
            self._allowed_url = None   # discard any stale token

    def intercept_url(self, navigation_type, url, is_main_frame):
        """
        Called by InterceptPage.acceptNavigationRequest().

        Decision tree
        ─────────────
        1. Home / blank URL          → always allow
        2. Intercept OFF             → always allow
        3. Sub-frame request         → always allow (only gate main frames)
        4. _allowed_url matches      → allow once, clear token  ← FIX
        5. Download link             → plain Yes/No dialog
        6. Everything else           → show side panel, block until decided
        """
        url_str = url.toString()

        # 1. Internal pages
        if url_str.startswith(self.home_identifier) or url_str in ("about:blank", ""):
            return True

        # 2. Intercept OFF — let everything through
        if not self.intercept_enabled:
            return True

        # 3. Sub-frames (ads, iframes, etc.) — never gate these
        if not is_main_frame:
            return True

        # 4. ── POST-ALLOW PASSTHROUGH (the core fix) ──────────
        #    When the user clicked ALLOW, _on_intercept_decision stored
        #    the target URL in self._allowed_url and called setUrl().
        #    That triggers acceptNavigationRequest again, so we must
        #    let that exact URL through once and then consume the token.
        if self._allowed_url and url_str == self._allowed_url:
            self._allowed_url = None
            return True

        # 5. Download link — synchronous dialog, no API call
        if is_download_link(url_str):
            reply = QMessageBox.question(
                self, "🛡️ Armor Shield — Download",
                f"Allow download from:\n\n{randomise(url_str)}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes

        # 6. Regular navigation — open side panel asynchronously
        self._pending_intercept = {"url": url_str}
        QTimer.singleShot(0, lambda: self._show_intercept_panel(url_str))
        return False   # block this attempt; re-navigate on ALLOW

    def _show_intercept_panel(self, url: str):
        self.intercept_panel.show_for_url(url, self.rect())

    @pyqtSlot(bool)
    def _on_intercept_decision(self, allow: bool):
        if not self._pending_intercept:
            return
        url = self._pending_intercept.get("url", "")
        self._pending_intercept = None

        if allow and url:
            # Store token → intercept_url will pass this URL through once
            self._allowed_url = url
            self.current_browser().setUrl(QUrl(url))
        # Blocked → do nothing, navigation already cancelled

    # ──────────────────────────────────────────────────────────
    #  SHARE PANEL
    # ──────────────────────────────────────────────────────────

    def _toggle_share_panel(self):
        self.share_panel.set_current_url(self.url_bar.text().strip())
        anchor = self._navbar.mapTo(self, QPoint(0, self._navbar.height()))
        self.share_panel.move(anchor)
        self.share_panel.raise_()
        if self.share_panel.isVisible():
            self.share_panel.hide()
        else:
            self.share_panel.show()
            self.share_panel.paste_field.setFocus()

    def _navigate_from_share(self, url: str):
        if "." not in url:
            base = self.search_engines[self.search_engine.currentText()]
            url = base + url
        elif not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))
        self.share_panel.hide()

    # ──────────────────────────────────────────────────────────
    #  WINDOW / TAB HELPERS
    # ──────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.progress_bar.setFixedWidth(self.width())
        self.progress_bar.move(0, 75)
        if self.intercept_panel.isVisible():
            panel_h = self.rect().height() - 75
            self.intercept_panel.setFixedHeight(panel_h)
            self.intercept_panel.move(
                self.width() - InterceptSidePanel._PANEL_WIDTH, 75
            )

    def handle_download(self, item):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", item.suggestedFileName())
        if path:
            item.setDownloadDirectory(os.path.dirname(path))
            item.setDownloadFileName(os.path.basename(path))
            item.accept()

    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()
        request.accept()

    def handle_feature_permission(self, page, url, feature):
        feature_names = {
            QWebEnginePage.Feature.MediaAudioCapture:        "Microphone",
            QWebEnginePage.Feature.MediaVideoCapture:        "Camera",
            QWebEnginePage.Feature.MediaAudioVideoCapture:   "Camera & Microphone",
            QWebEnginePage.Feature.Geolocation:              "Location",
            QWebEnginePage.Feature.DesktopVideoCapture:      "Screen Capture",
            QWebEnginePage.Feature.DesktopAudioVideoCapture: "Screen & Audio Capture",
        }
        name = feature_names.get(feature, "Unknown Permission")
        reply = QMessageBox.question(
            self, "Permission Request",
            f"{url.host()} wants to access your {name}.\n\nAllow?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        policy = (QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
                  if reply == QMessageBox.StandardButton.Yes
                  else QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)
        page.setFeaturePermission(url, feature, policy)

    def animate_tab_change(self, index):
        widget = self.tabs.widget(index)
        if widget:
            if index in self._tab_animations:
                try:
                    self._tab_animations[index].stop()
                except Exception:
                    pass
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)
            anim = QPropertyAnimation(opacity_effect, b"opacity")
            anim.setDuration(250)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutQuart)
            anim.start()
            self._tab_animations[index] = anim

    def add_new_tab(self):
        browser = SmoothWebEngineView()
        outer_self = self

        class InterceptPage(QWebEnginePage):
            def acceptNavigationRequest(self, url, nav_type, is_main_frame):
                return outer_self.intercept_url(nav_type, url, is_main_frame)

        page = InterceptPage(self.profile, browser)
        browser.setPage(page)
        browser.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        page.fullScreenRequested.connect(self.handle_fullscreen_request)
        page.featurePermissionRequested.connect(
            lambda url, feature, p=page: self.handle_feature_permission(p, url, feature)
        )
        browser.loadStarted.connect(lambda b=browser: self._on_load_start(b))
        browser.loadProgress.connect(lambda prog, b=browser: self._on_load_progress(prog, b))
        browser.loadFinished.connect(lambda ok, b=browser: self._on_load_finish(ok, b))
        browser.setHtml(self.home_html(), QUrl(self.home_identifier))
        i = self.tabs.addTab(browser, "New Secure Tab")
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_urlbar(qurl, b))

    def _on_load_start(self, browser):
        if browser == self.current_browser():
            self.progress_bar.start_loading()

    def _on_load_progress(self, progress, browser):
        if browser == self.current_browser():
            self.progress_bar.set_progress(progress)

    def _on_load_finish(self, ok, browser):
        if browser == self.current_browser():
            self.progress_bar.finish_loading()
        title = browser.page().title()
        idx = self.tabs.indexOf(browser)
        if idx >= 0:
            display = (title[:20] + "...") if len(title) > 20 else title or "New Secure Tab"
            self.tabs.setTabText(idx, display)
        browser.inject_smooth_scroll()

    def reload_page(self):
        self.current_browser().reload()

    def go_home(self):
        self.current_browser().setHtml(self.home_html(), QUrl(self.home_identifier))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            self.go_home()
            return
        if "." not in url:
            base = self.search_engines[self.search_engine.currentText()]
            url = base + url
        elif not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def sync_url_on_tab_change(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.update_urlbar(browser.url(), browser)
            if browser.url().toString() == "about:blank":
                self.progress_bar.hide()

    def update_urlbar(self, qurl, browser):
        if browser != self.current_browser():
            return
        url_str = qurl.toString()
        if url_str.startswith(self.home_identifier) or url_str == "about:blank":
            self.url_bar.setText("")
        else:
            self.url_bar.setText(randomise(url_str))

    def current_browser(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            if widget:
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity")
                anim.setDuration(150)
                anim.setStartValue(1.0)
                anim.setEndValue(0.0)
                anim.setEasingCurve(QEasingCurve.Type.InQuart)
                anim.finished.connect(lambda: self.tabs.removeTab(index))
                anim.start()
                self._close_anim = anim
            else:
                self.tabs.removeTab(index)

    def home_html(self):
        return """<!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; height: 100vh; display: flex; flex-direction: column;
                    justify-content: center; align-items: center;
                    font-family: 'Segoe UI', sans-serif;
                    background: radial-gradient(circle at center, #1a0033 0%, #05050a 100%);
                    color: #ffffff; overflow: hidden; position: relative; }
                .shield { position: absolute; width: 550px; height: 550px;
                    border-radius: 50%; display: flex; justify-content: center;
                    align-items: center; z-index: 0; }
                .shield::before { content: ""; position: absolute; width: 100%;
                    height: 100%; border-radius: 50%;
                    border: 4px dashed rgba(139, 92, 246, 0.3);
                    animation: rotateCounter 20s linear infinite; }
                .shield::after { content: ""; position: absolute; width: 85%;
                    height: 85%; border-radius: 50%;
                    border: 2px solid rgba(59, 130, 246, 0.1);
                    border-top: 4px solid rgba(168, 85, 247, 0.4);
                    border-bottom: 4px solid rgba(59, 130, 246, 0.4);
                    animation: rotateClockwise 10s linear infinite; }
                @keyframes rotateClockwise { 0%{transform:rotate(0deg)} 100%{transform:rotate(360deg)} }
                @keyframes rotateCounter  { 0%{transform:rotate(360deg)} 100%{transform:rotate(0deg)} }
                .glow-text { font-size: 50px; font-weight: 800; margin-bottom: 30px;
                    background: linear-gradient(90deg, #a855f7, #3b82f6);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    filter: drop-shadow(0 0 10px rgba(168,85,247,0.4));
                    position: relative; z-index: 1; }
                .search-container { display: flex; background: rgba(255,255,255,0.05);
                    padding: 15px; border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.1);
                    backdrop-filter: blur(20px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    position: relative; z-index: 1; }
                input { width: 450px; padding: 16px; font-size: 18px; border: none;
                    border-radius: 12px; outline: none; background: #0f172a;
                    color: white; transition: 0.3s; border: 1px solid #334155; }
                input:focus { border-color: #8b5cf6; box-shadow: 0 0 15px rgba(139,92,246,0.3); }
                button { padding: 14px 25px; font-size: 16px; margin-left: 12px;
                    border-radius: 12px; border: none; cursor: pointer;
                    background: linear-gradient(90deg, #8b5cf6, #3b82f6);
                    color: white; font-weight: bold; transition: 0.3s; }
            </style>
        </head>
        <body>
            <div class="shield"></div>
            <div class="glow-text">ARMOR VIEW ACTIVE</div>
            <div class="search-container">
                <input type="text" id="searchBox"
                    placeholder="Type a URL or search securely..." autofocus>
                <button onclick="search()">Search</button>
            </div>
            <script>
                function search() {
                    var query = document.getElementById("searchBox").value;
                    if(query.trim() !== "") {
                        window.location.href = query.includes('.') ?
                            (query.startsWith('http') ? query : "https://" + query) :
                            "https://www.google.com/search?q=" + encodeURIComponent(query);
                    }
                }
                document.getElementById("searchBox").addEventListener("keydown", function(e) {
                    if(e.key === "Enter") { search(); }
                });
            </script>
        </body>
        </html>"""


# ============================================================
#  APP ENTRY
# ============================================================
class App:
    def __init__(self):
        self.login_screen = LoginScreen()
        self.browser = None
        self.login_screen.login_success.connect(self.launch_browser)
        self.login_screen.show()

    def launch_browser(self, username: str, uid: str):
        self.browser = Browser(username=username, uid=uid)
        self.browser.show()
        self.login_screen.close()


if __name__ == "__main__":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-gpu-rasterization "
        "--enable-zero-copy "
        "--ignore-gpu-blocklist "
        "--enable-smooth-scrolling "
        "--enable-accelerated-2d-canvas "
        "--num-raster-threads=4 "
        "--disable-gpu-driver-bug-workarounds "
        "--enable-features=VaapiVideoDecodeLinuxGL,UseSkiaRenderer "
        "--enable-main-frame-before-activation "
        "--enable-quic "
        "--enable-tcp-fast-open "
        "--enable-features=NetworkServiceInProcess2"
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = app.font()
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    launcher = App()
    sys.exit(app.exec())