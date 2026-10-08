# Android TV & Akıllı TV - Türkiye Canlı TV (A-Z) M3U Listesi

Bu proje, Google TV / Android TV ve diğer tüm akıllı televizyonlar için özel olarak optimize edilmiş, **otomatik güncellenen**, **çalışmayan ölü linklerden arındırılmış**, **kategori karmaşası olmadan A'dan Z'ye sıralı** Türkiye canlı TV M3U çalma listesidir.

---

## 📺 Özellikler

1. **Özel Doğrulama (Aktiflik Kontrolü):**
   - GitHub Actions arka planda Famelack ve IPTV-org veri tabanındaki tüm Türkiye kanallarını ve doğrulanmış ulusal yayınları tek tek canlılık testine tabi tutar.
   - Sadece anlık olarak yanıt veren ve çalışan yayınlar listeye alınır; ölü, zaman aşımına uğrayan veya kapalı linkler elenir.

2. **Harf Sırasına Göre (A → Z) & Kategori Yok:**
   - TV arayüzünde klasörler veya karmaşık gruplarla uğraşmak istemeyenler için tüm kanallar Türkçe alfabesine göre (`A, B, C, Ç, D...`) sıralanmıştır.
   - Her kanal için en stabil tek yayın seçilmiş, tekrar eden klonlar (SD, 360p vb.) elenmiştir.

3. **Otomatik Güncelleme (URL Tabanlı):**
   - TV'nize dosyayı elle yüklemek yerine doğrudan GitHub linkini girdiğinizde, arka plandaki GitHub Actions botu listeyi her gün kontrol edip otomatik yeniler.

---

## 🚀 TV'ye Ekleme: Canlı M3U URL'si

Televizyonunuzdaki IPTV uygulamasına gireceğiniz doğrudan canlı liste adresi:

```text
https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u
```

> **Hızlı CDN Alternatifi (Önbellekli & Süper Hızlı):**
> ```text
> https://cdn.jsdelivr.net/gh/YosemiteSam6/turkiye-iptv-m3u-m3u8@main/kanallar.m3u
> ```

> **UTF-8 (.m3u8) Alternatifi:**
> ```text
> https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u8
> ```

---

## 📱 Android TV & Akıllı TV İçin En İyi IPTV Uygulamaları

Televizyonunuz veya cihazınız Google TV / Android TV tabanlı ise Google Play Store'dan şu uygulamalardan birini yükleyebilirsiniz:

1. **TiviMate IPTV Player** *(En çok önerilen, modern ve akıcı TV arayüzü)*
   - Uygulamayı açın -> **Add Playlist** (Çalma Listesi Ekle) -> **M3U Playlist** -> Yukarıdaki M3U URL'sini girin.
2. **Televizo** *(Ücretsiz, sade, kumanda uyumu harika)*
   - Ayarlar -> Çalma Listeleri -> Yeni Ekle (M3U) -> URL'yi yapıştırın.
3. **OTT Navigator IPTV** *(Geniş ayar desteği ve hızlı kanal geçişi)*
4. **IPTV Smarters Pro** veya **VLC Media Player**

---

## ⚙️ GitHub Kurulumu (3 Adımda Kendi Canlı URL'nizi Alın)

1. **GitHub'da Yeni Repo Açın:**
   - [github.com/new](https://github.com/new) adresine gidin.
   - Depo adı olarak örneğin `turkiye-iptv` yazın ve **Public (Herkese Açık)** seçin.

2. **Dosyaları Yükleyin:**
   Terminalden deponun bulunduğu dizinde şu komutları çalıştırarak GitHub'a gönderebilirsiniz:
   ```bash
   git remote add origin https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8.git
   git push -u origin main
   ```
   *(Veya GitHub web sitesinden dosyaları doğrudan sürükleyip bırakabilirsiniz)*

3. **Otomatik Güncelleme Ayarı:**
   - GitHub deposunda **Settings -> Actions -> General -> Workflow permissions** bölümünde **"Read and write permissions"** seçeneğini işaretleyip kaydedin.
   - Artık GitHub Actions her gün saat 04:00 UTC (TSİ 07:00) listeyi kontrol edip kanalları otomatik güncelleyecektir.
   - Dilediğiniz an GitHub'da **Actions** sekmesinden "Run workflow" diyerek listeyi tek tıkla yenileyebilirsiniz.

---

## 📂 Dosya Yapısı

- `kanallar.m3u` : TV'ye girilecek standart M3U çalma listesi (A-Z sıralı)
- `kanallar.m3u8` : UTF-8 destekli HLS oynatıcılar için alternatif dosya
- `generate_playlist.py` : Kanalları çeken, canlılık testi yapan ve listeyi oluşturan Python motoru
- `.github/workflows/update.yml` : Günlük otomatik çalışma iş akışı
