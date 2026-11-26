"""Enerji Atlası giriş sayfası."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import data

st.set_page_config(page_title=APP_TITLE, layout="wide")

st.title(APP_TITLE)
st.caption("Türkiye elektrik sektörü: kurulu güç, üretim, tüketim ve hedefler.")

kurulu = data.kurulu_guc().set_index("donem")
uretim = data.uretim().set_index("donem")
tuketim = data.tuketim().set_index("donem")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kurulu güç (2026 9A)", f"{kurulu.loc['2026 9A', 'toplam_gw']:.1f} GW")
c2.metric("Yenilenebilir üretim payı (2026 9A)", f"%{100 - uretim.loc['2026 9A', 'termik_pct']:.0f}")
c3.metric("Tüketim (2025)", f"{tuketim.loc['2025', 'tuketim_twh']:.0f} TWh")
c4.metric("Güneş payı (kurulu güç, 2026 9A)", f"%{kurulu.loc['2026 9A', 'gunes_pct']:.0f}")

st.subheader("Bölümler")
st.page_link("pages/1_Kurulu_Guc.py", label="Kaynaklara göre kurulu güç", icon="⚡")
st.page_link("pages/2_Uretim.py", label="Kaynaklara göre üretim", icon="🏭")
st.page_link("pages/3_Tuketim.py", label="Brüt elektrik tüketimi", icon="📈")
st.page_link("pages/4_Kisi_Basina.py", label="Kişi başına tüketim", icon="👥")
st.page_link("pages/5_Piyasa_Hedefleri.py", label="Piyasa hedefleri", icon="🎯")
st.page_link("pages/6_Devam_Eden_Yatirimlar.py", label="Devam eden yatırımlar", icon="🏗️")
st.page_link("pages/7_Iletim_Agi.py", label="Elektrik iletim ağı", icon="🔌")
st.page_link("pages/8_Depolama_Sebeke.py", label="Depolama ve şebeke", icon="🔋")
st.page_link("pages/9_Depolama_On_Lisans.py", label="Depolama ön lisansları", icon="🗺️")
