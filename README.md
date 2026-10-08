# Android TV & Akıllı TV - Profesyonel Türkiye Canlı TV (EPG & Kategorili)

Google TV / Android TV, Apple TV, Smart TV ve tüm mobil cihazlar için optimize edilmiş, **otomatik güncellenen**, **otomatik EPG (yayın akışı) destekli**, **akıllı kategorili**, **yedekli (failover) yayın korumalı** ve **çocuklara özel izole liste içeren** profesyonel Türkiye IPTV platformu.

---

## 🌟 Öne Çıkan Profesyonel Özellikler

1. **📡 Otomatik EPG (Elektronik Program Rehberi) Entegrasyonu:**
   - M3U başlığına entegre XMLTV EPG kaynağı sayesinde TiviMate, Televizo vb. oynatıcılar yayın akışını otomatik çeker.
   - TV'de kanalın altında *"Şu an ne oynuyor?"*, *"Sırada ne var?"*, *"Kalan süre"* ve 24 saatlik rehber tablosu ek bir ayar yapmadan kendiliğinden görüntülenir.
   - Kanallar standart `tvg-id` ve `tvg-name` etiketleriyle rehberle kusursuz eşleşir.

2. **🗂️ Akıllı Kategori Gruplaması (`group-title`):**
   - TV kumandasıyla kolay gezinme için kanallar 10 temiz gruba ayrılmıştır:
     - 📺 **Ulusal** (TRT 1, ATV, Kanal D, Star TV, NOW, TV8, TV8.5, A2, 360...)
     - 🧒 **Çocuk** (TRT Çocuk, Minika Çocuk, Minika Go, Spacetoon, Disney Jr, TRT Diyanet Çocuk...)
     - 📰 **Haber** (TRT Haber, A Haber, NTV, Habertürk, Haber Global, Bloomberg HT, TV100, Halk TV, Tele1...)
     - ⚽ **Spor** (TRT Spor, TRT Spor Yıldız, A Spor, Ekol Sports, FB TV...)
     - 🦁 **Belgesel** (TRT Belgesel, TGRT Belgesel...)
     - 🎵 **Müzik** (TRT Müzik, Power TV, PowerTürk, Kral Pop, Dream Türk, Number 1...)
     - 🎬 **Sinema & Dizi** (BBC First...)
     - 🏛️ **Kültür & Dini** (TRT 2, TRT EBA, Diyanet TV, Semerkand TV...)
     - 🌍 **Dünya** (TRT World, TRT Arabi, TRT Avaz, TRT Kurdî...)
     - 🏙️ **Yerel Kanallar** (Tüm Türkiye yerel ve şehir televizyonları)
   - *Not:* TiviMate veya Televizo'da "Tüm Kanallar" sekmesini seçtiğinizde liste yine kategori sırasına ve Türkçe alfabesine göre sıralı kalır.

3. **🧒 Çocuklara Özel İzole Liste (`cocuk.m3u`):**
   - Çocuk odasındaki televizyonlar veya tabletler için **sadece çocuk kanallarını** içeren izole bir liste üretilir.
   - Çocukların yanlışlıkla haber, tartışma veya yetişkin içeriklerine geçmesini engelleyen güvenli bir ebeveyn ortamı sunar.

4. **🛡️ Yedekli Yayın (Failover) & Toleranslı Test:**
   - Ulusal ve çocuk kanalları için birden fazla alternatif yayın kaynağı (failover) tanımlıdır. Ana yayın aksarsa bot otomatik olarak yedek akışı devreye sokar.
   - Anlık ağ gecikmelerinde tolerans koruması sayesinde TRT 1, TRT Çocuk vb. ana kanallar listeden asla silinmez.

5. **⚡ GitHub Actions ile Günlük Otomatik Yenileme:**
   - Bot her gün saat 04:00 UTC (TSİ 07:00) tüm linkleri test eder, ölü linkleri ayıklar, yeni yayınları ekler ve listeyi otomatik günceller.

---

## 🚀 TV'ye Ekleme: Canlı Liste Bağlantıları

Televizyonunuzdaki IPTV uygulamasına girebileceğiniz doğrudan linkler:

### 1. Genel Liste (Tüm Kanallar - Kategorili & EPG'li)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u
```
> **Hızlı CDN Alternatifi (Önbellekli):**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/kanallar.m3u
> ```

---

### 2. Çocuk Özel Listesi (Sadece Çocuk Kanalları - Güvenli Profil)
```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/cocuk.m3u
```
> **Çocuk Listesi CDN Alternatifi:**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/cocuk.m3u
> ```

---

### 3. Doğrudan EPG (Program Rehberi) Adresi
*(Çoğu uygulama M3U içinden otomatik tanır; tanımazsa manuel EPG adresi olarak ekleyebilirsiniz)*:
```text
https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz
```

---

## 📱 Android TV & Akıllı TV Kurulum Rehberi

Google TV / Android TV cihazınızda Google Play Store'dan şu uygulamaları tercih edebilirsiniz:

### 📺 TiviMate IPTV Player (En Çok Önerilen)
1. TiviMate'i açın -> **Add Playlist (Çalma Listesi Ekle)** seçin.
2. **M3U Playlist** seçeneğine tıklayın.
3. Yukarıdaki **Genel Liste** veya **Çocuk Listesi** URL'sini yapıştırın.
4. TiviMate, dosya başlığındaki EPG adresini otomatik algılar. Kanalları gezerken alt barda yayın akışı otomatik görünür!

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
| `kanallar.m3u` | Tüm kanalların yer aldığı ana M3U çalma listesi (EPG + Akıllı Kategori) |
| `kanallar.m3u8` | UTF-8 destekli HLS oynatıcılar için ana liste |
| `cocuk.m3u` | Sadece çocuk kanallarını barındıran ebeveyn korumalı özel liste |
| `cocuk.m3u8` | Çocuk listesinin UTF-8 HLS alternatifi |
| `generate_playlist.py` | Failover, tolerans testi, EPG ve kategori motorunu çalıştıran Python betiği |
| `.github/workflows/update.yml` | Günlük otomatik test ve güncelleme iş akışı |
