#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android / Google TV & Akıllı TV - Profesyonel Türkiye Canlı TV M3U Oluşturucu
- 🧒 Eksiksiz Çocuk Kanalları (11 Çalışan Çocuk Kanalı)
- 📰 Haber, ⚽ Spor, 🦁 Belgesel, 🎵 Müzik, 🎬 Sinema, 📺 Ulusal, 🏛️ Kültür ve 🏙️ Yerel
- 🔄 Çoklu Kategori (Cross-Category) Desteği: Çok yönlü kanallar ilgili tüm kategorilerde listelenir
- ❌ Yabancı / Uluslararası / Arapça Kanallar Tamamen Elenmiş (Sadece %100 Türkiye Kanalları)
- 📡 Otomatik EPG (Elektronik Program Rehberi) Entegrasyonu (epg_ripper_TR1)
- 🧒 Çocuk Özel Listesi (cocuk.m3u & cocuk.m3u8 - 11 Kanal)
- ⭐ TOP 50 Özel Listesi (top50.m3u & top50.m3u8 - 50 Kanal)
- 🛡️ Yedekli Yayın (Failover) & Toleranslı Canlılık Testi (Retry + Backup URL)
"""

import os
import re
import sys
import json
import gzip
import unicodedata
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# İstek ve Zaman Aşımı Ayarları (Toleranslı Test)
TIMEOUT_CONNECT = 3.5
TIMEOUT_READ = 4.0
MAX_WORKERS = 20
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# EPG Kaynağı (Türkiye Kanalları XMLTV Rehberi)
EPG_URL = "https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz"

# Kategori Öncelik Sıralaması
CATEGORY_ORDER = [
    "TÜM KANALLAR (A-Z Sıralı)",
    "TOP 50",
    "Çocuk",
    "Haber",
    "Spor",
    "Belgesel",
    "Müzik",
    "Sinema & Dizi",
    "Kültür & Dini",
    "Yerel"
]

# Yabancı / Arapça / Uluslararası Engelli Kanallar (Sadece Türkiye Kanalları Filtresi)
BLOCKED_CHANNELS = {
    'almahriah tv', 'al-zahra tv turkic', 'elsharq tv', 'mekameleen tv',
    'persiana turkiye', 'sat 7 turk', 'trt arabi', 'trt world',
    'kanal avrupa', 'luys tv', 'tyt turk', '4u tv'
}

def is_foreign_or_blocked(name: str) -> bool:
    """Yabancı / Uluslararası / Türkiye dışı kanalları eler."""
    if not name:
        return True
    n = name.lower()
    if n in BLOCKED_CHANNELS:
        return True
    blocked_keywords = [
        'almahriah', 'elsharq', 'mekameleen', 'al-zahra', 'al zahra', 'persiana',
        'sat 7', 'luys', 'tyt turk', 'kanal avrupa', 'trt arabi', 'trt world',
        'tagesschau', 'ndr', 'wdr', 'zdf', 'ard', 'dw '
    ]
    return any(b in n for b in blocked_keywords)

# Türkiye'de En Çok İzlenen 50 Kanal (Reyting ve Popülerlik Sıralı - Diyanet TV #1)
TOP_50_RANKS = [
    # 1. Sıra (Özel İstek):
    "Diyanet TV",
    # 2-8. Ulusal Ana Reyting Liderleri:
    "TRT 1", "ATV", "NOW", "Kanal D", "Star TV", "TV8", "Kanal 7 Avrupa",
    # 9-14. En Popüler Çocuk ve Ana Haber Kanalları:
    "TRT Çocuk", "TRT Haber", "A Haber", "NTV", "Habertürk TV", "Halk TV",
    # 15-20. Spor, Belgesel ve Popüler Tematik Kanallar:
    "TRT Spor", "A Spor", "TRT Belgesel", "A2", "TV8.5", "360",
    # 21-26. Popüler Haber ve Eğlence:
    "Haber Global", "TV100", "CNBC-e", "Tele1", "TGRT Haber", "Show Max",
    # 27-30. Popüler Çocuk Kanalları:
    "Minika Çocuk", "Minika Go", "Cartoon Network", "Disney Jr.",
    # 31-35. Kültür, Spor ve Müzik:
    "TRT Müzik", "TRT 2", "TRT Spor Yıldız", "FB TV", "HTSpor TV",
    # 36-40. Ekonomi, Haber ve Yarış:
    "Bloomberg HT", "24 TV", "Bengütürk TV", "Ekol TV", "TJK TV",
    # 41-42. Çocuk:
    "TRT Diyanet Çocuk", "Baby TV",
    # 43-47. Popüler Müzik Kanalları:
    "PowerTurk TV", "Power TV", "Kral Pop TV", "Dream Turk", "Number 1 TV",
    # 48-50. Belgesel ve Ulusal Kanallar:
    "TGRT Belgesel", "Euro D", "TV 4"
]

# Doğrulanmış Öncelikli Kanallar (Failover Yedekleri ve EPG Kimlikleri ile)
VERIFIED_CHANNELS = [
    # ==================== ULUSAL ====================
    {
        "name": "TRT 1",
        "category": "Ulusal",
        "epg_id": "TRT.1.HD.tr",
        "url": "https://tv-trt1.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trt1.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-1-tr.png"
    },
    {
        "name": "ATV",
        "category": "Ulusal",
        "epg_id": "ATV.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/atv/atv.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/atv/atv.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/atv-tr.png"
    },
    {
        "name": "Kanal D",
        "category": "Ulusal",
        "epg_id": "KANAL.D.HD.tr",
        "url": "https://demiroren.daioncdn.net/kanald/kanald.m3u8?app=kanald_web&ce=3",
        "logo": "https://i.imgur.com/9o1atM6.png"
    },
    {
        "name": "Star TV",
        "category": "Ulusal",
        "epg_id": "STAR.TV.HD.tr",
        "url": "https://dogus.daioncdn.net/startv/startv_720p.m3u8?app=a20ac41e-bdc3-4aa1-934d-26b484480ac9&ce=3&sid=8l4w3lst4co5",
        "logo": "https://i.imgur.com/9O3DHRB.png"
    },
    {
        "name": "NOW",
        "category": "Ulusal",
        "epg_id": "FOX.HD.tr",
        "url": "https://uycyyuuzyh.turknet.ercdn.net/nphindgytw/nowtv/nowtv.m3u8",
        "logo": "https://i.imgur.com/5EYjWK7.png"
    },
    {
        "name": "TV8",
        "category": "Ulusal",
        "epg_id": "TV8.HD.tr",
        "url": "https://tv8.daioncdn.net/tv8/tv8.m3u8?app=7ddc255a-ef47-4e81-ab14-c0e5f2949788&ce=3",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tv8-tr.png"
    },
    {
        "name": "TV8.5",
        "category": "Ulusal",
        "epg_id": "",
        "url": "https://tv8.daioncdn.net/tv8bucuk/tv8bucuk.m3u8?app=tv8bucuk_web&ce=3",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tv85-tr.png"
    },
    {
        "name": "A2",
        "category": "Ulusal",
        "epg_id": "A2.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/a2tv/a2tv.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/a2tv/a2tv.m3u8"],
        "logo": "https://iatv.tmgrup.com.tr/site/v2/a2tv/i/a2tv-logo.png"
    },
    {
        "name": "360",
        "category": "Ulusal",
        "epg_id": "360.HD.tr",
        "url": "https://turkmedya-live.ercdn.net/tv360/tv360.m3u8",
        "logo": "https://i.imgur.com/agn47sQ.png"
    },
    {
        "name": "Kanal 7 Avrupa",
        "category": "Ulusal",
        "epg_id": "KANAL.7.HD.tr",
        "url": "https://livetv.radyotvonline.net/kanal7live/kanal7avr/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/kanal-7-avrupa-tr.png"
    },

    # ==================== ÇOCUK (TAM VE KORUMALI) ====================
    {
        "name": "TRT Çocuk",
        "category": "Çocuk",
        "epg_id": "TRT.ÇOCUK.HD.tr",
        "url": "https://tv-trtcocuk.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtcocuk.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-cocuk-tr.png"
    },
    {
        "name": "Minika Çocuk",
        "category": "Çocuk",
        "epg_id": "MİNİKA.ÇOCUK.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/minikago_cocuk/minikago_cocuk.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/minikacocuk/minikacocuk.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/minika-cocuk-tr.png"
    },
    {
        "name": "Minika Go",
        "category": "Çocuk",
        "epg_id": "MİNİKA.GO.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/minikago/minikago.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/minikago/minikago.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/minika-go-tr.png"
    },
    {
        "name": "Baby TV",
        "category": "Çocuk",
        "epg_id": "BABY.TV.tr",
        "url": "https://saran-live.ercdn.net/babytv/index.m3u8",
        "logo": "https://i.imgur.com/02kCsqR.png"
    },
    {
        "name": "Disney Jr.",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://saran-live.ercdn.net/disneyjunior/index.m3u8",
        "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/disneyjr.png"
    },
    {
        "name": "Spacetoon Turkey",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://live-tr-next.spacetoongo.com/ST_TR_NEXT/hls/h7qefeiwfbjn1.m3u8",
        "logo": "https://spacetoon.com/logo.png"
    },
    {
        "name": "TRT Diyanet Çocuk",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://tv-trtdiyanetcocuk.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtdiyanetcocuk.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-cocuk-tr.png"
    },
    {
        "name": "TRT EBA İlkokul",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://tv-e-okul00.medya.trt.com.tr/master.m3u8",
        "logo": "https://i.imgur.com/CRBfZi4.png"
    },
    {
        "name": "TRT EBA Ortaokul",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://tv-e-okul01.medya.trt.com.tr/master.m3u8",
        "logo": "https://i.imgur.com/CRBfZi4.png"
    },
    {
        "name": "TRT EBA Lise",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://tv-e-okul02.medya.trt.com.tr/master.m3u8",
        "logo": "https://i.imgur.com/vj2L2L2.png"
    },
    {
        "name": "Zarok TV",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://zindikurmanci.zaroktv.com.tr/hls/stream.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/zarok-tv-tr.png"
    },

    # ==================== HABER ====================
    {
        "name": "TRT Haber",
        "category": "Haber",
        "epg_id": "TRT.HABER.HD.tr",
        "url": "https://tv-trthaber.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trthaber.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-haber-tr.png"
    },
    {
        "name": "A Haber",
        "category": "Haber",
        "epg_id": "A.HABER.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/ahaber/ahaber.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/ahaber/ahaber.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/a-haber-tr.png"
    },
    {
        "name": "NTV",
        "category": "Haber",
        "epg_id": "NTV.HD.tr",
        "url": "https://dogus.daioncdn.net/ntv/ntv_720p.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ntv-tr.png"
    },
    {
        "name": "Habertürk TV",
        "category": "Haber",
        "epg_id": "HABERTÜRK.tr",
        "url": "https://tv.ensonhaber.com/haberturk/haberturk.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/haberturk-tr.png"
    },
    {
        "name": "Haber Global",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tv.ensonhaber.com/haberglobal/haberglobal.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/haber-global-tr.png"
    },
    {
        "name": "Bloomberg HT",
        "category": "Haber",
        "epg_id": "BLOOMBERG.HT.HD.tr",
        "url": "https://tv.ensonhaber.com/bloomberght/bloomberght.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/bloomberg-ht-tr.png"
    },
    {
        "name": "CNBC-e",
        "category": "Haber",
        "epg_id": "",
        "url": "https://hnpsechtsc.turknet.ercdn.net/xpnvudnlsv/cnbc-e/cnbc-e.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/cnbc-e-tr.png"
    },
    {
        "name": "TV100",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tv.ensonhaber.com/tv100/tv100.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tv100-tr.png"
    },
    {
        "name": "Halk TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://halktv-live.daioncdn.net/halktv/halktv.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/halk-tv-tr.png"
    },
    {
        "name": "Tele1",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tele1-live.ercdn.net/tele1/tele1.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tele1-tr.png"
    },
    {
        "name": "TGRT Haber",
        "category": "Haber",
        "epg_id": "TGRT.HABER.tr",
        "url": "https://canli.tgrthaber.com/tgrt.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tgrt-haber-tr.png"
    },
    {
        "name": "Flash Haber TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://b01c02nl.mediatriple.net/videoonlylive/mtyycglqauzjhlive/broadcast_67c053c48829f.smil/playlist.m3u8",
        "logo": "https://i.imgur.com/8FO41es.png"
    },
    {
        "name": "Bengütürk TV",
        "category": "Haber",
        "epg_id": "BENGÜ.TÜRK.tr",
        "url": "https://tv.ensonhaber.com/benguturk/benguturk.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/bengu-turk-tr.png"
    },
    {
        "name": "Ekol TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://ekoltv-live.ercdn.net/ekoltv/ekoltv.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ekoturk-tr.png"
    },
    {
        "name": "24 TV",
        "category": "Haber",
        "epg_id": "24.TV.tr",
        "url": "https://turkmedya-live.ercdn.net/tv24/tv24.m3u8",
        "logo": "https://i.imgur.com/8FO41es.png"
    },
    {
        "name": "TRT 3 / TBMM TV",
        "category": "Haber",
        "epg_id": "TRT.3.-..SPOR.tr",
        "url": "https://tv-trt3.live.trt.com.tr/master.m3u8",
        "logo": "https://i.imgur.com/JrWFwBd.png"
    },
    {
        "name": "TVNET",
        "category": "Haber",
        "epg_id": "TVNET.tr",
        "url": "https://tvnet-live.lg.mncdn.com/tvnet-live/tvnet/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tvnet-tr.png"
    },
    {
        "name": "Ülke TV",
        "category": "Haber",
        "epg_id": "ÜLKE.TV.HD.tr",
        "url": "https://livetv.radyotvonline.net/kanal7live/ulketv/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ulke-tv-tr.png"
    },

    # ==================== SPOR ====================
    {
        "name": "TRT Spor",
        "category": "Spor",
        "epg_id": "TRT.SPOR.HD.tr",
        "url": "https://tv-trtspor1.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtspor1.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-spor-tr.png"
    },
    {
        "name": "TRT Spor Yıldız",
        "category": "Spor",
        "epg_id": "",
        "url": "https://tv-trtspor2.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtspor2.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-spor-yildiz-tr.png"
    },
    {
        "name": "A Spor",
        "category": "Spor",
        "epg_id": "A.SPOR.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/aspor/aspor.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/aspor/aspor.m3u8"],
        "logo": "https://i.imgur.com/ZhkZzLf.png"
    },
    {
        "name": "HTSpor TV",
        "category": "Spor",
        "epg_id": "",
        "url": "https://ciner.daioncdn.net/ht-spor/ht-spor.m3u8?app=web",
        "logo": "https://www.htspor.com/images/manifest/social-share-logo.png"
    },
    {
        "name": "Ekol Sports",
        "category": "Spor",
        "epg_id": "",
        "url": "https://ekoltv-live.ercdn.net/ekolsport/ekolsport.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ekoturk-tr.png"
    },
    {
        "name": "FB TV",
        "category": "Spor",
        "epg_id": "FENERBAHÇE.TV.tr",
        "url": "http://1hskrdto.rocketcdn.com/fenerbahcetv.smil/playlist.m3u8",
        "logo": "https://i.imgur.com/qBVqtYd.png"
    },

    # ==================== BELGESEL ====================
    {
        "name": "TRT Belgesel",
        "category": "Belgesel",
        "epg_id": "TRT.BELGESEL.HD.tr",
        "url": "https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtbelgesel.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-belgesel-tr.png"
    },
    {
        "name": "TGRT Belgesel",
        "category": "Belgesel",
        "epg_id": "",
        "url": "https://canli.tgrthaber.com/tgrtbelgesel.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tgrt-haber-tr.png"
    },

    # ==================== MÜZİK ====================
    {
        "name": "TRT Müzik",
        "category": "Müzik",
        "epg_id": "TRT.MÜZİK.tr",
        "url": "https://tv-trtmuzik.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtmuzik.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-muzik-tr.png"
    },

    # ==================== SİNEMA & DİZİ ====================
    {
        "name": "BBC First Turkiye",
        "category": "Sinema & Dizi",
        "epg_id": "",
        "url": "http://88.212.15.29/live/bbc_first/index.m3u8",
        "logo": "https://i.imgur.com/UBoBYUI.png"
    },
    {
        "name": "Cine 1",
        "category": "Sinema & Dizi",
        "epg_id": "",
        "url": "https://canliyayin.cine1.com.tr/memfs/cbaef080-a742-4644-9e9e-2b9f6a5103c3_output_0.m3u8",
        "logo": "https://cine1.com.tr/img/cine1loogo.png"
    },
    {
        "name": "Kanal Plus",
        "category": "Sinema & Dizi",
        "epg_id": "",
        "url": "https://live.artidijitalmedya.com/artidijital_kanalplus/kanalplus/mpeg/playlist.m3u8",
        "fallbacks": [],
        "logo": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22gplus%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%230f172a%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%231e293b%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23gplus)%22%20stroke%3D%22%23334155%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%2244%25%22%20y%3D%2254%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2219%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%222%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2282%25%22%20y%3D%2252%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2228%22%20fill%3D%22%2338bdf8%22%3E%2B%3C%2Ftext%3E%3C%2Fsvg%3E"
    },

    # ==================== KÜLTÜR & DİNİ ====================
    {
        "name": "TRT 2",
        "category": "Kültür & Dini",
        "epg_id": "",
        "url": "https://tv-trt2.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trt2.live.trt.com.tr/master.m3u8"],
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-2-tr.png"
    },
    {
        "name": "TRT Türk",
        "category": "Kültür & Dini",
        "epg_id": "TRT.TÜRK.tr",
        "url": "https://tv-trtturk.medya.trt.com.tr/master.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-turk-tr.png"
    },
    {
        "name": "TRT Avaz",
        "category": "Kültür & Dini",
        "epg_id": "TRT.AVAZ.HD.tr",
        "url": "https://tv-trtavaz.medya.trt.com.tr/master.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-avaz-tr.png"
    },
    {
        "name": "TRT Kurdî",
        "category": "Kültür & Dini",
        "epg_id": "TRT.KURDİ.tr",
        "url": "https://tv-trtkurdi.medya.trt.com.tr/master.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-kurdi-tr.png"
    },
    {
        "name": "Diyanet TV",
        "category": "Kültür & Dini",
        "epg_id": "",
        "url": "https://eustr73.mediatriple.net/videoonlylive/mtikoimxnztxlive/broadcast_5e3bf95a47e07.smil/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/diyanet-tv-tr.png"
    },

    # ==================== YEREL ====================
    {
        "name": "Kanal 19",
        "category": "Yerel",
        "epg_id": "",
        "url": "https://live.euromediacenter.com/kanal19/tracks-v1a1/mono.m3u8",
        "fallbacks": [
            "https://live.euromediacenter.com/kanal19/tracks-v1a1/playlist.m3u8",
            "https://live.euromediacenter.com/kanal19/playlist.m3u8"
        ],
        "logo": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22g19%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23b91c1c%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23dc2626%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23g19)%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2236%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2216%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%223%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2268%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2230%22%20fill%3D%22%23fef08a%22%3E19%3C%2Ftext%3E%3C%2Fsvg%3E"
    }
]

# Dinamik Kanal EPG Haritası (XMLTV ID eşleştirmeleri - Sadece kendi resmi EPG'si olan kanallar)
EPG_MAP = {
    # Ulusal
    "trt 1": "TRT.1.HD.tr",
    "atv": "ATV.HD.tr",
    "kanal d": "KANAL.D.HD.tr",
    "star tv": "STAR.TV.HD.tr",
    "now": "FOX.HD.tr",
    "now tv": "FOX.HD.tr",
    "tv8": "TV8.HD.tr",
    "a2": "A2.HD.tr",
    "360": "360.HD.tr",
    "show tv": "SHOW.TV.HD.tr",
    "kanal 7": "KANAL.7.HD.tr",
    "kanal 7 avrupa": "KANAL.7.HD.tr",
    "beyaz tv": "BEYAZ.TV.HD.tr",
    "teve2": "TEVE2.HD.tr",
    "tlc": "TLC.HD.tr",
    "dmax": "DMAX.HD.tr",
    
    # Çocuk
    "trt çocuk": "TRT.ÇOCUK.HD.tr",
    "minika çocuk": "MİNİKA.ÇOCUK.tr",
    "minika go": "MİNİKA.GO.tr",
    "baby tv": "BABY.TV.tr",
    "cartoon network": "CARTOON.NETWORK.tr",
    "ducktv": "DUCKTV.HD.tr",

    # Haber
    "trt haber": "TRT.HABER.HD.tr",
    "a haber": "A.HABER.HD.tr",
    "ntv": "NTV.HD.tr",
    "habertürk": "HABERTÜRK.HD.tr",
    "habertürk tv": "HABERTÜRK.HD.tr",
    "bloomberg ht": "BLOOMBERG.HT.HD.tr",
    "tgrt haber": "TGRT.HABER.tr",
    "24 tv": "24.TV.HD.tr",
    "bengütürk tv": "BENGÜ.TÜRK.tr",
    "bengü türk": "BENGÜ.TÜRK.tr",
    "cnn türk": "CNN.TÜRK.HD.tr",
    "ulusal kanal": "ULUSAL.KANAL.tr",
    "akit tv": "AKİT.TV.tr",
    "a para": "A.PARA.tr",
    "ekotürk": "EKOTÜRK.tr",
    "ülke tv": "ÜLKE.TV.HD.tr",
    "kanal b": "KANAL.B.tr",
    "trt 3": "TRT.3.-..SPOR.tr",
    "trt 3 / tbmm tv": "TRT.3.-..SPOR.tr",

    # Spor
    "trt spor": "TRT.SPOR.HD.tr",
    "a spor": "A.SPOR.HD.tr",
    "bein sports haber": "beIN.SPORTS.HABER.HD.tr",
    "fb tv": "FENERBAHÇE.TV.tr",
    "fenerbahçe tv": "FENERBAHÇE.TV.tr",
    "sports tv": "SPORTS.TV.tr",

    # Belgesel
    "trt belgesel": "TRT.BELGESEL.HD.tr",
    "national geographic": "NATIONAL.GEOGRAPHIC.HD.tr",

    # Müzik
    "trt müzik": "TRT.MÜZİK.tr",
    "power tv": "POWER.TV.HD.tr",
    "dream tv": "DREAM.TV.tr",
    "tmb": "TMB.tr",

    # Kültür, Dini & Yerel
    "trt türk": "TRT.TÜRK.tr",
    "trt avaz": "TRT.AVAZ.HD.tr",
    "trt kurdî": "TRT.KURDİ.tr",
    "trt kurdi": "TRT.KURDİ.tr",
    "kon tv": "KON.TV.tr",
    "olay tv": "OLAY.TV.tr",
    "kanal 16": "KANAL.16.tr",
    "line tv": "LINETV.tr",

    # Yeni Eklenen Popüler Kanallar
    "trt 4k": "TRT.4K.tr",
    "tabii": "TABİİ.tr",
    "krt": "KRT.tr",
    "krt tv": "KRT.tr",
    "tvnet": "TVNET.tr"
}

# Statik ve Doğrulanmış Kanal Logoları Kütüphanesi
STATIC_LOGOS = {
    "show max": "https://www.showmax.com.tr/assets/dist/images/base/logo.svg",
    "kanal b": "https://www.kanalb.com.tr/assets/images/logo/1683624355Kanal_B_logosu.png",
    "cem tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/cem-tv-tr.png",
    "cine 1": "https://cine1.com.tr/img/cine1loogo.png",
    "as tv": "https://www.astv.com.tr/static/2026/07/06/astv-logo-1783346167-699-x80.jpeg",
    "bodrum kent tv": "https://static.daktilo.com/sites/1600/uploads/2024/07/27/social.png",
    "erciyes tv": "https://s.erciyestv.com.tr/dosya/logo/erciyes-tv-og.jpg",
    "kanal urfa": "https://www.kanalurfa.com/upload/masaustu.png",
    "bi kanal": "http://www.bikanal.com/uploads/banners/01K6DG6S1EPCZN7DQH406HGMES.webp",
    "sonmez tv": "https://www.astv.com.tr/static/2026/07/06/astv-logo-1783346167-699-x80.jpeg",
    "dost tv": "https://dosttv.com/wp-content/uploads/2020/09/dost-tv-logo.png",
    "bir tv": "https://birtv.com.tr/wp-content/uploads/2022/10/bir-tv-logo.png",
    "tbmm tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tbmm-tv-tr.png",
    "trt 3 / tbmm tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tbmm-tv-tr.png",
    "frt tv": "https://s.gercekfethiye.com/dosya/logo/svg/logo-ana.svg",
    "malatya vuslat tv": "https://vuslattv.com.tr/uploads/logo/logo_66bdb4352c7ab7-60769650.png",
    "ruha tv": "https://ruhatv.com.tr/kunye_dosyalar/kunye_logo.png",
    "karadeniz tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/mavi-karadeniz-tr.png",
    "krt tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/krt-tr.png",
    "krt": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/krt-tr.png",
    "tvnet": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tvnet-tr.png",
    "ülke tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ulke-tv-tr.png",
    "ulke tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/ulke-tv-tr.png",
    "trt 4k": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/trt-4k-tr.png",
    "tabii": "https://cms-tabii-assets.tabii.com/thumbnails/23963_781e9dee-cbd8-491a-b166-0b1df25b3bd0_720.jpeg",
    "dmax": "https://img-tlctv.mncdn.com/logo-dmax.png",
    "tlc": "https://img-tlctv.mncdn.com/logo.png",
    "euro d": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/euro-d-tr.png",
    "show türk": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/show-turk-tr.png",
    "atv avrupa": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/atv-avrupa-tr.png",
    "kanal 19": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22g19%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23b91c1c%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23dc2626%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23g19)%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2236%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2216%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%223%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2268%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2230%22%20fill%3D%22%23fef08a%22%3E19%3C%2Ftext%3E%3C%2Fsvg%3E",
    "kanal 19 tv": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22g19%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23b91c1c%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23dc2626%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23g19)%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2236%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2216%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%223%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2268%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2230%22%20fill%3D%22%23fef08a%22%3E19%3C%2Ftext%3E%3C%2Fsvg%3E",
    "kanal plus": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22gplus%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%230f172a%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%231e293b%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23gplus)%22%20stroke%3D%22%23334155%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%2244%25%22%20y%3D%2254%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2219%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%222%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2282%25%22%20y%3D%2252%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2228%22%20fill%3D%22%2338bdf8%22%3E%2B%3C%2Ftext%3E%3C%2Fsvg%3E",
    "kanalplus": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22gplus%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%230f172a%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%231e293b%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23gplus)%22%20stroke%3D%22%23334155%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%2244%25%22%20y%3D%2254%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2219%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%222%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2282%25%22%20y%3D%2252%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2228%22%20fill%3D%22%2338bdf8%22%3E%2B%3C%2Ftext%3E%3C%2Fsvg%3E",
    "kanal+": "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%20width%3D%22160%22%20height%3D%2290%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22gplus%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%230f172a%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%231e293b%22%2F%3E%3C%2Fdefs%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20rx%3D%2214%22%20fill%3D%22url(%23gplus)%22%20stroke%3D%22%23334155%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%2244%25%22%20y%3D%2254%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2219%22%20fill%3D%22%23ffffff%22%20letter-spacing%3D%222%22%3EKANAL%3C%2Ftext%3E%3Ctext%20x%3D%2282%25%22%20y%3D%2252%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-weight%3D%22900%22%20font-size%3D%2228%22%20fill%3D%22%2338bdf8%22%3E%2B%3C%2Ftext%3E%3C%2Fsvg%3E",
    "number 1 turk": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/nr1-turk-tr.png",
    "number 1 türk": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/nr1-turk-tr.png",
    "rehber tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/rehber-tv-tr.png",
    "cartoon network": "https://www.cartoonnetwork.com.tr/static/img/cn-logo.png",
    "fx": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/fx-tr.png",
    "tbmm tv": "https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/tbmm-tv-tr.png"
}

def clean_channel_name(raw_name: str) -> str:
    """Kanal adlarındaki gereksiz etiketleri temizler ve standartlaştırır."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    
    patterns = [
        r'\s*\((?:1080p|720p|576p|480p|360p|1440p|4k|hd|sd|\d+p\w*)\)',
        r'\s*\[.*?\]',
        r'\s*\((?:Turkiye|Turkey|TR)\)',
        r'\b(?:1080p|720p|576p|480p|360p|1440p|\d+p\w*)\b',
        r'\bSD\b',
    ]
    for p in patterns:
        name = re.sub(p, '', name, flags=re.IGNORECASE)
    
    name = re.sub(r'\s+', ' ', name).strip()
    
    name_map = {
        "A2TV": "A2",
        "AHaber": "A Haber",
        "ASpor": "A Spor",
        "ASPOR": "A Spor",
        "A SPOR": "A Spor",
        "A HABER": "A Haber",
        "A PARA": "A Para",
        "AKIT TV": "Akit TV",
        "ALANYA ATV": "ATV Alanya",
        "ANADOLUNET TV": "Anadolu Net TV",
        "BENGU TURK": "Bengütürk TV",
        "BENGÜ TÜRK": "Bengütürk TV",
        "Benguturk TV": "Bengütürk TV",
        "BEYAZ TV": "Beyaz TV",
        "BIR TV": "Bir TV",
        "BİR TV": "Bir TV",
        "BODRUM KENT TV": "Bodrum Kent TV",
        "BURSA LiNE TV": "Line TV",
        "CAY TV": "Çay TV",
        "Cay TV": "Çay TV",
        "CINE 1": "Cine 1",
        "Ciftci TV": "Çiftçi TV",
        "ÇİFTÇİ TV": "Çiftçi TV",
        "CNN TURK": "CNN Türk",
        "DENiZ POSTASI TV": "Deniz Postasi TV",
        "DiYANET TV": "Diyanet TV",
        "DIYANET TV": "Diyanet TV",
        "DOST TV": "Dost TV",
        "Dream Turk": "Dream Türk",
        "DREAM TURK": "Dream Türk",
        "EKOL TV": "Ekol TV",
        "Ekoturk": "Ekotürk",
        "EKOTURK": "Ekotürk",
        "ER TV": "ERTV",
        "ERCİYES TV": "Erciyes TV",
        "ES TV": "ES TV",
        "ETV KAYSERi": "ETV Kayseri",
        "EURO D": "Euro D",
        "EURO D HD SS": "Euro D",
        "EUROSTAR": "Eurostar",
        "FB TV": "FB TV",
        "GRT GAZİANTEP TV": "Gaziantep GRT TV",
        "GUNEYDOGU TV": "Güneydoğu TV",
        "GURBET 24 TV": "Gurbet 24 TV",
        "HABER 61": "Haber61 TV",
        "HABER GLOBAL": "Haber Global",
        "HABER TURK": "Habertürk TV",
        "HABERTURK": "Habertürk TV",
        "Haberturk": "Habertürk TV",
        "Haberturk TV": "Habertürk TV",
        "HALK TV": "Halk TV",
        "HT Spor": "HTSpor TV",
        "HT SPOR": "HTSpor TV",
        "HTSpor TV": "HTSpor TV",
        "HUNAT TV": "Hunat TV",
        "iCEL TV": "Icel TV",
        "KANAL 12": "Kanal 12",
        "KANAL 15": "Kanal 15",
        "KANAL 19": "Kanal 19",
        "KANAL19": "Kanal 19",
        "KANAL 19 TV": "Kanal 19",
        "KANAL 19 CORUM": "Kanal 19",
        "KANAL 19 ÇORUM": "Kanal 19",
        "KANAL 23": "Kanal 23",
        "KANAL 26": "Kanal 26",
        "KANAL 3": "Kanal 3",
        "KANAL 32": "Kanal 32",
        "KANAL 33": "Kanal 33",
        "KANAL 34": "Kanal 34",
        "KANAL 53": "Kanal 53",
        "KANAL 58": "Kanal 58",
        "KANAL 68": "Kanal 68",
        "KANAL 7": "Kanal 7",
        "KANAL 7 (Turkiye)": "Kanal 7",
        "KANAL 7 AVRUPA": "Kanal 7 Avrupa",
        "KANAL ADA": "Kanal Ada",
        "KANAL B": "Kanal B",
        "KANAL D": "Kanal D",
        "KANAL D (Turkiye)": "Kanal D",
        "KANAL D HD": "Kanal D",
        "KANAL FIRAT": "Kanal Fırat",
        "Kanal Firat": "Kanal Fırat",
        "KANAL PLUS": "Kanal Plus",
        "KANAL+": "Kanal Plus",
        "KANAL +": "Kanal Plus",
        "KANALPLUS": "Kanal Plus",
        "KANAL PLUS SiNEMA": "Kanal Plus",
        "KANAL PLUS SİNEMA": "Kanal Plus",
        "KANAL URFA": "Kanal Urfa",
        "KANAL Z": "Kanal Z",
        "KARDELEN TV": "Kardelen TV",
        "KAY TV": "Kay TV",
        "KOCAELİ TV": "Kocaeli TV",
        "KRAL POP": "Kral Pop TV",
        "KRAL POP TV FHD": "Kral Pop TV",
        "KRT": "KRT TV",
        "KTV KONYA": "KTV Konya",
        "Lalegul TV": "Lalegül TV",
        "LALEGUL TV": "Lalegül TV",
        "LIFE TV": "Life TV",
        "LİFE TV": "Life TV",
        "MAVi KARADENiZ TV": "MaviKaradeniz TV",
        "MELTEM TV": "Meltem TV",
        "MERCAN TV": "Mercan TV",
        "Minika Cocuk": "Minika Çocuk",
        "Minika Go": "Minika Go",
        "MINIKA GO": "Minika Go",
        "MUGLA TÜRK TV": "Muğla Türk TV",
        "NOW TV": "NOW",
        "NR 1 TV": "Number 1 TV",
        "NR 1 DAMAR": "Number 1 Damar",
        "NR 1 TURK": "Number 1 Türk",
        "NR1 TV": "Number 1 TV",
        "NR1 DAMAR": "Number 1 Damar",
        "NR1 TURK": "Number 1 Türk",
        "NR1 ASK": "Number 1 Ask",
        "NR1 DANCE": "Number 1 Dance",
        "ORDU BEL TV": "Ordu Bel TV",
        "POWER TURK": "PowerTurk TV",
        "POWER TURK SLOW": "PowerTurk Slow",
        "POWER TURK TAPTAZE": "PowerTurk Taptaze",
        "POWER TV AKUSTiK": "PowerTurk Akustik",
        "REHBER TV": "Rehber TV",
        "RIZE TURK HD": "Rize Türk TV",
        "SEMERKAND TV": "Semerkand TV",
        "SHOW TURK": "Show Türk",
        "SHOW TV": "Show TV",
        "SHOW TV HD": "Show TV",
        "SPORTS TV": "Sports TV",
        "STAR TV": "Star TV",
        "STAR TV (Turkiye)": "Star TV",
        "STAR TV HD": "Star TV",
        "SUN TV": "Sun RTV",
        "TABII TV": "Tabii",
        "Tabii TV HD": "Tabii",
        "TELE 1": "Tele1",
        "Tele 1": "Tele1",
        "Tele1 TV": "Tele1",
        "TELE1": "Tele1",
        "TEMPO TV": "Tempo TV",
        "TEVE 2": "Teve2",
        "TEVE2": "Teve2",
        "TGRT HABER": "TGRT Haber",
        "TGRT HABER HD": "TGRT Haber",
        "TH TURK HABER TV": "TurkHaber TV",
        "TIVI 6": "Tivi 6",
        "TJK TV": "TJK TV",
        "TON TV": "Ton TV",
        "TRAKYA TÜRK TV": "Trakya Türk TV",
        "TRT 1 (1440p)": "TRT 1",
        "TRT 4K": "TRT 4K",
        "TRT AVAZ": "TRT Avaz",
        "TRT COCUK": "TRT Çocuk",
        "TRT Cocuk": "TRT Çocuk",
        "TRT COCUK DIYANET": "TRT Diyanet Çocuk",
        "TRT Diyanet Cocuk": "TRT Diyanet Çocuk",
        "TRT DİYANET ÇOCUK": "TRT Diyanet Çocuk",
        "TRT EBA ORTAKUL": "TRT EBA Ortaokul",
        "TRT Haber (720p)": "TRT Haber",
        "TRT HABER": "TRT Haber",
        "TRT KURDI": "TRT Kurdî",
        "TRT MUZIK": "TRT Müzik",
        "TRT Muzik": "TRT Müzik",
        "TRT MÜZiK": "TRT Müzik",
        "TRT Spor Yildiz": "TRT Spor Yıldız",
        "TRT SPOR": "TRT Spor",
        "TRT SPOR YILDIZ": "TRT Spor Yıldız",
        "TRT Turk": "TRT Türk",
        "TRT TURK": "TRT Türk",
        "TRT TÜRK": "TRT Türk",
        "TRT1": "TRT 1",
        "TURKHABER": "TurkHaber TV",
        "TV 100": "TV100",
        "TV 4": "TV 4",
        "TV 41": "TV 41",
        "TV 52": "TV 52",
        "TV 8": "TV8",
        "TV 8 (Turkiye)": "TV8",
        "TV 8.5": "TV8.5",
        "TV 8 INT": "TV8 Int",
        "TV 8bucuk": "TV8.5",
        "TV 264": "TV 264",
        "TV4": "TV 4",
        "TV8 (Turkiye)": "TV8",
        "TVNET": "TVNET",
        "TV NET": "TVNET",
        "ULKE TV": "Ülke TV",
        "ÜLKE TV": "Ülke TV",
        "UR FANATiK TV": "Urfa Natik TV",
        "VAN GOLU TV": "Van Gölü TV",
        "VUSLAT TV": "Malatya Vuslat TV",
        "Zarok TV Kürtçe": "Zarok TV",
        "24": "24 TV",
        "360 TV": "360",
        "BabyTV": "Baby TV"
    }
    return name_map.get(name, name)

