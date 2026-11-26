"""Bölgesel karşılaştırma (IEA WEO 2026): seçilen gösterge ve yıla göre bölgeler."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Bölgesel karşılaştırma",
    "IEA WEO 2026. Bölgeleri aynı gösterge ve yılda karşılaştırın. Bölgeler birbirini kapsayabilir (ör. Kuzey Amerika ve ABD).",
)

gostergeler = {
    "Toplam enerji arzı (EJ)": ("Energy", "Total energy supply", "Total"),
    "Elektrik üretimi (TWh)": ("Energy", "Electricity generation", "Total"),
    "Güneş PV üretimi (TWh)": ("Energy", "Electricity generation", "Solar PV"),
    "Rüzgar üretimi (TWh)": ("Energy", "Electricity generation", "Wind"),
    "Yenilenebilir elektrik (TWh)": ("Energy", "Electricity generation", "Renewables"),
    "CO2 emisyonu (Mt CO2)": ("CO2 total", "Total energy supply", "Total"),
}
gosterge = st.selectbox("Gösterge", list(gostergeler.keys()), key="bolge_gosterge")
senaryo = ui.segment(data.WEO_SENARYOLAR, "bolge_senaryo")
yil = st.segmented_control("Yıl", [2025, 2035, 2040, 2050], default=2035, key="bolge_yil") or 2035

kategori, akis, urun = gostergeler[gosterge]
df = data.weo_tum()
secim = df[
    (df.kategori == kategori) & (df.akis == akis) & (df.urun == urun)
    & (df.yil == yil) & (df.senaryo.isin(["Gerçekleşen", senaryo]))
]
secim = secim[secim.kapsam != "Dünya"].copy()
secim["bolge"] = secim["kapsam"].map(data.weo_etiket)
secim = secim.sort_values("deger", ascending=False)
dunya = df[(df.kapsam == "Dünya") & (df.kategori == kategori) & (df.akis == akis) & (df.urun == urun) & (df.yil == yil) & (df.senaryo.isin(["Gerçekleşen", senaryo]))]

if secim.empty:
    st.info("Bu gösterge ve yıl için bölgesel veri yok.")
else:
    birim = secim["birim"].iloc[0]
    c1, c2 = st.columns(2)
    c1.metric(f"Dünya ({yil})", f"{ui.sayi(dunya['deger'].iloc[0], 0)} {birim}" if not dunya.empty else "-")
    c2.metric("En büyük bölge", secim.iloc[0]["bolge"], f"{ui.sayi(secim.iloc[0]['deger'], 0)} {birim}", delta_color="off")

    ui.bolum("01", "Bölgelere göre", f"{gosterge}, {yil}, {senaryo.lower()}.")
    st.plotly_chart(charts.yatay_deger_cubuk(secim, "bolge", "deger", f"{gosterge}: bölgeler ({yil})", birim), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A. Bölgeler birbirini kapsayabilir; toplamları dünya ile karıştırmayın.")

    ui.bolum("02", "Zaman içinde bölgeler", "Seçilen göstergede en büyük beş bölgenin yıllara göre seyri.")
    ilk5 = secim.head(5)["kapsam"].tolist()
    zaman = df[(df.kapsam.isin(ilk5)) & (df.kategori == kategori) & (df.akis == akis) & (df.urun == urun) & (df.senaryo.isin(["Gerçekleşen", senaryo]))]
    zaman = zaman.assign(bolge=zaman["kapsam"].map(data.weo_etiket))
    st.plotly_chart(charts.cizgi_coklu(zaman, "yil", "bolge", "deger", f"{gosterge}: en büyük 5 bölge", birim), use_container_width=True)

ui.veri_tablosu(df[df.kapsam != "Dünya"], "Veri tablosu (bölgeler)", "weo_2026.csv")
