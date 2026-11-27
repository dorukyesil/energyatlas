"""PTF analizleri: yıllık, aylık, saatlik ve TL/USD kur hesapları.

Saf pandas; Streamlit'e ve grafik kütüphanesine bağımlı değildir (testlerden doğrudan çağrılabilir).
Girdi: data/ptf_gunluk.csv (gün bazında ortalama, en düşük, en yüksek) ve data/ptf_profil.csv
(yıl, ay, saat bazında ortalama).
"""

from __future__ import annotations

import pandas as pd

AYLAR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def yillik(g: pd.DataFrame) -> pd.DataFrame:
    """Yıl bazında ortalamalar. Her gün 24 saat olduğundan gün ortalamalarının ortalaması saat ortalamasına eşittir."""
    d = g.assign(yil=g["tarih"].dt.year)
    out = d.groupby("yil").agg(
        tl=("tl_ort", "mean"),
        usd=("usd_ort", "mean"),
        eur=("eur_ort", "mean"),
        gun=("tarih", "size"),
        usd_std=("usd_ort", "std"),
        usd_min=("usd_min", "min"),
        usd_max=("usd_max", "max"),
    ).reset_index()
    out["kur"] = out["tl"] / out["usd"]
    yil_gun = out["yil"].map(lambda y: pd.Timestamp(int(y), 12, 31).dayofyear)
    out["kismi"] = out["gun"] < yil_gun
    out["donem"] = out["yil"].astype(str)
    return out


def aylik(g: pd.DataFrame, para: str) -> pd.DataFrame:
    """Yıl ve ay bazında ortalama. para: 'tl' ya da 'usd'."""
    kolon = f"{para}_ort"
    d = g.assign(yil=g["tarih"].dt.year, ay=g["tarih"].dt.month)
    out = d.groupby(["yil", "ay"], as_index=False)[kolon].mean()
    out["ay_adi"] = out["ay"].map(lambda m: AYLAR[m - 1])
    out["yil"] = out["yil"].astype(str)
    return out.rename(columns={kolon: "deger"})


def profil_matrisi(p: pd.DataFrame, yil: int, para: str) -> pd.DataFrame:
    """Saat (satır) x ay (sütun) matrisi. Veri olmayan hücreler boş kalır."""
    kolon = f"{para}_ort"
    s = p[p["yil"] == yil]
    m = s.pivot_table(index="saat", columns="ay", values=kolon, aggfunc="mean")
    m = m.reindex(index=range(24), columns=range(1, 13))
    m.columns = [AYLAR[c - 1] for c in m.columns]
    return m


def saat_ozeti(p: pd.DataFrame, yil: int, para: str) -> dict:
    """Yılın saatlik ortalama profilinde en yüksek ve en düşük saat."""
    kolon = f"{para}_ort"
    s = p[p["yil"] == yil].groupby("saat")[kolon].mean()
    return {
        "en_yuksek_saat": int(s.idxmax()), "en_yuksek": float(s.max()),
        "en_dusuk_saat": int(s.idxmin()), "en_dusuk": float(s.min()),
    }


def cagr(baslangic_deger: float, bitis_deger: float, baslangic_yil: int, bitis_yil: int) -> float | None:
    """Bileşik yıllık büyüme oranı (%). Başlangıç değeri sıfır veya negatifse, ya da yıllar eşit/ters ise None."""
    n = bitis_yil - baslangic_yil
    if n <= 0 or baslangic_deger <= 0 or bitis_deger <= 0:
        return None
    return ((bitis_deger / baslangic_deger) ** (1 / n) - 1) * 100
