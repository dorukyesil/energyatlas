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


def yekdem_fiyat() -> pd.DataFrame:
    return load_dataset("yekdem_fiyat")


def yekdem_formul() -> pd.DataFrame:
    return load_dataset("yekdem_formul")


def yekdem_yerli_katki() -> pd.DataFrame:
    return load_dataset("yekdem_yerli_katki")


def yekdem_duyuru() -> pd.DataFrame:
    return load_dataset("yekdem_duyuru")


def dunya_kurulu_guc() -> pd.DataFrame:
    return load_dataset("dunya_kurulu_guc")


def dunya_gunes_payi() -> pd.DataFrame:
    return load_dataset("dunya_gunes_payi")


def ulke_gunes_2024() -> pd.DataFrame:
    return load_dataset("ulke_gunes_2024")


def kuresel_yatirim() -> pd.DataFrame:
    return load_dataset("kuresel_yatirim")


def gunes_yatirim_bolge() -> pd.DataFrame:
    return load_dataset("gunes_yatirim_bolge")


def yillik_degisim(df: pd.DataFrame, deger: str) -> pd.DataFrame:
    """Yalnızca tam yıl satırlarını alıp bir önceki yıla göre yüzde değişimi ekler (degisim_pct)."""
    yillik = df[df["donem"].astype(str).str.fullmatch(r"\d{4}")].copy()
    yillik["degisim_pct"] = yillik[deger].pct_change() * 100
    return yillik.dropna(subset=["degisim_pct"]).reset_index(drop=True)


def tam_yillar(df: pd.DataFrame) -> pd.DataFrame:
    """Dönem sütunu tam yıl olan satırları (9A ve H1 hariç) döndürür."""
    return df[df["donem"].astype(str).str.fullmatch(r"\d{4}")].reset_index(drop=True)
