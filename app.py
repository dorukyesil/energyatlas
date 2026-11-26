"""Enerji Atlası giriş sayfası."""

import streamlit as st

from config import APP_TITLE, DATA_DIR
from src.energyatlas.data import load_csv

st.set_page_config(page_title=APP_TITLE, layout="wide")

st.title(APP_TITLE)
st.caption("Enerji sektörüne ilişkin veriler için web portalı. Soldaki menüden bir sayfa seçin.")

df = load_csv(DATA_DIR / "uretim_ornek.csv")

col1, col2, col3 = st.columns(3)
col1.metric("Toplam üretim (MWh)", f"{df['uretim_mwh'].sum():,.0f}")
col2.metric("Kaynak sayısı", df["kaynak"].nunique())
col3.metric("Kayıt sayısı", len(df))
