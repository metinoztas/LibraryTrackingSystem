# -*- coding: utf-8 -*-
"""
mainwindow.py — Kütüphane Yönetim Sistemi
Backend ve UI yapı kodları burada bulunur.
Stiller ve renkler için → styles.py
"""

import sys
import sqlite3
import os
from datetime import date

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QStackedWidget,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QVBoxLayout, QWidget
)

# Stiller ve yardımcı fonksiyonlar styles.py'den geliyor
from styles import (
    KOYU_ARKAPLAN, KENAR_CUBUGU, KART_ARKAPLAN,
    VURGU_MAVI, VURGU_YESIL, VURGU_TURUNCU, VURGU_KIRMIZI,
    YAZI_BIRINCIL, YAZI_IKINCIL, YAZI_SOLUK, KENARLIK,
    DURUM_RENKLERI,
    GENEL_STIL, SIDEBAR_BTN, SIDEBAR_BTN_AKTIF, SIDEBAR_BTN_AYARLAR,
    SIDEBAR_BTN_AYARLAR_AKTIF, ADMIN_GIRIS_BTN, ADMIN_AKTIF_BTN,
    KULLANICI_GIRIS_BTN, KULLANICI_AKTIF_BTN, KILITLI_BTN,
    ARAMA_STILI, COMBO_STILI, EKLE_BTN_STILI, TABLO_STILI,
    DIYALOG_STILI, DUZENLE_BTN, SIL_BTN, IADE_BTN,
    golge_ekle, etiket
)

# ── Veritabanı yolu ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_YOLU  = os.path.join(BASE_DIR, "veriSeti", "library_dataset.db")


# ══════════════════════════════════════════════════════════════════════════════
#  DİYALOG SINIFLARI
# ══════════════════════════════════════════════════════════════════════════════

class KitapDiyalogu(QDialog):
    def __init__(self, ebeveyn, kategoriler, kitap=None):
        super().__init__(ebeveyn)
        self.setWindowTitle("Kitap Ekle" if kitap is None else "Kitap Düzenle")
        self.setMinimumWidth(420)
        self.setStyleSheet(DIYALOG_STILI)
        d = QFormLayout(self)
        d.setSpacing(12)
        d.setContentsMargins(24, 24, 24, 24)
        self.adi      = QLineEdit(kitap["kitap_adi"]       if kitap else "")
        self.yazar    = QLineEdit(kitap["yazar"]           if kitap else "")
        self.isbn     = QLineEdit(kitap["isbn"]            if kitap else "")
        self.yayinevi = QLineEdit(kitap["yayinevi"]        if kitap else "")
        self.yil      = QLineEdit(str(kitap["yayin_yili"]) if kitap else "")
        self.stok     = QLineEdit(str(kitap["stok"])       if kitap else "1")
        self.kat = QComboBox()
        self.kat.addItems(kategoriler)
        if kitap:
            idx = self.kat.findText(kitap["kategori"])
            if idx >= 0:
                self.kat.setCurrentIndex(idx)
        d.addRow("Kitap Adı *", self.adi)
        d.addRow("Yazar *",     self.yazar)
        d.addRow("ISBN",        self.isbn)
        d.addRow("Yayınevi",    self.yayinevi)
        d.addRow("Yayın Yılı",  self.yil)
        d.addRow("Stok",        self.stok)
        d.addRow("Kategori",    self.kat)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        d.addRow(bb)

    def veri_al(self):
        return {
            "kitap_adi":  self.adi.text().strip(),
            "yazar":      self.yazar.text().strip(),
            "isbn":       self.isbn.text().strip(),
            "yayinevi":   self.yayinevi.text().strip(),
            "yayin_yili": int(self.yil.text().strip() or 0),
            "stok":       int(self.stok.text().strip() or 1),
            "kategori":   self.kat.currentText(),
        }


class UyeDiyalogu(QDialog):
    def __init__(self, ebeveyn, uye=None):
        super().__init__(ebeveyn)
        self.setWindowTitle("Üye Ekle" if uye is None else "Üye Düzenle")
        self.setMinimumWidth(400)
        self.setStyleSheet(DIYALOG_STILI)
        d = QFormLayout(self)
        d.setSpacing(12)
        d.setContentsMargins(24, 24, 24, 24)
        self.ad    = QLineEdit(uye["ad"]      if uye else "")
        self.soyad = QLineEdit(uye["soyad"]   if uye else "")
        self.tel   = QLineEdit(uye["telefon"] if uye else "")
        self.email = QLineEdit(uye["email"]   if uye else "")
        d.addRow("Ad *",    self.ad)
        d.addRow("Soyad *", self.soyad)
        d.addRow("Telefon", self.tel)
        d.addRow("E-posta", self.email)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        d.addRow(bb)

    def veri_al(self):
        return {"ad": self.ad.text().strip(), "soyad": self.soyad.text().strip(),
                "telefon": self.tel.text().strip(), "email": self.email.text().strip()}


class OduncDiyalogu(QDialog):
    def __init__(self, ebeveyn, kitaplar, uyeler):
        super().__init__(ebeveyn)
        self.setWindowTitle("Ödünç Ver")
        self.setMinimumWidth(440)
        self.setStyleSheet(DIYALOG_STILI)
        self._kid, self._uid = [], []
        d = QFormLayout(self)
        d.setSpacing(12)
        d.setContentsMargins(24, 24, 24, 24)
        self.kb = QComboBox()
        for k in kitaplar:
            self.kb.addItem(f"{k['kitap_adi']} ({k['isbn']})")
            self._kid.append(k["kitap_id"])
        self.ub = QComboBox()
        for u in uyeler:
            self.ub.addItem(f"{u['ad']} {u['soyad']} — {u['email']}")
            self._uid.append(u["uye_id"])
        d.addRow("Kitap *", self.kb)
        d.addRow("Üye *",   self.ub)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        d.addRow(bb)

    def veri_al(self):
        return self._kid[self.kb.currentIndex()], self._uid[self.ub.currentIndex()]


# ══════════════════════════════════════════════════════════════════════════════
#  GİRİŞ EKRANI (Başlangıç)
# ══════════════════════════════════════════════════════════════════════════════

# Sabit kimlik bilgileri — gerçek uygulamada hash'lenmiş DB'den gelmeli
_ADMIN_KULLANICI     = "admin"
_ADMIN_SIFRE         = "admin123"
_KULLANICI_KULLANICI = "kullanici"
_KULLANICI_SIFRE     = "kullanici123"

# Rol kartı stilleri
_ROL_KART_PASIF = f"""
QPushButton {{
    background-color:{KART_ARKAPLAN}; color:{YAZI_IKINCIL};
    font-family:'Segoe UI'; font-size:13px; font-weight:600;
    border:2px solid {KENARLIK}; border-radius:12px; padding:14px;
}}
QPushButton:hover {{ border-color:{YAZI_IKINCIL}; color:{YAZI_BIRINCIL}; }}
"""

_ROL_KART_ADMIN = f"""
QPushButton {{
    background-color:#1A0533; color:#C084FC;
    font-family:'Segoe UI'; font-size:13px; font-weight:700;
    border:2px solid #6B21A8; border-radius:12px; padding:14px;
}}
"""

_ROL_KART_KULLANICI = f"""
QPushButton {{
    background-color:#0C2A38; color:#22D3EE;
    font-family:'Segoe UI'; font-size:13px; font-weight:700;
    border:2px solid #0E7490; border-radius:12px; padding:14px;
}}
"""