def get_channel_category(name: str) -> str:
    """Kanal adına göre akıllı kategori sınıflandırması yapar."""
    n = name.lower()
    
    # 1. Çocuk Kanalları
    if any(k in n for k in ['çocuk', 'cocuk', 'minika', 'cartoon', 'disney', 'baby', 'spacetoon', 'zarok', 'animasyon', 'eba']):
        return 'Çocuk'
        
    # 2. Ulusal Kanallar
    if n in ['trt 1', 'atv', 'kanal d', 'star tv', 'now', 'tv8', 'tv8.5', 'show tv', 'show max', 'kanal 7', 'kanal 7 avrupa', 'a2', 'teve2', 'beyaz tv', '360', 'tlc', 'euro d', 'tv 4', 'trt 4k']:
        return 'Ulusal'
        
    # 3. Spor
    if any(k in n for k in ['spor', 'sport', 'tjk', 'fb tv', 'gs tv', 'bjk tv', 'satranc']):
        return 'Spor'
        
    # 4. Haber & Ekonomi
    if any(k in n for k in ['haber', 'news', 'bloomberg', 'finans', 'dha', 'tele1', 'halk tv', '24 tv', 'tv100', 'bengütürk', 'ekotürk', 'ekoturk', 'ulusal kanal', 'tbmm', 'cnbc-e', 'cnbce', 'kanal b', 'ilke', 'krt', 'tvnet', 'ülke tv', 'ulke tv']):
        return 'Haber'
        
    # 5. Belgesel
    if any(k in n for k in ['belgesel', 'docu', 'wild', 'ciftci', 'çiftçi', 'yaban', 'dmax', 'nat geo']):
        return 'Belgesel'
        
    # 6. Müzik
    if any(k in n for k in ['müzik', 'muzik', 'music', 'power', 'kral', 'dream', 'nr1', 'nr 1', 'number 1', 'damar', 'pop', 'akustik', 'slow', 'dance', 'arabesk']):
        return 'Müzik'
        
    # 7. Sinema & Dizi
    if any(k in n for k in ['sinema', 'cinema', 'film', 'dizi', 'bbc first', 'cine 1', 'cine1', 'kanal plus', 'tabii', 'screen', 'moviesmart']):
        return 'Sinema & Dizi'
        
    # 8. Kültür & Dini
    if any(k in n for k in ['trt 2', 'diyanet', 'semerkand', 'dost tv', 'lalegül', 'lalegul', 'hilal', 'kudus', 'kudüs', 'berat', 'rehber', 'vav', 'meltem', 'trt avaz', 'trt kurdî', 'trt kurdi', 'trt türk', 'cem tv', 'kanal hayat', 'yol tv', 'trt genc', 'kabe', 'quran', 'madinah', 'makkah']):
        return 'Kültür & Dini'
        
    # 9. Yerel (Varsayılan)
    return 'Yerel'

