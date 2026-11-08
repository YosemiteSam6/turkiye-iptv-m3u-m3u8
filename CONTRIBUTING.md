# Katkıda Bulunma Rehberi (Contributing Guidelines)

Projeye katkıda bulunmak istediğiniz için teşekkür ederiz! **Türkiye IPTV M3U & M3U8**, Türkiye'deki tüm yasal ve kamuya açık yayınları tek bir çatıda toplayarak akıllı televizyonlarda en yüksek izleme deneyimini sunmayı hedefler.

Aşağıdaki kurallar, projenin kalitesini, yasal güvencesini ve teknik bütünlüğünü korumak için belirlenmiştir.

---

## ⚖️ Temel İlkelerimiz: %100 Yasal ve Açık Yayınlar (FTA)

1. **Sıfır Korsan & Sıfır Ücretli Platform Yayını:**
   - Projeye kesinlikle **Digiturk, beIN Sports (şifreli), Exxen, D-Smart, Tivibu, S Sport, Netflix** vb. ücretli/şifreli platformlara ait akışlar **EKLENEMEZ**.
   - Bu tür yayınları içeren öneriler ve Pull Request'ler derhal reddedilir.
2. **Yalnızca Resmi & FTA (Free-To-Air) Yayınlar:**
   - Yayıncı kuruluşun resmi internet sitesinde, YouTube canlı yayınında veya kamuya açık CDN sunucusunda ücretsiz sunduğu açık `.m3u8` / HLS akışları kabul edilir.
3. **Sadece Türkiye Kanalları:**
   - Türkiye sınırları içindeki ulusal, bölgesel ve yerel kanallar listelenir. Yabancı / Arapça yayınlar kabul edilmez.

---

## 🛠️ Yerel Ortamda Test ve Geliştirme

Değişiklik yapmadan veya yeni bir kanal eklemeden önce projeyi yerel makinenizde test edebilirsiniz:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8.git
   cd turkiye-iptv-m3u-m3u8
   ```

2. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Üretici betiği çalıştırın:**
   ```bash
   python generate_playlist.py
   ```
   Bu komut canlılık testlerini gerçekleştirecek ve güncel `.m3u`, `.m3u8` ve `channels.json` dosyalarını oluşturacaktır.

---

## 📺 Yeni Kanal Ekleme Kuralları

Yeni bir kanal eklemek için `generate_playlist.py` dosyasındaki `VERIFIED_CHANNELS` listesine ekleme yapabilirsiniz.

Eklenen kanal objesi şu standartlara sahip olmalıdır:
```python
{
    "name": "Kanal Adı",
    "category": "Ulusal | Çocuk | Haber | Spor | Belgesel | Müzik | Sinema & Dizi | Kültür & Dini | Yerel",
    "epg_id": "EPG_KODU.tr",  # epgshare01_TR1 içinde varsa (yoksa boş bırakın)
    "url": "https://.../live.m3u8",
    "fallbacks": [            # Varsa alternatif yedek akış adresleri
        "https://.../backup.m3u8"
    ],
    "logo": "https://.../logo.png"  # Yüksek çözünürlüklü ve şeffaf (PNG/SVG) logo
}
```

- **Kanal Adı:** Resmi kanal adı kullanılmalıdır (1080p, HD, Canlı gibi ekler yazılmamalıdır; script otomatik temizler).
- **Yayın Akışı (Stream):** Tercihen `https://` protokolü üzerinden yayın yapan stabil bir HLS akışı olmalıdır.
- **Failover (Yedek):** Varsa kanalın yedek sunucu linki `fallbacks` dizisine eklenmelidir.

---

## 🚨 Bozuk veya Donan Kanal Bildirimi

Bir kanal yayını açılmıyor, donuyor veya logosu hatalıysa:
1. GitHub [Issues](https://github.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/issues) sekmesine gidin.
2. **Bozuk Kanal Bildirimi** şablonunu seçin ve formu doldurun.
3. Varsa hatanın ekran görüntüsünü veya hata kodunu ekleyin.

---

## 🔀 Pull Request (PR) Gönderme

1. Depoyu kendi hesabınıza fork'layın.
2. Yeni bir özellik dalı (feature branch) oluşturun: `git checkout -b ozellik/yeni-kanal-ekle`
3. Değişikliğinizi yapıp `python generate_playlist.py` ile test edin.
4. Anlamlı bir commit mesajı ile kaydedin: `git commit -m "feat: Kanal Adı eklendi"`
5. Dalınızı push edin ve bir Pull Request açın.
6. PR şablonundaki kontrol listesini doldurun.

Desteğiniz ve katkılarınız için teşekkür ederiz! ❤️

