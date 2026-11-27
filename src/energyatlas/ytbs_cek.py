"""YTBS güncel kurulu güç verisini herkese açık veri deposundan çeker ve portal CSV'sine yazar.

Kaynak: github.com/emresoykan/turkiye-energy-mcp, dal 'ytbs-data', kurulu_guc/<yıl>/<yıl>-<ay>.csv.
Günlük kayıtlar kaynak bazında toplanır (kurulu_guc_mw toplamı; santral sayısı santral_sayisi veri setinden).
Ağ hatalarında istisna fırlatır; çağıran taraf kullanıcıya bildirir.
"""

from __future__ import annotations

import io
import urllib.request
from datetime import date

import pandas as pd

from config import DATA_DIR

KOK = "https://raw.githubusercontent.com/emresoykan/turkiye-energy-mcp/ytbs-data"
CSV_YOLU = DATA_DIR / "teias_ytbs_kurulu_guc.csv"


def _ay_dosyasi(yil: int, ay: int, veri: str = "kurulu_guc") -> pd.DataFrame:
    url = f"{KOK}/{veri}/{yil}/{yil}-{ay:02d}.csv"
    with urllib.request.urlopen(url, timeout=30) as r:
        return pd.read_csv(io.BytesIO(r.read()))


def son_gun_ozeti(ham: pd.DataFrame, santral: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """En güncel günü seçer ve kaynak bazında toplar. Döner: (tarih 'YYYY-MM-DD', özet tablo)."""
    ham = ham.assign(tarih=pd.to_datetime(ham["tarih"]).dt.strftime("%Y-%m-%d"))
    santral = santral.assign(tarih=pd.to_datetime(santral["tarih"]).dt.strftime("%Y-%m-%d"))
    son = ham["tarih"].max()
    gun = ham[ham["tarih"] == son].groupby("kaynak", as_index=False)["kurulu_guc_mw"].sum()
    sgun = santral[santral["tarih"] == son].groupby("kaynak", as_index=False)["santral_sayisi"].sum()
    ozet = gun.merge(sgun, on="kaynak", how="left").fillna({"santral_sayisi": 0})
    ozet["santral_sayisi"] = ozet["santral_sayisi"].round().astype(int)
    ozet.insert(0, "tarih", son)
    return son, ozet[["tarih", "kaynak", "kurulu_guc_mw", "santral_sayisi"]]


def guncelle_ytbs() -> dict:
    """Son iki ayın dosyasını çeker, en güncel günü yazar. Döner: {'tarih', 'toplam_gw', 'kaynak_sayisi'}."""
    bugun = date.today()
    onceki = pd.Timestamp(bugun.replace(day=1) - pd.Timedelta(days=1))
    aylar = [(onceki.year, onceki.month), (bugun.year, bugun.month)]
    ham = pd.concat([_ay_dosyasi(y, a) for y, a in aylar], ignore_index=True)
    santral = pd.concat([_ay_dosyasi(y, a, "santral_sayisi") for y, a in aylar], ignore_index=True)
    son, ozet = son_gun_ozeti(ham, santral)
    if ozet.empty or ozet["kurulu_guc_mw"].sum() <= 0:
        raise ValueError("Kaynaktan boş veri geldi; mevcut veri korunuyor.")
    ozet.to_csv(CSV_YOLU, index=False, encoding="utf-8-sig")
    return {"tarih": son, "toplam_gw": round(float(ozet["kurulu_guc_mw"].sum()) / 1000, 1), "kaynak_sayisi": len(ozet)}