def normalize_category(group_name: str, channel_name: str) -> str:
    """Kategori adını standart ve temiz Türkçe kategorilere dönüştürür."""
    if not group_name:
        return get_channel_category(channel_name)
    g_up = group_name.strip().upper()
    if any(k in g_up for k in ['ÇOCUK', 'COCUK', 'KIDS']):
        return 'Çocuk'
    if any(k in g_up for k in ['HABER', 'NEWS']):
        return 'Haber'
    if any(k in g_up for k in ['SPOR', 'SPORT']):
        return 'Spor'
    if any(k in g_up for k in ['BELGESEL', 'DOCU']):
        return 'Belgesel'
    if any(k in g_up for k in ['MÜZİK', 'MUZIK', 'MUSIC']):
        return 'Müzik'
    if any(k in g_up for k in ['SİNEMA', 'SINEMA', 'SiNEMA', 'FILM', 'MOVIE', 'DİZİ', 'DIZI']):
        return 'Sinema & Dizi'
    if any(k in g_up for k in ['DİNİ', 'DINI', 'KÜLTÜR', 'KULTUR', 'RELIGIOUS']):
        return 'Kültür & Dini'
    if any(k in g_up for k in ['ULUSAL', 'NATIONAL', 'GENEL']):
        return get_channel_category(channel_name)
    if any(k in g_up for k in ['YEREL', 'LOCAL']):
        return 'Yerel'
    return get_channel_category(channel_name)

