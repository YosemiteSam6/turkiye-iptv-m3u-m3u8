#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android / Google TV & Akıllı TV - Türkiye Canlı TV Kanalları M3U Oluşturucu
- Famelack + IPTV-org + Doğrulanmış Ulusal ve Yerel Kanallar
- Aktiflik ve yayın kontrolü (ölü ve çalışmayan linkleri eler)
- Tekrarları temizler (kanal başına en stabil tek yayın)
- Kategori/grup karmaşası olmadan, Türkçe harf sırasına göre (A-Z) sıralar.
"""

import os
import re
import sys
import json
import gzip
import unicodedata
from concurrent.futures import ThreadPoolExecutor
import requests

# İstek ayarları
TIMEOUT_CONNECT = 2.5
TIMEOUT_READ = 3.0
MAX_WORKERS = 25
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Öncelikli ve doğrulanmış ana kanal kaynakları (Logolar ve direkt HLS yayınları)
VERIFIED_CHANNELS = [
    {
        "name": "TRT 1",
        "url": "https://tv-trt1.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/TRT_1_logo_2021.svg/512px-TRT_1_logo_2021.svg.png"
    },
    {
        "name": "TRT 2",
        "url": "https://tv-trt2.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/TRT_2_logo_2021.svg/512px-TRT_2_logo_2021.svg.png"
    },
    {
        "name": "TRT Haber",
        "url": "https://tv-trthaber.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/TRT_Haber_logo_2021.svg/512px-TRT_Haber_logo_2021.svg.png"
    },
    {
        "name": "TRT Spor",
        "url": "https://tv-trtspor1.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/TRT_Spor_logo_2021.svg/512px-TRT_Spor_logo_2021.svg.png"
    },
    {
        "name": "TRT Spor Yıldız",
        "url": "https://tv-trtspor2.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/TRT_Spor_Y%C4%B1ld%C4%B1z_logo_2021.svg/512px-TRT_Spor_Y%C4%B1ld%C4%B1z_logo_2021.svg.png"
    },
    {
        "name": "TRT Belgesel",
        "url": "https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/TRT_Belgesel_logo_2021.svg/512px-TRT_Belgesel_logo_2021.svg.png"
    },
    {
        "name": "TRT Çocuk",
        "url": "https://tv-trtcocuk.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/TRT_%C3%87ocuk_logo_2021.svg/512px-TRT_%C3%87ocuk_logo_2021.svg.png"
    },
    {
        "name": "TRT Müzik",
        "url": "https://tv-trtmuzik.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/TRT_M%C3%BCzik_logo_2021.svg/512px-TRT_M%C3%BCzik_logo_2021.svg.png"
    },
    {
        "name": "TRT Türk",
        "url": "https://tv-trtturk.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/TRT_T%C3%BCrk_logo_2021.svg/512px-TRT_T%C3%BCrk_logo_2021.svg.png"
    },
    {
        "name": "TRT Avaz",
        "url": "https://tv-trtavaz.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/TRT_Avaz_logo_2021.svg/512px-TRT_Avaz_logo_2021.svg.png"
    },
    {
        "name": "TRT Kurdî",
        "url": "https://tv-trtkurdi.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/TRT_Kurd%C3%AE_logo_2021.svg/512px-TRT_Kurd%C3%AE_logo_2021.svg.png"
    },
    {
        "name": "TRT World",
        "url": "https://tv-trtworld.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/TRT_World_logo_2021.svg/512px-TRT_World_logo_2021.svg.png"
    },
    {
        "name": "ATV",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/atv/atv.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/ATV_logo.svg/512px-ATV_logo.svg.png"
    },
    {
        "name": "A2",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/a2tv/a2tv.m3u8",
        "logo": "https://iatv.tmgrup.com.tr/site/v2/a2tv/i/a2tv-logo.png"
    },
    {
        "name": "A Haber",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/ahaber/ahaber.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Ahaber_Logo.png"
    },
    {
        "name": "A Spor",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/aspor/aspor.m3u8",
        "logo": "https://i.imgur.com/ZhkZzLf.png"
    },
    {
        "name": "Kanal D",
        "url": "https://demiroren.daioncdn.net/kanald/kanald.m3u8?app=kanald_web&ce=3",
        "logo": "https://i.imgur.com/9o1atM6.png"
    },
    {
        "name": "Star TV",
        "url": "https://dogus.daioncdn.net/startv/startv_720p.m3u8?app=a20ac41e-bdc3-4aa1-934d-26b484480ac9&ce=3&sid=8l4w3lst4co5",
        "logo": "https://i.imgur.com/9O3DHRB.png"
    },
    {
        "name": "NOW TV",
        "url": "https://uycyyuuzyh.turknet.ercdn.net/nphindgytw/nowtv/nowtv.m3u8",
        "logo": "https://i.imgur.com/5EYjWK7.png"
    },
    {
        "name": "TV8",
        "url": "https://tv8.daioncdn.net/tv8/tv8.m3u8?app=7ddc255a-ef47-4e81-ab14-c0e5f2949788&ce=3",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/6/68/Tv8_Yeni_Logo.png/960px-Tv8_Yeni_Logo.png"
    },
    {
        "name": "Habertürk TV",
        "url": "https://tv.ensonhaber.com/haberturk/haberturk.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Habert%C3%BCrk_TV_logo.svg/512px-Habert%C3%BCrk_TV_logo.svg.png"
    },
    {
        "name": "Haber Global",
        "url": "https://tv.ensonhaber.com/haberglobal/haberglobal.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Haber_Global_logo.svg/512px-Haber_Global_logo.svg.png"
    },
    {
        "name": "Bloomberg HT",
        "url": "https://tv.ensonhaber.com/bloomberght/bloomberght.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Bloomberg_HT_logo.svg/512px-Bloomberg_HT_logo.svg.png"
    },
    {
        "name": "TV100",
        "url": "https://tv.ensonhaber.com/tv100/tv100.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/TV100_logosu.svg/512px-TV100_logosu.svg.png"
    },
    {
        "name": "Halk TV",
        "url": "https://halktv-live.daioncdn.net/halktv/halktv.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Halk_TV_logo.svg/512px-Halk_TV_logo.svg.png"
    },
    {
        "name": "Tele 1",
        "url": "https://tele1-live.ercdn.net/tele1/tele1.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Tele1_logo.svg/512px-Tele1_logo.svg.png"
    },
    {
        "name": "TGRT Haber",
        "url": "https://canli.tgrthaber.com/tgrt.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/TGRT_Haber_logo.svg/512px-TGRT_Haber_logo.svg.png"
    },
    {
        "name": "Flash Haber TV",
        "url": "https://b01c02nl.mediatriple.net/videoonlylive/mtyycglqauzjhlive/broadcast_67c053c48829f.smil/playlist.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Flash_Haber_logosu.png/512px-Flash_Haber_logosu.png"
    },
    {
        "name": "Kanal 7 Avrupa",
        "url": "https://livetv.radyotvonline.net/kanal7live/kanal7avr/playlist.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Kanal_7_logo.svg/512px-Kanal_7_logo.svg.png"
    },
    {
        "name": "Bengütürk TV",
        "url": "https://tv.ensonhaber.com/benguturk/benguturk.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/8/8c/Beng%C3%BCt%C3%BCrk_TV_logosu.png/512px-Beng%C3%BCt%C3%BCrk_TV_logosu.png"
    },
    {
        "name": "Ekol TV",
        "url": "https://ekoltv-live.ercdn.net/ekoltv/ekoltv.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ekol_TV_logosu.png/512px-Ekol_TV_logosu.png"
    },
    {
        "name": "Ekol Sports",
        "url": "https://ekoltv-live.ercdn.net/ekolsport/ekolsport.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ekol_TV_logosu.png/512px-Ekol_TV_logosu.png"
    },
    {
        "name": "24 TV",
        "url": "https://turkmedya-live.ercdn.net/tv24/tv24.m3u8",
        "logo": "https://i.imgur.com/8FO41es.png"
    },
    {
        "name": "360",
        "url": "https://turkmedya-live.ercdn.net/tv360/tv360.m3u8",
        "logo": "https://i.imgur.com/agn47sQ.png"
    }
]

def clean_channel_name(raw_name: str) -> str:
    """Kanal adlarındaki gereksiz çözünürlük ve ek ifadeleri temizler."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    
    # Gereksiz etiketleri kaldır
    patterns = [
        r'\s*\((?:1080p|720p|576p|480p|360p|1440p|4k|hd|sd)\)',
        r'\s*\[(?:Not 24/7|Geo-blocked|Blocked)\]',
        r'\s*\((?:Turkiye|Turkey|TR)\)',
        r'\b(?:1080p|720p|576p|480p|360p|1440p)\b',
        r'\bSD\b',
    ]
    for p in patterns:
        name = re.sub(p, '', name, flags=re.IGNORECASE)
    
    name = re.sub(r'\s+', ' ', name).strip()
    
    # İsim standartlaştırma
    name_map = {
        "A2TV": "A2",
        "AHaber": "A Haber",
        "ASpor": "A Spor",
        "Haberturk": "Habertürk TV",
        "Haberturk TV": "Habertürk TV",
        "Kanal 7 (Turkiye)": "Kanal 7",
        "Kanal D (Turkiye)": "Kanal D",
        "Star TV (Turkiye)": "Star TV",
        "TV8 (Turkiye)": "TV8",
        "Benguturk TV": "Bengütürk TV",
        "Tele 1": "Tele1",
        "Tele1 TV": "Tele1",
        "TRT 1 (1440p)": "TRT 1",
        "TRT Haber (720p)": "TRT Haber",
        "TRT Spor Yildiz": "TRT Spor Yıldız",
        "TRT Cocuk": "TRT Çocuk",
        "TRT Muzik": "TRT Müzik",
        "TRT Turk": "TRT Türk",
        "NOW TV": "NOW",
    }
    return name_map.get(name, name)

