"""Ortak arayüz bileşenleri: başlık, kategori kartları ve veri tablosu."""

import html

import pandas as pd
import streamlit as st


def hero(baslik: str, aciklama: str) -> None:
    """Sayfanın üstündeki renkli başlık bloğu."""
    st.markdown(
        f"""<div class="ea-hero"><h1>{html.escape(baslik)}</h1><p>{html.escape(aciklama)}</p></div>""",
        unsafe_allow_html=True,
    )


def kart(ikon: str, baslik: str, maddeler: list[str]) -> None:
    """Kategori kartı. Ana sayfada bölümleri özetlemek için kullanılır."""
    liste = "".join(f"<li>{html.escape(m)}</li>" for m in maddeler)
    st.markdown(
        f"""<div class="ea-kart"><div class="ea-ikon">{ikon}</div><h4>{html.escape(baslik)}</h4><ul>{liste}</ul></div>""",
        unsafe_allow_html=True,
    )


def veri_tablosu(df: pd.DataFrame, baslik: str = "Veriyi tablo olarak göster", dosya: str = "veri.csv") -> None:
    """Tabloyu açılır bölümde gösterir ve CSV olarak indirme düğmesi sunar."""
    with st.expander(baslik):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "CSV olarak indir",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=dosya,
            mime="text/csv",
        )
