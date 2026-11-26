"""Veri okuma katmanı.

Veri kaynağı değiştiğinde (CSV -> API, veritabanı vb.) yalnızca bu dosya değişir.
Arayüz kodu veriyi buradan alır.
"""

from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    """Verilen CSV dosyasını DataFrame olarak okur."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
    return pd.read_csv(path, parse_dates=["tarih"])


def filter_by_year(df: pd.DataFrame, yil: int) -> pd.DataFrame:
    """Tarih sütununa göre belirli bir yılın kayıtlarını döndürür."""
    return df[df["tarih"].dt.year == yil].reset_index(drop=True)
