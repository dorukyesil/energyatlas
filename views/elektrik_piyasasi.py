"""Elektrik piyasası: kurulu güç, üretim, tüketim, iletim ağı ve depolama."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import depolama_on_lisans, depolama_sebeke, dis_ticaret
from src.energyatlas.sayfalar import isletmedeki_depolama, kisi_basina, kurulu_guc, santral_listesi, tuketim, uretim

ui.sayfa_basligi("Elektrik piyasası", "Elektrik piyasası", "Kurulu güç, üretim, tüketim, iletim ağı ve depolama.")
ui.geri_linki()

sekme_kurulu, sekme_uretim, sekme_tuketim, sekme_iletim, sekme_depolama = st.tabs(
    ["Kurulu güç", "Üretim", "Tüketim", "İletim ağı", "Depolama"]
)
with sekme_kurulu:
    kurulu_guc.render()
with sekme_uretim:
    uretim.render()
with sekme_tuketim:
    alt_brut, alt_kisi, alt_dis, alt_faktor = st.tabs(["Brüt tüketim", "Kişi başına", "Dış ticaret", "Etkileyen faktörler"])
    with alt_brut:
        tuketim.render()
    with alt_kisi:
        kisi_basina.render()
    with alt_dis:
        dis_ticaret.render()
    with alt_faktor:
        ui.yakinda("Tüketimi etkileyen faktörler")
with sekme_iletim:
    ui.yakinda("Elektrik iletim ağı mevcut durumu")
with sekme_depolama:
    alt_sebeke, alt_tur, alt_on, alt_isletme, alt_liste = st.tabs(
        ["Şebeke ilişkisi", "Kullanım türleri", "Ön lisanslar", "İşletmedeki depolama", "EPDK santral listesi"]
    )
    with alt_sebeke:
        depolama_sebeke.render()
    with alt_tur:
        ui.yakinda("Elektrik depolama kullanım türleri")
    with alt_on:
        depolama_on_lisans.render()
    with alt_isletme:
        isletmedeki_depolama.render()
    with alt_liste:
        santral_listesi.render()
