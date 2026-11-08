# 🇹🇷 Türkiye Canlı TV - Profesyonel IPTV Platformu (EPG & Akıllı Kategorili)

<div align="center">

[![Otomatik Güncelleme](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/actions/workflows/update.yml/badge.svg)](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/actions/workflows/update.yml)
[![Yasal FTA](https://img.shields.io/badge/Yasal-%25100%20FTA%20A%C3%A7%C4%B1k%20Yay%C4%B1n-success.svg?logo=checkmarx&logoColor=white)](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8#-%C5%9F%C4%B1k%C3%A7a-sorulan-sorular-sss)
[![EPG Desteği](https://img.shields.io/badge/EPG-Otomatik%20XMLTV-purple.svg?logo=rss&logoColor=white)](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8#-do%C4%9Frudan-epg-program-rehberi-adresi)
[![API JSON](https://img.shields.io/badge/API-channels.json-blueviolet.svg?logo=json&logoColor=white)](https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/channels.json)
[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-blue.svg?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/YosemiteSam6/turkiye-iptv-m3u-m3u8?style=social)](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/stargazers)

**Google TV / Android TV, Apple TV, Smart TV (Samsung Tizen, LG webOS) ve tüm mobil cihazlar için optimize edilmiş; %100 yerli, yedekli (failover) yayın korumalı ve otomatik EPG destekli profesyonel Türkiye IPTV platformu.**

[🌐 Canlı Web Sitesi (GitHub Pages)](https://yosemitesam6.github.io/turkiye-iptv-m3u-m3u8/) • [🚨 Bozuk Kanal Bildir](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/issues/new?template=broken_channel.yml) • [📺 Yeni Kanal Öner](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/issues/new?template=channel_request.yml)

</div>

---

## 📑 İçindekiler
- [🌟 Öne Çıkan Özellikler](#-öne-çıkan-profesyonel-özellikler)
- [🚀 Çalma Listesi Bağlantıları](#-tvye-ekleme-canlı-liste-bağlantıları)
  - [1. Genel Liste (Tüm Kanallar)](#1--genel-liste-tüm-türkiye-kanalları---kategorili--epg)
  - [2. Çocuk Özel Listesi](#2--çocuk-özel-listesi-sadece-çocuk-kanalları---güvenli-profil)
  - [3. TOP 50 Özel Listesi](#3--top-50-özel-listesi-sadece-en-çok-izlenen-50-kanal)
  - [4. Doğrudan EPG Adresi](#4--doğrudan-epg-program-rehberi-adresi)
  - [5. API / JSON Veri Çıktısı](#5--api--json-veri-çıktısı-channelsjson)
- [📱 Tüm Cihazlar İçin Kurulum Rehberi](#-tüm-cihazlar-için-kurulum-rehberi)
  - [Android TV & Google TV](#-android-tv--google-tv)
  - [Apple TV, iPad & iPhone](#-apple-tv-ipad--iphone)
  - [Smart TV (LG webOS & Samsung Tizen)](#-smart-tv-lg-webos--samsung-tizen)
  - [PC, Mac & Linux (VLC, Kodi, PotPlayer)](#-pc-mac--linux)
- [📂 Proje ve Dosya Mimarisi](#-dosya-yapısı)
- [🛡️ Sıkça Sorulan Sorular & Yasal Güvence](#-sıkça-sorulan-sorular-sss)
- [🤝 Katkıda Bulunma ve Lisans](#-katkıda-bulunma-ve-lisans)

---

## 🌟 Öne Çıkan Profesyonel Özellikler

1. **🧒 Eksiksiz Çocuk Kanalları (11 Çalışan Çocuk Kanalı):**
   - TV'de çocuk kategorisinde eksiklik yaşanmaması için tüm aktif çocuk ve eğitim yayınları doğrulanıp listeye dahil edilmiştir:
     - **TRT Çocuk**, **Minika Çocuk**, **Minika Go**, **Baby TV**, **Disney Jr.**, **Spacetoon Turkey**, **TRT Diyanet Çocuk**, **TRT EBA İlkokul**, **TRT EBA Ortaokul**, **TRT EBA Lise**, **Zarok TV**
   - Çocuk odaları ve tabletler için sadece bu 11 kanalı içeren izole **`cocuk.m3u`** listesi mevcuttur.

2. **🇹🇷 Sadece %100 Türkiye Kanalları (Yabancı Kanallardan Arındırılmış):**
   - IPTV-org ve Famelack kaynaklarındaki Arapça, Orta Doğu ve yabancı yayınlar filtrelenmiştir.
   - Listede yalnızca Türkiye'ye ait ulusal, çocuk, haber, spor, belgesel, müzik ve yerel kanallar yer alır.

3. **📡 Otomatik EPG (Elektronik Program Rehberi) Entegrasyonu:**
   - M3U başlığına entegre XMLTV EPG kaynağı sayesinde TiviMate, Televizo vb. oynatıcılar yayın akışını otomatik çeker.
   - TV'de kanalın altında *"Şu an ne oynuyor?"*, *"Sırada ne var?"*, *"Kalan süre"* ve kumandanın Rehber tuşunda 24 saatlik yayın akışı tablosu kendiliğinden görüntülenir.

4. **🗂️ Akıllı & Çapraz Kategori Gruplaması (`group-title`):**
   - TV kumandasıyla kolay gezinme için kanallar net ve zengin kategorilere ayrılmıştır. Özellikle 'Tüm Kanallar' sekmesi bulunmayan oynatıcılar için listenin başında tüm kanalları içeren A-Z grubu yer alır:
     - ⭐ **TÜM KANALLAR (A-Z Sıralı):** Tüm yerli kanalları tek bir ekranda, alfabetik olarak listeler (24 TV, ATV, Kanal D, TRT 1, TV8, Zarok TV...).
     - 🏆 **TOP 50 (Reyting & Popülerlik Sıralı):** Diyanet TV (#1), TRT 1, ATV, NOW, Kanal D, Star TV, TV8, Kanal 7 Avrupa, TRT Çocuk, TRT Haber, A Haber, NTV, Habertürk TV, Halk TV, TRT Spor, A Spor, TRT Belgesel... (Türkiye'nin en çok izlenen 50 kanalı izlenme oranına göre sıralı)
     - 🧒 **Çocuk:** TRT Çocuk, Minika Çocuk, Minika Go, Baby TV, Disney Jr., Spacetoon Turkey, TRT Diyanet Çocuk, TRT EBA İlkokul, Ortaokul, Lise, Zarok TV...
     - 📰 **Haber & Ekonomi:** TRT Haber, NTV, Habertürk TV, A Haber, Haber Global, Bloomberg HT, CNBC-e, TV100, Halk TV, Tele1, TGRT Haber, Flash Haber TV, Bengütürk TV, Ekol TV, 24 TV, TRT 3 / TBMM TV, Ekotürk, DHA...
     - ⚽ **Spor:** TRT Spor, TRT Spor Yıldız, A Spor, HTSpor TV, Ekol Sports, FB TV, TJK TV, TJK TV 2, TRT 3 Spor / TBMM TV, Bric ve Satranc TV...
     - 🦁 **Belgesel:** TRT Belgesel, TGRT Belgesel, TRT 2 (Kültür & Belgesel), Çiftçi TV...
     - 🎵 **Müzik:** TRT Müzik, Power TV, PowerTürk TV, Power Dance, Power Love, Kral Pop TV, Dream Türk, Number 1 TV, Number 1 Damar, Number 1 Slow...
     - 🎬 **Sinema & Dizi:** A2 (Dizi & Sinema), Show Max (Dizi & Sinema), BBC First Türkiye, Cine 1, Kanal Plus...
     - 🏛️ **Kültür & Dini:** TRT 2, TRT Müzik, TRT Türk, TRT Avaz, TRT Kurdî, TRT Genç, Diyanet TV, Semerkand TV, Vav TV, Dost TV, Lalegül TV, Cem TV, YOL TV...
     - 🏙️ **Yerel Kanallar:** Türkiye'nin dört bir yanından çalışan tüm yerel şehir televizyonları (AS TV, TV264, TV41, TV52, TV Den, Kanal 23, Kanal V...)

5. **🛡️ Yedekli Yayın (Failover) & Toleranslı Canlılık Testi:**
   - Ana kanallar ve çocuk kanalları için alternatif yayın kaynakları (failover) tanımlıdır. Birincil CDN yanıt vermezse bot otomatik olarak yedek akışı devreye sokar.
   - Anlık ağ gecikmelerinde tolerans koruması sayesinde TRT 1, TRT Çocuk vb. ana kanallar listeden asla düşmez.

---

## 🚀 TV'ye Ekleme: Canlı Liste Bağlantıları

Televizyonunuzdaki IPTV uygulamasına doğrudan girebileceğiniz linkler:

### 1. 📺 Genel Liste (Tüm Türkiye Kanalları - Kategorili & EPG)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u
```
> **Hızlı CDN Alternatifi (Hızlı İndirme):**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/kanallar.m3u
> ```

---

### 2. 🧒 Çocuk Özel Listesi (Sadece Çocuk Kanalları - Güvenli Profil)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/cocuk.m3u
```
> **Hızlı CDN Alternatifi:**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/cocuk.m3u
> ```

---

### 3. ⭐ TOP 50 Özel Listesi (Sadece En Çok İzlenen 50 Kanal)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/top50.m3u
```
> **Hızlı CDN Alternatifi:**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/top50.m3u
> ```

---

### 4. 📡 Doğrudan EPG (Program Rehberi) Adresi
*(Çoğu uygulama M3U başlığından otomatik çeker; gerekirse oynatıcınıza manuel EPG kaynağı olarak ekleyebilirsiniz)*:
```text
https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz
```

---

### 5. 📊 API & JSON Veri Çıktısı (`channels.json`)
Geliştiriciler, web siteleri ve botlar için tüm canlı kanalların logo, URL, kategori ve canlılık durumunu içeren makine tarafından okunabilir JSON akışı:
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/channels.json
```

---

## 📱 Tüm Cihazlar İçin Kurulum Rehberi

### 📺 Android TV & Google TV
*TCL, Philips, Xiaomi Mi Box / TV Stick, Sony, Google Chromecast vb.*

#### TiviMate IPTV Player (En Çok Önerilen)
1. TiviMate'i açın ➔ **Çalma Listesi Ekle (Add Playlist)** seçeneğine tıklayın.
2. **M3U Playlist** seçeneğini seçin.
3. Çalma listesi URL'si alanına `kanallar.m3u` veya `top50.m3u` bağlantısını yapıştırın.
4. Dosya başlığındaki EPG otomatik tanınır; kanalları gezerken alt barda yayın akışı otomatik görüntülenir!

#### Televizo (Ücretsiz & Hafif)
1. **Ayarlar (Çark)** ➔ **Çalma Listeleri (Playlists)** ➔ **Yeni Ekle (+)** ➔ **M3U Çalma Listesi**.
2. Ad olarak `Türkiye Canlı TV`, bağlantı olarak M3U URL'sini girin ve onaylayın.

---

### 🍏 Apple TV, iPad & iPhone
*Apple TV 4K, iPad, iPhone, Mac*

1. App Store'dan **IPTVX**, **GSE Smart IPTV** veya **VLC Player** uygulamasını indirin.
2. Çalma Listesi Ekle (Add Remote Playlist) butonuna dokunun.
3. `https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u` linkini yapıştırın.

---

### 🖥️ Smart TV (LG webOS & Samsung Tizen)
*Samsung TV (Tizen) & LG Smart TV (webOS)*

1. TV uygulama mağazasından **SS IPTV**, **Nanomid Player** veya **Smart IPTV** uygulamasını yükleyin.
2. Uygulama ayarlarından harici çalma listesi (External Playlist) ekle bölümüne gidin.
3. M3U bağlantısını girerek kanalları TV kumandanızla izlemeye başlayın.

---

### 💻 PC, Mac & Linux

#### VLC Media Player
1. VLC'yi açın ➔ Üst menüden **Medya** ➔ **Ağ Akışı Aç (Ctrl + N)**.
2. `kanallar.m3u` bağlantısını yapıştırın ve **Oynat** butonuna basın.
3. `Ctrl + L` tuş kombinasyonuyla tüm kanal listesini ve kategorileri görüntüleyebilirsiniz.

#### Kodi
1. **Eklentiler** ➔ **PVR İstemcileri** ➔ **PVR IPTV Simple Client** eklentisini açın.
2. Yapılandır ➔ **M3U Oynatma Listesi URL** kısmına `kanallar.m3u` bağlantısını, **XMLTV URL** kısmına EPG linkini girip kaydedin.

---

## 📂 Dosya Yapısı

| Dosya / Dizin | Açıklama |
| :--- | :--- |
| `index.html` | Web tarayıcıları ve arama motorları için SEO uyumlu Türk bayrağı temalı landing page (GitHub Pages) |
| `kanallar.m3u` | Tüm Türkiye kanallarının yer aldığı ana M3U çalma listesi (EPG + Kategorili) |
| `kanallar.m3u8` | Ana listenin UTF-8 HLS alternatifi |
| `cocuk.m3u` | Sadece 11 çocuk kanalını barındıran ebeveyn korumalı özel liste |
| `cocuk.m3u8` | Çocuk listesinin UTF-8 HLS alternatifi |
| `top50.m3u` | Türkiye'de en çok izlenen 50 kanalın yer aldığı reyting sıralı bağımsız liste |
| `top50.m3u8` | TOP 50 listesinin UTF-8 HLS alternatifi |
| `channels.json` | Harici uygulamalar ve botlar için zengin meta veriler içeren JSON API çıktısı |
| `generate_playlist.py` | Filtreleme, Failover, Tolerans, EPG ve Kategori motoru betiği |
| `requirements.txt` | Python bağımlılıkları |
| `LICENSE` | Açık kaynak MIT Lisansı |
| `CONTRIBUTING.md` | Katkıda bulunma kuralları ve yerel test kılavuzu |
| `SECURITY.md` | Güvenlik, DMCA ve 5846 Sayılı FSEK telif politikası |
| `.github/workflows/update.yml` | Günlük otomatik test ve güncelleme iş akışı (GitHub Actions) |
| `.github/ISSUE_TEMPLATE/` | Bozuk kanal bildirimi ve yeni kanal talebi şablonları |

---

## 🌐 Canlı Web Sitesi (GitHub Pages)

Çalma listesi bağlantılarını tek tıkla kopyalamak ve mobil / TV tarayıcısından hızlıca erişmek için web sitesini ziyaret edebilirsiniz:  
👉 **[https://yosemitesam6.github.io/turkiye-iptv-m3u-m3u8/](https://yosemitesam6.github.io/turkiye-iptv-m3u-m3u8/)**

---

## ❓ Sıkça Sorulan Sorular (SSS)

- **🛡️ Bu liste yasal mı? (Yasal / Legal Durum ve Telif Güvencesi)**  
  **Evet, kesinlikle %100 yasaldır (legal).** Projemiz telif haklarına ve yasal mevzuata azami titizlikle bağlıdır:
  1. **Yalnızca Resmi & Kamu Yayınları (FTA):** TRT kanalları, ulusal ve yerel televizyonların tamamı; yayıncı kuruluşların kendi resmi internet siteleri, YouTube canlı yayınları veya kamuya ücretsiz sunduğu açık HLS (`.m3u8`) akışlarıdır.
  2. **Sıfır Korsan & Sıfır Şifreli Kanal:** Digiturk, beIN Sports, Exxen, D-Smart, Tivibu, S Sport veya şifreli/ücretli hiçbir platform yayını **KESİNLİKLE yer almaz**. Yasadışı korsan yayıncılığa tamamen karşıyız.
  3. **Yayın Sunucusu Değil, Açık Dizin:** Sunucularımızda hiçbir görüntü barındırılmaz veya yeniden dağıtılmaz (re-stream yapılmaz). İnternette zaten kamuya açık paylaşılan yasal bağlantıları derleyen açık kaynaklı bir rehber niteliğindedir.
  4. **5846 Sayılı FSEK & DMCA Uyumluluğu:** 5846 sayılı Fikir ve Sanat Eserleri Kanunu ile uluslararası telif normlarına tam uyumludur. Hak sahibi yayıncıların talebi halinde ilgili yayın anında listeden çıkarılır.

- **⚡ Yayınlar neden donmuyor / kesilmiyor?**  
  GitHub Actions otomasyon botumuz her gün saatlik ve günlük canlılık/tolerans testleri yaparak çalışmayan adresleri günceller. Ayrıca ana kanallar için tanımlı yedek CDN (Failover) mimarisi sayesinde kesintiler önlenir.

- **📱 Hangi IPTV uygulamalarıyla uyumludur?**  
  Tüm standart M3U ve HLS destekli cihazlar: TiviMate, Televizo, OTT Navigator, IPTV Smarters Pro, GSE Smart IPTV, VLC Player, Kodi, Apple TV, Smart TV (Samsung Tizen, LG webOS) ve Android TV.

- **📡 Yayın akışı (EPG) nasıl çalışır?**  
  M3U başlığındaki entegre XMLTV EPG kaynağı sayesinde TiviMate ve Televizo yayın akışını otomatik indirir; 24 saatlik rehber kumandanızın rehber tuşunda kendiliğinden görünür.

---

## 🤝 Katkıda Bulunma ve Lisans

Projeye katkıda bulunmak, çalışmayan bir kanalı bildirmek veya yeni bir yerli kanal önermek isterseniz [Katkıda Bulunma Rehberi (CONTRIBUTING.md)](CONTRIBUTING.md)'ni inceleyebilirsiniz.

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmaktadır.
