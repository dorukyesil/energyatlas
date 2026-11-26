"""Depolama ve yatırımlar: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import depolama_sebeke
from src.energyatlas.sayfalar import devam_eden_yatirimlar
from src.energyatlas.sayfalar import depolama_on_lisans
from src.energyatlas.sayfalar import isletmedeki_depolama
from src.energyatlas.sayfalar import santral_listesi

ui.sayfa_basligi("Depolama ve yatırımlar", "Depolama ve yatırımlar", "Depolamalı santraller, ön lisanslar, işletmedeki projeler ve EPDK santral listesi.")
ui.geri_linki()

sekme_0, sekme_1, sekme_2, sekme_3, sekme_4 = st.tabs(["Şebeke ilişkisi", "Devam eden yatırımlar", "Ön lisanslar", "İşletmedeki depolama", "EPDK santral listesi"])
with sekme_0:
    depolama_sebeke.render()
with sekme_1:
    devam_eden_yatirimlar.render()
with sekme_2:
    depolama_on_lisans.render()
with sekme_3:
    isletmedeki_depolama.render()
with sekme_4:
    santral_listesi.render()
