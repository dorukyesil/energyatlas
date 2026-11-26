"""Resmî Gazete arşivinden enerji mevzuatını çıkarır.

resmigazete.gov.tr'deki günlük arşiv sayfalarını (eskiler/YYYY/MM/YYYYMMDD.htm) tarar, her günün
yayımlanan metinlerinin başlıklarını ve bağlantılarını alır, enerjiyle ilgili olanları sınıflandırıp
data/mevzuat_resmi_gazete.csv dosyasına yazar. Ham günlük sayfalar yerel önbellekte tutulur.

Kullanım:
    python scripts/mevzuat_resmi_gazete.py --baslangic 2019-01-01 --bitis 2026-11-26
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import html
import re
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from config import DATA_DIR

TABAN = "https://www.resmigazete.gov.tr/eskiler/{y}/{m:02d}/{y}{m:02d}{d:02d}.htm"
BAGLANTI = re.compile(r'<a[^>]+href="((?:https?://www\.resmigazete\.gov\.tr/)?eskiler/[^"]*?|\d{8}-\d+\.(?:htm|pdf))"[^>]*>(.*?)</a>', re.S | re.I)

# Enerji ile ilgili anahtar kelimeler (büyük/küçük harf duyarsız, Türkçe karakter kökleri)
ENERJI_KELIMELERI = [
    "enerji", "elektrik", "doğalgaz", "dogalgaz", "petrol", "akaryakıt", "akaryakit", "lpg", "nükleer", "nukleer",
    "yenilenebilir", "güneş", "gunes", "rüzgâr", "rüzgar", "jeotermal", "hidroelektrik", "biyokütle", "biyokutle",
    "kömür", "komur", "linyit", "batarya", "depolama", "yekdem", "yeka", "epdk", "teiaş", "teias", "eüaş", "euas",
    "boru hattı", "rafineri", "kaynak tipi", "elektrik piyasası", "iletim sistemi", "dağıtım sistemi",
]

TUR_KURALLARI = [
    (r"Anayasa Mahkemesi", "Anayasa Mahkemesi kararı"),
    (r"Yargıtay|Danıştay", "Yargı kararı"),
    (r"Cumhurbaşkanlığı Kararnamesi", "Cumhurbaşkanlığı Kararnamesi"),
    (r"Kanun Hükmünde Kararname", "Kanun hükmünde kararname"),
    (r"\bKanun\b(?!\s+Teklif)", "Kanun"),
    (r"Tebliğ", "Tebliğ"),
    (r"Yönetmelik", "Yönetmelik"),
    (r"Karar", "Karar"),
    (r"Uluslararası Anlaşma|Anlaşma", "Uluslararası anlaşma"),
]


def indir(url: str, deneme: int = 3) -> str | None:
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return r.read().decode("windows-1254", errors="replace")
        except urllib.error.HTTPError as e:
            return None if e.code == 404 else None
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def temizle(metin: str) -> str:
    metin = re.sub(r"<[^>]+>", " ", metin)
    metin = html.unescape(metin)
    metin = re.sub(r"\s+", " ", metin).strip()
    return re.sub(r"^[\s\u2013\u2014\-–—]+", "", metin)


def tur_bul(baslik: str) -> str:
    for kalip, ad in TUR_KURALLARI:
        if re.search(kalip, baslik, flags=re.I):
            return ad
    return "Diğer"


def enerji_anahtarlari(baslik: str) -> list[str]:
    b = baslik.lower()
    return sorted({k for k in ENERJI_KELIMELERI if k in b})


def gun_kayitlari(gun: date, onbellek: Path) -> list[dict]:
    dosya = onbellek / f"{gun:%Y%m%d}.html"
    if dosya.exists():
        icerik = dosya.read_text(encoding="utf-8", errors="ignore")
    else:
        icerik = indir(TABAN.format(y=gun.year, m=gun.month, d=gun.day))
        if icerik is None:
            return []
        dosya.write_text(icerik, encoding="utf-8")
    kayitlar = []
    for href, govde in BAGLANTI.findall(icerik):
        baslik = temizle(govde)
        if len(baslik) < 12 or "Mevzuat" in baslik and len(baslik) < 20:
            continue
        anahtarlar = enerji_anahtarlari(baslik)
        if not anahtarlar:
            continue
        url = href if href.startswith("http") else f"https://www.resmigazete.gov.tr/eskiler/{gun:%Y/%m}/{href}"
        kayitlar.append({
            "tarih": gun.isoformat(),
            "baslik": baslik,
            "tur": tur_bul(baslik),
            "degisiklik": bool(re.search(r"Değişiklik|Değiştiril|Değişik", baslik, flags=re.I)),
            "yururluk_kaldirma": bool(re.search(r"Yürürlükten\s+Kaldır", baslik, flags=re.I)),
            "anahtar_kelimeler": ", ".join(anahtarlar),
            "baglanti": url.replace("eskiler/", "eskiler/") if "eskiler" in url else url,
        })
    return kayitlar


def main(baslangic: date, bitis: date, onbellek: Path, cikti: Path, is_parcacigi: int) -> None:
    onbellek.mkdir(parents=True, exist_ok=True)
    gunler = []
    g = baslangic
    while g <= bitis:
        gunler.append(g)
        g += timedelta(days=1)
    sonuc: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=is_parcacigi) as havuz:
        for i, kayitlar in enumerate(havuz.map(lambda gun: gun_kayitlari(gun, onbellek), gunler), start=1):
            sonuc.extend(kayitlar)
            if i % 250 == 0:
                print(f"{i}/{len(gunler)} gün, {len(sonuc)} kayıt", flush=True)
    df = pd.DataFrame(sonuc).drop_duplicates(subset=["tarih", "baslik"]).sort_values(["tarih", "baslik"])
    cikti.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cikti, index=False, encoding="utf-8-sig")
    print(f"Yazıldı: {cikti} ({len(df)} kayıt)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslangic", default="2019-01-01")
    ap.add_argument("--bitis", default=date.today().isoformat())
    ap.add_argument("--onbellek", default="/tmp/claude-0/resmigazete-onbellek")
    ap.add_argument("--cikti", default=str(DATA_DIR / "mevzuat_resmi_gazete.csv"))
    ap.add_argument("--is", type=int, default=6, dest="is_parcacigi")
    a = ap.parse_args()
    main(date.fromisoformat(a.baslangic), date.fromisoformat(a.bitis), Path(a.onbellek), Path(a.cikti), a.is_parcacigi)
