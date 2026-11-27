"""Hedefler ve güncel gelişmeler: geçmiş ve yeni hedefler, devam eden yatırımlar ve güncel gelişmeler."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import devam_eden_yatirimlar, hedefler_vizyon, piyasa_hedefleri

ui.sayfa_basligi("Türkiye Elektrik Piyasası Hedefleri ve Güncel Gelişmeler", "Türkiye Elektrik Piyasası Hedefleri ve Güncel Gelişmeler",
                 "Geçmiş ve yeni hedefler, devam eden yatırımlar ve güncel gelişmeler.")
ui.geri_linki()

sekme_hedef, sekme_yatirim, sekme_iletim, sekme_guncel = st.tabs(
    ["Geçmiş ve yeni hedefler", "Devam eden yatırımlar", "Elektrik iletim ağı hedefleri", "Güncel gelişmeler ve beklentiler"]
)
with sekme_hedef:
    alt_gecmis, alt_piyasa = st.tabs(["Hedeflerin gelişimi", "Piyasa hedefleri"])
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
        ["Enerjide 2026 vizyonu", "Lisanssız kapasite tahsisleri", "Hibrit kapasite tahsisleri"]
    )
    with alt_vizyon:
        ui.yakinda("Enerjide 2026 vizyonu açıklamalarına göre gerçekleşenler")
    with alt_lisanssiz:
        ui.yakinda("Lisanssız enerji santralleri için kapasite tahsisleri: geçmiş, mevcut ve gelecek (varsa)")
    with alt_hibrit:
        ui.yakinda("Hibrit yenilenebilir enerji santralleri için bağlantı kapasitesi tahsisleri: geçmiş, mevcut ve gelecek (varsa)")
