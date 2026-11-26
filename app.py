"""Enerji Atlası: giriş noktası. Gezinme menüsünü ve sayfa kategorilerini tanımlar."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import theme

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.uygula()

sayfalar = {
    "Genel": [
        st.Page("views/genel_bakis.py", title="Genel Bakış", icon="🏠", default=True),
        st.Page("views/hakkinda.py", title="Hakkında", icon="📘"),
    ],
    "Kapasite ve üretim": [
        st.Page("views/kurulu_guc.py", title="Kaynaklara göre kurulu güç", icon="⚡"),
        st.Page("views/uretim.py", title="Kaynaklara göre üretim", icon="🏭"),
        st.Page("views/tuketim.py", title="Brüt elektrik tüketimi", icon="📈"),
        st.Page("views/kisi_basina.py", title="Kişi başına tüketim", icon="👥"),
    ],
    "Yenilenebilir ve depolama": [
        st.Page("views/devam_eden_yatirimlar.py", title="Devam eden yatırımlar", icon="🏗️"),
        st.Page("views/depolama_sebeke.py", title="Depolama ve şebeke", icon="🔋"),
        st.Page("views/depolama_on_lisans.py", title="Depolama ön lisansları", icon="🗺️"),
        st.Page("views/on_lisans_tarihleri.py", title="Ön lisans bitiş tarihleri", icon="📅"),
        st.Page("views/isletmedeki_depolama.py", title="İşletmedeki depolama projeleri", icon="🏭"),
    ],
    "Fiyatlar ve tarifeler": [
        st.Page("views/ptf.py", title="Piyasa takas fiyatı (PTF)", icon="💹"),
        st.Page("views/epdk_tarifeleri.py", title="EPDK elektrik tarifeleri", icon="💡"),
        st.Page("views/yekdem.py", title="YEKDEM fiyatlandırması", icon="⚖️"),
        st.Page("views/yekdem_duyurular.py", title="YEKDEM duyuruları", icon="📢"),
    ],
    "Altyapı ve hedefler": [
        st.Page("views/iletim_agi.py", title="Elektrik iletim ağı", icon="🔌"),
        st.Page("views/piyasa_hedefleri.py", title="Piyasa hedefleri", icon="🎯"),
    ],
    "Dünya ve karşılaştırma": [
        st.Page("views/dunya_kurulu_guc.py", title="Dünya kurulu güç", icon="🌍"),
        st.Page("views/dunya_gunes_payi.py", title="Dünyada güneş payı", icon="☀️"),
        st.Page("views/ulke_karsilastirma.py", title="Ülkeler: güneş kurulu gücü", icon="🗺️"),
        st.Page("views/kuresel_yatirimlar.py", title="Küresel enerji yatırımları", icon="💰"),
    ],
}

st.navigation(sayfalar).run()