def make_svg_logo(name: str) -> str:
    """Logo bulunamayan kanallar için standart ve estetik SVG data-uri logosu üretir."""
    clean = re.sub(r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ ]', '', name or 'TV').strip()
    words = clean.split()
    if len(words) == 1:
        initials = words[0][:3].upper()
    elif len(words) >= 2:
        initials = (words[0][0] + words[1][0] + (words[2][0] if len(words) > 2 else '')).upper()[:3]
    else:
        initials = 'TV'
    
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="90" viewBox="0 0 160 90">'
        f'<rect width="160" height="90" rx="14" fill="#0f172a" stroke="#2563eb" stroke-width="2"/>'
        f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" '
        f'font-family="system-ui,-apple-system,sans-serif" font-weight="900" font-size="24" fill="#38bdf8">{initials}</text>'
        f'</svg>'
    )
    import urllib.parse
    return 'data:image/svg+xml;charset=utf-8,' + urllib.parse.quote(svg)

def fetch_tv_logos_map() -> dict:
    """tv-logo/tv-logos Türkiye açık kaynak kütüphanesinden güncel kanal logolarını çeker."""
    mapping = {}
    url = "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/turkey/0_all_logos_mosaic.md"
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            entries = re.findall(r'\[([^\]]+)\]:\s*([^\s]+-tr\.png)', r.text)
            for slug, fn in entries:
                clean = slug.replace('-', ' ').strip().lower()
                logo_url = f"https://raw.githubusercontent.com/tv-logo/tv-logos/refs/heads/main/countries/turkey/{fn}"
                mapping[clean] = logo_url
                mapping[slug.lower()] = logo_url
                norm = clean.replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u')
                mapping[norm] = logo_url
            print(f"[tv-logos] Toplam {len(entries)} adet yüksek çözünürlüklü kanal logosu yüklendi.")
    except Exception as e:
        print(f"[tv-logos] Logo kütüphanesi yüklenemedi: {e}")
    return mapping

