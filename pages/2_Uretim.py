"""Kaynaklara göre Türkiye elektrik üretimi (TWh), 2016-2026."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"Üretim | {APP_TITLE}", layout="wide")
st.title("Kaynaklara Göre Elektrik Üretimi")
st.caption("Türkiye brüt elektrik üretimi, TWh. Pay değerleri yüzde olarak gösterilir.")

df = data.uretim()
son = df[df["donem"] == "2026 9A"].iloc[0]
onceki = df[df["donem"] == "2016"].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Toplam üretim (2026 9A)", f"{son['toplam_twh']:.0f} TWh")
c2.metric("Termik payı (2026 9A)", f"%{son['termik_pct']:.0f}", f"%{son['termik_pct'] - onceki['termik_pct']:+.0f} (2016'ya göre)", delta_color="inverse")
c3.metric("Yenilenebilir payı (2026 9A)", f"%{100 - son['termik_pct']:.0f}")

st.plotly_chart(
    charts.toplam_cubuk(df, "toplam_twh", "Toplam brüt üretim (TWh)", "TWh"),
    use_container_width=True,
)
st.plotly_chart(
    charts.pay_yiginli_cubuk(df, "Kaynaklara göre üretim payı (%)"),
    use_container_width=True,
)

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
