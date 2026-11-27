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
        sayfa("views/elektrik_piyasasi.py", "Türkiye Elektrik Piyasası"),
        sayfa("views/hedefler_gelismeler.py", "Türkiye Elektrik Piyasası Hedefleri ve Güncel Gelişmeler"),
        sayfa("views/lisanssiz.py", "Türkiye Lisanssız Elektrik Üretimi Piyasası"),
        sayfa("views/fiyatlandirma.py", "Yenilenebilir Enerji Santralleri için Fiyatlandırma Mekanizmaları"),
        sayfa("views/dunya_istatistikleri.py", "Dünya İstatistikleri"),
    ],
    position="hidden",
).run()