class GirisEkrani(QDialog):
    """Uygulama başlangıcında gösterilen giriş ekranı."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("📖 Kütüphane — Giriş")
        self.setFixedSize(440, 460)
        self.setStyleSheet(DIYALOG_STILI)
        self.rol = None          # "admin" veya "kullanici"
        self._secili_rol = None  # Henüz seçilmedi

        ana = QVBoxLayout(self)
        ana.setContentsMargins(36, 32, 36, 28)
        ana.setSpacing(18)

        # ── Logo / Başlık ─────────────────────────────────────────────────
        logo = QLabel("📖")
        logo.setStyleSheet("font-size:38px; background:transparent; border:none;")
        logo.setAlignment(Qt.AlignCenter)
        ana.addWidget(logo)

        baslik = QLabel("Kütüphane Yönetim Sistemi")
        baslik.setStyleSheet(
            f"color:{YAZI_BIRINCIL}; font-family:'Segoe UI';"
            "font-size:18px; font-weight:700; background:transparent; border:none;"
        )
        baslik.setAlignment(Qt.AlignCenter)
        ana.addWidget(baslik)

        alt = QLabel("Devam etmek için giriş yapın")
        alt.setStyleSheet(
            f"color:{YAZI_SOLUK}; font-family:'Segoe UI';"
            "font-size:11px; background:transparent; border:none;"
        )
        alt.setAlignment(Qt.AlignCenter)
        ana.addWidget(alt)

        # ── Rol Seçimi ────────────────────────────────────────────────────
        rol_lbl = QLabel("Giriş türünü seçin:")
        rol_lbl.setStyleSheet(
            f"color:{YAZI_IKINCIL}; font-family:'Segoe UI';"
            "font-size:11px; font-weight:600; background:transparent; border:none;"
            "margin-top:4px;"
        )
        ana.addWidget(rol_lbl)

        rol_satir = QHBoxLayout()
        rol_satir.setSpacing(12)
        self._btn_rol_kullanici = QPushButton("👤  Kullanıcı")
        self._btn_rol_admin     = QPushButton("🔐  Admin")
        for b in (self._btn_rol_kullanici, self._btn_rol_admin):
            b.setFixedHeight(48)
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setStyleSheet(_ROL_KART_PASIF)
        self._btn_rol_kullanici.clicked.connect(lambda: self._rol_sec("kullanici"))
        self._btn_rol_admin.clicked.connect(lambda: self._rol_sec("admin"))
        rol_satir.addWidget(self._btn_rol_kullanici)
        rol_satir.addWidget(self._btn_rol_admin)
        ana.addLayout(rol_satir)

        # ── Form ──────────────────────────────────────────────────────────
        form = QFormLayout()
        form.setSpacing(10)
        self.kullanici = QLineEdit()
        self.kullanici.setPlaceholderText("Kullanıcı adı")
        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        form.addRow("Kullanıcı:", self.kullanici)
        form.addRow("Şifre:",     self.sifre)
        ana.addLayout(form)

        # ── Hata mesajı ──────────────────────────────────────────────────
        self.hata_lbl = QLabel("")
        self.hata_lbl.setStyleSheet(
            f"color:{VURGU_KIRMIZI}; font-family:'Segoe UI';"
            "font-size:11px; background:transparent; border:none;"
        )
        self.hata_lbl.setAlignment(Qt.AlignCenter)
        ana.addWidget(self.hata_lbl)

        # ── Giriş butonu ─────────────────────────────────────────────────
        self.giris_btn = QPushButton("Giriş Yap")
        self.giris_btn.setFixedHeight(42)
        self.giris_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.giris_btn.clicked.connect(self._dogrula)
        ana.addWidget(self.giris_btn)

        self.sifre.returnPressed.connect(self._dogrula)

        # Varsayılan olarak kullanıcı seçili başlat
        self._rol_sec("kullanici")

    def _rol_sec(self, rol):
        self._secili_rol = rol
        self.hata_lbl.clear()
        if rol == "admin":
            self._btn_rol_admin.setStyleSheet(_ROL_KART_ADMIN)
            self._btn_rol_kullanici.setStyleSheet(_ROL_KART_PASIF)
        else:
            self._btn_rol_kullanici.setStyleSheet(_ROL_KART_KULLANICI)
            self._btn_rol_admin.setStyleSheet(_ROL_KART_PASIF)

    def _dogrula(self):
        k = self.kullanici.text().strip()
        s = self.sifre.text()
        if self._secili_rol == "admin":
            if k == _ADMIN_KULLANICI and s == _ADMIN_SIFRE:
                self.rol = "admin"
                self.accept()
                return
        else:
            if k == _KULLANICI_KULLANICI and s == _KULLANICI_SIFRE:
                self.rol = "kullanici"
                self.accept()
                return
        self.hata_lbl.setText("❌  Kullanıcı adı veya şifre yanlış!")
        self.sifre.clear()
        self.sifre.setFocus()


# ══════════════════════════════════════════════════════════════════════════════
#  AYARLAR DİYALOGU
# ══════════════════════════════════════════════════════════════════════════════

class AyarlarDialog(QDialog):
    def __init__(self, ebeveyn, mevcut_db_yolu):
        super().__init__(ebeveyn)
        self.setWindowTitle("⚙️ Ayarlar")
        self.setFixedSize(480, 220)
        self.setStyleSheet(DIYALOG_STILI)
        self._mevcut = mevcut_db_yolu
        self._yeni_yol = None

        ana = QVBoxLayout(self)
        ana.setContentsMargins(32, 28, 32, 28)
        ana.setSpacing(14)

        baslik = QLabel("⚙️  Veritabanı Ayarları")
        baslik.setStyleSheet(
            f"color:{YAZI_BIRINCIL}; font-family:'Segoe UI';"
            "font-size:15px; font-weight:700; background:transparent; border:none;"
        )
        ana.addWidget(baslik)

        db_satir = QHBoxLayout()
        self._db_lbl = QLabel(self._kisalt(mevcut_db_yolu))
        self._db_lbl.setStyleSheet(
            f"color:{YAZI_IKINCIL}; font-family:'Segoe UI';"
            "font-size:11px; background:transparent; border:none;"
        )
        self._db_lbl.setToolTip(mevcut_db_yolu)
        secim_btn = QPushButton("📂  Seç")
        secim_btn.setFixedWidth(90)
        secim_btn.clicked.connect(self._db_sec)
        db_satir.addWidget(QLabel("Veritabanı:"))
        db_satir.addWidget(self._db_lbl, 1)
        db_satir.addWidget(secim_btn)
        ana.addLayout(db_satir)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("Kaydet")
        bb.button(QDialogButtonBox.Cancel).setText("İptal")
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        ana.addWidget(bb)

    def _kisalt(self, yol, maks=50):
        return ("..." + yol[-maks:]) if len(yol) > maks else yol

    def _db_sec(self):
        yol, _ = QFileDialog.getOpenFileName(
            self, "Veritabanı Seç", "", "SQLite Veritabanı (*.db *.sqlite *.sqlite3);;Tüm Dosyalar (*)"
        )
        if yol:
            self._yeni_yol = yol
            self._db_lbl.setText(self._kisalt(yol))
            self._db_lbl.setToolTip(yol)

    def yeni_db_yolu(self):
        return self._yeni_yol


# ══════════════════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):

    def __init__(self, rol):
        super().__init__()
        self._admin_mod     = (rol == "admin")
        self._kullanici_mod = (rol == "kullanici")
        # Veritabanı
        self.db = sqlite3.connect(DB_YOLU)
        self.db.row_factory = sqlite3.Row
        self.sayfa = "kitaplar"
        # UI kur
        self._ui_kur()
        # Bağlantılar
        self.btn_kitaplar.clicked.connect(self.kitaplar_sayfasi)
        self.btn_uyeler.clicked.connect(self.uyeler_sayfasi)
        self.btn_odunc.clicked.connect(self.odunc_sayfasi)
        self.btn_rapor.clicked.connect(self.rapor_sayfasi)
        self.arama_kutusu.textChanged.connect(self.ara)
        self.kategori_combo.currentTextChanged.connect(self.kitaplari_yukle)
        self.ekle_btn.clicked.connect(self.ekle)
        
        self._btn_cikis.clicked.connect(self._cikis_yap)
        self._btn_ayar.clicked.connect(self._ayarlar_ac)
        
        # Başlangıç
        self._kategori_yukle()
        self._istatistik_guncelle()
        self.kitaplar_sayfasi()

    # ══════════════════════════════════════════════════════════════════════════
    #  UI KURULUM
    # ══════════════════════════════════════════════════════════════════════════

    # Tasarım referans boyutları
    _REF_W = 1100
    _REF_H = 820
    _SIDEBAR_W = 240   # referanstaki sol panel genişliği

    def _ui_kur(self):
        self.setObjectName("MainWindow")
        self.resize(QSize(self._REF_W, self._REF_H))
        self.setMinimumSize(QSize(700, 500))
        self.setStyleSheet(GENEL_STIL)
        self.setWindowTitle("📖 Kütüphane Yönetim Sistemi")

        merkez = QWidget(self)
        merkez.setObjectName("centralwidget")
        self.setCentralWidget(merkez)

        self._sol_panel(merkez)
        self._icerik_alani(merkez)

        # Ölçekleme referanslarını sakla (ilk kurulumdan sonra)
        self._merkez = merkez

    def _sol_panel(self, ebeveyn):
        self._panel = QFrame(ebeveyn)
        self._panel.setGeometry(QRect(0, 0, self._SIDEBAR_W, self._REF_H))
        self._panel.setStyleSheet(f"QFrame{{background-color:{KENAR_CUBUGU};border:none;border-right:1px solid {KENARLIK};}}")
        golge_ekle(self._panel, blur=30, x=4, y=0, renk=(0, 0, 0, 120))

        # Logo
        self._logo = QFrame(self._panel)
        self._logo.setGeometry(QRect(0, 0, self._SIDEBAR_W, 80))
        self._logo.setStyleSheet(f"QFrame{{background:transparent;border:none;border-bottom:1px solid {KENARLIK};}}")
        self._logo_baslik = etiket(self._logo, "📖  Kütüphane\nYönetim Sistemi", YAZI_BIRINCIL, 14, kalin=True, hizalama=Qt.AlignCenter)
        self._logo_baslik.setGeometry(QRect(0, 0, self._SIDEBAR_W, 80))

        self._menu_etiketi = etiket(self._panel, "  MENÜ", YAZI_SOLUK, 10)
        self._menu_etiketi.setGeometry(QRect(16, 90, 200, 24))

        self.btn_kitaplar = self._menu_btn(self._panel, "📚  Kitaplar",        130)
        self.btn_uyeler   = self._menu_btn(self._panel, "👤  Üyeler",          200)
        self.btn_odunc    = self._menu_btn(self._panel, "📄  Ödünç İşlemleri", 270)
        self.btn_rapor    = self._menu_btn(self._panel, "📊  Raporlar",        340)

        # Alt butonlar: Çıkış Yap + Ayarlar
        rol_metin = "Admin" if self._admin_mod else "Kullanıcı"
        rol_renk = "#C084FC" if self._admin_mod else "#22D3EE"
        self._rol_bilgi = etiket(self._panel, f"Oturum: {rol_metin}", YAZI_SOLUK, 11, hizalama=Qt.AlignCenter)
        self._rol_bilgi.setStyleSheet(f"color:{rol_renk}; font-weight:600; background:transparent;")
        self._rol_bilgi.setGeometry(QRect(0, 640, self._SIDEBAR_W, 24))

        self._btn_cikis = QPushButton("🚪  Çıkış Yap", self._panel)
        self._btn_cikis.setGeometry(QRect(12, 692, 216, 44))
        self._btn_cikis.setStyleSheet(SIDEBAR_BTN)
        self._btn_cikis.setCursor(QCursor(Qt.PointingHandCursor))

        self._btn_ayar = QPushButton("⚙️  Ayarlar", self._panel)
        self._btn_ayar.setGeometry(QRect(12, 744, 216, 44))
        self._btn_ayar.setStyleSheet(SIDEBAR_BTN_AYARLAR_AKTIF if self._admin_mod else SIDEBAR_BTN_AYARLAR)
        self._btn_ayar.setEnabled(self._admin_mod)
        self._btn_ayar.setCursor(QCursor(Qt.PointingHandCursor))

        self._versiyon_etiketi = etiket(self._panel, "v1.0.0", YAZI_SOLUK, 10, hizalama=Qt.AlignCenter)
        self._versiyon_etiketi.setGeometry(QRect(0, 796, self._SIDEBAR_W, 24))

    def _menu_btn(self, ebeveyn, metin, y):
        b = QPushButton(metin, ebeveyn)
        b.setGeometry(QRect(12, y, 216, 48))
        b.setStyleSheet(SIDEBAR_BTN)
        b.setCursor(QCursor(Qt.PointingHandCursor))
        return b

    def _icerik_alani(self, ebeveyn):
        self._alan = QWidget(ebeveyn)
        self._alan.setGeometry(QRect(self._SIDEBAR_W, 0, self._REF_W - self._SIDEBAR_W, self._REF_H))
        self._alan.setStyleSheet(f"background-color:{KOYU_ARKAPLAN};")

        # Üst bar
        self._ust = QFrame(self._alan)
        self._ust.setGeometry(QRect(0, 0, self._REF_W - self._SIDEBAR_W, 72))
        self._ust.setStyleSheet(f"QFrame{{background-color:{KENAR_CUBUGU};border:none;border-bottom:1px solid {KENARLIK};}}")

        self.sayfa_baslik  = etiket(self._ust, "Kitap Yönetimi",         YAZI_BIRINCIL, 18, kalin=True)
        self.sayfa_alt     = etiket(self._ust, "Koleksiyonunuzu yönetin", YAZI_SOLUK,   11)
        self.sayfa_baslik.setGeometry(QRect(24, 8, 300, 30))
        self.sayfa_alt.setGeometry(QRect(24, 40, 300, 20))

        self.arama_kutusu = QLineEdit(self._ust)
        self.arama_kutusu.setGeometry(QRect(330, 16, 230, 40))
        self.arama_kutusu.setStyleSheet(ARAMA_STILI)
        self.arama_kutusu.setPlaceholderText("🔍  Kitap ara...")

        self.kategori_combo = QComboBox(self._ust)
        self.kategori_combo.setGeometry(QRect(574, 16, 160, 40))
        self.kategori_combo.setStyleSheet(COMBO_STILI)

        self.ekle_btn = QPushButton("＋  Kitap Ekle", self._ust)
        self.ekle_btn.setGeometry(QRect(748, 16, 100, 40))
        self.ekle_btn.setStyleSheet(EKLE_BTN_STILI)
        self.ekle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        golge_ekle(self.ekle_btn, blur=16, y=3, renk=(37, 99, 235, 100))

        # İstatistik kartları
        self._istatistik_kartlari(self._alan)

        # Tablo alanı
        self._tablo_alani(self._alan)

        # Rapor (grafik) alanı — başlangıçta gizli
        self._rapor_alani(self._alan)

    def _istatistik_kartlari(self, ebeveyn):
        # Kart verilerini saklayarak resize sırasında geometrileri güncelleyebiliriz
        self._kart_verileri = [
            ("lbl_toplam",  "📘  Toplam Kitaplar", VURGU_MAVI,
             f"background-color:#1E3A5F;border-radius:14px;border:1px solid {VURGU_MAVI};", 24/860),
            ("lbl_aktif",   "✅  Aktif Ödünç",     VURGU_YESIL,
             "background-color:#064E3B;border-radius:14px;border:1px solid #10B981;",       310/860),
            ("lbl_geciken", "⚠️  Geciken Ödünç",  VURGU_TURUNCU,
             "background-color:#451A03;border-radius:14px;border:1px solid #F59E0B;",       596/860),
        ]
        self._kartlar = []
        for attr, baslik, renk, stil, x_oran in self._kart_verileri:
            k = QFrame(ebeveyn)
            k.setGeometry(QRect(24, 88, 258, 90))
            k.setStyleSheet(f"QFrame{{{stil}}}")
            golge_ekle(k, blur=20, y=4)
            etiket(k, baslik, YAZI_IKINCIL, 11).setGeometry(QRect(16, 12, 226, 24))
            deger = etiket(k, "—", renk, 26, kalin=True)
            deger.setGeometry(QRect(16, 38, 226, 36))
            setattr(self, attr, deger)
            self._kartlar.append(k)

    def _tablo_alani(self, ebeveyn):
        self._tablo_cerceve = QFrame(ebeveyn)
        self._tablo_cerceve.setGeometry(QRect(24, 198, 812, 590))
        self._tablo_cerceve.setStyleSheet(f"QFrame{{background-color:{KART_ARKAPLAN};border-radius:16px;border:1px solid {KENARLIK};}}")
        golge_ekle(self._tablo_cerceve, blur=24, y=6)

        self._tablo_ust = QFrame(self._tablo_cerceve)
        self._tablo_ust.setGeometry(QRect(0, 0, 812, 56))
        self._tablo_ust.setStyleSheet(f"QFrame{{background:transparent;border:none;border-bottom:1px solid {KENARLIK};}}")

        self.tablo_baslik = etiket(self._tablo_ust, "📋  Kitap Listesi", YAZI_BIRINCIL, 13, kalin=True)
        self.tablo_baslik.setGeometry(QRect(18, 0, 300, 56))

        self.kayit_sayisi = etiket(self._tablo_ust, "", YAZI_SOLUK, 11, hizalama=Qt.AlignRight | Qt.AlignVCenter)
        self.kayit_sayisi.setGeometry(QRect(620, 0, 180, 56))
        self.kayit_sayisi.setStyleSheet(self.kayit_sayisi.styleSheet() + "padding-right:16px;")

        self.tablo = QTableWidget(self._tablo_cerceve)
        self.tablo.setGeometry(QRect(0, 56, 812, 534))
        self.tablo.setStyleSheet(TABLO_STILI)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setShowGrid(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setFocusPolicy(Qt.NoFocus)
        p = self.tablo.palette()
        p.setColor(QPalette.Base,          QColor("#1E293B"))
        p.setColor(QPalette.AlternateBase, QColor("#172035"))
        self.tablo.setPalette(p)

    def _rapor_alani(self, ebeveyn):
        """Raporlar sayfası için kaydırılabilir grafik alanı oluşturur."""
        self._rapor_scroll = QScrollArea(ebeveyn)
        self._rapor_scroll.setGeometry(QRect(24, 88, 812, 700))
        self._rapor_scroll.setWidgetResizable(True)
        self._rapor_scroll.setFrameShape(QFrame.NoFrame)
        self._rapor_scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background:{KOYU_ARKAPLAN}; width:8px; border-radius:4px; }}
            QScrollBar::handle:vertical {{ background:{KENARLIK}; border-radius:4px; min-height:30px; }}
            QScrollBar::handle:vertical:hover {{ background:{VURGU_MAVI}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        self._rapor_icerik = QWidget()
        self._rapor_icerik.setStyleSheet(f"background-color:{KOYU_ARKAPLAN};")
        self._rapor_scroll.setWidget(self._rapor_icerik)
        self._rapor_layout = QGridLayout(self._rapor_icerik)
        self._rapor_layout.setSpacing(16)
        self._rapor_layout.setContentsMargins(0, 0, 0, 16)
        self._rapor_scroll.setVisible(False)

    # ══════════════════════════════════════════════════════════════════════════
    #  PENCERE YENİDEN BOYUTLANDIRMA
    # ══════════════════════════════════════════════════════════════════════════

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        h = event.size().height()
        # Ölçek oranları
        sx = w / self._REF_W
        sy = h / self._REF_H

        # Sol panel
        sw = int(self._SIDEBAR_W * sx)
        self._panel.setGeometry(0, 0, sw, h)
        self._logo.setGeometry(0, 0, sw, 80)
        self._logo_baslik.setGeometry(0, 0, sw, 80)
        self._menu_etiketi.setGeometry(int(16 * sx), 96, int(200 * sx), 24)

        # Menü butonları (y konumları orantılı, genişlikleri panel genişliğine göre)
        btn_w = sw - 24
        btn_yakonumlari = {self.btn_kitaplar: 130, self.btn_uyeler: 200,
                           self.btn_odunc: 270, self.btn_rapor: 340}
        for btn, ref_y in btn_yakonumlari.items():
            btn.setGeometry(12, int(ref_y * sy), btn_w, int(48 * sy))

        self._rol_bilgi.setGeometry(0, h - int(160 * sy), sw, int(24 * sy))
        self._btn_cikis.setGeometry(12, h - int(120 * sy), btn_w, int(44 * sy))
        self._btn_ayar.setGeometry(12, h - int(72 * sy), btn_w, int(44 * sy))
        self._versiyon_etiketi.setGeometry(0, h - int(24 * sy), sw, int(24 * sy))

        # İçerik alanı
        cw = w - sw
        self._alan.setGeometry(sw, 0, cw, h)

        # Üst bar
        self._ust.setGeometry(0, 0, cw, 72)
        # Arama kutusu — referansta 330..560 arası (230px geniş)
        ara_x = int(330 * cw / 860)
        ara_w = int(230 * cw / 860)
        self.arama_kutusu.setGeometry(ara_x, 16, ara_w, 40)
        # Kategori combo — referansta 574..734
        cat_x = int(574 * cw / 860)
        cat_w = int(160 * cw / 860)
        self.kategori_combo.setGeometry(cat_x, 16, cat_w, 40)
        # Ekle butonu — referansta 748..848
        ekle_x = int(748 * cw / 860)
        ekle_w = cw - ekle_x - 12
        self.ekle_btn.setGeometry(ekle_x, 16, max(80, ekle_w), 40)

        # İstatistik kartları
        kart_w = int(258 * cw / 860)
        kart_h = 90
        x_baslangiclar = [int(24 * cw / 860), int(310 * cw / 860), int(596 * cw / 860)]
        for i, kart in enumerate(self._kartlar):
            kart.setGeometry(x_baslangiclar[i], 88, kart_w, kart_h)
            # kart içi etiketler
            for j, child in enumerate(kart.findChildren(type(kart.children()[0]) if kart.children() else object)):
                pass  # etiketler QLabel, boyutları kart ile birlikte yeterince esner

        # Tablo çerçevesi
        tablo_w = cw - 48
        tablo_h = h - 198 - 30
        self._tablo_cerceve.setGeometry(24, 198, tablo_w, tablo_h)
        self._tablo_ust.setGeometry(0, 0, tablo_w, 56)
        self.kayit_sayisi.setGeometry(tablo_w - 200, 0, 190, 56)
        self.tablo.setGeometry(0, 56, tablo_w, tablo_h - 56)

        # Rapor grafik alanı
        rapor_h = h - 88 - 16
        self._rapor_scroll.setGeometry(24, 88, tablo_w, rapor_h)

    # ══════════════════════════════════════════════════════════════════════════
    #  YARDIMCI UI METODLARI
    # ══════════════════════════════════════════════════════════════════════════

    def _aktif_btn_ayarla(self, aktif):
        for b in [self.btn_kitaplar, self.btn_uyeler, self.btn_odunc, self.btn_rapor]:
            b.setStyleSheet(SIDEBAR_BTN_AKTIF if b is aktif else SIDEBAR_BTN)

    def _sayfa_ayarla(self, baslik, alt, btn_metin, kat_goster, aktif_btn, rapor=False):
        self.sayfa_baslik.setText(baslik)
        self.sayfa_alt.setText(alt)
        self.ekle_btn.setText(btn_metin)
        self.tablo_baslik.setText(f"📋  {baslik}")
        self.arama_kutusu.clear()
        self.kategori_combo.setVisible(kat_goster)
        self._aktif_btn_ayarla(aktif_btn)
        # Rapor sayfasında tablo gizle, grafik alanını göster
        self._tablo_cerceve.setVisible(not rapor)
        self._rapor_scroll.setVisible(rapor)
        # Rapor sayfasında istatistik kartlarını ve arama/ekleme UI'ını gizle
        for kart in self._kartlar:
            kart.setVisible(not rapor)
        self.arama_kutusu.setVisible(not rapor)
        self.ekle_btn.setVisible(not rapor)

    def _tablo_hazirla(self, sutunlar, islemler_sutun_genisligi=100):
        self.tablo.clearContents()
        self.tablo.setColumnCount(len(sutunlar))
        self.tablo.setHorizontalHeaderLabels(sutunlar)
        hv = self.tablo.horizontalHeader()
        hv.setSectionResizeMode(len(sutunlar) - 1, QHeaderView.Fixed)
        self.tablo.setColumnWidth(len(sutunlar) - 1, islemler_sutun_genisligi)

    def _satir(self, satir, degerler):
        self.tablo.setRowHeight(satir, 50)
        for sutun, deger in enumerate(degerler):
            item = QTableWidgetItem(f"  {deger}")
            item.setForeground(QBrush(QColor(YAZI_BIRINCIL)))
            self.tablo.setItem(satir, sutun, item)

    def _islem_butonlari(self, satir, sutun, kayit_id, tip):
        kap = QWidget()
        kap.setStyleSheet("background:transparent;")
        d = QHBoxLayout(kap)
        d.setContentsMargins(14, 6, 4, 6)
        d.setSpacing(10)
        e = QPushButton("✏")
        e.setFixedSize(34, 34)
        s = QPushButton("🗑")
        s.setFixedSize(34, 34)
        if self._admin_mod:
            e.setStyleSheet(DUZENLE_BTN)
            s.setStyleSheet(SIL_BTN)
            e.setToolTip("Düzenle")
            s.setToolTip("Sil")
            if tip == "kitap":
                e.clicked.connect(lambda _, r=kayit_id: self.kitap_duzenle(r))
                s.clicked.connect(lambda _, r=kayit_id: self.kitap_sil(r))
            else:
                e.clicked.connect(lambda _, r=kayit_id: self.uye_duzenle(r))
                s.clicked.connect(lambda _, r=kayit_id: self.uye_sil(r))
        else:
            e.setStyleSheet(KILITLI_BTN)
            s.setStyleSheet(KILITLI_BTN)
            e.setToolTip("🔒 Admin girişi gerekli")
            s.setToolTip("🔒 Admin girişi gerekli")
            e.setCursor(QCursor(Qt.ForbiddenCursor))
            s.setCursor(QCursor(Qt.ForbiddenCursor))
        d.addWidget(e)
        d.addWidget(s)
        d.addStretch()
        self.tablo.setCellWidget(satir, sutun, kap)

    def _iade_butonu(self, satir, sutun, odunc_id):
        kap = QWidget()
        kap.setStyleSheet("background:transparent;")
        d = QHBoxLayout(kap)
        d.setContentsMargins(14, 6, 4, 6)
        if self._admin_mod or self._kullanici_mod:
            b = QPushButton("↩ İade Et")
            b.setFixedHeight(32)
            b.setStyleSheet(IADE_BTN)
            b.clicked.connect(lambda _, r=odunc_id: self.odunc_iade(r))
            b.setToolTip("İade işlemi yap")
        else:
            b = QPushButton("🔒 Kilitli")
            b.setFixedHeight(32)
            b.setStyleSheet(KILITLI_BTN)
            b.setToolTip("🔒 Giriş yapmanız gerekli")
            b.setCursor(QCursor(Qt.ForbiddenCursor))
        d.addWidget(b)
        d.addStretch()
        self.tablo.setCellWidget(satir, sutun, kap)

    def _kategori_listesi(self):
        return [self.kategori_combo.itemText(i) for i in range(self.kategori_combo.count())]

    # ══════════════════════════════════════════════════════════════════════════
    #  BACKEND — İSTATİSTİK & KATEGORİ
    # ══════════════════════════════════════════════════════════════════════════

    # ── Oturum yönetimi ────────────────────────────────────────────────────────

    def _cikis_yap(self):
        """Oturumu kapatıp uygulamayı giriş ekranına döndürür."""
        cevap = QMessageBox.question(
            self, "Çıkış Yap", "Oturumu kapatmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if cevap == QMessageBox.Yes:
            # Pencereyi kapat, bu sayede main()'deki app.exec() sonlanır ve
            # while döngüsü tekrar GirisEkrani'ni gösterir.
            self.close()

    def _ayarlar_ac(self):
        """Ayarlar diyaloğunu açar; sadece admin erişebilir."""
        if not self._admin_mod:
            QMessageBox.warning(self, "Erişim Engellendi", "Bu işlem için admin yetkisi gereklidir.")
            return
        dlg = AyarlarDialog(self, self.db.execute("PRAGMA database_list").fetchone()[2])
        if dlg.exec():
            yeni_yol = dlg.yeni_db_yolu()
            if yeni_yol and yeni_yol != self.db.execute("PRAGMA database_list").fetchone()[2]:
                try:
                    yeni_db = sqlite3.connect(yeni_yol)
                    yeni_db.row_factory = sqlite3.Row
                    # Bağlantının geçerli olduğunu doğrula
                    yeni_db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                    self.db.close()
                    self.db = yeni_db
                    self._istatistik_guncelle()
                    self._kategori_yukle()
                    self.kitaplar_sayfasi()
                    QMessageBox.information(self, "Başarılı",
                        f"✅ Veritabanı başarıyla değiştirildi:\n{yeni_yol}")
                except Exception as ex:
                    QMessageBox.critical(self, "Hata",
                        f"Veritabanı açılamadı:\n{ex}")

    # ── İstatistik & Kategori ─────────────────────────────────────────────────

    def _istatistik_guncelle(self):
        toplam  = self.db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        aktif   = self.db.execute("SELECT COUNT(*) FROM loans WHERE durum='ödünçte'").fetchone()[0]
        geciken = self.db.execute(
            "SELECT COUNT(*) FROM loans WHERE durum='ödünçte' "
            "AND julianday('now') - julianday(odunc_tarihi) > 14"
        ).fetchone()[0]
        self.lbl_toplam.setText(str(toplam))
        self.lbl_aktif.setText(str(aktif))
        self.lbl_geciken.setText(str(geciken))

    def _kategori_yukle(self):
        rows = self.db.execute("SELECT DISTINCT kategori FROM books ORDER BY kategori").fetchall()
        self.kategori_combo.blockSignals(True)
        mevcut = self.kategori_combo.currentText()
        self.kategori_combo.clear()
        self.kategori_combo.addItem("Tümü")
        for r in rows:
            self.kategori_combo.addItem(r[0])
        idx = self.kategori_combo.findText(mevcut)
        self.kategori_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.kategori_combo.blockSignals(False)

    # ══════════════════════════════════════════════════════════════════════════
    #  SAYFA GEÇİŞLERİ & ARAMA
    # ══════════════════════════════════════════════════════════════════════════

    def kitaplar_sayfasi(self):
        self.sayfa = "kitaplar"
        self._sayfa_ayarla("Kitap Yönetimi", "Koleksiyonunuzu yönetin",
                            "＋  Kitap Ekle", True, self.btn_kitaplar)
        self._kategori_yukle()
        self.kitaplari_yukle()

    def uyeler_sayfasi(self):
        self.sayfa = "uyeler"
        self._sayfa_ayarla("Üye Yönetimi", "Üyelerinizi yönetin",
                            "＋  Üye Ekle", False, self.btn_uyeler)
        self.uyeleri_yukle()

    def odunc_sayfasi(self):
        self.sayfa = "odunc"
        self._sayfa_ayarla("Ödünç İşlemleri", "Ödünç alma/iade işlemleri",
                            "＋  Ödünç Ver", False, self.btn_odunc)
        self.oduncleri_yukle()

    def rapor_sayfasi(self):
        self.sayfa = "rapor"
        self._sayfa_ayarla("Raporlar", "Genel istatistikler ve özetler",
                            "—", False, self.btn_rapor, rapor=True)
        self.raporlari_yukle()

    def ara(self):
        {"kitaplar": self.kitaplari_yukle,
         "uyeler":   self.uyeleri_yukle,
         "odunc":    self.oduncleri_yukle}.get(self.sayfa, lambda: None)()

    def ekle(self):
        {"kitaplar": self.kitap_ekle,
         "uyeler":   self.uye_ekle,
         "odunc":    self.odunc_ekle}.get(self.sayfa, lambda: None)()

    # ══════════════════════════════════════════════════════════════════════════
    #  KİTAP İŞLEMLERİ
    # ══════════════════════════════════════════════════════════════════════════

    def kitaplari_yukle(self):
        arama  = self.arama_kutusu.text()
        kat    = self.kategori_combo.currentText()
        sql    = "SELECT * FROM books WHERE 1=1"
        params = []
        if arama:
            sql += " AND (kitap_adi LIKE ? OR yazar LIKE ? OR isbn LIKE ?)"
            params += [f"%{arama}%"] * 3
        if kat and kat != "Tümü":
            sql += " AND kategori=?"
            params.append(kat)
        kitaplar = self.db.execute(sql, params).fetchall()

        sutunlar = ["  Kitap Adı", "  Yazar", "  ISBN", "  Kategori", "  Yayınevi", "  Yıl", "  Stok", "  İşlemler"]
        self._tablo_hazirla(sutunlar)
        self.tablo.setRowCount(len(kitaplar))
        hv = self.tablo.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Stretch)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        for i in range(2, len(sutunlar) - 1):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        for satir, k in enumerate(kitaplar):
            self._satir(satir, [k["kitap_adi"], k["yazar"], k["isbn"], k["kategori"],
                                k["yayinevi"], k["yayin_yili"], k["stok"]])
            self._islem_butonlari(satir, len(sutunlar) - 1, k["kitap_id"], "kitap")
        self.kayit_sayisi.setText(f"{len(kitaplar)} kitap gösteriliyor")

    def kitap_ekle(self):
        dlg = KitapDiyalogu(self, self._kategori_listesi())
        if dlg.exec():
            d = dlg.veri_al()
            if not d["kitap_adi"] or not d["yazar"]:
                QMessageBox.warning(self, "Uyarı", "Kitap adı ve yazar boş bırakılamaz!")
                return
            self.db.execute(
                "INSERT INTO books (kitap_adi,yazar,kategori,yayin_yili,isbn,yayinevi,stok) VALUES (?,?,?,?,?,?,?)",
                (d["kitap_adi"], d["yazar"], d["kategori"], d["yayin_yili"], d["isbn"], d["yayinevi"], d["stok"])
            )
            self.db.commit()
            self._istatistik_guncelle()
            self.kitaplari_yukle()

    def kitap_duzenle(self, kitap_id):
        k = self.db.execute("SELECT * FROM books WHERE kitap_id=?", (kitap_id,)).fetchone()
        if not k:
            return
        dlg = KitapDiyalogu(self, self._kategori_listesi(), k)
        if dlg.exec():
            d = dlg.veri_al()
            self.db.execute(
                "UPDATE books SET kitap_adi=?,yazar=?,kategori=?,yayin_yili=?,isbn=?,yayinevi=?,stok=? WHERE kitap_id=?",
                (d["kitap_adi"], d["yazar"], d["kategori"], d["yayin_yili"], d["isbn"], d["yayinevi"], d["stok"], kitap_id)
            )
            self.db.commit()
            self.kitaplari_yukle()

    def kitap_sil(self, kitap_id):
        if QMessageBox.question(self, "Sil", "Bu kitabı silmek istiyor musunuz?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.execute("DELETE FROM books WHERE kitap_id=?", (kitap_id,))
            self.db.commit()
            self._istatistik_guncelle()
            self.kitaplari_yukle()

    # ══════════════════════════════════════════════════════════════════════════
    #  ÜYE İŞLEMLERİ
    # ══════════════════════════════════════════════════════════════════════════

    def uyeleri_yukle(self):
        arama  = self.arama_kutusu.text()
        sql    = "SELECT * FROM members WHERE 1=1"
        params = []
        if arama:
            sql += " AND (ad LIKE ? OR soyad LIKE ? OR email LIKE ? OR telefon LIKE ?)"
            params += [f"%{arama}%"] * 4
        uyeler = self.db.execute(sql, params).fetchall()

        sutunlar = ["  Ad", "  Soyad", "  Telefon", "  E-posta", "  Üyelik Tarihi", "  İşlemler"]
        self._tablo_hazirla(sutunlar)
        self.tablo.setRowCount(len(uyeler))
        hv = self.tablo.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Stretch)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.Stretch)
        hv.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        for satir, u in enumerate(uyeler):
            self._satir(satir, [u["ad"], u["soyad"], u["telefon"], u["email"], u["uyelik_tarihi"]])
            self._islem_butonlari(satir, len(sutunlar) - 1, u["uye_id"], "uye")
        self.kayit_sayisi.setText(f"{len(uyeler)} üye gösteriliyor")

    def uye_ekle(self):
        dlg = UyeDiyalogu(self)
        if dlg.exec():
            d = dlg.veri_al()
            if not d["ad"] or not d["soyad"]:
                QMessageBox.warning(self, "Uyarı", "Ad ve soyad boş bırakılamaz!")
                return
            self.db.execute(
                "INSERT INTO members (ad,soyad,telefon,email,uyelik_tarihi) VALUES (?,?,?,?,?)",
                (d["ad"], d["soyad"], d["telefon"], d["email"], str(date.today()))
            )
            self.db.commit()
            self.uyeleri_yukle()

    def uye_duzenle(self, uye_id):
        u = self.db.execute("SELECT * FROM members WHERE uye_id=?", (uye_id,)).fetchone()
        if not u:
            return
        dlg = UyeDiyalogu(self, u)
        if dlg.exec():
            d = dlg.veri_al()
            self.db.execute(
                "UPDATE members SET ad=?,soyad=?,telefon=?,email=? WHERE uye_id=?",
                (d["ad"], d["soyad"], d["telefon"], d["email"], uye_id)
            )
            self.db.commit()
            self.uyeleri_yukle()

    def uye_sil(self, uye_id):
        if QMessageBox.question(self, "Sil", "Bu üyeyi silmek istiyor musunuz?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.execute("DELETE FROM members WHERE uye_id=?", (uye_id,))
            self.db.commit()
            self.uyeleri_yukle()

    # ══════════════════════════════════════════════════════════════════════════
    #  ÖDÜNÇ İŞLEMLERİ
    # ══════════════════════════════════════════════════════════════════════════

    def oduncleri_yukle(self):
        arama  = self.arama_kutusu.text()
        sql = """
            SELECT l.odunc_id, b.kitap_adi, b.isbn,
                   m.ad || ' ' || m.soyad AS uye_adi,
                   l.odunc_tarihi, l.iade_tarihi, l.durum
            FROM loans l
            JOIN books   b ON l.kitap_id = b.kitap_id
            JOIN members m ON l.uye_id   = m.uye_id
        """
        params = []
        if arama:
            sql += " WHERE (b.kitap_adi LIKE ? OR m.ad LIKE ? OR m.soyad LIKE ?)"
            params += [f"%{arama}%"] * 3
        sql += " ORDER BY l.odunc_id DESC"
        oduncler = self.db.execute(sql, params).fetchall()

        sutunlar = ["  Kitap Adı", "  ISBN", "  Üye", "  Ödünç Tarihi", "  İade Tarihi", "  Durum", "  İşlemler"]
        self._tablo_hazirla(sutunlar, islemler_sutun_genisligi=110)
        self.tablo.setRowCount(len(oduncler))
        hv = self.tablo.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Stretch)
        hv.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(2, QHeaderView.Stretch)
        for i in range(3, len(sutunlar) - 1):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        for satir, l in enumerate(oduncler):
            self._satir(satir, [l["kitap_adi"], l["isbn"], l["uye_adi"],
                                l["odunc_tarihi"], l["iade_tarihi"] or "—"])
            durum = l["durum"]
            fg, bg = DURUM_RENKLERI.get(durum, (YAZI_IKINCIL, KART_ARKAPLAN))
            d_item = QTableWidgetItem(f"  {durum.capitalize()}")
            d_item.setForeground(QBrush(QColor(fg)))
            d_item.setBackground(QBrush(QColor(bg)))
            d_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.tablo.setItem(satir, 5, d_item)
            if durum == "ödünçte":
                self._iade_butonu(satir, len(sutunlar) - 1, l["odunc_id"])
            else:
                bitti = QTableWidgetItem("  ✓ İade Edildi")
                bitti.setForeground(QBrush(QColor(YAZI_SOLUK)))
                self.tablo.setItem(satir, len(sutunlar) - 1, bitti)
        self.kayit_sayisi.setText(f"{len(oduncler)} kayıt gösteriliyor")

    def odunc_ekle(self):
        kitaplar = self.db.execute("SELECT kitap_id, kitap_adi, isbn FROM books").fetchall()
        uyeler   = self.db.execute("SELECT uye_id, ad, soyad, email FROM members").fetchall()
        dlg = OduncDiyalogu(self, kitaplar, uyeler)
        if dlg.exec():
            kitap_id, uye_id = dlg.veri_al()
            self.db.execute(
                "INSERT INTO loans (kitap_id,uye_id,odunc_tarihi,iade_tarihi,durum) VALUES (?,?,?,'','ödünçte')",
                (kitap_id, uye_id, str(date.today()))
            )
            self.db.commit()
            self._istatistik_guncelle()
            self.oduncleri_yukle()

    def odunc_iade(self, odunc_id):
        if QMessageBox.question(self, "İade", "Kitabı iade olarak işaretlemek istiyor musunuz?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.execute(
                "UPDATE loans SET durum='iade edildi', iade_tarihi=? WHERE odunc_id=?",
                (str(date.today()), odunc_id)
            )
            self.db.commit()
            self._istatistik_guncelle()
            self.oduncleri_yukle()

    # ══════════════════════════════════════════════════════════════════════════
    #  RAPORLAR — Matplotlib Grafikleri
    # ══════════════════════════════════════════════════════════════════════════

    # ── Grafik renk paleti (koyu tema ile uyumlu) ─────────────────────────────
    _GRAFIK_RENKLER = [
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
        "#EC4899", "#06B6D4", "#F97316", "#14B8A6", "#A855F7",
        "#6366F1", "#22D3EE", "#FB923C", "#4ADE80", "#F472B6",
    ]

    def _grafik_stili(self, fig, ax):
        """Matplotlib figure ve axes'e koyu tema uygular."""
        fig.patch.set_facecolor("#1E293B")
        ax.set_facecolor("#1E293B")
        ax.tick_params(colors="#94A3B8", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#334155")
        ax.spines["bottom"].set_color("#334155")
        ax.xaxis.label.set_color("#94A3B8")
        ax.yaxis.label.set_color("#94A3B8")
        ax.title.set_color("#F1F5F9")

    def _grafik_karti(self, canvas):
        """Bir matplotlib canvas'ı kart görünümlü QFrame'e sarar."""
        kart = QFrame()
        kart.setStyleSheet(
            f"QFrame{{background-color:{KART_ARKAPLAN};"
            f"border-radius:14px;border:1px solid {KENARLIK};}}"
        )
        layout = QVBoxLayout(kart)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(canvas)
        golge_ekle(kart, blur=20, y=4)
        return kart

    def raporlari_yukle(self):
        """Rapor sayfasını 4 adet matplotlib grafiği ile doldurur."""
        # Önceki grafikleri temizle
        while self._rapor_layout.count():
            item = self._rapor_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # ── VERİ SORGULARI ────────────────────────────────────────────────────

        # 1) Kategorilere göre kitap dağılımı
        kat_veriler = self.db.execute("""
            SELECT kategori, COUNT(*) AS toplam
            FROM books GROUP BY kategori ORDER BY toplam DESC
        """).fetchall()
        kat_isim  = [r["kategori"] for r in kat_veriler]
        kat_sayi  = [r["toplam"]   for r in kat_veriler]

        # 2) Kategori bazlı ödünç durumu
        durum_veriler = self.db.execute("""
            SELECT b.kategori,
                   COUNT(DISTINCT b.kitap_id) AS toplam,
                   COUNT(DISTINCT CASE WHEN l.durum='ödünçte' THEN l.odunc_id END) AS oduncte
            FROM books b
            LEFT JOIN loans l ON b.kitap_id = l.kitap_id
            GROUP BY b.kategori ORDER BY toplam DESC
        """).fetchall()

        # 3) Aylık ödünç trendi
        ay_veriler = self.db.execute("""
            SELECT strftime('%Y-%m', odunc_tarihi) AS ay, COUNT(*) AS sayi
            FROM loans
            WHERE odunc_tarihi != ''
            GROUP BY ay ORDER BY ay
        """).fetchall()

        # 4) En çok ödünç alınan kitaplar (top 10)
        pop_veriler = self.db.execute("""
            SELECT b.kitap_adi, COUNT(l.odunc_id) AS odunc_sayi
            FROM loans l
            JOIN books b ON l.kitap_id = b.kitap_id
            GROUP BY l.kitap_id
            ORDER BY odunc_sayi DESC
            LIMIT 10
        """).fetchall()

        # ── GRAFİK 1: Pasta — Kategorilere Göre Dağılım ──────────────────────
        fig1 = Figure(figsize=(5, 3.5), dpi=100)
        fig1.patch.set_facecolor("#1E293B")
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor("#1E293B")
        renkler = self._GRAFIK_RENKLER[:len(kat_isim)]
        wedges, texts, autotexts = ax1.pie(
            kat_sayi, labels=None, autopct="%1.1f%%",
            colors=renkler, startangle=140,
            pctdistance=0.80,
            wedgeprops={"linewidth": 1.5, "edgecolor": "#1E293B"},
        )
        for t in autotexts:
            t.set_color("#F1F5F9")
            t.set_fontsize(8)
            t.set_fontweight("bold")
        ax1.legend(
            wedges, kat_isim, loc="center left", bbox_to_anchor=(1.0, 0.5),
            fontsize=8, frameon=False, labelcolor="#94A3B8"
        )
        ax1.set_title("Kategorilere Göre Kitap Dağılımı", fontsize=13,
                      fontweight="bold", color="#F1F5F9", pad=12)
        fig1.tight_layout()
        canvas1 = FigureCanvas(fig1)
        canvas1.setMinimumHeight(300)

        # ── GRAFİK 2: Gruplu Bar — Ödünç Durumu ──────────────────────────────
        fig2 = Figure(figsize=(5, 3.5), dpi=100)
        ax2 = fig2.add_subplot(111)
        self._grafik_stili(fig2, ax2)
        d_kat   = [r["kategori"]  for r in durum_veriler]
        d_top   = [r["toplam"]    for r in durum_veriler]
        d_odunc = [r["oduncte"] or 0 for r in durum_veriler]
        d_mevcut = [t - o for t, o in zip(d_top, d_odunc)]
        import numpy as np
        x = np.arange(len(d_kat))
        bar_w = 0.35
        b1 = ax2.bar(x - bar_w / 2, d_mevcut, bar_w, label="Mevcut",
                     color="#10B981", edgecolor="#1E293B", linewidth=0.5, zorder=3)
        b2 = ax2.bar(x + bar_w / 2, d_odunc, bar_w, label="Ödünçte",
                     color="#3B82F6", edgecolor="#1E293B", linewidth=0.5, zorder=3)
        ax2.set_xticks(x)
        ax2.set_xticklabels(d_kat, rotation=35, ha="right", fontsize=8, color="#94A3B8")
        ax2.set_ylabel("Adet", fontsize=10)
        ax2.set_title("Kategorilere Göre Ödünç Durumu", fontsize=13,
                      fontweight="bold", color="#F1F5F9", pad=12)
        ax2.legend(fontsize=9, frameon=False, labelcolor="#94A3B8")
        ax2.grid(axis="y", color="#334155", linewidth=0.5, alpha=0.5)
        ax2.set_axisbelow(True)
        fig2.tight_layout()
        canvas2 = FigureCanvas(fig2)
        canvas2.setMinimumHeight(300)

        # ── GRAFİK 3: Çizgi — Aylık Ödünç Trendi ─────────────────────────────
        fig3 = Figure(figsize=(5, 3.5), dpi=100)
        ax3 = fig3.add_subplot(111)
        self._grafik_stili(fig3, ax3)
        aylar  = [r["ay"]   for r in ay_veriler]
        sayilar = [r["sayi"] for r in ay_veriler]
        ax3.fill_between(range(len(aylar)), sayilar, alpha=0.15, color="#3B82F6")
        ax3.plot(range(len(aylar)), sayilar, color="#3B82F6", linewidth=2.5,
                 marker="o", markersize=5, markerfacecolor="#60A5FA",
                 markeredgecolor="#1E293B", markeredgewidth=1.5, zorder=5)
        ax3.set_xticks(range(len(aylar)))
        ax3.set_xticklabels(aylar, rotation=45, ha="right", fontsize=7, color="#94A3B8")
        ax3.set_ylabel("Ödünç Sayısı", fontsize=10)
        ax3.set_title("Aylık Ödünç Alma Trendi", fontsize=13,
                      fontweight="bold", color="#F1F5F9", pad=12)
        ax3.grid(axis="y", color="#334155", linewidth=0.5, alpha=0.5)
        ax3.set_axisbelow(True)
        fig3.tight_layout()
        canvas3 = FigureCanvas(fig3)
        canvas3.setMinimumHeight(300)

        # ── GRAFİK 4: Yatay Bar — En Popüler Kitaplar ────────────────────────
        fig4 = Figure(figsize=(5, 3.5), dpi=100)
        ax4 = fig4.add_subplot(111)
        self._grafik_stili(fig4, ax4)
        p_isim = [r["kitap_adi"][:25] + ("…" if len(r["kitap_adi"]) > 25 else "")
                  for r in reversed(pop_veriler)]
        p_sayi = [r["odunc_sayi"] for r in reversed(pop_veriler)]
        renk_grad = ["#3B82F6" if i >= len(p_sayi) - 3 else "#60A5FA"
                     for i in range(len(p_sayi))]
        bars = ax4.barh(range(len(p_isim)), p_sayi, color=renk_grad,
                        edgecolor="#1E293B", linewidth=0.5, height=0.6, zorder=3)
        ax4.set_yticks(range(len(p_isim)))
        ax4.set_yticklabels(p_isim, fontsize=8, color="#94A3B8")
        ax4.set_xlabel("Ödünç Sayısı", fontsize=10)
        ax4.set_title("En Çok Ödünç Alınan Kitaplar (Top 10)", fontsize=13,
                      fontweight="bold", color="#F1F5F9", pad=12)
        # Barların ucuna değer yaz
        for bar, val in zip(bars, p_sayi):
            ax4.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     str(val), va="center", fontsize=9, color="#60A5FA", fontweight="bold")
        ax4.grid(axis="x", color="#334155", linewidth=0.5, alpha=0.5)
        ax4.set_axisbelow(True)
        fig4.tight_layout()
        canvas4 = FigureCanvas(fig4)
        canvas4.setMinimumHeight(300)

        # ── Kartları grid'e yerleştir (2×2) ───────────────────────────────────
        self._rapor_layout.addWidget(self._grafik_karti(canvas1), 0, 0)
        self._rapor_layout.addWidget(self._grafik_karti(canvas2), 0, 1)
        self._rapor_layout.addWidget(self._grafik_karti(canvas3), 1, 0)
        self._rapor_layout.addWidget(self._grafik_karti(canvas4), 1, 1)


# ── Uygulama başlangıcı ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    while True:
        giris = GirisEkrani()
        if giris.exec() == QDialog.Accepted:
            # Giriş başarılı, ana pencereyi aç
            pencere = MainWindow(giris.rol)
            pencere.show()
            app.exec()  # Pencere kapatılana kadar bekle
        else:
            # Çarpıya basıp iptal edildiyse tamamen çık
            break
            
    sys.exit(0)
