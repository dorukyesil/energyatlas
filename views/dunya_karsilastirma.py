"""Dünya karşılaştırma: ilgili sayfalar sekmeler halinde."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import weo_bolgesel
from src.energyatlas.sayfalar import ulke_karsilastirma
from src.energyatlas.sayfalar import kuresel_yatirimlar

ui.sayfa_basligi("Dünya karşılaştırma", "Dünya karşılaştırma", "Bölgesel karşılaştırma, ülke ve bölge güneş üretimi ve küresel yatırımlar.")
ui.geri_linki()

sekme_0, sekme_1, sekme_2 = st.tabs(["Bölgesel karşılaştırma", "Ülke ve bölge", "Küresel yatırımlar"])
with sekme_0:
    weo_bolgesel.render()
with sekme_1:
    ulke_karsilastirma.render()
with sekme_2:
    kuresel_yatirimlar.render()
