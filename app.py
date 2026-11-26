"""Enerji Atlası: giriş noktası. Gezinme menüsünü ve sayfa kategorilerini tanımlar."""

from pathlib import Path

import streamlit as st

from config import APP_TITLE
from src.energyatlas import export, guncelleme, theme

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.uygula()


@st.cache_data(show_spinner="Sunum hazırlanıyor…")
def _sunum_bytes(surum: str) -> bytes:
    """Sunum dosyasını üretir. `surum` (son güncelleme zamanı) değiştiğinde yeniden üretilir."""
    return export.ozet_sunum_bytes()


with st.sidebar:
    st.caption(f"Son güncelleme: {guncelleme.son_guncelleme_metni()}")
    if st.button("Verileri güncelle", use_container_width=True, help="Veri dosyalarını yeniden okur ve sunumu yeniler."):
        st.cache_data.clear()
        guncelleme.guncelle()
        st.rerun()
    st.download_button(
        "Sunumu indir (.pptx)",
        data=_sunum_bytes(guncelleme.son_guncelleme_metni()),
        file_name="enerji_atlasi_ozet.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )


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
        sayfa("views/santral_listesi.py", "EPDK santral listesi", "📋"),
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
