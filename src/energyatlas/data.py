"""Veri okuma katmanı.

Veri kaynağı değiştiğinde (CSV -> API, veritabanı vb.) yalnızca bu dosya değişir.
Arayüz ve grafik kodu veriyi buradan alır.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from config import DATA_DIR


@lru_cache(maxsize=64)
def _oku(name: str, data_dir: str) -> pd.DataFrame:
    path = Path(data_dir) / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
    return pd.read_csv(path)


def load_dataset(name: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """data/<name>.csv dosyasını DataFrame olarak okur."""
    return _oku(name, str(data_dir)).copy()


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


def _epdk_tarihli(ad: str) -> pd.DataFrame:
    df = load_dataset(ad)
    df["bitis"] = pd.to_datetime(df["bitis"], errors="coerce")
    df["baslangic"] = pd.to_datetime(df["baslangic"], errors="coerce")
    return df


def epdk_lisans() -> pd.DataFrame:
    """EPDK lisanslı üretim tesisleri (santral bazında)."""
    return _epdk_tarihli("epdk_lisans")


def epdk_onlisans() -> pd.DataFrame:
    """EPDK ön lisanslı üretim tesisleri (santral bazında)."""
    return _epdk_tarihli("epdk_onlisans")


def weo_dunya() -> pd.DataFrame:
    """IEA WEO 2026 dünya verisi: kapasite (GW) ve üretim (TWh), senaryo ve yıl bazında."""
    return load_dataset("weo_dunya")


SENARYO_ADLARI = {
    "Current Policies Scenario": "Mevcut politikalar",
    "Stated Policies Scenario": "Belirlenmiş politikalar",
    "Net Zero Emissions by 2050 Scenario": "Net sıfır (2050)",
    "Historical": "Gerçekleşen",
}


def yatirim_bolge() -> pd.DataFrame:
    """IEA Dünya Enerji Yatırımları 2025: bölge, kategori, yıl (milyar USD, 2024 MER)."""
    return load_dataset("yatirim_bolge")


# ---- IEA WEO 2026: dünya ve bölgesel veriler ----

WEO_SENARYOLAR = ["Mevcut politikalar", "Belirlenmiş politikalar", "Net sıfır (2050)"]

WEO_ETIKET = {
    # ürünler / kaynaklar
    "Total": "Toplam", "Coal": "Kömür", "Coal: unabated": "Kömür (önlemsiz)", "Coal: with CCUS": "Kömür (CCUS)",
    "Oil": "Petrol", "Natural gas": "Doğalgaz", "Natural gas: unabated": "Doğalgaz (önlemsiz)",
    "Natural gas: with CCUS": "Doğalgaz (CCUS)", "Nuclear": "Nükleer", "Hydro": "Hidroelektrik",
    "Solar": "Güneş", "Solar PV": "Güneş PV", "Wind": "Rüzgar", "Renewables": "Yenilenebilir",
    "Modern bioenergy: solid": "Modern biyoenerji (katı)", "Modern bioenergy: liquid": "Modern biyoenerji (sıvı)",
    "Modern bioenergy: gas": "Modern biyoenerji (gaz)", "Traditional use of biomass": "Geleneksel biyokütle",
    "Modern bioenergy and renewable waste": "Biyoenerji ve atık", "Geothermal": "Jeotermal", "Marine": "Deniz enerjisi",
    "Battery storage": "Batarya depolama", "Electricity": "Elektrik", "Hydrogen": "Hidrojen",
    "Biomethane": "Biyometan", "District heat": "Bölgesel ısı", "Total liquids": "Sıvı yakıtlar",
    "Total gases": "Gazlar", "Total solid fuels": "Katı yakıtlar", "Hydrogen: low-emissions": "Düşük emisyonlu hidrojen",
    "Bioenergy and waste": "Biyoenerji ve atık", "Oil: non-energy use": "Petrol (enerji dışı)",
    "Concentrating solar power": "Yoğunlaştırılmış güneş", "Hydrogen and H2-based fuels": "Hidrojen ve türevleri",
    "Electricity generation": "Elektrik üretimi", "Power sector inputs": "Elektrik sektörü",
    "Industry": "Sanayi", "Transport": "Ulaştırma", "Buildings": "Binalar", "Services": "Hizmetler",
    "Residential": "Konut", "Total energy supply": "Enerji arzı", "Total final consumption": "Son tüketim",
    "Electrical capacity": "Elektrik kapasitesi", "Gross domestic product": "GSYH", "GDP per capita": "Kişi başına GSYH",
    "Population": "Nüfus", "Chemicals": "Kimya", "Iron and steel": "Demir-çelik",
    "Non-ferrous metals: aluminium": "Alüminyum", "Non-metallic minerals: cement": "Çimento",
    "Direct air capture": "Doğrudan hava yakalama", "Biofuels production": "Biyoyakıt üretimi",
    "Biofuels production and direct air capture": "Biyoyakıt ve hava yakalama",
    "Hydrogen production: offsite": "Hidrojen üretimi (dış)", "Hydrogen-based fuels production inputs": "Hidrojen türev yakıt girdisi",
    "TES per GDP": "Birincil enerji / GSYH", "Total final consumption per GDP": "Son tüketim / GSYH",
    "Road freight trucks": "Kamyon", "Road passenger light duty vehicles": "Binek araç",
    # bölgeler
    "Africa": "Afrika", "Asia Pacific": "Asya Pasifik", "Brazil": "Brezilya", "Central and South America": "Orta ve Güney Amerika",
    "China": "Çin", "Eurasia": "Avrasya", "Europe": "Avrupa", "European Union": "Avrupa Birliği", "India": "Hindistan",
    "Japan": "Japonya", "Middle East": "Orta Doğu", "North America": "Kuzey Amerika", "Russia": "Rusya",
    "Southeast Asia": "Güneydoğu Asya", "United States": "ABD", "Dünya": "Dünya",
}


def weo_tum() -> pd.DataFrame:
    """WEO 2026 uzun tablo: kapsam, senaryo, kategori, akis, urun, birim, yil, deger."""
    df = load_dataset("weo_2026")
    df["senaryo"] = df["senaryo"].astype(str)
    return df


def weo_etiket(ad: str) -> str:
    return WEO_ETIKET.get(ad, ad)


def weo_seri(kategori: str, akis: str, urun: str, senaryo: str, kapsam: str = "Dünya") -> pd.DataFrame:
    """Gerçekleşen yıllar + seçilen senaryonun yılları. Sütunlar: yil, deger."""
    df = weo_tum()
    sec = df[(df.kapsam == kapsam) & (df.kategori == kategori) & (df.akis == akis) & (df.urun == urun)]
    sec = sec[sec.senaryo.isin(["Gerçekleşen", senaryo])]
    return sec.sort_values("yil")[["yil", "deger"]].drop_duplicates("yil").reset_index(drop=True)


def weo_coklu(kategori: str, akis: str, urunler: list[str], senaryo: str, kapsam: str = "Dünya") -> pd.DataFrame:
    """Birden çok ürün için uzun seri: yil, urun (Türkçe etiket), deger."""
    parcalar = []
    for u in urunler:
        s = weo_seri(kategori, akis, u, senaryo, kapsam)
        if not s.empty:
            s = s.assign(urun=weo_etiket(u))
            parcalar.append(s)
    return pd.concat(parcalar, ignore_index=True) if parcalar else pd.DataFrame(columns=["yil", "urun", "deger"])


def yenile() -> None:
    """Veri önbelleğini temizler; sonraki okumalar dosyaları yeniden okur."""
    _oku.cache_clear()
