"""Kaynak dosyalarını portal veri CSV'lerine dönüştürür.

Kullanım:
    python scripts/import_kaynak_verileri.py <klasor>

<klasor> içinde şu dosyalar aranır:
  - *Lisanslar*.xls            (EPDK lisanslı üretim tesisleri)
  - *O_nlisanslar*.xls          (EPDK ön lisanslı üretim tesisleri)
  - *WEO2026_AnnexA_Free_Dataset_World.csv*   (IEA WEO dünya verisi)

Kişisel iletişim bilgileri (adres, telefon) çıktıya alınmaz.
"""

import sys
from pathlib import Path

import pandas as pd

from config import DATA_DIR

SUTUNLAR = {
    "Lisans Sahibi": "lisans_sahibi",
    "Lisans Durumu": "durum",
    "Lisans No": "lisans_no",
    "Başlangıç Tarihi": "baslangic",
    "Bitiş Tarihi": "bitis",
    "Tesis Adı": "tesis_adi",
    "İl": "il",
    "İlçe": "ilce",
    "Tesis Türü": "tesis_turu",
    "Kaynak Türü": "kaynak_turu",
    "Kurulu Güç (MWe)": "kurulu_mwe",
    "İşletmedeki Kapasite (MWe)": "isletmedeki_mwe",
    "Toplam Depolama Kapasitesi (MWh)": "depolama_mwh",
    "Toplam Depolama Kurulu Gücü (MWe)": "depolama_mwe",
    "İşletmedeki Depolama Kapasite (MWh)": "isletmedeki_depolama_mwh",
    "İşletmedeki Depolama Güç (MWe)": "isletmedeki_depolama_mwe",
}


def tr_baslik(metin: str) -> str:
    """Türkçe harflere uygun baş harf büyütme: 'TEKİRDAĞ' -> 'Tekirdağ', 'İZMİR' -> 'İzmir'."""
    if not isinstance(metin, str):
        return metin
    kucuk = metin.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(k[:1].replace("i", "İ").upper() + k[1:] if k[:1] != "i" else "İ" + k[1:] for k in kucuk.split(" "))


def epdk_duzeltmelerini_uygula(df: pd.DataFrame, tur: str) -> pd.DataFrame:
    """data/epdk_duzeltmeler.csv içindeki, kaynak dosyadaki hatalı değerleri belgeli düzeltmeleri uygular."""
    yol = DATA_DIR / "epdk_duzeltmeler.csv"
    if not yol.exists():
        return df
    duz = pd.read_csv(yol, dtype=str)
    for _, r in duz[duz["kaynak"] == tur].iterrows():
        maske = df["lisans_no"] == r["lisans_no"]
        if maske.any():
            df.loc[maske, r["alan"]] = float(r["yeni"])
            print(f"Düzeltme uygulandı: {r['lisans_no']} {r['alan']} {r['eski']} -> {r['yeni']}")
    return df


def epdk_tablosu(yol: Path, tur: str = "") -> pd.DataFrame:
    df = pd.read_excel(yol)
    df = df[list(SUTUNLAR.keys())].rename(columns=SUTUNLAR)
    for kolon in ["kurulu_mwe", "isletmedeki_mwe", "depolama_mwh", "depolama_mwe", "isletmedeki_depolama_mwh", "isletmedeki_depolama_mwe"]:
        df[kolon] = pd.to_numeric(df[kolon], errors="coerce").fillna(0.0)
    df["bitis"] = pd.to_datetime(df["bitis"], dayfirst=True, errors="coerce")
    df["il"] = df["il"].map(tr_baslik)
    df["ilce"] = df["ilce"].map(tr_baslik)
    return epdk_duzeltmelerini_uygula(df, tur)


def weo_dunya(yol: Path) -> pd.DataFrame:
    w = pd.read_csv(yol)
    secim = w[
        ((w["CATEGORY"] == "Capacity: installed") | ((w["CATEGORY"] == "Energy") & (w["FLOW"] == "Electricity generation")))
        & (w["PRODUCT"].isin(["Total", "Solar PV", "Wind", "Hydro", "Nuclear", "Natural gas: unabated", "Coal: unabated", "Renewables"]))
    ]
    secim = secim.assign(gosterge=secim["CATEGORY"].map({"Capacity: installed": "Kurulu güç (GW)", "Energy": "Elektrik üretimi (TWh)"}))
    return secim[["SCENARIO", "gosterge", "PRODUCT", "YEAR", "VALUE"]].rename(
        columns={"SCENARIO": "senaryo", "PRODUCT": "kaynak", "YEAR": "yil", "VALUE": "deger"}
    )


