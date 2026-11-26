"""Kişi başına elektrik tüketimi karşılaştırması."""

import streamlit as st

from src.energyatlas import charts, data

st.title("Kişi Başına Elektrik Tüketimi")
st.caption("kWh / kişi. OECD değeri 38 ülkenin ortalamasıdır.")

df = data.kisi_basina().set_index("kaynak")
turkiye = df.loc["Türkiye", "kwh_kisi"]
oecd = df.loc["OECD", "kwh_kisi"]
dunya = df.loc["Dünya", "kwh_kisi"]

c1, c2, c3 = st.columns(3)
c1.metric("Türkiye", f"{turkiye:,.0f} kWh")
c2.metric("Dünya ortalaması", f"{dunya:,.0f} kWh", f"Türkiye {turkiye - dunya:+,.0f} kWh")
c3.metric("OECD ortalaması", f"{oecd:,.0f} kWh", f"Türkiye {turkiye - oecd:+,.0f} kWh")

st.plotly_chart(
    charts.kisi_basina_cubuk(df.reset_index(), "Kişi başına yıllık elektrik tüketimi"),
    use_container_width=True,
)

st.info(
    f"Türkiye'nin kişi başına tüketimi dünya ortalamasının yaklaşık {turkiye / dunya:.2f} katı, "
    f"OECD ortalamasının ise yaklaşık %{turkiye / oecd * 100:.0f}'i düzeyinde."
)
