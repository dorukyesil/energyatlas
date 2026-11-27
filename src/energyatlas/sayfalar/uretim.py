"""Üretim: kaynak ve dönem seçilerek incelenir (TEİAŞ yıllık ve aylık tabloları).

Portal tanımı: biyokütle ve atık ısı yenilenebilirdir; termik bu iki kalemi içermez.
2026 dönemleri Ocak'tan seçilen aya kadar birikimli (kümülatif) toplamlardır.
"""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

# Kaynak adı -> TWh kolonu. Kurulu güç sayfasıyla aynı kırılım.
KAYNAKLAR = {
    "Doğal gaz": "dogalgaz_twh",
    "Linyit": "linyit_twh",
    "İthal ve taş kömür": "ithal_tas_twh",
    "Diğer termik": "diger_termik_twh",
    "Biyokütle ve atık ısı": "atik_biyokutle_twh",
    "Jeotermal": "jeotermal_twh",
    "Hidro": "hidro_twh",
    "Güneş": "gunes_twh",
    "Rüzgar": "ruzgar_twh",
    "Termik (toplam)": "termik_twh",
    "Yenilenebilir (toplam)": "yenilenebilir_twh",
    "Toplam": "toplam_twh",
}
TOPLAMLAR = ("Termik (toplam)", "Yenilenebilir (toplam)", "Toplam")
KOLONLAR = list(dict.fromkeys(KAYNAKLAR.values()))
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def _yillik() -> pd.DataFrame:
    """Yıllık üretim (TWh). Rüzgar ve jeotermal yıllık tabloda birleşik olduğundan, 2021'den itibaren aylık toplamlardan ayrılır."""
    y = data.teias_uretim().copy()
    a = data.teias_aylik()
    ayrik = a.groupby("yil")[["wind", "geothermal"]].sum() / 1000
    y["ruzgar_twh"] = y["yil"].map(ayrik["wind"])
    y["jeotermal_twh"] = y["yil"].map(ayrik["geothermal"])
    y["ithal_tas_twh"] = y["ithal_komur_twh"] + y["tas_komuru_twh"]
    y["diger_termik_twh"] = y["termik_twh"] - y["dogalgaz_twh"] - y["linyit_twh"] - y["ithal_tas_twh"]
    return y


def _kumulatif_2026() -> pd.DataFrame:
    """2026 için Ocak'tan seçilen aya kadar birikimli toplamlar (TWh)."""
    a = data.teias_aylik()
    s = a[a["yil"] == 2026].sort_values("ay_no").copy()
    aylik = pd.DataFrame({
        "ay_no": s["ay_no"].values,
        "dogalgaz_twh": s["natural_gas"].values / 1000,
        "linyit_twh": s["lignite"].values / 1000,
        "ithal_tas_twh": s["coal_imported_and_hard"].values / 1000,
        "atik_biyokutle_twh": s["waste_and_biomass"].values / 1000,
        "hidro_twh": s["hydro"].values / 1000,
        "jeotermal_twh": s["geothermal"].values / 1000,
        "ruzgar_twh": s["wind"].values / 1000,
        "gunes_twh": s["solar"].values / 1000,
        "toplam_twh": s["total_generation"].values / 1000,
    })
    aylik["termik_twh"] = (s["thermal"].values - s["waste_and_biomass"].values) / 1000
    aylik["diger_termik_twh"] = aylik["termik_twh"] - aylik["dogalgaz_twh"] - aylik["linyit_twh"] - aylik["ithal_tas_twh"]
    aylik["yenilenebilir_twh"] = aylik[["hidro_twh", "jeotermal_twh", "ruzgar_twh", "gunes_twh", "atik_biyokutle_twh"]].sum(axis=1)

    kumulatif = aylik.copy()
    kumulatif[KOLONLAR] = aylik[KOLONLAR].cumsum()
    kumulatif["donem"] = [
        "2026 Ocak" if k == 1 else f"2026 Ocak–{AYLAR[k - 1]}"
        for k in kumulatif["ay_no"]
    ]
    return kumulatif


def _tablo() -> pd.DataFrame:
    tum = pd.concat([_yillik(), _kumulatif_2026()], ignore_index=True)
    for kol in KOLONLAR:
        tum[f"{kol}_pct"] = tum[kol] / tum["toplam_twh"] * 100
    return tum


