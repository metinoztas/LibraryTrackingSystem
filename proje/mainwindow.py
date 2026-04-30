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

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QVBoxLayout, QWidget
)

# Stiller ve yardımcı fonksiyonlar styles.py'den geliyor
from styles import (
    KOYU_ARKAPLAN, KENAR_CUBUGU, KART_ARKAPLAN,
    VURGU_MAVI, VURGU_YESIL, VURGU_TURUNCU, VURGU_KIRMIZI,
    YAZI_BIRINCIL, YAZI_IKINCIL, YAZI_SOLUK, KENARLIK,
    DURUM_RENKLERI,
    GENEL_STIL, SIDEBAR_BTN, SIDEBAR_BTN_AKTIF, SIDEBAR_BTN_AYARLAR,
    SIDEBAR_BTN_AYARLAR_AKTIF, ADMIN_GIRIS_BTN, ADMIN_AKTIF_BTN, KILITLI_BTN,
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
#  ADMİN GİRİŞ DİYALOGU
# ══════════════════════════════════════════════════════════════════════════════

# Sabit kimlik bilgileri — gerçek uygulamada hash'lenmiş DB'den gelmeli
_ADMIN_KULLANICI = "admin"
_ADMIN_SIFRE     = "admin123"


class AdminGirisDialog(QDialog):
    def __init__(self, ebeveyn):
        super().__init__(ebeveyn)
        self.setWindowTitle("🔐 Admin Girişi")
        self.setFixedSize(380, 240)
        self.setStyleSheet(DIYALOG_STILI)

        ana = QVBoxLayout(self)
        ana.setContentsMargins(32, 28, 32, 28)
        ana.setSpacing(16)

        baslik = QLabel("🔐  Admin Girişi")
        baslik.setStyleSheet(
            f"color:{YAZI_BIRINCIL}; font-family:'Segoe UI';"
            "font-size:17px; font-weight:700; background:transparent; border:none;"
        )
        baslik.setAlignment(Qt.AlignCenter)
        ana.addWidget(baslik)

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

        self.hata_lbl = QLabel("")
        self.hata_lbl.setStyleSheet(
            f"color:{VURGU_KIRMIZI}; font-family:'Segoe UI';"
            "font-size:11px; background:transparent; border:none;"
        )
        self.hata_lbl.setAlignment(Qt.AlignCenter)
        ana.addWidget(self.hata_lbl)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("Giriş Yap")
        bb.button(QDialogButtonBox.Cancel).setText("İptal")
        bb.accepted.connect(self._dogrula)
        bb.rejected.connect(self.reject)
        ana.addWidget(bb)

        # Enter tuşuyla giriş
        self.sifre.returnPressed.connect(self._dogrula)

    def _dogrula(self):
        k = self.kullanici.text().strip()
        s = self.sifre.text()
        if k == _ADMIN_KULLANICI and s == _ADMIN_SIFRE:
            self.accept()
        else:
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

    def __init__(self):
        super().__init__()
        self._admin_mod = False   # Admin oturum durumu
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
        self._btn_admin.clicked.connect(self._admin_giris_cikis)
        self._btn_ayar.clicked.connect(self._ayarlar_ac)
        # Başlangıç
        self._kategori_yukle()
        self._istatistik_guncelle()
        self.kitaplar_sayfasi()
        self._admin_ui_guncelle()

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

        # Alt butonlar: Admin Girişi + Ayarlar
        self._btn_admin = QPushButton("🔐  Admin Girişi", self._panel)
        self._btn_admin.setGeometry(QRect(12, 692, 216, 44))
        self._btn_admin.setStyleSheet(ADMIN_GIRIS_BTN)
        self._btn_admin.setCursor(QCursor(Qt.PointingHandCursor))

        self._btn_ayar = QPushButton("⚙️  Ayarlar", self._panel)
        self._btn_ayar.setGeometry(QRect(12, 744, 216, 44))
        self._btn_ayar.setStyleSheet(SIDEBAR_BTN_AYARLAR)
        self._btn_ayar.setEnabled(False)    # Admin olmadan kilitli
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

        self._btn_admin.setGeometry(12, h - int(120 * sy), btn_w, int(44 * sy))
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

    # ══════════════════════════════════════════════════════════════════════════
    #  YARDIMCI UI METODLARI
    # ══════════════════════════════════════════════════════════════════════════

    def _aktif_btn_ayarla(self, aktif):
        for b in [self.btn_kitaplar, self.btn_uyeler, self.btn_odunc, self.btn_rapor]:
            b.setStyleSheet(SIDEBAR_BTN_AKTIF if b is aktif else SIDEBAR_BTN)

    def _sayfa_ayarla(self, baslik, alt, btn_metin, kat_goster, aktif_btn):
        self.sayfa_baslik.setText(baslik)
        self.sayfa_alt.setText(alt)
        self.ekle_btn.setText(btn_metin)
        self.tablo_baslik.setText(f"📋  {baslik}")
        self.arama_kutusu.clear()
        self.kategori_combo.setVisible(kat_goster)
        self._aktif_btn_ayarla(aktif_btn)

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
        if self._admin_mod:
            b = QPushButton("↩ İade Et")
            b.setFixedHeight(32)
            b.setStyleSheet(IADE_BTN)
            b.clicked.connect(lambda _, r=odunc_id: self.odunc_iade(r))
            b.setToolTip("İade işlemi yap")
        else:
            b = QPushButton("🔒 Kilitli")
            b.setFixedHeight(32)
            b.setStyleSheet(KILITLI_BTN)
            b.setToolTip("🔒 Admin girişi gerekli")
            b.setCursor(QCursor(Qt.ForbiddenCursor))
        d.addWidget(b)
        d.addStretch()
        self.tablo.setCellWidget(satir, sutun, kap)

    def _kategori_listesi(self):
        return [self.kategori_combo.itemText(i) for i in range(self.kategori_combo.count())]

    # ══════════════════════════════════════════════════════════════════════════
    #  BACKEND — İSTATİSTİK & KATEGORİ
    # ══════════════════════════════════════════════════════════════════════════

    # ── Admin yönetimi ────────────────────────────────────────────────────────

    def _admin_giris_cikis(self):
        """Admin giriş/çıkış toggle."""
        if self._admin_mod:
            cevap = QMessageBox.question(
                self, "Admin Çıkışı", "Admin oturumunu kapatmak istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No
            )
            if cevap == QMessageBox.Yes:
                self._admin_mod = False
                self._admin_ui_guncelle()
                self.ara()  # Tabloyu yenile (butonları kilitle)
        else:
            dlg = AdminGirisDialog(self)
            if dlg.exec():
                self._admin_mod = True
                self._admin_ui_guncelle()
                self.ara()  # Tabloyu yenile (butonları aç)
                QMessageBox.information(self, "Başarılı", "✅ Admin olarak giriş yapıldı.")

    def _admin_ui_guncelle(self):
        """Admin durumuna göre sidebar butonlarının görünümünü günceller."""
        if self._admin_mod:
            self._btn_admin.setText("🔓  Admin Çıkışı")
            self._btn_admin.setStyleSheet(ADMIN_AKTIF_BTN)
            self._btn_ayar.setEnabled(True)
            self._btn_ayar.setStyleSheet(SIDEBAR_BTN_AYARLAR_AKTIF)
        else:
            self._btn_admin.setText("🔐  Admin Girişi")
            self._btn_admin.setStyleSheet(ADMIN_GIRIS_BTN)
            self._btn_ayar.setEnabled(False)
            self._btn_ayar.setStyleSheet(SIDEBAR_BTN_AYARLAR)

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
                            "—", False, self.btn_rapor)
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
    #  RAPORLAR
    # ══════════════════════════════════════════════════════════════════════════

    def raporlari_yukle(self):
        veriler = self.db.execute("""
            SELECT b.kategori,
                   COUNT(b.kitap_id) AS toplam,
                   SUM(CASE WHEN l.durum='ödünçte' THEN 1 ELSE 0 END) AS oduncte
            FROM books b
            LEFT JOIN loans l ON b.kitap_id = l.kitap_id
            GROUP BY b.kategori
            ORDER BY toplam DESC
        """).fetchall()

        sutunlar = ["  Kategori", "  Toplam Kitap", "  Ödünçte", "  Mevcut"]
        self._tablo_hazirla(sutunlar, islemler_sutun_genisligi=120)
        self.tablo.setRowCount(len(veriler))
        hv = self.tablo.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, len(sutunlar)):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        for satir, r in enumerate(veriler):
            oduncte = r["oduncte"] or 0
            self._satir(satir, [r["kategori"], str(r["toplam"]), str(oduncte), str(r["toplam"] - oduncte)])
        self.kayit_sayisi.setText(f"{len(veriler)} kategori gösteriliyor")


# ── Uygulama başlangıcı ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pencere = MainWindow()
    pencere.show()
    sys.exit(app.exec())
