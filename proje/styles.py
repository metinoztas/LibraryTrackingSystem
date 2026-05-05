# -*- coding: utf-8 -*-
"""
styles.py — Renk paleti, stil tanımları ve yardımcı UI fonksiyonları
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel

# ══════════════════════════════════════════════════════════════════════════════
#  RENK PALETİ
# ══════════════════════════════════════════════════════════════════════════════
KOYU_ARKAPLAN  = "#0F172A"
KENAR_CUBUGU   = "#1E293B"
KART_ARKAPLAN  = "#1E293B"
VURGU_MAVI     = "#3B82F6"
VURGU_YESIL    = "#10B981"
VURGU_TURUNCU  = "#F59E0B"
VURGU_KIRMIZI  = "#EF4444"
YAZI_BIRINCIL  = "#F1F5F9"
YAZI_IKINCIL   = "#94A3B8"
YAZI_SOLUK     = "#475569"
KENARLIK       = "#334155"

# Ödünç durum renkleri → (yazı rengi, arka plan rengi)
DURUM_RENKLERI = {
    "ödünçte":     (VURGU_MAVI,    "#1E3A5F"),
    "iade edildi": (VURGU_YESIL,   "#064E3B"),
    "gecikmiş":    (VURGU_TURUNCU, "#451A03"),
}

# ══════════════════════════════════════════════════════════════════════════════
#  STİL TANIMLARI
# ══════════════════════════════════════════════════════════════════════════════

GENEL_STIL = f"""
QMainWindow, QWidget#centralwidget {{ background-color: {KOYU_ARKAPLAN}; }}
QScrollBar:vertical {{ background:{KOYU_ARKAPLAN}; width:8px; border-radius:4px; }}
QScrollBar::handle:vertical {{ background:{KENARLIK}; border-radius:4px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:{VURGU_MAVI}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QToolTip {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_BIRINCIL};
    border:1px solid {VURGU_MAVI}; border-radius:6px;
    padding:6px 10px; font-family:'Segoe UI'; font-size:11px;
}}
"""

SIDEBAR_BTN = f"""
QPushButton {{
    background-color:transparent; color:{YAZI_IKINCIL};
    font-family:'Segoe UI'; font-size:13px; font-weight:600;
    text-align:left; padding-left:20px; border:none; border-radius:10px;
}}
QPushButton:hover {{ background-color:{KENARLIK}; color:{YAZI_BIRINCIL}; }}
QPushButton:pressed {{ background-color:{VURGU_MAVI}; color:#FFFFFF; }}
"""

SIDEBAR_BTN_AKTIF = f"""
QPushButton {{
    background-color:{VURGU_MAVI}; color:#FFFFFF;
    font-family:'Segoe UI'; font-size:13px; font-weight:600;
    text-align:left; padding-left:20px; border:none; border-radius:10px;
    border-left:3px solid #93C5FD;
}}
"""

SIDEBAR_BTN_AYARLAR = f"""
QPushButton {{
    background-color:transparent; color:{YAZI_SOLUK};
    font-family:'Segoe UI'; font-size:12px; font-weight:500;
    text-align:left; padding-left:20px; border:none; border-radius:10px;
}}
QPushButton:hover {{ background-color:{KENARLIK}; color:{YAZI_IKINCIL}; }}
QPushButton:disabled {{ color:#2D3748; background-color:transparent; }}
"""

SIDEBAR_BTN_AYARLAR_AKTIF = f"""
QPushButton {{
    background-color:#1A2E1A; color:{VURGU_YESIL};
    font-family:'Segoe UI'; font-size:12px; font-weight:600;
    text-align:left; padding-left:20px; border:1px solid #1A4D2E; border-radius:10px;
}}
QPushButton:hover {{ background-color:#133913; color:#34D399; }}
QPushButton:pressed {{ background-color:#064E3B; }}
"""

ADMIN_GIRIS_BTN = f"""
QPushButton {{
    background-color:transparent; color:{YAZI_SOLUK};
    font-family:'Segoe UI'; font-size:12px; font-weight:500;
    text-align:left; padding-left:20px; border:none; border-radius:10px;
}}
QPushButton:hover {{ background-color:#1F1020; color:#C084FC; }}
QPushButton:pressed {{ background-color:#3B0764; }}
"""

ADMIN_AKTIF_BTN = f"""
QPushButton {{
    background-color:#1A0533; color:#C084FC;
    font-family:'Segoe UI'; font-size:12px; font-weight:600;
    text-align:left; padding-left:20px; border:1px solid #6B21A8; border-radius:10px;
}}
QPushButton:hover {{ background-color:#2D0F5E; color:#E879F9; }}
QPushButton:pressed {{ background-color:#3B0764; }}
"""

KULLANICI_GIRIS_BTN = f"""
QPushButton {{
    background-color:transparent; color:{YAZI_SOLUK};
    font-family:'Segoe UI'; font-size:12px; font-weight:500;
    text-align:left; padding-left:20px; border:none; border-radius:10px;
}}
QPushButton:hover {{ background-color:#0D2D3A; color:#22D3EE; }}
QPushButton:pressed {{ background-color:#164E63; }}
"""

KULLANICI_AKTIF_BTN = f"""
QPushButton {{
    background-color:#0C2A38; color:#22D3EE;
    font-family:'Segoe UI'; font-size:12px; font-weight:600;
    text-align:left; padding-left:20px; border:1px solid #0E7490; border-radius:10px;
}}
QPushButton:hover {{ background-color:#164E63; color:#67E8F9; }}
QPushButton:pressed {{ background-color:#155E75; }}
"""

KILITLI_BTN = f"""
QPushButton {{
    background-color:#1a1a2e; color:#334155;
    border:1px solid #1e293b; border-radius:6px; font-size:14px; padding:2px 6px;
}}
"""

ARAMA_STILI = f"""
QLineEdit {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_IKINCIL};
    font-family:'Segoe UI'; font-size:12px; font-weight:500;
    border:1.5px solid {KENARLIK}; border-radius:10px; padding-left:14px;
}}
QLineEdit:focus {{
    border:1.5px solid {VURGU_MAVI}; color:{YAZI_BIRINCIL}; background-color:#243044;
}}
"""

COMBO_STILI = f"""
QComboBox {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_IKINCIL};
    font-family:'Segoe UI'; font-size:12px; font-weight:500;
    border:1.5px solid {KENARLIK}; border-radius:10px;
    padding-left:14px; padding-right:28px;
}}
QComboBox:hover {{ border:1.5px solid {VURGU_MAVI}; color:{YAZI_BIRINCIL}; }}
QComboBox::drop-down {{ border:none; width:28px; }}
QComboBox::down-arrow {{
    border-left:5px solid transparent; border-right:5px solid transparent;
    border-top:6px solid {YAZI_IKINCIL}; width:0; height:0; margin-right:8px;
}}
QComboBox QAbstractItemView {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_BIRINCIL};
    border:1px solid {KENARLIK}; selection-background-color:{VURGU_MAVI};
    selection-color:#FFFFFF; border-radius:8px; padding:4px;
}}
"""

EKLE_BTN_STILI = f"""
QPushButton {{
    background-color:{VURGU_MAVI}; color:#FFFFFF;
    font-family:'Segoe UI'; font-size:12px; font-weight:700;
    border:none; border-radius:10px; padding-left:6px;
}}
QPushButton:hover {{ background-color:#2563EB; }}
QPushButton:pressed {{ background-color:#1D4ED8; }}
"""

TABLO_STILI = f"""
QTableWidget {{
    background-color:transparent; border:none;
    gridline-color:{KENARLIK}; color:{YAZI_BIRINCIL};
    font-family:'Segoe UI'; font-size:12px;
    selection-background-color:#243B53; selection-color:{YAZI_BIRINCIL};
}}
QTableWidget::item {{ padding:6px 12px; border-bottom:1px solid {KENARLIK}; }}
QTableWidget::item:selected {{ background-color:#1E3A5F; color:{YAZI_BIRINCIL}; }}
QHeaderView::section {{
    background-color:#1E3A5F; color:{YAZI_IKINCIL};
    font-family:'Segoe UI'; font-size:11px; font-weight:700;
    border:none; border-bottom:2px solid {VURGU_MAVI}; padding:10px 12px;
}}
"""

DIYALOG_STILI = f"""
QDialog {{ background-color:{KOYU_ARKAPLAN}; color:{YAZI_BIRINCIL}; }}
QLabel {{
    color:{YAZI_IKINCIL}; font-family:'Segoe UI'; font-size:12px;
    background:transparent; border:none;
}}
QLineEdit, QComboBox {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_BIRINCIL};
    border:1.5px solid {KENARLIK}; border-radius:8px;
    padding:6px 10px; font-family:'Segoe UI'; font-size:12px;
}}
QLineEdit:focus, QComboBox:focus {{ border:1.5px solid {VURGU_MAVI}; }}
QComboBox QAbstractItemView {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_BIRINCIL};
    selection-background-color:{VURGU_MAVI};
}}
QPushButton {{
    background-color:{VURGU_MAVI}; color:#FFFFFF; border:none;
    border-radius:8px; padding:8px 18px;
    font-family:'Segoe UI'; font-size:12px; font-weight:600;
}}
QPushButton:hover {{ background-color:#1D4ED8; }}
"""

DUZENLE_BTN = f"""
QPushButton {{
    background-color:#1E3A5F; color:{VURGU_MAVI};
    border:1px solid {VURGU_MAVI}; border-radius:6px; font-size:14px; padding:2px 6px;
}}
QPushButton:hover {{ background-color:{VURGU_MAVI}; color:#fff; }}
"""

SIL_BTN = f"""
QPushButton {{
    background-color:#450A0A; color:{VURGU_KIRMIZI};
    border:1px solid {VURGU_KIRMIZI}; border-radius:6px; font-size:14px; padding:2px 6px;
}}
QPushButton:hover {{ background-color:#DC2626; color:#fff; }}
"""

IADE_BTN = f"""
QPushButton {{
    background-color:#064E3B; color:{VURGU_YESIL};
    border:1px solid {VURGU_YESIL}; border-radius:6px;
    font-size:11px; font-weight:600; padding:2px 8px;
}}
QPushButton:hover {{ background-color:#059669; color:#fff; }}
"""

# ══════════════════════════════════════════════════════════════════════════════
#  YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════════════════════════

def golge_ekle(hedef, blur=20, x=0, y=4, renk=(0, 0, 0, 80)):
    """Verilen widget'a gölge efekti ekler."""
    g = QGraphicsDropShadowEffect()
    g.setBlurRadius(blur)
    g.setOffset(x, y)
    g.setColor(QColor(*renk))
    hedef.setGraphicsEffect(g)


def etiket(ebeveyn, metin, renk, boyut, kalin=False, hizalama=Qt.AlignLeft | Qt.AlignVCenter):
    """Hızlıca stillendirilmiş QLabel oluşturur."""
    lbl = QLabel(metin, ebeveyn)
    lbl.setStyleSheet(
        f"color:{renk}; font-family:'Segoe UI'; font-size:{boyut}px; "
        f"font-weight:{'700' if kalin else '400'}; background:transparent; border:none;"
    )
    lbl.setAlignment(hizalama)
    return lbl