def turkish_lower(text: str) -> str:
    """Türkçe İ ve I harflerini doğru şekilde küçük harfe dönüştürür."""
    return text.replace('İ', 'i').replace('I', 'ı').lower()

def turkish_sort_key(text: str):
    """
    Türkçe alfabesine ve sözlük sırasına göre harf sıralama anahtarı üretir.
    Boşluk en başta, sonra sayılar, sonra Türkçe alfabe.
    a, b, c, ç, d, e, f, g, ğ, h, ı, i, j, k, l, m, n, o, ö, p, r, s, ş, t, u, ü, v, y, z
    """
    order = {
        ' ': 0,
        'a': 1, 'b': 2, 'c': 3, 'ç': 4, 'd': 5, 'e': 6, 'f': 7,
        'g': 8, 'ğ': 9, 'h': 10, 'ı': 11, 'i': 12, 'j': 13, 'k': 14,
        'l': 15, 'm': 16, 'n': 17, 'o': 18, 'ö': 19, 'p': 20, 'r': 21,
        's': 22, 'ş': 23, 't': 24, 'u': 25, 'ü': 26, 'v': 27, 'y': 28, 'z': 29
    }
    lowered = turkish_lower(text)
    res = []
    for char in lowered:
        if char == ' ':
            res.append((0, 0))
        elif char.isdigit():
            res.append((1, int(char)))
        elif char in order:
            res.append((2, order[char]))
        else:
            res.append((3, ord(char)))
    return res

