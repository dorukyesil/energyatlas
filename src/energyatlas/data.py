"""Veri okuma katmanı.

TEİAŞ verileri scripts/teias_cek.py ile resmi TEİAŞ tablolarından (turkiye-energy-mcp) çekilir.
EPDK, IEA WEO ve IEA yatırım verileri kullanıcının sağladığı kaynak dosyalardan içe aktarılır
(scripts/import_kaynak_verileri.py). Hiçbir veri görsellerden okunmaz.
"""

import json
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


# ---- TEİAŞ (turkiye-energy-mcp) ----

def teias_kurulu_guc() -> pd.DataFrame:
    """Yıllık kurulu güç, GW ve pay (%).

    Portal tanımı: biyokütle ve atık ısı YENİLENEBİLİR sayılır. TEİAŞ'in 'termik' toplamından bu iki kalem çıkarılır.
    """
    d = load_dataset("teias_kurulu_guc")
    out = pd.DataFrame({"yil": d["yil"], "donem": d["yil"].astype(str)})
    out["toplam_gw"] = d["total"] / 1000
    out["atik_biyokutle_gw"] = d["waste_and_biomass"] / 1000
    out["termik_gw"] = (d["thermal"] - d["waste_and_biomass"]) / 1000
    out["hidro_gw"] = d["hydro"] / 1000
    out["jeotermal_gw"] = d["geothermal"] / 1000
    out["ruzgar_gw"] = d["wind"] / 1000
    out["gunes_gw"] = d["solar"] / 1000
    out["tas_komuru_gw"] = d["hard_coal"] / 1000
    out["linyit_gw"] = d["lignite"] / 1000
    out["dogalgaz_gw"] = d["natural_gas"] / 1000
    out["sivi_yakit_gw"] = d["liquid_fuels"] / 1000
    out["coklu_yakit_gw"] = d["multi_fuel_total"] / 1000
    out["diger_ye_gw"] = out["hidro_gw"] + out["jeotermal_gw"]
    out["yenilenebilir_gw"] = out[["hidro_gw", "jeotermal_gw", "ruzgar_gw", "gunes_gw", "atik_biyokutle_gw"]].sum(axis=1)
    for kolon, ad in [("termik", "termik"), ("gunes", "gunes"), ("ruzgar", "ruzgar"), ("diger_ye", "diger_ye"), ("yenilenebilir", "yenilenebilir")]:
        out[f"{ad}_pct"] = out[f"{kolon}_gw"] / out["toplam_gw"] * 100
    out["hidro_pct"] = out["hidro_gw"] / out["toplam_gw"] * 100
    out["jeotermal_pct"] = out["jeotermal_gw"] / out["toplam_gw"] * 100
    return out


def teias_uretim() -> pd.DataFrame:
    """Yıllık brüt elektrik üretimi, TWh ve pay (%). Rüzgar ve jeotermal TEİAŞ tablosunda birleşiktir.

    Portal tanımı: biyokütle ve atık ısı yenilenebilirdir; 'termik_twh' bu iki kalemi içermez.
    """
    d = load_dataset("teias_uretim")
    out = pd.DataFrame({"yil": d["yil"], "donem": d["yil"].astype(str)})
    out["toplam_twh"] = d["total"] / 1000
    out["atik_biyokutle_twh"] = d["waste_and_biomass"] / 1000
    out["termik_twh"] = (d["thermal"] - d["waste_and_biomass"]) / 1000
    out["hidro_twh"] = d["hydro"] / 1000
    out["ruzgar_jeotermal_twh"] = d["geothermal_and_wind"] / 1000
    out["gunes_twh"] = d["solar"] / 1000
    out["yenilenebilir_twh"] = out[["hidro_twh", "ruzgar_jeotermal_twh", "gunes_twh", "atik_biyokutle_twh"]].sum(axis=1)
    out["dogalgaz_twh"] = d["natural_gas"] / 1000
    out["linyit_twh"] = d["lignite"] / 1000
    out["ithal_komur_twh"] = d["imported_coal"] / 1000
    out["tas_komuru_twh"] = d["hard_coal_and_asphaltite"] / 1000
    for k in ["termik", "hidro", "ruzgar_jeotermal", "gunes", "atik_biyokutle", "yenilenebilir"]:
        out[f"{k}_pct"] = out[f"{k}_twh"] / out["toplam_twh"] * 100
    return out


