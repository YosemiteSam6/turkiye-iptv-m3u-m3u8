# Android TV & Akıllı TV - Profesyonel Türkiye Canlı TV (EPG & Kategorili)

Google TV / Android TV, Apple TV, Smart TV ve tüm mobil cihazlar için optimize edilmiş, **otomatik güncellenen**, **otomatik EPG (yayın akışı) destekli**, **akıllı kategorili**, **yabancı/Arapça kanallardan tamamen arındırılmış (%100 yerli)**, **yedekli (failover) yayın korumalı** ve **çocuklara özel izole liste barındıran** profesyonel Türkiye IPTV platformu.

---

## 🌟 Öne Çıkan Profesyonel Özellikler

1. **🧒 Eksiksiz Çocuk Kanalları (11 Çalışan Çocuk Kanalı):**
   - TV'de çocuk kategorisinde eksiklik yaşanmaması için tüm aktif çocuk ve eğitim yayınları doğrulanıp listeye dahil edilmiştir:
     - **TRT Çocuk**, **Minika Çocuk**, **Minika Go**, **Baby TV**, **Disney Jr.**, **Spacetoon Turkey**, **TRT Diyanet Çocuk**, **TRT EBA İlkokul**, **TRT EBA Ortaokul**, **TRT EBA Lise**, **Zarok TV**
   - Çocuk odaları ve tabletler için sadece bu 11 kanalı içeren izole **`cocuk.m3u`** listesi mevcuttur.

2. **🇹🇷 Sadece %100 Türkiye Kanalları (Yabancı Kanallardan Arındırılmış):**
   - IPTV-org ve Famelack kaynaklarındaki Arapça, Orta Doğu ve yabancı yayınlar (Almahriah, Elsharq, Mekameleen, Persiana vb.) tamamen filtrelenmiştir.
   - Listede yalnızca Türkiye'ye ait ulusal, çocuk, haber, spor, belgesel, müzik ve yerel kanallar yer alır.

3. **📡 Otomatik EPG (Elektronik Program Rehberi) Entegrasyonu:**
   - M3U başlığına entegre XMLTV EPG kaynağı sayesinde TiviMate, Televizo vb. oynatıcılar yayın akışını otomatik çeker.
   - TV'de kanalın altında *"Şu an ne oynuyor?"*, *"Sırada ne var?"*, *"Kalan süre"* ve kumandanın Rehber tuşunda 24 saatlik yayın akışı tablosu kendiliğinden görüntülenir.

4. **🗂️ Temiz Kategori Gruplaması (`group-title`):**
   - TV kumandasıyla kolay gezinme için kanallar çakışmasız ve tekilleştirilmiş net gruplara ayrılmıştır:
     - 📺 **Ulusal** (TRT 1, ATV, NOW, Kanal D, Star TV, TV8, TV8.5, A2, 360, Kanal 7, Euro D, Show Max, TV 4)
     - 🧒 **Çocuk** (11 aktif çocuk ve gençlik kanalı)
     - 📰 **Haber** (TRT Haber, NTV, Habertürk, A Haber, Haber Global, Bloomberg HT, TV100, Halk TV, Tele1...)
     - ⚽ **Spor** (TRT Spor, TRT Spor Yıldız, A Spor, Ekol Sports, FB TV, TJK TV...)
     - 🦁 **Belgesel** (TRT Belgesel, TGRT Belgesel...)
     - 🎵 **Müzik** (TRT Müzik, Power TV, PowerTürk, Kral Pop, Dream Türk, Number 1...)
     - 🎬 **Sinema & Dizi** (BBC First...)
     - 🏛️ **Kültür & Dini** (TRT 2, Diyanet TV, Semerkand TV, Vav TV...)
     - 🏙️ **Yerel Kanallar** (Tüm Türkiye yerel ve şehir televizyonları)

5. **🛡️ Yedekli Yayın (Failover) & Toleranslı Test:**
   - Ana kanallar ve çocuk kanalları için alternatif yayın kaynakları (failover) tanımlıdır. Birincil CDN yanıt vermezse bot otomatik olarak yedek akışı devreye sokar.
   - Anlık ağ gecikmelerinde tolerans koruması sayesinde TRT 1, TRT Çocuk vb. ana kanallar listeden asla düşmez.

---

## 🚀 TV'ye Ekleme: Canlı Liste Bağlantıları

Televizyonunuzdaki IPTV uygulamasına girebileceğiniz doğrudan linkler:

### 1. 📺 Genel Liste (Tüm Türkiye Kanalları - Kategorili & EPG)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u
```
> **Hızlı CDN Alternatifi:**
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
*(Çoğu uygulama M3U başlığından otomatik çeker; gerekirse manuel EPG kaynağı olarak ekleyebilirsiniz)*:
```text
https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz
```

---

## 📱 Android TV & Akıllı TV Kurulum Rehberi

Google TV / Android TV cihazınızda Google Play Store'dan şu uygulamaları tercih edebilirsiniz:

### 📺 TiviMate IPTV Player (En Çok Önerilen)
1. TiviMate'i açın -> **Add Playlist (Çalma Listesi Ekle)** seçin.
2. **M3U Playlist** seçeneğine tıklayın.
3. Yukarıdaki **Genel Liste** (`kanallar.m3u`) veya **Çocuk Listesi** (`cocuk.m3u`) URL'sini yapıştırın.
4. TiviMate dosya başlığındaki EPG adresini otomatik tanır. Kanalları gezerken alt barda yayın akışı otomatik görünür!

### 📺 Televizo (Ücretsiz & Kumanda Dostu)
1. Ayarlar -> **Çalma Listeleri (Playlists)** -> **Yeni Ekle (M3U)**.
2. Ad olarak `Türkiye Canlı TV`, URL olarak M3U adresini girin.
3. EPG sekmesinde otomatik EPG'nin aktif olduğunu göreceksiniz.

### 📺 OTT Navigator & IPTV Smarters Pro
- Çalma listesi URL'si alanına M3U adresini yapıştırmanız yeterlidir. Kategoriler sol sekmede gruplar halinde listelenir.

---

## 📂 Dosya Yapısı

| Dosya | Açıklama |
| :--- | :--- |
| `kanallar.m3u` | Tüm Türkiye kanallarının yer aldığı ana M3U çalma listesi (EPG + Kategorili) |
| `kanallar.m3u8` | Ana listenin UTF-8 HLS alternatifi |
| `cocuk.m3u` | Sadece 11 çocuk kanalını barındıran ebeveyn korumalı özel liste |
| `cocuk.m3u8` | Çocuk listesinin UTF-8 HLS alternatifi |
| `top50.m3u` | Türkiye'de en çok izlenen 50 kanalın yer aldığı bağımsız liste |
| `top50.m3u8` | TOP 50 listesinin UTF-8 HLS alternatifi |
| `generate_playlist.py` | Filtreleme, Failover, Tolerans, EPG ve Kategori motoru |
| `.github/workflows/update.yml` | Günlük otomatik test ve güncelleme iş akışı |
