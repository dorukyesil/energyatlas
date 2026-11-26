"""Dünya enerji görünümü: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import dunya_gunes
from src.energyatlas.sayfalar import weo_enerji_arz
from src.energyatlas.sayfalar import weo_elektrik
from src.energyatlas.sayfalar import weo_emisyon
from src.energyatlas.sayfalar import weo_talep_ekonomi
from src.energyatlas.sayfalar import weo_teknoloji

ui.sayfa_basligi("Dünya enerji görünümü", "Dünya enerji görünümü", "IEA verileri: güneş kapasitesi, enerji arzı, elektrik, emisyonlar, talep ve teknolojiler (WEO 2026).")
ui.geri_linki()

sekme_0, sekme_1, sekme_2, sekme_3, sekme_4, sekme_5 = st.tabs(["Güneş kapasitesi", "Enerji arzı", "Elektrik", "CO2 emisyonları", "Talep ve ekonomi", "Hidrojen ve CCUS"])
with sekme_0:
    dunya_gunes.render()
with sekme_1:
    weo_enerji_arz.render()
with sekme_2:
    weo_elektrik.render()
with sekme_3:
    weo_emisyon.render()
with sekme_4:
    weo_talep_ekonomi.render()
with sekme_5:
    weo_teknoloji.render()
