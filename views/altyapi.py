"""Altyapı ve hedefler: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import iletim_agi
from src.energyatlas.sayfalar import piyasa_hedefleri

ui.sayfa_basligi("Altyapı ve hedefler", "Altyapı ve hedefler", "Elektrik iletim ağı ve piyasa hedefleri.")
ui.geri_linki()

sekme_0, sekme_1 = st.tabs(["İletim ağı", "Piyasa hedefleri"])
with sekme_0:
    iletim_agi.render()
with sekme_1:
    piyasa_hedefleri.render()