YATIRIM_SATIRLARI = {
    "Total Billion USD (2024, MER)": "Toplam",
    "of which: Clean energy": "Temiz enerji",
    "Fossil fuels": "Fosil yakıtlar",
    "Fuels": "Yakıtlar",
    "Generation": "Elektrik üretimi",
    "Renewables": "Yenilenebilir elektrik",
    "o/w solar": "Güneş",
    "o/w wind": "Rüzgar",
    "Nuclear": "Nükleer",
    "Battery storage": "Batarya depolama",
    "Electricity networks": "Elektrik şebekeleri",
    "Energy efficiency": "Enerji verimliliği",
}
YATIRIM_SAYFALARI = [
    "World", "Advanced economies", "EMDE", "China", "North America", "Central and South America",
    "Europe", "Africa", "Middle East", "Eurasia", "Asia Pacific",
]
BOLGE_ADLARI = {"EMDE": "Gelişmekte olan ekonomiler (Çin dahil)", "Advanced economies": "İleri ekonomiler"}


def yatirim_tablosu(yol: Path) -> pd.DataFrame:
    """Dünya enerji yatırımları dosyasını bölge, kategori, yıl biçiminde uzun tabloya çevirir (milyar USD, 2024 MER)."""
    satirlar = []
    for sayfa in YATIRIM_SAYFALARI:
        d = pd.read_excel(yol, sheet_name=sayfa, header=None)
        yillar = d.iloc[1, 2:].tolist()
        bolge = BOLGE_ADLARI.get(sayfa, sayfa)
        etiketler = d.iloc[:, 1].tolist()
        for etiket, ad in YATIRIM_SATIRLARI.items():
            if etiket not in etiketler:
                continue
            satir = d.iloc[etiketler.index(etiket), 2:].tolist()
            for yil, deger in zip(yillar, satir):
                if pd.notna(yil) and pd.notna(deger):
                    satirlar.append({"bolge": bolge, "kategori": ad, "yil": int(yil), "deger": float(deger)})
    return pd.DataFrame(satirlar)


BOLGE_URUNLERI = {
    ("Energy", "Total energy supply"): ["Total", "Renewables", "Coal", "Natural gas", "Oil", "Nuclear", "Solar", "Wind", "Hydro"],
    ("Energy", "Electricity generation"): ["Total", "Renewables", "Coal", "Natural gas", "Nuclear", "Solar PV", "Wind"],
    ("Energy", "Total final consumption"): ["Total"],
    ("CO2 total", "Total energy supply"): ["Total"],
}


def weo_tum(dunya: Path, bolge: Path) -> pd.DataFrame:
    """IEA WEO 2026 dünya ve bölge verilerini tek uzun tabloda birleştirir.

    Sütunlar: kapsam, senaryo, kategori, akis, urun, birim, yil, deger.
    """
    from src.energyatlas.data import SENARYO_ADLARI

    d = pd.read_csv(dunya)
    d["kapsam"] = "Dünya"
    b = pd.read_csv(bolge)
    b = b[b.apply(lambda r: r["PRODUCT"] in BOLGE_URUNLERI.get((r["CATEGORY"], r["FLOW"]), []), axis=1)].copy()
    b["kapsam"] = b["REGION"]
    b = b[b["REGION"] != "World"]
    birlesik = pd.concat([d, b], ignore_index=True)
    birlesik = birlesik.rename(columns={"SCENARIO": "senaryo", "CATEGORY": "kategori", "FLOW": "akis",
                                       "PRODUCT": "urun", "UNIT": "birim", "YEAR": "yil", "VALUE": "deger"})
    birlesik["senaryo"] = birlesik["senaryo"].map(SENARYO_ADLARI).fillna(birlesik["senaryo"])
    birlesik = birlesik[["kapsam", "senaryo", "kategori", "akis", "urun", "birim", "yil", "deger"]]
    birlesik = birlesik[birlesik["deger"].notna()]
    birlesik["yil"] = birlesik["yil"].astype(int)
    return birlesik.sort_values(["kapsam", "senaryo", "kategori", "akis", "urun", "yil"]).reset_index(drop=True)


def main(klasor: Path) -> None:
    lisans = list(klasor.glob("*Lisanslar*.xls"))
    onlisans = list(klasor.glob("*O_nlisanslar*.xls"))
    weo = list(klasor.glob("*WEO2026_AnnexA_Free_Dataset_World.csv"))
    if lisans:
        epdk_tablosu(lisans[0], "lisans").to_csv(DATA_DIR / "epdk_lisans.csv", index=False, encoding="utf-8-sig")
        print("epdk_lisans.csv yazıldı")
    if onlisans:
        epdk_tablosu(onlisans[0], "onlisans").to_csv(DATA_DIR / "epdk_onlisans.csv", index=False, encoding="utf-8-sig")
        print("epdk_onlisans.csv yazıldı")
    yatirim = list(klasor.glob("*WorldEnergyInvestment*.xlsx"))
    if yatirim:
        yatirim_tablosu(yatirim[0]).to_csv(DATA_DIR / "yatirim_bolge.csv", index=False, encoding="utf-8-sig")
        print("yatirim_bolge.csv yazıldı")
    bolge = list(klasor.glob("*WEO2026_AnnexA_Free_Dataset_Regions.csv"))
    if weo and bolge:
        weo_tum(weo[0], bolge[0]).to_csv(DATA_DIR / "weo_2026.csv", index=False, encoding="utf-8-sig")
        print("weo_2026.csv yazıldı")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