def render() -> None:
    tum = _tablo()
    yillik = tum[~tum["donem"].str.startswith("2026")]
    donemler = tum["donem"].tolist()
    secenekler = list(KAYNAKLAR.keys())

    c1, c2 = st.columns([1, 2])
    with c1:
        kaynak = st.selectbox("Kaynak", secenekler, index=secenekler.index("Toplam"), key="uretim_kaynak")
    with c2:
        donem = st.select_slider("Dönem", options=donemler, value=donemler[-1], key="uretim_donem")

    kol = KAYNAKLAR[kaynak]
    pct_kol = f"{kol}_pct"
    secili = tum[tum["donem"] == donem].iloc[0]
    ilk = yillik[yillik["donem"] == "2016"].iloc[0]
    kumulatif_mi = donem.startswith("2026")
    twh = float(secili[kol])
    toplam = float(secili["toplam_twh"])

    k1, k2, k3 = st.columns(3)
    k1.metric(f"{kaynak} üretimi ({donem})", f"{ui.sayi(twh)} TWh")
    if kaynak == "Toplam":
        fark = None if kumulatif_mi else f"{toplam - float(ilk['toplam_twh']):+.1f} TWh (2016'ya göre)".replace(".", ",")
        k2.metric(f"Toplam üretim ({donem})", f"{ui.sayi(toplam)} TWh", fark, delta_color="off")
    else:
        pay = twh / toplam * 100
        fark = None
        if not kumulatif_mi and pd.notna(ilk[pct_kol]):
            fark = f"{pay - float(ilk[pct_kol]):+.1f} puan (2016'ya göre)".replace(".", ",")
        k2.metric(f"{kaynak} payı ({donem})", f"%{ui.sayi(pay)}", fark, delta_color="off")
    k3.metric("Dönem", donem)

    ui.bolum("01", f"{kaynak}: yıllık gelişim", "Yıllık üretim (sütun) ve toplam içindeki payı (çizgi). Rüzgar ve jeotermal 2021'den itibaren ayrı verilebilir.")
    yillik_kaynak = yillik.dropna(subset=[kol])
    st.plotly_chart(charts.toplam_cubuk(yillik_kaynak, kol, f"{kaynak} üretimi (TWh)", "TWh"), use_container_width=True)
    if kaynak != "Toplam":
        st.plotly_chart(charts.cizgi_alan(yillik.dropna(subset=[pct_kol]), "donem", pct_kol, f"{kaynak} payı (%)", "%", "%"),
                        use_container_width=True)

    ui.bolum("02", "2026 kümülatif üretim", "Ocak'tan seçilen aya kadar biriken üretim (TWh) ve payı.")
    kumu = tum[tum["donem"].str.startswith("2026")].dropna(subset=[kol])
    st.plotly_chart(charts.toplam_cubuk(kumu, kol, f"2026 kümülatif {kaynak} üretimi (TWh)", "TWh"), use_container_width=True)
    if kaynak != "Toplam":
        st.plotly_chart(charts.cizgi_alan(kumu, "donem", pct_kol, f"2026 kümülatif {kaynak} payı (%)", "%", "%"), use_container_width=True)
    ui.teias_notu("uretim", "aylik", ek="2026 değerleri birikimli toplamdır. Rüzgar ve jeotermal 2021 öncesinde yıllık tabloda birleşiktir.")

    ui.bolum("03", "Kaynaklara göre karşılaştırma", f"{donem} dönemi, tüm kaynaklar.")
    satirlar = [(ad, float(secili[KAYNAKLAR[ad]])) for ad in KAYNAKLAR if ad not in TOPLAMLAR]
    karsilastirma = pd.DataFrame(satirlar, columns=["kaynak", "twh"]).dropna()
    st.plotly_chart(charts.yatay_deger_cubuk(karsilastirma, "kaynak", "twh", f"Kaynaklara göre üretim, {donem} (TWh)", "TWh"),
                    use_container_width=True)

    ui.veri_tablosu(tum, "Veri tablosu (yıllık ve 2026 kümülatif)", "teias_uretim.csv")
