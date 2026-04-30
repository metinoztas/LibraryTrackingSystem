# Kütüphane Yönetim Sistemi

Bu proje, PySide6 (PyQt6) kullanılarak geliştirilmiş modern ve kullanıcı dostu bir Kütüphane Yönetim Sistemi masaüstü uygulamasıdır. İçerisinde kitap, üye ve ödünç verme işlemlerinin takibi yapılmaktadır. Ayrıca, güvenli işlemler için bir yönetici (admin) modülü bulunur.

---

## Proje Dosyaları ve İşlevleri

Proje dizinindeki her bir dosyanın ve klasörün amacı aşağıda açıklanmıştır:

* **`mainwindow.py`**: Projenin kalbidir. Uygulamanın çalıştırıldığı ana dosyadır. Kullanıcı arayüzünün (UI) oluşturulması, buton etkileşimleri, veritabanı bağlantıları, sayfa geçişleri ve ekleme/silme/düzenleme (CRUD) operasyonlarının tamamı bu dosya içerisinde yönetilir.
* **`styles.py`**: Uygulamanın modern ve şık görünmesini sağlayan renk paletlerini, CSS/QSS stil tanımlarını ve görsel bileşen (gölge, etiket vb.) oluşturan yardımcı fonksiyonları barındırır. `mainwindow.py` tarafından içeri aktarılır.
* **`veriSeti/library_dataset.db`**: Uygulamanın veritabanı dosyasıdır. Kitaplar, üyeler ve ödünç kayıtları bu SQLite veritabanında saklanır.
* **`adminBilgiler.txt`**: Yönetici (Admin) girişi için gerekli olan kullanıcı adı ve şifre bilgilerini referans amaçlı tutan basit bir metin dosyasıdır.
* **`requirements.txt`**: Projenin çalışması için kurulması gereken Python kütüphanelerini listeler. Bu proje için temel olarak `PySide6` gereklidir.
* **`pyproject.toml`**: Python projesinin temel yapılandırma dosyasıdır.


---

## Kod Yapısı ve Parça Parça Açıklamalar

Projenin temelini oluşturan Python dosyaları modüler bir yapıda tasarlanmıştır.

### 1. `mainwindow.py` Yapısı

Bu dosya kendi içerisinde belirli sorumluluklara ayrılmış sınıflardan (class) oluşur:

* **Diyalog Sınıfları (`KitapDiyalogu`, `UyeDiyalogu`, `OduncDiyalogu`)**:
  Kullanıcı "Ekle" veya "Düzenle" butonuna tıkladığında açılan açılır pencerelerdir (Modal Dialog). Arayüzdeki form elemanlarını (metin kutuları, açılır listeler) içerir ve kullanıcının girdiği verileri toplayıp bir sözlük (dictionary) veya veri seti halinde ana pencereye geri döndürür.

* **Admin ve Ayarlar Diyalogları (`AdminGirisDialog`, `AyarlarDialog`)**:
  * `AdminGirisDialog`: Hassas işlemler (silme, düzenleme, iade etme) yapılmadan önce kullanıcının yetkisini doğrulamak için tasarlanmıştır.
  * `AyarlarDialog`: Sadece yetkili adminlerin erişebildiği, mevcut `.db` veritabanı dosyasının konumunu değiştirmeye yarayan bir menüdür.

* **Ana Pencere Sınıfı (`MainWindow`)**:
  * **`__init__`**: Uygulama başlatıldığında veritabanına bağlanır, arayüzü kurar, sinyal-slot (buton tıklama) bağlantılarını yapar ve varsayılan olarak kitaplar sayfasını yükler.
  * **UI Kurulum Metodları (`_ui_kur`, `_sol_panel`, `_icerik_alani`, `_istatistik_kartlari`, vb.)**: Arayüzün Qt Designer kullanmadan doğrudan Python kodları ile dinamik olarak çizildiği kısımdır. Sol menü, üst bar, istatistik kartları ve veri tabloları burada oluşturulur.
  * **Pencere Boyutlandırma (`resizeEvent`)**: Pencere boyutu değiştiğinde, içindeki elemanların (butonlar, tablolar, kartlar) oranlı bir şekilde yeniden boyutlanmasını sağlayarak *responsive* (duyarlı) bir görünüm sunar.
  * **Admin Yönetimi (`_admin_giris_cikis`, `_admin_ui_guncelle`)**: Sistemde admin girişinin yapılıp yapılmadığını takip eder. Eğer giriş yapılmamışsa, tablodaki "Düzenle", "Sil", "İade Et" gibi butonları görsel olarak kilitler ve tıklanmasını engeller.
  * **Veritabanı İşlemleri (`kitaplari_yukle`, `kitap_ekle`, vb.)**: SQLite veritabanına SQL sorguları atarak (SELECT, INSERT, UPDATE, DELETE) verileri çeker ve tablolara (`QTableWidget`) yansıtır. Aynı işlemler Üyeler ve Ödünç fonksiyonları için de tanımlanmıştır.

### 2. `styles.py` Yapısı

Kapsamlı bir UI kütüphanesi gibi görev yapar. Tasarım bütünlüğünü sağlamak için ayrılmıştır:

* **Renk Paleti**: Arka plan, vurgu (mavi, yeşil, kırmızı vb.) ve metin renkleri için sabit değişkenler (Örn: `KOYU_ARKAPLAN`, `VURGU_MAVI`) tanımlanmıştır.
* **QSS Stilleri**: PySide6 bileşenlerinin görünümünü özelleştirmek için yazılmış CSS benzeri string değişkenleridir. `GENEL_STIL`, `TABLO_STILI`, `DIYALOG_STILI` gibi yapıların içinde tabloların satır aralıkları, menü butonlarının hover (üzerine gelme) renkleri gibi detaylar bulunur.
* **Yardımcı Fonksiyonlar**:
  * `golge_ekle`: Bileşenlerin arkasına modern bir derinlik/gölge (DropShadow) katmak için kullanılır.
  * `etiket`: Sürekli aynı QSS kodlarını yazmamak için; metin, boyut ve renk parametreleri alıp özelleştirilmiş bir `QLabel` döndüren pratik bir fonksiyondur.