# Çapraz Kategori Eşleştirmeleri (Bir kanal birden fazla kategoride yer alabilir)
CROSS_CATEGORY_MAPPINGS = [
    # TRT 3 / TBMM TV hem Haber hem Spor kategorisinde (Sadece TRT 3 için)
    {
        "match": lambda n: "trt 3" in n.lower(),
        "extra_category": "Spor",
        "url_suffix": "#spor",
        "custom_name": "TRT 3 Spor / TBMM TV"
    },
    # CNBC-e hem Haber hem Ulusal kategorisinde
    {
        "match": lambda n: "cnbc-e" in n.lower(),
        "extra_category": "Ulusal",
        "url_suffix": "#ulusal",
        "custom_name": "CNBC-e"
    },
    # HTSpor hem Spor hem Haber kategorisinde
    {
        "match": lambda n: "htspor" in n.lower(),
        "extra_category": "Haber",
        "url_suffix": "#haber",
        "custom_name": "HTSpor TV"
    },
    # Show Max hem Ulusal hem Sinema & Dizi kategorisinde
    {
        "match": lambda n: "show max" in n.lower(),
        "extra_category": "Sinema & Dizi",
        "url_suffix": "#dizi",
        "custom_name": "Show Max (Dizi & Sinema)"
    },
    # A2 hem Ulusal hem Sinema & Dizi kategorisinde
    {
        "match": lambda n: n.lower() == "a2",
        "extra_category": "Sinema & Dizi",
        "url_suffix": "#dizi",
        "custom_name": "A2 (Dizi & Sinema)"
    },
    # TRT 2 hem Kültür & Dini hem Belgesel kategorisinde
    {
        "match": lambda n: n.lower() == "trt 2",
        "extra_category": "Belgesel",
        "url_suffix": "#belgesel",
        "custom_name": "TRT 2 (Kültür & Belgesel)"
    },
    # TRT Müzik hem Müzik hem Kültür kategorisinde
    {
        "match": lambda n: "trt müzik" in n.lower() or "trt muzik" in n.lower(),
        "extra_category": "Kültür & Dini",
        "url_suffix": "#kultur",
        "custom_name": "TRT Müzik"
    }
]

