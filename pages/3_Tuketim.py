"""Türkiye brüt elektrik tüketimi (TWh), 2016-2026."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"Tüketim | {APP_TITLE}", layout="wide")
st.title("Brüt Elektrik Tüketimi")
st.caption("Türkiye brüt elektrik tüketimi, TWh. Grafikteki noktaların üzerine gelerek olayları görebilirsiniz.")

df = data.tuketim()
yillik = df[df["donem"].str.fullmatch(r"\d{4}")].reset_index(drop=True)
ilk, son = yillik.iloc[0], yillik.iloc[-1]
yillik_artis = ((son["tuketim_twh"] / ilk["tuketim_twh"]) ** (1 / (len(yillik) - 1)) - 1) * 100

c1, c2, c3 = st.columns(3)
c1.metric("2025 tüketimi", f"{son['tuketim_twh']:.0f} TWh")
c2.metric("2016-2025 yıllık ortalama artış", f"%{yillik_artis:.1f}")
c3.metric("2026 ilk yarı", "175 TWh", "+%2,3 (2025 H1'e göre)")

st.plotly_chart(
    charts.tuketim_cubuk(df, "Türkiye brüt elektrik tüketimi (TWh)"),
    use_container_width=True,
)

st.subheader("Öne çıkan olaylar")
olaylar = df[df["olay"].notna()]
for _, satir in olaylar.iterrows():
    st.markdown(f"- **{satir['donem']}**: {satir['olay']} ({satir['tuketim_twh']:.0f} TWh)")

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
