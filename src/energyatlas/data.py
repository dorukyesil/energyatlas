"""Veri okuma katmanı.

Veri kaynağı değiştiğinde (CSV -> API, veritabanı vb.) yalnızca bu dosya değişir.
Arayüz ve grafik kodu veriyi buradan alır.
"""

from pathlib import Path

import pandas as pd

from config import DATA_DIR


def load_dataset(name: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """data/<name>.csv dosyasını DataFrame olarak okur."""
    path = Path(data_dir) / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
    return pd.read_csv(path)


def kurulu_guc() -> pd.DataFrame:
    return load_dataset("kurulu_guc")


def uretim() -> pd.DataFrame:
    return load_dataset("uretim")


def tuketim() -> pd.DataFrame:
    return load_dataset("tuketim")


def kisi_basina() -> pd.DataFrame:
    return load_dataset("kisi_basina")


def hedefler() -> pd.DataFrame:
    return load_dataset("hedefler")


def devam_eden_yatirim() -> pd.DataFrame:
    return load_dataset("devam_eden_yatirim")


def depolama_kapasite() -> pd.DataFrame:
    return load_dataset("depolama_kapasite")


def depolama_sirketler() -> pd.DataFrame:
    return load_dataset("depolama_sirketler")


def iletim() -> pd.DataFrame:
    return load_dataset("iletim")


def baglantilar() -> pd.DataFrame:
    return load_dataset("baglantilar")


def depolama_on_lisans() -> pd.DataFrame:
    return load_dataset("depolama_on_lisans")


def isletmedeki_depolama() -> pd.DataFrame:
    return load_dataset("isletmedeki_depolama")


def tarife() -> pd.DataFrame:
    return load_dataset("tarife")


def ptf() -> pd.DataFrame:
    return load_dataset("ptf")