def turkish_lower(text: str) -> str:
    """Türkçe İ ve I harflerini doğru şekilde küçük harfe dönüştürür."""
    return text.replace('İ', 'i').replace('I', 'ı').lower()

def turkish_sort_key(text: str):
    """Türkçe alfabesine göre sıralama anahtarı üretir."""
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

def check_single_url(session, url: str, retries: int = 1) -> bool:
    """URL'nin canlı ve geçerli bir HLS / m3u8 akışı olduğunu test eder."""
    for _ in range(retries):
        try:
            r = session.get(url, headers=HEADERS, timeout=(TIMEOUT_CONNECT, TIMEOUT_READ), stream=True, verify=False)
            if r.status_code in (200, 206):
                chunk = next(r.iter_content(chunk_size=512), b'')
                if b'#EXTM3U' in chunk or b'#EXTINF' in chunk or len(chunk) > 100:
                    return True
        except Exception:
            pass
    return False

def check_stream(item):
    """
    Failover ve Toleranslı Canlılık Testi:
    - Primary URL'yi dener (verified için 2 deneme).
    - Başarısız olursa 'fallbacks' listesindeki yedek URL'leri sırayla test eder.
    - Doğrulanmış ana kanal ise, geçici ağ kesintilerinde kanalı listeden düşürmez (koruma kalkanı).
    """
    name = item['name']
    url = item['url']
    logo = item.get('logo', '')
    category = item.get('category') or get_channel_category(name)
    epg_id = item.get('epg_id', '')
    is_verified = item.get('is_verified', False)
    fallbacks = item.get('fallbacks', [])

    with requests.Session() as session:
        # 1. Ana adresi test et
        retries = 2 if is_verified else 1
        if check_single_url(session, url, retries=retries):
            return {
                'name': name,
                'url': url,
                'logo': logo,
                'category': category,
                'epg_id': epg_id,
                'ok': True
            }

        # 2. Yedek (Failover) adresleri test et
        for fb_url in fallbacks:
            if check_single_url(session, fb_url, retries=2):
                print(f"  [Failover Aktif] {name}: Yedek yayın devreye alındı.")
                return {
                    'name': name,
                    'url': fb_url,
                    'logo': logo,
                    'category': category,
                    'epg_id': epg_id,
                    'ok': True
                }

        # 3. Tolerans Mekanizması: Doğrulanmış ana kanalları listeden silme
        if is_verified:
            print(f"  [Tolerans Koruması] {name}: Geçici yanıt alınamadı, ana URL korundu.")
            return {
                'name': name,
                'url': url,
                'logo': logo,
                'category': category,
                'epg_id': epg_id,
                'ok': True
            }

    return {
        'name': name,
        'url': url,
        'logo': logo,
        'category': category,
        'epg_id': epg_id,
        'ok': False
    }

