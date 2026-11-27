"""Fiyatlandırma: lisanslı ve lisanssız santrallerin mekanizmaları, EPDK tarifeleri, PTF ve YEKDEM."""

import streamlit as st

from src.energyatlas import ui
from src.energyatlas.sayfalar import epdk_tarifeleri, ptf, yekdem

ui.sayfa_basligi("Yenilenebilir Enerji Santralleri için Fiyatlandırma Mekanizmaları", "Yenilenebilir Enerji Santralleri için Fiyatlandırma Mekanizmaları",
                 "Lisanslı ve lisanssız santrallerin fiyatlandırma mekanizmaları, EPDK tarifeleri, PTF ve YEKDEM.")
ui.geri_linki()

sekme_lisansli, sekme_lisanssiz, sekme_tarife, sekme_ptf, sekme_yekdem, sekme_karsilastirma = st.tabs(
    ["Lisanslı santrallerin mekanizmaları", "Lisanssız santrallerin mekanizmaları", "EPDK tarifeleri", "PTF", "YEKDEM", "Fiyat kategorilerinin karşılaştırması"]
)
with sekme_lisansli:
    ui.yakinda("Lisanslı santrallerin fiyatlandırma mekanizmaları")
with sekme_lisanssiz:
    ui.yakinda("Lisanssız santrallerin fiyatlandırma mekanizmaları")
with sekme_tarife:
    epdk_tarifeleri.render()
with sekme_ptf:
    ptf.render()
with sekme_yekdem:
    yekdem.render()
with sekme_karsilastirma:
    ui.yakinda("Tüm fiyat kategorilerinin karşılaştırılması")
