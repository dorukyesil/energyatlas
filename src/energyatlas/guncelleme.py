"""Veri güncelleme kaydı.

Son güncelleme zamanını ve her veri kaynağının durumunu data/guncelleme.json dosyasında tutar.
Otomatik çekiciler (TEİAŞ, EPİAŞ, EPDK) eklendikçe KAYNAKLAR listesine bağlanır.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR

KAYIT_DOSYASI = DATA_DIR / "guncelleme.json"

# Her kaynak: ad, durum ("elle" = sunum görsellerinden girildi, "otomatik" = çekici var).
KAYNAKLAR = [
    {"ad": "TEİAŞ (kurulu güç, üretim, tüketim, iletim)", "durum": "elle"},
    {"ad": "EPİAŞ (PTF, YEKDEM)", "durum": "elle"},
    {"ad": "EPDK (tarifeler, ön lisanslar, depolama)", "durum": "elle"},
    {"ad": "IEA ve küresel veriler", "durum": "elle"},
]


def oku() -> dict:
    """Kayıt dosyasını okur. Dosya yoksa boş kayıt döner."""
    try:
        return json.loads(KAYIT_DOSYASI.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"son_guncelleme": None, "kaynaklar": KAYNAKLAR}


def guncelle() -> dict:
    """Veri güncelleme işaretini şu anki zamanla kaydeder ve kaydı döndürür."""
    kayit = oku()
    kayit["son_guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    kayit["kaynaklar"] = KAYNAKLAR
    KAYIT_DOSYASI.write_text(json.dumps(kayit, ensure_ascii=False, indent=2), encoding="utf-8")
    return kayit


def son_guncelleme_metni() -> str:
    kayit = oku()
    return kayit.get("son_guncelleme") or "Henüz güncellenmedi"