def check_stream(item):
    """Yayın URL'sinin canlı ve oynatılabilir olduğunu doğrular."""
    name, url, logo = item['name'], item['url'], item.get('logo', '')
    try:
        r = requests.get(url, headers=HEADERS, timeout=(TIMEOUT_CONNECT, TIMEOUT_READ), stream=True)
        if r.status_code in (200, 206):
            chunk = next(r.iter_content(chunk_size=512), b'')
            # m3u8 veya canlı video akış başlığını doğrula
            if b'#EXTM3U' in chunk or b'#EXTINF' in chunk or len(chunk) > 100:
                return {'name': name, 'url': url, 'logo': logo, 'ok': True}
    except Exception:
        pass
    return {'name': name, 'url': url, 'logo': logo, 'ok': False}

def fetch_famelack_channels():
    """Famelack veri tabanındaki Türkiye kanallarını çeker."""
    url = 'https://raw.githubusercontent.com/famelack/famelack-data/main/tv/compressed/countries/tr.json'
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = json.loads(gzip.decompress(r.content).decode('utf-8'))
            for ch in data:
                name = clean_channel_name(ch.get('name', ''))
                logo = ch.get('logo') or ''
                streams = ch.get('sources', {}).get('streams') or []
                for s in streams:
                    if s and s.startswith('http'):
                        items.append({'name': name, 'url': s, 'logo': logo})
            print(f"[Famelack] Toplam {len(items)} yayın adresi çekildi.")
    except Exception as e:
        print(f"[Famelack] Çekme hatası: {e}")
    return items

