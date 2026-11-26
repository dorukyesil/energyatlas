"""Üretim sayfası: kaynaklara göre aylık üretim."""

import plotly.express as px
import streamlit as st

from config import DATA_DIR
from src.energyatlas.data import load_csv

st.set_page_config(page_title="Üretim", layout="wide")
st.title("Üretim")

df = load_csv(DATA_DIR / "uretim_ornek.csv")

kaynaklar = sorted(df["kaynak"].unique())
secilen = st.multiselect("Enerji kaynağı", kaynaklar, default=kaynaklar)
filtreli = df[df["kaynak"].isin(secilen)]

if filtreli.empty:
    st.info("Gösterilecek veri yok. En az bir kaynak seçin.")
else:
    fig = px.bar(
        filtreli,
        x="tarih",
        y="uretim_mwh",
        color="kaynak",
        labels={"tarih": "Ay", "uretim_mwh": "Üretim (MWh)", "kaynak": "Kaynak"},
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(filtreli, use_container_width=True, hide_index=True)
