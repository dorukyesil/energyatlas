"""Dünya istatistikleri: IEA verileriyle dünya görünümü ve Türkiye ile karşılaştırmalar."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import dunya_gunes, kuresel_yatirimlar, ulke_karsilastirma, weo_bolgesel
from src.energyatlas.sayfalar import weo_elektrik, weo_emisyon, weo_enerji_arz, weo_talep_ekonomi, weo_teknoloji

ui.sayfa_basligi("Dünya İstatistikleri", "Dünya İstatistikleri",
                 "IEA verileriyle dünya görünümü, bölgesel ve ülke karşılaştırmaları.")
ui.geri_linki()

sekme_gorunum, sekme_karsilastirma = st.tabs(["Dünya enerji görünümü", "Dünya ile karşılaştırma"])
with sekme_gorunum:
    alt_gunes, alt_arz, alt_elektrik, alt_emisyon, alt_talep, alt_teknoloji = st.tabs(
        ["Güneş kapasitesi", "Enerji arzı", "Elektrik", "CO2 emisyonları", "Talep ve ekonomi", "Hidrojen ve CCUS"]
    )
    with alt_gunes:
        dunya_gunes.render()
    with alt_arz:
        weo_enerji_arz.render()
    with alt_elektrik:
        weo_elektrik.render()
    with alt_emisyon:
        weo_emisyon.render()
    with alt_talep:
        weo_talep_ekonomi.render()
    with alt_teknoloji:
        weo_teknoloji.render()
with sekme_karsilastirma:
    alt_bolgesel, alt_ulke, alt_kuresel = st.tabs(["Bölgesel karşılaştırma", "Ülke ve bölge", "Küresel yatırımlar"])
    with alt_bolgesel:
        weo_bolgesel.render()
    with alt_ulke:
        ulke_karsilastirma.render()
    with alt_kuresel:
        kuresel_yatirimlar.render()
