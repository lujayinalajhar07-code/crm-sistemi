"""
╔══════════════════════════════════════════════════════════════╗
║   🏢  BASİT CRM SİSTEMİ — Ultra-Modern PyQt5 GUI            ║
║   Glassmorphism + Dark Futuristic Aesthetic                  ║
║   Requires: PyQt5                                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import math
from datetime import datetime
from typing import Optional, List, Any
from crm_console import (
    CRMSistemi, Musteri, Satis, DestekTalebi, 
    SatisDurumu, TalepDurumu
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget,
    QGridLayout, QSpacerItem, QDialog, QDateTimeEdit, QSpinBox,
    QDoubleSpinBox, QMessageBox, QProgressBar, QScrollBar,
    QTextEdit
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSize, pyqtSignal, QThread, QDateTime,
    QParallelAnimationGroup
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QLinearGradient,
    QRadialGradient, QPixmap, QBrush, QPen, QFontDatabase,
    QConicalGradient, QPolygon, QIcon, QCursor
)

from pydantic import ValidationError


# ═══════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════

BG_DEEP    = "#050811"
BG_MID     = "#090e1a"
BG_SURFACE = "#0d1424"

CYAN       = "#38bdf8"
CYAN_DIM   = "#0ea5e9"
CYAN_GLOW  = "#7dd3fc"
VIOLET     = "#818cf8"
VIOLET_DIM = "#6366f1"
ROSE       = "#f43f5e"
EMERALD    = "#10b981"
AMBER      = "#f59e0b"

TEXT_PRI   = "#e2e8f0"
TEXT_SEC   = "#94a3b8"
TEXT_MUTED = "#475569"


# ═══════════════════════════════════════════════════════════════
#  ANIMATED BACKGROUND
# ═══════════════════════════════════════════════════════════════

class AnimatedBG(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)

    def _tick(self):
        self._t += 0.012
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor("#050811"))
        bg.setColorAt(0.5, QColor("#07101f"))
        bg.setColorAt(1.0, QColor("#050811"))
        p.fillRect(self.rect(), bg)

        orbs = [
            (0.18, 0.22, 320, QColor(56, 189, 248, 28), math.sin(self._t * 0.7) * 40),
            (0.75, 0.35, 280, QColor(129, 140, 248, 22), math.cos(self._t * 0.5) * 50),
            (0.50, 0.80, 380, QColor(16, 185, 129, 18), math.sin(self._t * 0.4 + 1) * 35),
            (0.88, 0.72, 200, QColor(244, 63, 94, 20), math.cos(self._t * 0.9 + 2) * 30),
        ]
        for rx, ry, r, col, dy in orbs:
            cx, cy = int(w * rx), int(h * ry + dy)
            grad = QRadialGradient(cx, cy, r)
            grad.setColorAt(0.0, col)
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        pen = QPen(QColor(56, 189, 248, 12))
        pen.setWidth(1)
        p.setPen(pen)
        for x in range(0, w, 60): p.drawLine(x, 0, x, h)
        for y in range(0, h, 60): p.drawLine(0, y, w, y)
        p.end()


# ═══════════════════════════════════════════════════════════════
#  UI COMPONENTS (GlassCard, NeonButton, etc.)
# ═══════════════════════════════════════════════════════════════

class GlassCard(QFrame):
    def __init__(self, parent=None, accent=None):
        super().__init__(parent)
        self._accent = accent or QColor(56, 189, 248)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_style()
        self._add_shadow()

    def _setup_style(self):
        self.setStyleSheet("""
            GlassCard {
                background: rgba(13, 22, 42, 0.72);
                border: 1px solid rgba(56, 189, 248, 0.18);
                border-radius: 18px;
            }
        """)

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(56, 189, 248, 30))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self._accent)
        pen.setWidth(2)
        p.setPen(pen)
        p.drawLine(30, 0, self.width() - 30, 0)
        p.end()


class NeonButton(QPushButton):
    def __init__(self, text, color=CYAN, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self._base_style(False)

    def _base_style(self, hovered):
        alpha = "55" if hovered else "22"
        border_alpha = "cc" if hovered else "88"
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color}{alpha};
                color: {self._color};
                border: 1px solid {self._color}{border_alpha};
                border-radius: 10px;
                padding: 0 22px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.8px;
            }}
        """)

    def enterEvent(self, e):
        self._base_style(True)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(self._color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def leaveEvent(self, e):
        self._base_style(False)
        self.setGraphicsEffect(None)


class DangerButton(NeonButton):
    def __init__(self, text, parent=None):
        super().__init__(text, ROSE, parent)


class SuccessButton(NeonButton):
    def __init__(self, text, parent=None):
        super().__init__(text, EMERALD, parent)


INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background: rgba(8, 14, 28, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        padding: 10px 14px;
        color: {TEXT_PRI};
        font-size: 13px;
        min-height: 20px;
        selection-background-color: rgba(56, 189, 248, 0.3);
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 1px solid {CYAN};
        background: rgba(56, 189, 248, 0.06);
    }}
    QLineEdit::placeholder {{ color: {TEXT_MUTED}; }}
    QComboBox::drop-down {{ border: none; width: 28px; }}
    QComboBox::down-arrow {{
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {CYAN};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_SURFACE};
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: {TEXT_PRI};
        selection-background-color: rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        padding: 4px;
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        background: transparent; border: none; width: 20px;
    }}
    QTextEdit {{
        min-height: 80px;
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background: transparent;
        border: none;
        gridline-color: rgba(56, 189, 248, 0.08);
        color: {TEXT_PRI};
        font-size: 13px;
        outline: none;
    }}
    QTableWidget::item {{
        padding: 12px 16px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.06);
    }}
    QTableWidget::item:selected {{
        background: rgba(56, 189, 248, 0.15);
        color: {CYAN_GLOW};
    }}
    QHeaderView::section {{
        background: rgba(56, 189, 248, 0.08);
        color: {CYAN};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        padding: 10px 16px;
        border: none;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        text-transform: uppercase;
    }}
    QScrollBar:vertical {{
        background: transparent; width: 4px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(56, 189, 248, 0.3);
        border-radius: 2px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# ═══════════════════════════════════════════════════════════════
#  MODERN DIALOGS
# ═══════════════════════════════════════════════════════════════

class ModernDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.setStyleSheet(f"background: {BG_MID}; color: {TEXT_PRI};")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(25, 25, 25, 25)
        
        header = QLabel(title.upper())
        header.setStyleSheet(f"color: {CYAN}; font-weight: 800; font-size: 16px; letter-spacing: 2px;")
        self.layout.addWidget(header)
        self.layout.addSpacing(10)

    def add_input(self, label_text, placeholder=""):
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setStyleSheet(INPUT_STYLE)
        self.layout.addWidget(lbl)
        self.layout.addWidget(edit)
        return edit

    def add_buttons(self):
        btn_layout = QHBoxLayout()
        save_btn = SuccessButton("KAYDET")
        cancel_btn = DangerButton("İPTAL")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        self.layout.addLayout(btn_layout)

# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ═══════════════════════════════════════════════════════════════

class CRMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistem = CRMSistemi()
        self._init_demo_data()
        self.setWindowTitle("Ultra-Modern CRM System")
        self.resize(1280, 800)
        
        # Central Widget & Background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.bg = AnimatedBG(self.central_widget)
        self.bg.lower()

        self._setup_sidebar()
        self._setup_content()
        
        # Start on Dashboard
        self.switch_page(0)

    def _init_demo_data(self):
        # Demo verileri ekle
        m1 = Musteri("M001", "Ahmet Teknoloji", "0555", "ahmet@tech.com")
        m2 = Musteri("M002", "Selin Yazılım", "0444", "selin@soft.com")
        self.sistem.musteri_ekle(m1)
        self.sistem.musteri_ekle(m2)
        self.sistem.satis_ekle("M001", "Bulut Sunucu", 12500, "Yıllık abonelik")
        self.sistem.talep_olustur("M002", "Giriş Sorunu", "Şifre sıfırlama talebi")

    def _setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background: rgba(5, 8, 17, 0.6);
                border-right: 1px solid rgba(56, 189, 248, 0.1);
            }}
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(10)

        logo = QLabel("🏢 CRM PRO")
        logo.setStyleSheet(f"color: {CYAN}; font-size: 22px; font-weight: 900; margin-bottom: 30px;")
        sidebar_layout.addWidget(logo)

        menus = [
            ("📊 Genel Bakış", 0),
            ("👥 Müşteriler", 1),
            ("💰 Satışlar", 2),
            ("🎧 Destek", 3)
        ]

        self.menu_buttons = []
        for text, idx in menus:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 15px;
                    background: transparent;
                    color: {TEXT_SEC};
                    border-radius: 10px;
                    font-weight: 600;
                    border: none;
                }}
                QPushButton:hover {{
                    background: rgba(56, 189, 248, 0.1);
                    color: {TEXT_PRI};
                }}
                QPushButton:checked {{
                    background: rgba(56, 189, 248, 0.2);
                    color: {CYAN};
                    border-left: 3px solid {CYAN};
                }}
            """)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        sidebar_layout.addStretch()
        
        self.status_lbl = QLabel("Sistem Çevrimiçi")
        self.status_lbl.setStyleSheet(f"color: {EMERALD}; font-size: 11px; font-weight: 700;")
        sidebar_layout.addWidget(self.status_lbl)

        self.main_layout.addWidget(self.sidebar)

    def _setup_content(self):
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Pages
        self.page_dashboard = QWidget()
        self.page_customers = QWidget()
        self.page_sales = QWidget()
        self.page_support = QWidget()

        self._setup_dashboard_ui()
        self._setup_customers_ui()
        self._setup_sales_ui()
        self._setup_support_ui()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_customers)
        self.stack.addWidget(self.page_sales)
        self.stack.addWidget(self.page_support)

    def switch_page(self, idx):
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == idx)
        self.stack.setCurrentIndex(idx)
        self.refresh_data()

    # ─── DASHBOARD ───────────────────────────────────────────
    def _setup_dashboard_ui(self):
        layout = QVBoxLayout(self.page_dashboard)
        layout.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel("Sistem Özeti")
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 28px; font-weight: 800;")
        layout.addWidget(header)
        layout.addSpacing(30)

        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        layout.addLayout(self.grid)
        layout.addStretch()

    def refresh_dashboard(self):
        # Clear grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
            
        ozet = self.sistem.detayli_rapor()
        colors = [CYAN, EMERALD, VIOLET, AMBER, ROSE, CYAN_GLOW]
        
        for i, (k, v) in enumerate(ozet.items()):
            card = GlassCard(accent=QColor(colors[i % len(colors)]))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(25, 25, 25, 25)
            
            val_lbl = QLabel(str(v))
            val_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 32px; font-weight: 800;")
            key_lbl = QLabel(k.upper())
            key_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
            
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(key_lbl)
            self.grid.addWidget(card, i // 3, i % 3)

    # ─── CUSTOMERS ───────────────────────────────────────────
    def _setup_customers_ui(self):
        layout = QVBoxLayout(self.page_customers)
        layout.setContentsMargins(40, 40, 40, 40)

        ctrl_layout = QHBoxLayout()
        title = QLabel("Müşteri Portföyü")
        title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 24px; font-weight: 800;")
        add_btn = SuccessButton("+ YENİ MÜŞTERİ")
        add_btn.clicked.connect(self.add_customer_dialog)
        
        ctrl_layout.addWidget(title)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(add_btn)
        layout.addLayout(ctrl_layout)

        self.cust_table = QTableWidget()
        self.cust_table.setColumnCount(5)
        self.cust_table.setHorizontalHeaderLabels(["ID", "AD SOYAD", "E-POSTA", "HARCAMA", "AKSİYON"])
        self.cust_table.setStyleSheet(TABLE_STYLE)
        self.cust_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.cust_table)

    def refresh_customers(self):
        musteriler = self.sistem.get_musteriler()
        self.cust_table.setRowCount(len(musteriler))
        for i, m in enumerate(musteriler.values()):
            self.cust_table.setItem(i, 0, QTableWidgetItem(m.get_musteri_id()))
            self.cust_table.setItem(i, 1, QTableWidgetItem(m.get_ad()))
            self.cust_table.setItem(i, 2, QTableWidgetItem(m.get_email()))
            self.cust_table.setItem(i, 3, QTableWidgetItem(f"₺{m.toplam_harcama():,.0f}"))
            
            del_btn = QPushButton("Sil")
            del_btn.setStyleSheet(f"color: {ROSE}; background: transparent; font-weight: bold;")
            del_btn.clicked.connect(lambda checked, mid=m.get_musteri_id(): self.delete_customer(mid))
            self.cust_table.setCellWidget(i, 4, del_btn)

    def add_customer_dialog(self):
        dlg = ModernDialog("Yeni Müşteri Ekle", self)
        e_id = dlg.add_input("MÜŞTERİ ID", "M00X")
        e_ad = dlg.add_input("AD SOYAD", "Tam isim giriniz")
        e_mail = dlg.add_input("E-POSTA", "ornek@mail.com")
        dlg.add_buttons()
        
        if dlg.exec_():
            try:
                cust = Musteri(e_id.text(), e_ad.text(), email=e_mail.text())
                ok, msg = self.sistem.musteri_ekle(cust)
                if ok: self.refresh_data()
                else: QMessageBox.warning(self, "Hata", msg)
            except ValidationError as e:
                QMessageBox.warning(self, "Doğrulama Hatası", str(e))

    def delete_customer(self, mid):
        ok, msg = self.sistem.musteri_sil(mid)
        if ok: self.refresh_data()
        else: QMessageBox.warning(self, "Uyarı", msg)

    # ─── SALES ───────────────────────────────────────────────
    def _setup_sales_ui(self):
        layout = QVBoxLayout(self.page_sales)
        layout.setContentsMargins(40, 40, 40, 40)

        ctrl_layout = QHBoxLayout()
        title = QLabel("Satış Kayıtları")
        title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 24px; font-weight: 800;")
        add_btn = SuccessButton("+ YENİ SATIŞ")
        add_btn.clicked.connect(self.add_sale_dialog)
        
        ctrl_layout.addWidget(title)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(add_btn)
        layout.addLayout(ctrl_layout)

        self.sale_table = QTableWidget()
        self.sale_table.setColumnCount(5)
        self.sale_table.setHorizontalHeaderLabels(["ID", "MÜŞTERİ", "ÜRÜN", "TUTAR", "DURUM"])
        self.sale_table.setStyleSheet(TABLE_STYLE)
        self.sale_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.sale_table)

    def refresh_sales(self):
        satislar = self.sistem.get_tum_satislar()
        self.sale_table.setRowCount(len(satislar))
        for i, s in enumerate(satislar):
            self.sale_table.setItem(i, 0, QTableWidgetItem(f"#{s.get_satis_id()}"))
            m_ad = s.get_musteri().get_ad() if s.get_musteri() else "Bilinmeyen"
            self.sale_table.setItem(i, 1, QTableWidgetItem(m_ad))
            self.sale_table.setItem(i, 2, QTableWidgetItem(s.get_urun()))
            self.sale_table.setItem(i, 3, QTableWidgetItem(f"₺{s.get_fiyat():,.0f}"))
            
            status_btn = QPushButton(s.get_durum().value)
            color = EMERALD if s.get_durum() == SatisDurumu.TAMAMLANDI else AMBER
            status_btn.setStyleSheet(f"color: {color}; background: rgba(0,0,0,0.2); border-radius: 5px;")
            status_btn.clicked.connect(lambda checked, sid=s.get_satis_id(): self.update_sale_status(sid))
            self.sale_table.setCellWidget(i, 4, status_btn)

    def add_sale_dialog(self):
        musteriler = self.sistem.get_musteriler()
        if not musteriler: return QMessageBox.warning(self, "Hata", "Önce müşteri ekleyin.")

        dlg = ModernDialog("Satış Kaydı", self)
        e_mid = QComboBox()
        e_mid.setStyleSheet(INPUT_STYLE)
        for m in musteriler.values(): e_mid.addItem(f"{m.get_ad()} ({m.get_musteri_id()})", m.get_musteri_id())
        
        e_urun = dlg.add_input("ÜRÜN / HİZMET")
        e_fiyat = QDoubleSpinBox()
        e_fiyat.setMaximum(1000000)
        e_fiyat.setStyleSheet(INPUT_STYLE)
        
        dlg.layout.insertWidget(2, QLabel("MÜŞTERİ SEÇİN"))
        dlg.layout.insertWidget(3, e_mid)
        dlg.layout.insertWidget(6, QLabel("FİYAT"))
        dlg.layout.insertWidget(7, e_fiyat)
        dlg.add_buttons()

        if dlg.exec_():
            self.sistem.satis_ekle(e_mid.currentData(), e_urun.text(), e_fiyat.value())
            self.refresh_data()

    def update_sale_status(self, sid):
        # Basit toggle (Beklemede <-> Tamamlandı)
        s = next(x for x in self.sistem.get_tum_satislar() if x.get_satis_id() == sid)
        yeni = SatisDurumu.TAMAMLANDI if s.get_durum() == SatisDurumu.BEKLEMEDE else SatisDurumu.BEKLEMEDE
        self.sistem.satis_durum_guncelle(sid, yeni)
        self.refresh_data()

    # ─── SUPPORT ─────────────────────────────────────────────
    def _setup_support_ui(self):
        layout = QVBoxLayout(self.page_support)
        layout.setContentsMargins(40, 40, 40, 40)

        ctrl_layout = QHBoxLayout()
        title = QLabel("Destek Talepleri")
        title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 24px; font-weight: 800;")
        add_btn = SuccessButton("+ YENİ TALEP")
        add_btn.clicked.connect(self.add_ticket_dialog)
        
        ctrl_layout.addWidget(title)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(add_btn)
        layout.addLayout(ctrl_layout)

        self.ticket_table = QTableWidget()
        self.ticket_table.setColumnCount(4)
        self.ticket_table.setHorizontalHeaderLabels(["ID", "MÜŞTERİ", "KONU", "DURUM"])
        self.ticket_table.setStyleSheet(TABLE_STYLE)
        self.ticket_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.ticket_table)

    def refresh_support(self):
        talepler = self.sistem.get_tum_talepler()
        self.ticket_table.setRowCount(len(talepler))
        for i, t in enumerate(talepler):
            self.ticket_table.setItem(i, 0, QTableWidgetItem(f"T#{t.get_talep_id()}"))
            self.ticket_table.setItem(i, 1, QTableWidgetItem(t.get_musteri().get_ad()))
            self.ticket_table.setItem(i, 2, QTableWidgetItem(t.get_konu()))
            
            status_btn = QPushButton(t.get_durum().value)
            color = EMERALD if t.get_durum() == TalepDurumu.COZULDU else AMBER
            status_btn.setStyleSheet(f"color: {color}; background: rgba(0,0,0,0.1); border: 1px solid {color};")
            status_btn.clicked.connect(lambda checked, tid=t.get_talep_id(): self.resolve_ticket(tid))
            self.ticket_table.setCellWidget(i, 3, status_btn)

    def add_ticket_dialog(self):
        musteriler = self.sistem.get_musteriler()
        if not musteriler: return
        
        dlg = ModernDialog("Yeni Destek Talebi", self)
        e_mid = QComboBox()
        e_mid.setStyleSheet(INPUT_STYLE)
        for m in musteriler.values(): e_mid.addItem(m.get_ad(), m.get_musteri_id())
        e_konu = dlg.add_input("KONU")
        e_desc = QTextEdit()
        e_desc.setStyleSheet(INPUT_STYLE)
        
        dlg.layout.insertWidget(2, e_mid)
        dlg.layout.addWidget(QLabel("DETAYLAR"))
        dlg.layout.addWidget(e_desc)
        dlg.add_buttons()

        if dlg.exec_():
            self.sistem.talep_olustur(e_mid.currentData(), e_konu.text(), e_desc.toPlainText())
            self.refresh_data()

    def resolve_ticket(self, tid):
        self.sistem.talep_durum_guncelle(tid, TalepDurumu.COZULDU, "Sorun giderildi.")
        self.refresh_data()

    # ─── GLOBAL REFRESH ──────────────────────────────────────
    def refresh_data(self):
        idx = self.stack.currentIndex()
        if idx == 0: self.refresh_dashboard()
        elif idx == 1: self.refresh_customers()
        elif idx == 2: self.refresh_sales()
        elif idx == 3: self.refresh_support()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dark Mode Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BG_DEEP))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRI))
    palette.setColor(QPalette.Base, QColor(BG_MID))
    palette.setColor(QPalette.AlternateBase, QColor(BG_SURFACE))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, QColor(TEXT_PRI))
    palette.setColor(QPalette.Button, QColor(BG_SURFACE))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRI))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(CYAN))
    palette.setColor(QPalette.Highlight, QColor(CYAN_DIM))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Global Font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = CRMApp()
    window.show()
    sys.exit(app.exec_())