def fetch_iptv_org_channels():
    """IPTV-org Türkiye listesindeki kanalları çeker."""
    url = 'https://iptv-org.github.io/iptv/countries/tr.m3u'
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            curr_name = ""
            curr_logo = ""
            for line in lines:
                if line.startswith('#EXTINF'):
                    m_logo = re.search(r'tvg-logo="([^"]+)"', line)
                    curr_logo = m_logo.group(1) if m_logo else ''
                    raw_title = line.split(',')[-1].strip()
                    curr_name = clean_channel_name(raw_title)
                elif curr_name and line.startswith('http'):
                    items.append({'name': curr_name, 'url': line.strip(), 'logo': curr_logo})
                    curr_name = ""
            print(f"[IPTV-org] Toplam {len(items)} yayın adresi çekildi.")
    except Exception as e:
        print(f"[IPTV-org] Çekme hatası: {e}")
    return items

def build_playlist():
    print("=" * 60)
    print("Türkiye Özel Canlı TV Listesi Oluşturuluyor...")
    print("=" * 60)

    # 1. Kaynakları topla
    all_candidates = []
    
    # Öncelikle doğrulanmış ana kanallar
    for ch in VERIFIED_CHANNELS:
        all_candidates.append({
            'name': clean_channel_name(ch['name']),
            'url': ch['url'],
            'logo': ch.get('logo', '')
        })

    # Famelack ve IPTV-org listelerini ekle
    all_candidates.extend(fetch_famelack_channels())
    all_candidates.extend(fetch_iptv_org_channels())

    # 2. URL bazlı tekilleştirme
    seen_urls = set()
    unique_candidates = []
    for item in all_candidates:
        url = item['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append(item)

    print(f"\nCanlılık testi yapılacak toplam benzersiz yayın: {len(unique_candidates)}")
    print("Yayınlar eş zamanlı olarak kontrol ediliyor...")

    # 3. Canlılık testi (Çok iş parçacıklı)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        test_results = list(pool.map(check_stream, unique_candidates))

    working_streams = [r for r in test_results if r['ok']]
    print(f"Çalışır durumda tespit edilen yayın: {len(working_streams)}")

    # 4. Kanal adı bazlı tekilleştirme (Kanal başına en iyi tek yayın)
    # VERIFIED_CHANNELS listesinde olanların logoları ve isimleri önceliklidir
    verified_names = {clean_channel_name(v['name']).lower(): v for v in VERIFIED_CHANNELS}

    final_channel_map = {}
    for item in working_streams:
        norm_name = clean_channel_name(item['name'])
        if not norm_name:
            continue
        key = norm_name.lower()

        # Logo güncelleme (öncelikli listeden veya iptv-org'dan)
        logo = item.get('logo', '')
        if key in verified_names and verified_names[key].get('logo'):
            logo = verified_names[key]['logo']

        if key not in final_channel_map:
            final_channel_map[key] = {
                'name': norm_name,
                'url': item['url'],
                'logo': logo
            }
        else:
            # Eğer mevcut olanın logosu yoksa ve yenisinde varsa al
            if not final_channel_map[key]['logo'] and logo:
                final_channel_map[key]['logo'] = logo

    final_channels = list(final_channel_map.values())
    print(f"Tekilleştirme sonrası toplam net kanal: {len(final_channels)}")

    # 5. Türkçe Alfabetik Sıralama (A -> Z)
    final_channels.sort(key=lambda x: turkish_sort_key(x['name']))

    # 6. M3U Dosyasını Oluştur (Kategori/grup bilgisi olmadan, temiz ve standart)
    output_lines = [
        "#EXTM3U",
        "# Generated automatically for Android TV & Smart TV",
        f"# Total Working Turkish Channels: {len(final_channels)} (Sorted A-Z)",
        ""
    ]

    for ch in final_channels:
        name = ch['name']
        url = ch['url']
        logo = ch.get('logo', '')
        
        if logo:
            extinf = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}",{name}'
        else:
            extinf = f'#EXTINF:-1 tvg-name="{name}",{name}'
            
        output_lines.append(extinf)
        output_lines.append(url)

    content = "\n".join(output_lines) + "\n"

    # Dosyalara kaydet (hem .m3u hem .m3u8 olarak)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    m3u_path = os.path.join(base_dir, "kanallar.m3u")
    m3u8_path = os.path.join(base_dir, "kanallar.m3u8")

    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(m3u8_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n[Başarılı] '{m3u_path}' oluşturuldu!")
    print(f"[Başarılı] '{m3u8_path}' oluşturuldu!")
    print(f"İlk 10 kanal sıralaması:")
    for ch in final_channels[:10]:
        print(f"  • {ch['name']}")
    print(f"Son 5 kanal sıralaması:")
    for ch in final_channels[-5:]:
        print(f"  • {ch['name']}")
    print("=" * 60)

if __name__ == "__main__":
    build_playlist()
