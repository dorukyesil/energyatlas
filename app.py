"""Enerji Atlası: giriş noktası. Sayfalar ana sayfadaki konu kartlarından açılır."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import theme

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
theme.uygula()


def sayfa(yol: str, baslik: str, varsayilan: bool = False) -> st.Page:
    return st.Page(yol, title=baslik, url_path=yol.split("/")[-1].removesuffix(".py"), default=varsayilan)


st.navigation(
    [
        sayfa("views/genel_bakis.py", "Enerji Atlası", varsayilan=True),
        sayfa("views/hakkinda.py", "Hakkında"),
        sayfa("views/elektrik.py", "Elektrik sistemi"),
        sayfa("views/depolama.py", "Depolama ve yatırımlar"),
        sayfa("views/fiyatlar.py", "Fiyatlar ve tarifeler"),
        sayfa("views/altyapi.py", "Altyapı ve hedefler"),
        sayfa("views/dunya_enerji.py", "Dünya enerji görünümü"),
        sayfa("views/dunya_karsilastirma.py", "Dünya karşılaştırma"),
        sayfa("views/mevzuat.py", "Mevzuat"),
    ],
    position="hidden",
).run()
