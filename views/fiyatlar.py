"""Fiyatlar ve tarifeler: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import ptf
from src.energyatlas.sayfalar import epdk_tarifeleri
from src.energyatlas.sayfalar import yekdem

ui.sayfa_basligi("Fiyatlar ve tarifeler", "Fiyatlar ve tarifeler", "Piyasa takas fiyatı, EPDK elektrik tarifeleri ve YEKDEM.")
ui.geri_linki()

sekme_0, sekme_1, sekme_2 = st.tabs(["PTF", "EPDK tarifeleri", "YEKDEM"])
with sekme_0:
    ptf.render()
with sekme_1:
    epdk_tarifeleri.render()
with sekme_2:
    yekdem.render()
