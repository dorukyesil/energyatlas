"""Ülkeler bazında güneş enerjisi kurulu gücü (GW)."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Ülkeler Bazında Güneş Kurulu Gücü")
st.caption("En büyük güneş kapasitesine sahip ülkeler, GW. Kaynak: IEA World Energy Outlook 2025, Renewables 2025 ve TEİAŞ.")

df = data.ulke_gunes_2024().sort_values("gunes_gw", ascending=False).reset_index(drop=True)
dunya_toplam = 2164
tr = df[df["ulke"] == "Türkiye"].iloc[0]
lider = df.iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Dünya güneş kurulu gücü (2024)", f"{dunya_toplam:,} GW")
c2.metric("Türkiye", f"{tr['gunes_gw']:.0f} GW", f"sıralama: {int(df.index[df['ulke'] == 'Türkiye'][0]) + 1}. / {len(df)}", delta_color="off")
c3.metric("Lider", f"{lider['ulke']}", f"{lider['gunes_gw']:,.0f} GW", delta_color="off")

st.plotly_chart(
    charts.ulke_yatay_cubuk(df, "Ülkelere göre güneş kurulu gücü (GW)"),
    use_container_width=True,
)

st.subheader("Not")
st.info(
    "Türkiye değeri 2025 yıl sonu itibarıyla TEİAŞ verisinden alınmıştır. Diğer ülkeler 2024 yılına aittir. "
    "Bu nedenle karşılaştırma tam olarak aynı yıl üzerinden yapılmamaktadır."
)

ui.veri_tablosu(df, "Veriyi tablo olarak göster")
