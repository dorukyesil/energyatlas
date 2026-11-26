"""Kaynaklara göre Türkiye elektrik kurulu gücü (GW), 2016-2026."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"Kurulu Güç | {APP_TITLE}", layout="wide")
st.title("Kaynaklara Göre Kurulu Güç")
st.caption("Türkiye elektrik kurulu gücü, GW. Pay değerleri yüzde olarak gösterilir.")

df = data.kurulu_guc()
son = df[df["donem"] == "2026 9A"].iloc[0]
onceki = df[df["donem"] == "2016"].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Toplam kurulu güç (2026 9A)", f"{son['toplam_gw']:.1f} GW", f"{son['toplam_gw'] - onceki['toplam_gw']:+.1f} GW (2016'dan beri)")
c2.metric("Güneş payı (2026 9A)", f"%{son['gunes_pct']:.0f}")
c3.metric("Rüzgar payı (2026 9A)", f"%{son['ruzgar_pct']:.0f}")

st.plotly_chart(
    charts.toplam_cubuk(df, "toplam_gw", "Toplam kurulu güç (GW)", "GW"),
    use_container_width=True,
)
st.plotly_chart(
    charts.pay_yiginli_cubuk(df, "Kaynaklara göre kurulu güç payı (%)"),
    use_container_width=True,
)

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
