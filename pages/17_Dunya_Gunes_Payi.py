"""Güneş enerjisinin dünya toplam kurulu güç ve yenilenebilir kapasite içindeki payı."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"Güneş Payı | {APP_TITLE}", layout="wide")
st.title("Dünya Toplam Kurulu Gücü İçinde Güneş Payı")
st.caption("Güneşin dünya toplam kurulu gücü ve yenilenebilir kurulu gücü içindeki payı, %.")

df = data.dunya_gunes_payi().astype({"donem": str})
son = df[df["donem"] == "2024"].iloc[0]
tr_toplam, tr_yen = 17, 29

c1, c2, c3, c4 = st.columns(4)
c1.metric("Dünya: güneş / toplam (2024)", f"%{son['gunes_toplam_pct']:.0f}")
c2.metric("Dünya: güneş / yenilenebilir (2024)", f"%{son['gunes_yenilenebilir_pct']:.0f}")
c3.metric("Türkiye: güneş / toplam (2024)", f"%{tr_toplam}")
c4.metric("Türkiye: güneş / yenilenebilir (2024)", f"%{tr_yen}")

st.plotly_chart(
    charts.dunya_pay_nokta(df, "Güneşin kurulu güç içindeki payı (%)"),
    use_container_width=True,
)

st.subheader("Türkiye 2024")
st.markdown(
    """
- Türkiye'nin toplam kurulu gücü yaklaşık **116 GW**. Güneşin payı yaklaşık **%17**.
- 2024'te toplam yenilenebilir kurulu güç yaklaşık **69 GW**. Güneşin yenilenebilir içindeki payı yaklaşık **%29**.
"""
)
st.caption(
    "Türkiye yüzdeleri sunumdaki açıklama metninden alınmıştır. Dünya değerleri grafiklerden okunmuştur."
)

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
