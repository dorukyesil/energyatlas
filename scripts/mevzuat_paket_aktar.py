"""enerji-mevzuat-takip paketinin veritabanını portal verisine (data/mevzuat_belgeler.csv) aktarır.

Önkoşul: paket kurulu olmalı (karahanOS/enerji-mevzuat-takip). Çalıştırma, paketin Python'u ile yapılır:

    ENERJI_TAKIP_HOME=<veri dizini> <paket>/.venv/bin/python scripts/mevzuat_paket_aktar.py

Paket, Resmî Gazete ve kurum duyurularını kendisi tarayıp veritabanına yazar (`guncelle`). Bu betik yalnızca
o veritabanını okuyup CSV üretir; kendisi ağa çıkmaz.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import DATA_DIR  # noqa: E402

TUR_ADLARI = {
    "KANUN": "Kanun",
    "CB_KARARI": "Cumhurbaşkanlığı kararı",
    "YONETMELIK": "Yönetmelik",
    "TEBLIG": "Tebliğ",
    "KURUL_KARARI": "Kurul kararı",
    "AYM_KARARI": "Anayasa Mahkemesi kararı",
    "YARGI_KARARI": "Yargı kararı",
    "ANDLASMA": "Uluslararası anlaşma",
    "DUYURU": "Kurum duyurusu",
    "ILAN": "İlan",
    "ATAMA": "Atama",
}
DEGISIKLIK = re.compile(r"Değişiklik|Değiştir|Değişik", re.IGNORECASE)


def aktar(cikti: Path) -> int:
    from enerji_takip.db import init_db, session_scope
    from enerji_takip.models import RegulatoryChange, RegulatoryDocument

    init_db()
    satirlar = []
    with session_scope() as s:
        degisiklik_by_doc: dict[str, RegulatoryChange] = {}
        for c in s.query(RegulatoryChange).all():
            degisiklik_by_doc[c.document_id] = c
        for d in s.query(RegulatoryDocument).all():
            tarih = d.published_date or d.rg_date
            if tarih is None or d.relevance not in ("alakali", "baslangic"):
                continue
            c = degisiklik_by_doc.get(d.id)
            kategoriler = list(c.categories) if c and c.categories else list(d.matched_categories or [])
            anahtarlar = list(d.matched_keywords or [])
            satirlar.append({
                "tarih": tarih.isoformat(),
                "baslik": d.title,
                "tur": TUR_ADLARI.get(d.doc_type, d.doc_type),
                "degisiklik": bool(DEGISIKLIK.search(d.title or "")),
                "yururluk_kaldirma": bool(re.search(r"Yürürlükten\s+Kaldır", d.title or "", re.IGNORECASE)),
                "anahtar_kelimeler": ", ".join(sorted(set(kategoriler + anahtarlar))),
                "baglanti": d.url,
                "kurum": d.institution or "",
                "kaynak": d.source.name if d.source else "",
                "resmi_gazete_no": d.rg_number or "",
                "onem": c.importance if c and c.importance else "",
                "yururluk_tarihi": c.effective_date.isoformat() if c and c.effective_date else "",
                "yururluk_durumu": c.effective_date_status if c else "",
                "alaka": d.relevance,
            })
    satirlar.sort(key=lambda r: (r["tarih"], r["baslik"]), reverse=True)
    cikti.parent.mkdir(parents=True, exist_ok=True)
    with cikti.open("w", encoding="utf-8-sig", newline="") as f:
        yazar = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()) if satirlar else ["tarih"])
        yazar.writeheader()
        yazar.writerows(satirlar)
    return len(satirlar)


if __name__ == "__main__":
    n = aktar(DATA_DIR / "mevzuat_belgeler.csv")
    print(f"mevzuat_belgeler.csv yazıldı: {n} kayıt")
