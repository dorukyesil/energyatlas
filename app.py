"""Enerji Atlası: giriş noktası. Gezinme menüsünü ve sayfa kategorilerini tanımlar."""

from pathlib import Path

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


def sayfa(yol: str, baslik: str, ikon: str, varsayilan: bool = False) -> st.Page:
    """Sayfa adresi dosya adından türetilir (ör. /kurulu_guc)."""
    return st.Page(yol, title=baslik, icon=ikon, url_path=Path(yol).stem, default=varsayilan)


sayfalar = {
    "Genel": [
        sayfa("views/genel_bakis.py", "Genel Bakış", "🏠", varsayilan=True),
        sayfa("views/hakkinda.py", "Hakkında", "📘"),
    ],
    "Elektrik sistemi": [
        sayfa("views/kurulu_guc.py", "Kaynaklara göre kurulu güç", "⚡"),
        sayfa("views/uretim.py", "Kaynaklara göre üretim", "🏭"),
        sayfa("views/tuketim.py", "Brüt elektrik tüketimi", "📈"),
        sayfa("views/kisi_basina.py", "Kişi başına tüketim", "👥"),
    ],
    "Depolama ve yatırımlar": [
        sayfa("views/devam_eden_yatirimlar.py", "Devam eden yatırımlar", "🏗️"),
        sayfa("views/depolama_sebeke.py", "Depolama ve şebeke", "🔋"),
        sayfa("views/depolama_on_lisans.py", "Depolama ön lisansları", "📅"),
        sayfa("views/isletmedeki_depolama.py", "İşletmedeki depolama", "🏭"),
    ],
    "Fiyatlar ve tarifeler": [
        sayfa("views/ptf.py", "Piyasa takas fiyatı (PTF)", "💹"),
        sayfa("views/epdk_tarifeleri.py", "EPDK elektrik tarifeleri", "💡"),
        sayfa("views/yekdem.py", "YEKDEM", "⚖️"),
    ],
    "Altyapı ve hedefler": [
        sayfa("views/iletim_agi.py", "Elektrik iletim ağı", "🔌"),
        sayfa("views/piyasa_hedefleri.py", "Piyasa hedefleri", "🎯"),
    ],
    "Dünya ve karşılaştırma": [
        sayfa("views/dunya_gunes.py", "Dünya güneş kapasitesi", "☀️"),
        sayfa("views/ulke_karsilastirma.py", "Ülke karşılaştırması", "🗺️"),
        sayfa("views/kuresel_yatirimlar.py", "Küresel enerji yatırımları", "💰"),
    ],
}

st.navigation(sayfalar).run()
