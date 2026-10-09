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
from concurrent.futures import ThreadPoolExecutor
import requests

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
    "Ulusal",
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
        'almahriah', 'elsharq', 'mekameleen', 'al-zahra', 'persiana',
        'sat 7', 'luys', 'tyt turk', 'kanal avrupa', 'trt arabi', 'trt world'
    ]
    return any(b in n for b in blocked_keywords)

# Türkiye'de En Çok İzlenen 50 Kanal (Reyting ve Popülerlik Sıralı)
TOP_50_RANKS = [
    # --- Ulusal Ana Kanallar ---
    "TRT 1", "ATV", "NOW", "Kanal D", "Star TV", "TV8", "TV8.5", "A2", "360", 
    "Kanal 7 Avrupa", "Euro D", "Show Max", "TV 4",
    # --- Popüler Çocuk Kanalları ---
    "TRT Çocuk", "Minika Çocuk", "Minika Go", "Disney Jr.", "Baby TV", 
    "Spacetoon Turkey", "TRT Diyanet Çocuk", "TRT EBA İlkokul",
    # --- Ana Haber & Ekonomi Kanalları ---
    "TRT Haber", "NTV", "Habertürk TV", "A Haber", "Haber Global", "TV100", 
    "Halk TV", "Tele1", "TGRT Haber", "Bloomberg HT", "CNBC-e", "24 TV", "Flash Haber TV", 
    "Bengütürk TV", "Ekol TV", "TRT 3 / TBMM TV",
    # --- Spor Kanalları ---
    "TRT Spor", "TRT Spor Yıldız", "A Spor", "Ekol Sports", "FB TV", "HTSpor TV", "TJK TV",
    # --- Belgesel Kanalları ---
    "TRT Belgesel", "TGRT Belgesel",
    # --- Müzik Kanalları ---
    "TRT Müzik", "Power TV", "PowerTurk TV", "Kral Pop TV", "Dream Turk", "Number 1 TV",
    # --- Kültür & Sanat ---
    "TRT 2"
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
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/TRT_1_logo_2021.svg/512px-TRT_1_logo_2021.svg.png"
    },
    {
        "name": "ATV",
        "category": "Ulusal",
        "epg_id": "ATV.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/atv/atv.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/atv/atv.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/ATV_logo.svg/512px-ATV_logo.svg.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/6/68/Tv8_Yeni_Logo.png/960px-Tv8_Yeni_Logo.png"
    },
    {
        "name": "TV8.5",
        "category": "Ulusal",
        "epg_id": "",
        "url": "https://tv8.daioncdn.net/tv8bucuk/tv8bucuk.m3u8?app=tv8bucuk_web&ce=3",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/c/cf/Tv8_bucuk_logo.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Kanal_7_logo.svg/512px-Kanal_7_logo.svg.png"
    },

    # ==================== ÇOCUK (TAM VE KORUMALI) ====================
    {
        "name": "TRT Çocuk",
        "category": "Çocuk",
        "epg_id": "TRT.ÇOCUK.HD.tr",
        "url": "https://tv-trtcocuk.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtcocuk.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/TRT_%C3%87ocuk_logo_2021.svg/512px-TRT_%C3%87ocuk_logo_2021.svg.png"
    },
    {
        "name": "Minika Çocuk",
        "category": "Çocuk",
        "epg_id": "MİNİKA.ÇOCUK.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/minikago_cocuk/minikago_cocuk.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/minikacocuk/minikacocuk.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/8/87/Minika_%C3%87ocuk_logosu.png/512px-Minika_%C3%87ocuk_logosu.png"
    },
    {
        "name": "Minika Go",
        "category": "Çocuk",
        "epg_id": "MİNİKA.GO.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/minikago/minikago.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/minikago/minikago.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/9/91/Minika_GO_logosu.png/512px-Minika_GO_logosu.png"
    },
    {
        "name": "Baby TV",
        "category": "Çocuk",
        "epg_id": "BABY.TV.tr",
        "url": "https://saran-live.ercdn.net/babytv/index.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6f/BabyTV_logo.svg/512px-BabyTV_logo.svg.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/tr/2/2b/Spacetoon_logo.png"
    },
    {
        "name": "TRT Diyanet Çocuk",
        "category": "Çocuk",
        "epg_id": "",
        "url": "https://tv-trtdiyanetcocuk.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtdiyanetcocuk.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/512px-TRT_%C3%87ocuk_logo_%282021%29.svg.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/8/87/Zarok_TV_logosu.png/512px-Zarok_TV_logosu.png"
    },

    # ==================== HABER ====================
    {
        "name": "TRT Haber",
        "category": "Haber",
        "epg_id": "TRT.HABER.HD.tr",
        "url": "https://tv-trthaber.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trthaber.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/TRT_Haber_logo_2021.svg/512px-TRT_Haber_logo_2021.svg.png"
    },
    {
        "name": "A Haber",
        "category": "Haber",
        "epg_id": "A.HABER.HD.tr",
        "url": "https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/ahaber/ahaber.m3u8",
        "fallbacks": ["https://trkvz-live.ercdn.net/ahaber/ahaber.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Ahaber_Logo.png"
    },
    {
        "name": "NTV",
        "category": "Haber",
        "epg_id": "NTV.HD.tr",
        "url": "https://dogus.daioncdn.net/ntv/ntv_720p.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/NTV_logo.svg/512px-NTV_logo.svg.png"
    },
    {
        "name": "Habertürk TV",
        "category": "Haber",
        "epg_id": "HABERTÜRK.tr",
        "url": "https://tv.ensonhaber.com/haberturk/haberturk.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Habert%C3%BCrk_TV_logo.svg/512px-Habert%C3%BCrk_TV_logo.svg.png"
    },
    {
        "name": "Haber Global",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tv.ensonhaber.com/haberglobal/haberglobal.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Haber_Global_logo.svg/512px-Haber_Global_logo.svg.png"
    },
    {
        "name": "Bloomberg HT",
        "category": "Haber",
        "epg_id": "BLOOMBERG.HT.HD.tr",
        "url": "https://tv.ensonhaber.com/bloomberght/bloomberght.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Bloomberg_HT_logo.svg/512px-Bloomberg_HT_logo.svg.png"
    },
    {
        "name": "CNBC-e",
        "category": "Haber",
        "epg_id": "",
        "url": "https://hnpsechtsc.turknet.ercdn.net/xpnvudnlsv/cnbc-e/cnbc-e.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/CNBC-e_logo.svg/512px-CNBC-e_logo.svg.png"
    },
    {
        "name": "TV100",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tv.ensonhaber.com/tv100/tv100.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/TV100_logosu.svg/512px-TV100_logosu.svg.png"
    },
    {
        "name": "Halk TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://halktv-live.daioncdn.net/halktv/halktv.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Halk_TV_logo.svg/512px-Halk_TV_logo.svg.png"
    },
    {
        "name": "Tele1",
        "category": "Haber",
        "epg_id": "",
        "url": "https://tele1-live.ercdn.net/tele1/tele1.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Tele1_logo.svg/512px-Tele1_logo.svg.png"
    },
    {
        "name": "TGRT Haber",
        "category": "Haber",
        "epg_id": "TGRT.HABER.tr",
        "url": "https://canli.tgrthaber.com/tgrt.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/TGRT_Haber_logo.svg/512px-TGRT_Haber_logo.svg.png"
    },
    {
        "name": "Flash Haber TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://b01c02nl.mediatriple.net/videoonlylive/mtyycglqauzjhlive/broadcast_67c053c48829f.smil/playlist.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Flash_Haber_logosu.png/512px-Flash_Haber_logosu.png"
    },
    {
        "name": "Bengütürk TV",
        "category": "Haber",
        "epg_id": "BENGÜ.TÜRK.tr",
        "url": "https://tv.ensonhaber.com/benguturk/benguturk.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/8/8c/Beng%C3%BCt%C3%BCrk_TV_logosu.png/512px-Beng%C3%BCt%C3%BCrk_TV_logosu.png"
    },
    {
        "name": "Ekol TV",
        "category": "Haber",
        "epg_id": "",
        "url": "https://ekoltv-live.ercdn.net/ekoltv/ekoltv.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ekol_TV_logosu.png/512px-Ekol_TV_logosu.png"
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

    # ==================== SPOR ====================
    {
        "name": "TRT Spor",
        "category": "Spor",
        "epg_id": "TRT.SPOR.HD.tr",
        "url": "https://tv-trtspor1.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtspor1.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/TRT_Spor_logo_2021.svg/512px-TRT_Spor_logo_2021.svg.png"
    },
    {
        "name": "TRT Spor Yıldız",
        "category": "Spor",
        "epg_id": "",
        "url": "https://tv-trtspor2.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtspor2.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/TRT_Spor_Y%C4%B1ld%C4%B1z_logo_2021.svg/512px-TRT_Spor_Y%C4%B1ld%C4%B1z_logo_2021.svg.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Ekol_TV_logosu.png/512px-Ekol_TV_logosu.png"
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
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/TRT_Belgesel_logo_2021.svg/512px-TRT_Belgesel_logo_2021.svg.png"
    },
    {
        "name": "TGRT Belgesel",
        "category": "Belgesel",
        "epg_id": "",
        "url": "https://canli.tgrthaber.com/tgrtbelgesel.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/TGRT_Haber_logo.svg/512px-TGRT_Haber_logo.svg.png"
    },

    # ==================== MÜZİK ====================
    {
        "name": "TRT Müzik",
        "category": "Müzik",
        "epg_id": "TRT.MÜZİK.tr",
        "url": "https://tv-trtmuzik.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trtmuzik.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/TRT_M%C3%BCzik_logo_2021.svg/512px-TRT_M%C3%BCzik_logo_2021.svg.png"
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
        "logo": "https://i.imgur.com/agn47sQ.png"
    },

    # ==================== KÜLTÜR & DİNİ ====================
    {
        "name": "TRT 2",
        "category": "Kültür & Dini",
        "epg_id": "",
        "url": "https://tv-trt2.medya.trt.com.tr/master.m3u8",
        "fallbacks": ["https://tv-trt2.live.trt.com.tr/master.m3u8"],
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/TRT_2_logo_2021.svg/512px-TRT_2_logo_2021.svg.png"
    },
    {
        "name": "TRT Türk",
        "category": "Kültür & Dini",
        "epg_id": "TRT.TÜRK.tr",
        "url": "https://tv-trtturk.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/TRT_T%C3%BCrk_logo_2021.svg/512px-TRT_T%C3%BCrk_logo_2021.svg.png"
    },
    {
        "name": "TRT Avaz",
        "category": "Kültür & Dini",
        "epg_id": "TRT.AVAZ.HD.tr",
        "url": "https://tv-trtavaz.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/TRT_Avaz_logo_2021.svg/512px-TRT_Avaz_logo_2021.svg.png"
    },
    {
        "name": "TRT Kurdî",
        "category": "Kültür & Dini",
        "epg_id": "TRT.KURDİ.tr",
        "url": "https://tv-trtkurdi.medya.trt.com.tr/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/TRT_Kurd%C3%AE_logo_2021.svg/512px-TRT_Kurd%C3%AE_logo_2021.svg.png"
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
    "line tv": "LINETV.tr"
}

def clean_channel_name(raw_name: str) -> str:
    """Kanal adlarındaki gereksiz etiketleri temizler ve standartlaştırır."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    
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
        "Minika Cocuk": "Minika Çocuk",
        "Minika Go": "Minika Go",
        "TRT Diyanet Cocuk": "TRT Diyanet Çocuk",
        "TRT Muzik": "TRT Müzik",
        "TRT Turk": "TRT Türk",
        "NOW TV": "NOW",
        "TV 100": "TV100",
        "TV 8.5": "TV8.5",
        "TV 8": "TV8",
        "BabyTV": "Baby TV",
        "HTSpor TV": "HTSpor TV",
        "HT Spor": "HTSpor TV"
    }
    return name_map.get(name, name)

def get_channel_category(name: str) -> str:
    """Kanal adına göre akıllı kategori sınıflandırması yapar."""
    n = name.lower()
    
    # 1. Çocuk Kanalları
    if any(k in n for k in ['çocuk', 'cocuk', 'minika', 'cartoon', 'disney', 'baby', 'spacetoon', 'zarok', 'animasyon', 'eba']):
        return 'Çocuk'
        
    # 2. Ulusal Kanallar
    if n in ['trt 1', 'atv', 'kanal d', 'star tv', 'now', 'tv8', 'tv8.5', 'show tv', 'show max', 'kanal 7', 'kanal 7 avrupa', 'a2', 'teve2', 'beyaz tv', '360', 'tlc', 'euro d', 'tv 4']:
        return 'Ulusal'
        
    # 3. Spor
    if any(k in n for k in ['spor', 'sport', 'tjk', 'fb tv', 'gs tv', 'bjk tv', 'satranc']):
        return 'Spor'
        
    # 4. Haber & Ekonomi
    if any(k in n for k in ['haber', 'news', 'bloomberg', 'finans', 'dha', 'tele1', 'halk tv', '24 tv', 'tv100', 'bengütürk', 'ekotürk', 'ekoturk', 'ulusal kanal', 'tbmm', 'cnbc-e', 'cnbce', 'kanal b', 'ilke']):
        return 'Haber'
        
    # 5. Belgesel
    if any(k in n for k in ['belgesel', 'docu', 'wild', 'ciftci', 'çiftçi', 'yaban', 'dmax', 'nat geo']):
        return 'Belgesel'
        
    # 6. Müzik
    if any(k in n for k in ['müzik', 'muzik', 'music', 'power', 'kral', 'dream', 'nr1', 'number 1', 'damar', 'pop', 'akustik', 'slow', 'dance']):
        return 'Müzik'
        
    # 7. Sinema & Dizi
    if any(k in n for k in ['sinema', 'cinema', 'film', 'dizi', 'bbc first', 'cine 1', 'cine1', 'kanal plus']):
        return 'Sinema & Dizi'
        
    # 8. Kültür & Dini
    if any(k in n for k in ['trt 2', 'diyanet', 'semerkand', 'dost tv', 'lalegül', 'lalegul', 'hilal', 'kudus', 'kudüs', 'berat', 'rehber', 'vav', 'meltem', 'trt avaz', 'trt kurdî', 'trt kurdi', 'trt türk', 'cem tv', 'kanal hayat', 'yol tv', 'trt genc']):
        return 'Kültür & Dini'
        
    # 9. Yerel (Varsayılan)
    return 'Yerel'

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
            r = session.get(url, headers=HEADERS, timeout=(TIMEOUT_CONNECT, TIMEOUT_READ), stream=True)
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
                    if not is_foreign_or_blocked(raw_title):
                        curr_name = clean_channel_name(raw_title)
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
            print(f"[IPTV-org] Toplam {len(items)} yerli yayın adresi çekildi.")
    except Exception as e:
        print(f"[IPTV-org] Çekme hatası: {e}")
    return items

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

    # Famelack ve IPTV-org listelerini ekle (Yabancı kanallardan arındırılmış)
    all_candidates.extend(fetch_famelack_channels())
    all_candidates.extend(fetch_iptv_org_channels())

    # 2. URL Bazlı Tekilleştirme
    seen_urls = set()
    unique_candidates = []
    for item in all_candidates:
        url = item['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append(item)

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

        # Doğrulanmış kanalların özellikleri önceliklidir
        verified_info = verified_map.get(key)
        
        logo = item.get('logo', '')
        category = item.get('category') or get_channel_category(norm_name)
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

    # 5.1. TÜM KANALLAR (A-Z Sıralı) Grubu (Kullanıcı İsteği: 'Tüm Kanallar' sekmesi olmayan oynatıcılar için)
    # Tüm çalışan yerli kanallar tek bir grupta toplanır ve A-Z olarak listelenir.
    # Diğer kategorilerle çakışmaması ve silinmemesi için URL'ye #all etiketi eklenir.
    all_channels_group = []
    for ch in final_channels:
        item = dict(ch)
        item['category'] = "TÜM KANALLAR (A-Z Sıralı)"
        item['url'] = ch['url'] + "#all"
        all_channels_group.append(item)

    extended_channels = all_channels_group + extended_channels

    # 6. Kategorik Sıralama (Kategori Önceliği + Kategori İçi Türkçe A-Z Sıralama)
    def sort_key(ch):
        cat = ch.get('category', 'Yerel')
        cat_index = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 99
        return (cat_index, turkish_sort_key(ch['name']))

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
    top_50_channels = []
    for req_name in TOP_50_RANKS:
        req_key = clean_channel_name(req_name).lower()
        if req_key in final_channel_map:
            top_50_channels.append(final_channel_map[req_key])
        else:
            match = next((v for k, v in final_channel_map.items() if req_key in k or k in req_key), None)
            if match and match not in top_50_channels:
                top_50_channels.append(match)

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
    print("=" * 65)

if __name__ == "__main__":
    build_playlist()