def teias_talep() -> pd.DataFrame:
    """Yıllık brüt talep (TWh), tepe talep (MW), ithalat ve ihracat (TWh)."""
    d = load_dataset("teias_talep")
    out = pd.DataFrame({"yil": d["yil"], "donem": d["yil"].astype(str)})
    out["brut_talep_twh"] = d["gross_demand_gwh"] / 1000
    out["tepe_talep_mw"] = d["instantaneous_peak_mw"]
    out["saatlik_tepe_mw"] = d["hourly_peak_mw"]
    out["ithalat_twh"] = d["imports_gwh"] / 1000
    out["ihracat_twh"] = d["exports_gwh"] / 1000
    out["net_ithalat_twh"] = d["net_import_gwh"] / 1000
    return out


ULKE_ADLARI = {
    "Bulgaria": "Bulgaristan", "Greece": "Yunanistan", "Georgia": "Gürcistan", "Azerbaijan": "Azerbaycan",
    "Iran": "İran", "Iraq": "Irak", "Syria": "Suriye", "Armenia": "Ermenistan",
}


def teias_dis_ticaret() -> pd.DataFrame:
    """Ülke bazında elektrik ithalatı ve ihracatı (TWh)."""
    d = load_dataset("teias_dis_ticaret")
    d["ulke"] = d["ulke"].map(lambda u: ULKE_ADLARI.get(u, u))
    d["twh"] = d["gwh"] / 1000
    return d


def teias_iletim() -> pd.DataFrame:
    """Yıllık iletim hattı (km) ve trafo istatistikleri."""
    d = load_dataset("teias_iletim")
    d["donem"] = d["yil"].astype(str)
    return d


def teias_yenilenebilir() -> pd.DataFrame:
    """Yenilenebilir kurulu güç ve üretim. Portal tanımına göre biyokütle ve atık ısı eklenir."""
    d = load_dataset("teias_yenilenebilir")
    d["donem"] = d["yil"].astype(str)
    kurulu = load_dataset("teias_kurulu_guc")[["yil", "waste_and_biomass"]]
    uretim = load_dataset("teias_uretim")[["yil", "waste_and_biomass"]]
    d = d.merge(kurulu, on="yil", how="left").merge(uretim, on="yil", how="left", suffixes=("", "_uretim"))
    d["yenilenebilir_gw"] = (d["renewable_capacity_mw"] + d["waste_and_biomass"].fillna(0)) / 1000
    d["yenilenebilir_uretim_twh"] = (d["renewable_generation_gwh"] + d["waste_and_biomass_uretim"].fillna(0)) / 1000
    return d


def teias_aylik() -> pd.DataFrame:
    """Aylık üretim, ithalat, ihracat ve brüt talep (GWh), 2021'den itibaren."""
    d = load_dataset("teias_aylik")
    d["yil"] = d["ay"].str[:4].astype(int)
    d["ay_no"] = d["ay"].str[5:].astype(int)
    return d


YTBS_GRUPLARI = {
    "akarsu": "Hidro", "barajli": "Hidro",
    "asfaltitkomur": "Termik", "taskomur": "Termik", "ithalkomur": "Termik", "linyit": "Termik",
    "dogalgaz": "Termik", "lng": "Termik", "fueloil": "Termik", "motorin": "Termik", "nafta": "Termik",
    "lpg": "Termik", "biyokutle": "Biyokütle ve atık", "atikisi": "Biyokütle ve atık",
    "jeotermal": "Jeotermal", "ruzgar": "Rüzgar", "gunes": "Güneş",
}


def teias_ytbs() -> pd.DataFrame:
    """Güncel kurulu güç (YTBS, en son gün). Kaynak grupları TEİAŞ yıllık tablosundaki sınıflamaya uyarlanmıştır."""
    d = load_dataset("teias_ytbs_kurulu_guc")
    d["grup"] = d["kaynak"].map(YTBS_GRUPLARI).fillna("Diğer")
    d["kurulu_guc_gw"] = d["kurulu_guc_mw"] / 1000
    return d


