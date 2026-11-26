"""Mevzuat: enerji mevzuatının akışı, analizleri ve takibi."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import mevzuat_akis, mevzuat_analiz, mevzuat_takip

ui.sayfa_basligi("Mevzuat", "Enerji mevzuatı", "Türkiye enerji sektörüne ilişkin Resmî Gazete metinleri: yayımlananlar, değişiklikler, analizler ve takip.")
ui.geri_linki()

sekme_akis, sekme_analiz, sekme_takip = st.tabs(["Metinler", "Analizler", "Takip"])
with sekme_akis:
    mevzuat_akis.render()
with sekme_analiz:
    mevzuat_analiz.render()
with sekme_takip:
    mevzuat_takip.render()
