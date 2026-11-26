"""Elektrik sistemi: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import kurulu_guc
from src.energyatlas.sayfalar import uretim
from src.energyatlas.sayfalar import tuketim
from src.energyatlas.sayfalar import dis_ticaret
from src.energyatlas.sayfalar import kisi_basina

ui.sayfa_basligi("Elektrik sistemi", "Elektrik sistemi", "Kurulu güç, üretim, tüketim ve kişi başına tüketim.")
ui.geri_linki()

sekme_0, sekme_1, sekme_2, sekme_3, sekme_4 = st.tabs(["Kurulu güç", "Üretim", "Tüketim", "Dış ticaret", "Kişi başına"])
with sekme_0:
    kurulu_guc.render()
with sekme_1:
    uretim.render()
with sekme_2:
    tuketim.render()
with sekme_3:
    dis_ticaret.render()
with sekme_4:
    kisi_basina.render()
