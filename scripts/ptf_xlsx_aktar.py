"""EPİAŞ saatlik PTF dosyalarını (Piyasa_Takas_Fiyati-*.xlsx) portal verisine çevirir.

Ham saatlik veri depoya konmaz. Betik iki türetilmiş dosya yazar:
  data/ptf_gunluk.csv  : günlük ortalama, en düşük ve en yüksek (TL, USD, EUR/MWh)
  data/ptf_profil.csv  : yıl, ay ve saat bazında ortalama (TL, USD/MWh)

Kullanım:
    python scripts/ptf_xlsx_aktar.py <xlsx klasörü>

Yinelenen saatler (yıl sınırındaki dosyalarda) tekrar sayılmadan atılır.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from config import DATA_DIR

SUTUNLAR = ["tarih", "saat", "tl", "usd", "eur"]


def oku(klasor: Path) -> pd.DataFrame:
    parcalar = []
    for dosya in sorted(klasor.glob("Piyasa_Takas_Fiyati-*.xlsx")):
        d = pd.read_excel(dosya, engine="openpyxl")
        d.columns = SUTUNLAR
        parcalar.append(d)
    if not parcalar:
        raise SystemExit(f"Dosya bulunamadı: {klasor}")
    df = pd.concat(parcalar, ignore_index=True)
    df["tarih"] = pd.to_datetime(df["tarih"])
    df = df.drop_duplicates(subset=["tarih", "saat"]).sort_values("tarih").reset_index(drop=True)
    return df


def gunluk(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(df["tarih"].dt.normalize())
    out = pd.DataFrame({
        "tarih": g.size().index,
        "saat_sayisi": g.size().values,
        "tl_ort": g["tl"].mean().values,
        "usd_ort": g["usd"].mean().values,
        "eur_ort": g["eur"].mean().values,
        "usd_min": g["usd"].min().values,
        "usd_max": g["usd"].max().values,
        "tl_min": g["tl"].min().values,
        "tl_max": g["tl"].max().values,
    })
    return out.round(2)


def profil(df: pd.DataFrame) -> pd.DataFrame:
    d = df.assign(yil=df["tarih"].dt.year, ay=df["tarih"].dt.month, saat=df["tarih"].dt.hour)
    p = d.groupby(["yil", "ay", "saat"], as_index=False).agg(tl_ort=("tl", "mean"), usd_ort=("usd", "mean"))
    return p.round(2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("klasor", type=Path)
    ap.add_argument("--cikti", type=Path, default=DATA_DIR)
    a = ap.parse_args()
    df = oku(a.klasor)
    g = gunluk(df)
    p = profil(df)
    a.cikti.mkdir(parents=True, exist_ok=True)
    g.to_csv(a.cikti / "ptf_gunluk.csv", index=False, encoding="utf-8-sig")
    p.to_csv(a.cikti / "ptf_profil.csv", index=False, encoding="utf-8-sig")
    print(f"Saat: {len(df)}, gün: {len(g)}, profil satırı: {len(p)}")


if __name__ == "__main__":
    main()