def fetch_onureroz_channels():
    """OnurEroz Türkiye listelerindeki (index.m3u & tv2.m3u) güncel kanalları ve alternatif yedek adreslerini çeker."""
    urls = [
        'https://onureroz.com/indirmeler/turk/index.m3u',
        'https://onureroz.com/indirmeler/turk/tv2.m3u'
    ]
    items = []
    logo_map = {}
    for playlist_url in urls:
        try:
            r = requests.get(playlist_url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                lines = r.text.splitlines()
                curr_name = ""
                curr_logo = ""
                curr_group = ""
                curr_epg = ""
                fallbacks = []
                for line in lines:
                    if line.startswith('#EXTINF'):
                        m_name = re.findall(r',([^,]+)$', line)
                        raw_title = m_name[0].strip() if m_name else ''
                        m_logo = re.search(r'tvg-logo="([^"]+)"', line)
                        curr_logo = m_logo.group(1).strip() if m_logo else ''
                        m_group = re.search(r'group-title="([^"]+)"', line)
                        curr_group = m_group.group(1).strip() if m_group else ''
                        m_epg = re.search(r'tvg-id="([^"]+)"', line)
                        curr_epg = m_epg.group(1).strip() if m_epg and m_epg.group(1) != 'ext' else ''

                        # Yedek, Yedek2, Yedek3 ... adreslerini failover listesine al
                        y_urls = re.findall(r'Yedek\d*="([^"]+)"', line)
                        fallbacks = [y for y in y_urls if y.startswith('http')]

                        if not is_foreign_or_blocked(raw_title):
                            curr_name = clean_channel_name(raw_title)
                            if curr_name and curr_logo:
                                logo_map[curr_name.lower()] = curr_logo
                                norm_key = curr_name.lower().replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u')
                                logo_map[norm_key] = curr_logo
                        else:
                            curr_name = ""
                    elif curr_name and line.startswith('http'):
                        items.append({
                            'name': curr_name,
                            'url': line.strip(),
                            'logo': curr_logo,
                            'category': normalize_category(curr_group, curr_name),
                            'epg_id': curr_epg,
                            'fallbacks': fallbacks,
                            'is_verified': False
                        })
                        curr_name = ""
                        curr_epg = ""
                        fallbacks = []
                print(f"[OnurEroz] '{playlist_url.split('/')[-1]}' listesinden {len(items)} yayın çekildi.")
        except Exception as e:
            print(f"[OnurEroz] Çekme hatası ({playlist_url}): {e}")
    return items, logo_map

def fetch_famelack_channels():
    """Famelack veri tabanındaki Türkiye kanallarını çeker."""
    url = 'https://raw.githubusercontent.com/famelack/famelack-data/main/tv/compressed/countries/tr.json'
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = json.loads(gzip.decompress(r.content).decode('utf-8'))
            for ch in data:
                raw_name = ch.get('name', '')
                if is_foreign_or_blocked(raw_name):
                    continue
                name = clean_channel_name(raw_name)
                logo = ch.get('logo') or ''
                streams = ch.get('sources', {}).get('streams') or []
                for s in streams:
                    if s and s.startswith('http'):
                        items.append({
                            'name': name,
                            'url': s,
                            'logo': logo,
                            'is_verified': False
                        })
            print(f"[Famelack] Toplam {len(items)} yerli yayın adresi çekildi.")
    except Exception as e:
        print(f"[Famelack] Çekme hatası: {e}")
    return items

def fetch_iptv_org_channels():
    """IPTV-org Türkiye listesindeki kanalları ve logo haritasını çeker."""
    url = 'https://iptv-org.github.io/iptv/countries/tr.m3u'
    items = []
    logo_map = {}
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            curr_name = ""
            curr_logo = ""
            for line in lines:
                if line.startswith('#EXTINF'):
                    m_logo = re.search(r'tvg-logo="([^"]+)"', line)
                    curr_logo = m_logo.group(1).strip() if m_logo and m_logo.group(1) else ''
                    raw_title = line.split(',')[-1].strip()
                    if not is_foreign_or_blocked(raw_title):
                        curr_name = clean_channel_name(raw_title)
                        if curr_name and curr_logo:
                            logo_map[curr_name.lower()] = curr_logo
                            norm_key = curr_name.lower().replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u')
                            logo_map[norm_key] = curr_logo
                    else:
                        curr_name = ""
                elif curr_name and line.startswith('http'):
                    items.append({
                        'name': curr_name,
                        'url': line.strip(),
                        'logo': curr_logo,
                        'is_verified': False
                    })
                    curr_name = ""
            print(f"[IPTV-org] Toplam {len(items)} yerli yayın adresi ve {len(logo_map)} logo çekildi.")
    except Exception as e:
        print(f"[IPTV-org] Çekme hatası: {e}")
    return items, logo_map

def format_m3u_entry(channel: dict, custom_group: str = None) -> list:
    """Standartlara uygun M3U kanal satırlarını üretir."""
    name = channel['name']
    url = channel['url']
    logo = channel.get('logo', '')
    category = custom_group or channel.get('category', 'Yerel')
    epg_id = channel.get('epg_id', '')

    parts = ['#EXTINF:-1']
    if epg_id:
        parts.append(f'tvg-id="{epg_id}"')
    parts.append(f'tvg-name="{name}"')
    if logo:
        parts.append(f'tvg-logo="{logo}"')
    if category:
        parts.append(f'group-title="{category}"')
        
    extinf = f'{" ".join(parts)},{name}'
    return [extinf, url]

def build_playlist():
    print("=" * 65)
    print("Sadece Türkiye Canlı TV (Eksiksiz Kategoriler, EPG) Oluşturuluyor...")
    print("=" * 65)

    # 1. Kaynakları Topla
    all_candidates = []
    
    # Öncelikle Doğrulanmış Öncelikli Kanallar
    for ch in VERIFIED_CHANNELS:
        if is_foreign_or_blocked(ch['name']):
            continue
        all_candidates.append({
            'name': clean_channel_name(ch['name']),
            'url': ch['url'],
            'logo': ch.get('logo', ''),
            'category': ch.get('category', 'Ulusal'),
            'epg_id': ch.get('epg_id', ''),
            'fallbacks': ch.get('fallbacks', []),
            'is_verified': True
        })

    # OnurEroz, IPTV-org ve Famelack listelerini ekle (Tüm zengin yerli kaynaklar)
    onur_candidates, onur_logo_map = fetch_onureroz_channels()
    iptv_candidates, iptv_logo_map = fetch_iptv_org_channels()
    famelack_candidates = fetch_famelack_channels()

    # Birleşik logo haritası (tv-logos + IPTV-org + OnurEroz)
    tv_logos_catalog = fetch_tv_logos_map()
    combined_logo_map = {**tv_logos_catalog, **iptv_logo_map, **onur_logo_map}

    all_candidates.extend(onur_candidates)
    all_candidates.extend(iptv_candidates)
    all_candidates.extend(famelack_candidates)

    # 2. URL Bazlı Tekilleştirme (Logo, Failover ve EPG korumalı)
    seen_urls = {}
    for item in all_candidates:
        url = item['url']
        if url not in seen_urls:
            seen_urls[url] = item
        else:
            # URL çakışmasında eğer mevcut kayıtta logo yoksa ama bu kayıtta varsa logoyu aktar
            if not seen_urls[url].get('logo') and item.get('logo'):
                seen_urls[url]['logo'] = item['logo']
            if not seen_urls[url].get('epg_id') and item.get('epg_id'):
                seen_urls[url]['epg_id'] = item['epg_id']
            if item.get('fallbacks'):
                existing_fb = seen_urls[url].get('fallbacks', [])
                for fb in item['fallbacks']:
                    if fb not in existing_fb and fb != url:
                        existing_fb.append(fb)
                seen_urls[url]['fallbacks'] = existing_fb

    unique_candidates = list(seen_urls.values())

    print(f"\nCanlılık testi yapılacak toplam benzersiz yerli yayın: {len(unique_candidates)}")
    print("Yayınlar eş zamanlı olarak kontrol ediliyor...")

    # 3. Canlılık Testi (Çok İş Parçacıklı + Toleranslı Test)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        test_results = list(pool.map(check_stream, unique_candidates))

    working_streams = [r for r in test_results if r['ok']]
    print(f"Çalışır durumda tespit edilen yayın: {len(working_streams)}")

    # 4. Kanal Adı Bazlı Akıllı Tekilleştirme & EPG/Kategori Zenginleştirme
    verified_map = {clean_channel_name(v['name']).lower(): v for v in VERIFIED_CHANNELS}

    final_channel_map = {}
    for item in working_streams:
        norm_name = clean_channel_name(item['name'])
        if not norm_name or is_foreign_or_blocked(norm_name):
            continue
        key = norm_name.lower()
        norm_key = key.replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u')

        # Doğrulanmış kanalların özellikleri önceliklidir
        verified_info = verified_map.get(key)
        
        logo = item.get('logo', '')
        category = normalize_category(item.get('category'), norm_name)
        epg_id = item.get('epg_id', '')

        if verified_info:
            if verified_info.get('logo'):
                logo = verified_info['logo']
            if verified_info.get('category'):
                category = verified_info['category']
            # Doğrulanmış kanalın EPG kimliği esastır (boş ise sahte/başka kanalın EPG'si atanmaz)
            epg_id = verified_info.get('epg_id', '')
        else:
            # Sadece resmi listede kendi EPG kimliği bulunan kanallar eşleştirilir
            epg_id = EPG_MAP.get(key, '')

        # Logo çözümleme hiyerarşisi: Verified -> Akış Logosu -> Statik Kütüphane -> Birleşik Logo Haritası
        if 'wikimedia.org' in logo:
            logo = ''

        if not logo:
            if key in STATIC_LOGOS:
                logo = STATIC_LOGOS[key]
            elif norm_key in STATIC_LOGOS:
                logo = STATIC_LOGOS[norm_key]
            elif key in combined_logo_map:
                logo = combined_logo_map[key]
            elif norm_key in combined_logo_map:
                logo = combined_logo_map[norm_key]

        if key not in final_channel_map:
            final_channel_map[key] = {
                'name': norm_name,
                'url': item['url'],
                'logo': logo,
                'category': category,
                'epg_id': epg_id,
                'is_verified': bool(verified_info)
            }
        else:
            if not final_channel_map[key]['logo'] and logo:
                final_channel_map[key]['logo'] = logo
            if not final_channel_map[key]['epg_id'] and epg_id:
                final_channel_map[key]['epg_id'] = epg_id

    # Kanal haritasında kalan boş veya Wikimedia logoları için ek zenginleştirme güvencesi
    for key, ch in final_channel_map.items():
        if not ch.get('logo') or 'wikimedia.org' in ch.get('logo', ''):
            ch['logo'] = ''
            norm_key = key.replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u')
            if key in STATIC_LOGOS:
                ch['logo'] = STATIC_LOGOS[key]
            elif norm_key in STATIC_LOGOS:
                ch['logo'] = STATIC_LOGOS[norm_key]
            elif key in combined_logo_map:
                ch['logo'] = combined_logo_map[key]
            elif norm_key in combined_logo_map:
                ch['logo'] = combined_logo_map[norm_key]
            else:
                ch['logo'] = make_svg_logo(ch['name'])

    final_channels = list(final_channel_map.values())
    print(f"Tekilleştirme sonrası net yerli kanal sayısı: {len(final_channels)}")

    # 5. Çapraz Kategori Eklemesi (Kullanıcı İsteği: Bir kanal birden fazla kategoride yer alabilir)
    # IPTV oynatıcılarının çakışmasını engellemek için URL'ye oynatıcıyı etkilemeyen benzersiz etiket eklenir (#kategori)
    extended_channels = list(final_channels)
    for ch in final_channels:
        c_name = ch['name']
        for mapping in CROSS_CATEGORY_MAPPINGS:
            if mapping['match'](c_name) and ch['category'] != mapping['extra_category']:
                extra_channel = dict(ch)
                extra_channel['category'] = mapping['extra_category']
                extra_channel['name'] = mapping.get('custom_name', c_name)
                # Oynatıcı önbellek çakışmasını önlemek için benzersiz URL son eki
                extra_channel['url'] = ch['url'] + mapping['url_suffix']
                extended_channels.append(extra_channel)

    # 5.1. TOP 50 Grubu (En Çok İzlenen 50 Kanal, Reyting ve Popülerlik Sıralı - Diyanet TV #1)
    # kanallar.m3u içinde Ulusal kategorisi yerine TOP 50 ana vitrin olarak yer alır.
    top_50_channels = []
    for req_name in TOP_50_RANKS:
        req_key = clean_channel_name(req_name).lower()
        if req_key in final_channel_map:
            top_50_channels.append(final_channel_map[req_key])
        else:
            match = next((v for k, v in final_channel_map.items() if req_key in k or k in req_key), None)
            if match and match not in top_50_channels:
                top_50_channels.append(match)

    top_50_group = []
    for rank, ch in enumerate(top_50_channels, start=1):
        item = dict(ch)
        item['category'] = "TOP 50"
        item['url'] = ch['url'] + "#top50"
        item['top50_rank'] = rank
        top_50_group.append(item)

    # 5.2. TÜM KANALLAR (A-Z Sıralı) Grubu (Kullanıcı İsteği: 'Tüm Kanallar' sekmesi olmayan oynatıcılar için)
    # Tüm çalışan yerli kanallar tek bir grupta toplanır ve A-Z olarak listelenir.
    # Diğer kategorilerle çakışmaması ve silinmemesi için URL'ye #all etiketi eklenir.
    all_channels_group = []
    for ch in final_channels:
        item = dict(ch)
        item['category'] = "TÜM KANALLAR (A-Z Sıralı)"
        item['url'] = ch['url'] + "#all"
        all_channels_group.append(item)

    # Ulusal kategorisi TOP 50 olarak adlandırıldı/değiştirildi (kullanıcı talebi).
    # Ulusal kategorisindeki kanallar zaten TOP 50 listesindedir.
    # Diğer tematik kategorileri (Çocuk, Haber, Spor, Belgesel, Müzik, Sinema & Dizi, Kültür & Dini, Yerel) ekliyoruz.
    category_channels = [ch for ch in extended_channels if ch.get('category') not in ('Ulusal', 'ULUSAL')]

    extended_channels = all_channels_group + top_50_group + category_channels

    # 6. Kategorik Sıralama (Kategori Önceliği + Kategori İçi Sıralama)
    def sort_key(ch):
        cat = ch.get('category', 'Yerel')
        cat_index = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 99
        if cat == "TOP 50":
            # TOP 50 kategorisinde kanallar en çok izlenenden en aza doğru sıralanır (Diyanet TV #1)
            return (cat_index, ch.get('top50_rank', 999), '')
        return (cat_index, 999, turkish_sort_key(ch['name']))

    extended_channels.sort(key=sort_key)

    # Kategori dağılımını yazdır
    cat_counts = {}
    for ch in extended_channels:
        cat = ch.get('category', 'Yerel')
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("\nGüncel Kategori Dağılımı:")
    for cat in CATEGORY_ORDER:
        if cat in cat_counts:
            print(f"  • {cat}: {cat_counts[cat]} kanal")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 7. GENEL M3U / M3U8 Dosyalarını Oluştur (kanallar.m3u & kanallar.m3u8)
    header_lines = [
        f'#EXTM3U url-tvg="{EPG_URL}" x-tvg-url="{EPG_URL}"',
        "# Generated automatically for Android TV & Smart TV - Turkiye Canli TV",
        f"# Total Verified Turkish Channels: {len(extended_channels)}",
        ""
    ]

    main_lines = list(header_lines)
    for ch in extended_channels:
        main_lines.extend(format_m3u_entry(ch))

    main_content = "\n".join(main_lines) + "\n"
    m3u_path = os.path.join(base_dir, "kanallar.m3u")
    m3u8_path = os.path.join(base_dir, "kanallar.m3u8")

    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(main_content)
    with open(m3u8_path, "w", encoding="utf-8") as f:
        f.write(main_content)

    print(f"\n[Başarılı] Ana Liste '{m3u_path}' oluşturuldu! ({len(extended_channels)} kanal)")
    print(f"[Başarılı] Ana Liste '{m3u8_path}' oluşturuldu!")

    # 8. ÇOCUK ÖZEL M3U / M3U8 Dosyalarını Oluştur (cocuk.m3u & cocuk.m3u8)
    kids_channels = [ch for ch in final_channels if ch.get('category') == 'Çocuk']
    kids_channels.sort(key=lambda x: turkish_sort_key(x['name']))

    kids_header = [
        f'#EXTM3U url-tvg="{EPG_URL}" x-tvg-url="{EPG_URL}"',
        "# Cocuklara Ozel Guvenli Canli TV Calma Listesi",
        f"# Total Kids Channels: {len(kids_channels)}",
        ""
    ]
    kids_lines = list(kids_header)
    for ch in kids_channels:
        kids_lines.extend(format_m3u_entry(ch, custom_group="Çocuk"))

    kids_content = "\n".join(kids_lines) + "\n"
    kids_m3u_path = os.path.join(base_dir, "cocuk.m3u")
    kids_m3u8_path = os.path.join(base_dir, "cocuk.m3u8")

    with open(kids_m3u_path, "w", encoding="utf-8") as f:
        f.write(kids_content)
    with open(kids_m3u8_path, "w", encoding="utf-8") as f:
        f.write(kids_content)

    print(f"[Başarılı] Çocuk Özel Listesi '{kids_m3u_path}' oluşturuldu! ({len(kids_channels)} kanal)")
    print(f"[Başarılı] Çocuk Özel Listesi '{kids_m3u8_path}' oluşturuldu!")
    print("  Aktif Çocuk Kanalları:")
    for k in kids_channels:
        print(f"    - {k['name']}")

    # 9. TOP 50 ÖZEL M3U / M3U8 Dosyalarını Oluştur (top50.m3u & top50.m3u8)
    top50_header = [
        f'#EXTM3U url-tvg="{EPG_URL}" x-tvg-url="{EPG_URL}"',
        "# Turkiye En Cok Izlenen TOP 50 Canli TV Listesi",
        f"# Total Channels: {len(top_50_channels)}",
        ""
    ]
    top50_lines = list(top50_header)
    for ch in top_50_channels:
        top50_lines.extend(format_m3u_entry(ch, custom_group="TOP 50"))

    top50_content = "\n".join(top50_lines) + "\n"
    top50_m3u_path = os.path.join(base_dir, "top50.m3u")
    top50_m3u8_path = os.path.join(base_dir, "top50.m3u8")

    with open(top50_m3u_path, "w", encoding="utf-8") as f:
        f.write(top50_content)
    with open(top50_m3u8_path, "w", encoding="utf-8") as f:
        f.write(top50_content)

    print(f"[Başarılı] TOP 50 Özel Listesi '{top50_m3u_path}' oluşturuldu! ({len(top_50_channels)} kanal)")
    print(f"[Başarılı] TOP 50 Özel Listesi '{top50_m3u8_path}' oluşturuldu!")

    # 10. API / JSON Formatında Veri Çıktısı (channels.json)
    now_utc = datetime.now(timezone.utc)
    now_tr = now_utc + timedelta(hours=3)

    stats_data = {
        "updated_at": now_tr.strftime("%Y-%m-%d %H:%M:%S (TSİ)"),
        "total_unique_channels": len(final_channels),
        "total_extended_entries": len(extended_channels),
        "total_kids_channels": len(kids_channels),
        "total_top50_channels": len(top_50_channels),
        "category_counts": {cat: cat_counts.get(cat, 0) for cat in CATEGORY_ORDER if cat in cat_counts},
        "epg_source": EPG_URL,
        "playlists": {
            "all_m3u": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u",
            "all_m3u8": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/kanallar.m3u8",
            "kids_m3u": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/cocuk.m3u",
            "kids_m3u8": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/cocuk.m3u8",
            "top50_m3u": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/top50.m3u",
            "top50_m3u8": "https://raw.githubusercontent.com/YosemiteSam6/turkiye-iptv-m3u-m3u8/main/top50.m3u8"
        },
        "channels": [
            {
                "name": ch["name"],
                "category": ch.get("category", "Yerel"),
                "logo": ch.get("logo", ""),
                "epg_id": ch.get("epg_id", ""),
                "url": ch["url"],
                "is_verified": ch.get("is_verified", False)
            }
            for ch in final_channels
        ]
    }

    json_path = os.path.join(base_dir, "channels.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    print(f"[Başarılı] JSON Veri Çıktısı '{json_path}' oluşturuldu! ({len(final_channels)} benzersiz kanal)")
    print("=" * 65)

if __name__ == "__main__":
    build_playlist()