def teias_kaynak() -> dict:
    """Her TEİAŞ veri setinin kaynak URL'si, dosya adı ve yayın tarihi."""
    yol = Path(DATA_DIR) / "teias_kaynak.json"
    try:
        return json.loads(yol.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def yillik_degisim(df: pd.DataFrame, deger: str) -> pd.DataFrame:
    """Bir önceki yıla göre yüzde değişim (degisim_pct). Yalnızca tam yıllar kullanılır (9A, H1 hariç)."""
    d = df.copy()
    if "yil" not in d.columns:
        d = d[d["donem"].astype(str).str.fullmatch(r"\d{4}")].copy()
        d["yil"] = d["donem"].astype(str).astype(int)
    d = d.sort_values("yil").copy()
    d["degisim_pct"] = d[deger].pct_change() * 100
    d["donem"] = d["yil"].astype(str)
    return d.dropna(subset=["degisim_pct"]).reset_index(drop=True)


# ---- EPDK (kullanıcının sağladığı lisans listeleri) ----

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


# ---- IEA (kullanıcının sağladığı WEO 2026 ve Dünya Enerji Yatırımları 2025 dosyaları) ----

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


# ---- Eski yükleyiciler (geriye dönük uyumluluk) ----


def kurulu_guc() -> pd.DataFrame:
    """Kurulu güç payları (%). Termik payı biyokütle ve atık hariç (fosil) değerdir; yenilenebilir = 100 - termik."""
    return load_dataset("kurulu_guc")


def uretim() -> pd.DataFrame:
    """Üretim payları (%). Termik payı biyokütle ve atık hariç (fosil) değerdir; yenilenebilir = 100 - termik."""
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


def ptf_gunluk() -> pd.DataFrame:
    """EPİAŞ saatlik PTF'den türetilmiş günlük özet (TL, USD, EUR/MWh; ortalama, en düşük, en yüksek)."""
    d = load_dataset("ptf_gunluk")
    d["tarih"] = pd.to_datetime(d["tarih"])
    return d


def ptf_profil() -> pd.DataFrame:
    """Yıl, ay ve saat bazında PTF ortalaması (TL ve USD/MWh)."""
    return load_dataset("ptf_profil")


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


def tam_yillar(df: pd.DataFrame) -> pd.DataFrame:
    """Dönem sütunu tam yıl olan satırları (9A ve H1 hariç) döndürür."""
    return df[df["donem"].astype(str).str.fullmatch(r"\d{4}")].reset_index(drop=True)


def weo_dunya() -> pd.DataFrame:
    """IEA WEO 2026 dünya verisi: kapasite (GW) ve üretim (TWh), senaryo ve yıl bazında."""
    return load_dataset("weo_dunya")


TR_KARAKTER = str.maketrans("çğıöşüÇĞİÖŞÜâîû", "cgiosuCGIOSUaiu")
IL_TAKMA_AD = {"afyonkarahisar": "afyon"}


def il_anahtari(ad: str) -> str:
    """Türkçe il adını harita anahtarına çevirir (ör. 'Kırklareli' -> 'kirklareli', 'Afyonkarahisar' -> 'afyon')."""
    k = str(ad).translate(TR_KARAKTER).lower().strip().replace(" ", "").replace(".", "")
    return IL_TAKMA_AD.get(k, k)


def tr_il_geojson() -> dict:
    """81 il sınırı (ad_key özelliği ile). Kaynak: cihadturhan/tr-geojson."""
    import json

    with (Path(DATA_DIR) / "tr_iller.geojson").open(encoding="utf-8") as f:
        return json.load(f)


def hedef_2040() -> pd.DataFrame:
    """Milli Enerji 2040 açıklanan hedefleri (ETKB lansmanı; bilgi notu)."""
    return load_dataset("hedef_2040")


def lisanssiz_kurulu_guc() -> pd.DataFrame:
    """Lisanssız kurulu güç (GW): 2016-2026/09 sunum grafiği, son nokta TEİAŞ YTBS güncel değeri."""
    return load_dataset("lisanssiz_kurulu_guc")
