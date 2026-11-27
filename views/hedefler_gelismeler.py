"""Hedefler ve güncel gelişmeler: geçmiş ve yeni hedefler, devam eden yatırımlar ve güncel gelişmeler."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import devam_eden_yatirimlar, hedefler_vizyon, piyasa_hedefleri

ui.sayfa_basligi("Hedefler ve güncel gelişmeler", "Hedefler ve güncel gelişmeler",
                 "Geçmiş ve yeni hedefler, devam eden yatırımlar ve güncel gelişmeler.")
ui.geri_linki()

sekme_hedef, sekme_yatirim, sekme_iletim, sekme_guncel = st.tabs(
    ["Hedefler", "Devam eden yatırımlar", "İletim ağı hedefleri", "Güncel gelişmeler"]
)
with sekme_hedef:
    alt_gecmis, alt_piyasa = st.tabs(["Geçmiş ve yeni hedefler", "Piyasa hedefleri"])
    with alt_gecmis:
        hedefler_vizyon.render()
    with alt_piyasa:
        piyasa_hedefleri.render()
with sekme_yatirim:
    devam_eden_yatirimlar.render()
with sekme_iletim:
    ui.yakinda("Elektrik iletim ağı hedefleri")
with sekme_guncel:
    alt_vizyon, alt_lisanssiz, alt_hibrit = st.tabs(
        ["2026 vizyonu", "Lisanssız kapasite tahsisi", "Hibrit kapasite tahsisi"]
    )
    with alt_vizyon:
        ui.yakinda("Enerjide 2026 vizyonu açıklamalarına göre gerçekleşenler")
    with alt_lisanssiz:
        ui.yakinda("Lisanssız enerji santralleri için kapasite tahsisleri")
    with alt_hibrit:
        ui.yakinda("Hibrit yenilenebilir enerji santralleri için bağlantı kapasitesi tahsisleri")
