"""Ülkeler bazında güneş enerjisi kurulu gücü (GW)."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya ve karşılaştırma",
    "Ülke karşılaştırması: güneş kurulu gücü",
    "En büyük güneş kapasitesine sahip ülkeler, GW. Kaynak: IEA World Energy Outlook 2025, Renewables 2025 ve TEİAŞ.",
)

df = data.ulke_gunes_2024().sort_values("gunes_gw", ascending=False).reset_index(drop=True)
dunya_toplam = 2164
tr = df[df["ulke"] == "Türkiye"].iloc[0]
lider = df.iloc[0]
tr_sira = int(df.index[df["ulke"] == "Türkiye"][0]) + 1

c1, c2, c3 = st.columns(3)
c1.metric("Dünya güneş kurulu gücü (2024)", f"{ui.sayi(dunya_toplam, 0)} GW")
c2.metric("Türkiye", f"{ui.sayi(tr['gunes_gw'], 0)} GW", f"sıralama: {tr_sira}. / {len(df)}", delta_color="off")
c3.metric("Lider", f"{lider['ulke']}", f"{ui.sayi(lider['gunes_gw'], 0)} GW", delta_color="off")

ui.bolum("01", "Sıralama", "Türkiye kırmızıyla vurgulanmıştır.")
st.plotly_chart(charts.ulke_yatay_cubuk(df, "Ülkelere göre güneş kurulu gücü (GW)"), use_container_width=True)
ui.kaynak("Türkiye değeri 2025 yıl sonu itibarıyla TEİAŞ verisinden alınmıştır. Diğer ülkeler 2024 yılına aittir.")

st.info("Karşılaştırma tam olarak aynı yıl üzerinden yapılmamaktadır: Türkiye 2025, diğer ülkeler 2024.")
ui.veri_tablosu(df, "Veri tablosu", "ulke_gunes.csv")
