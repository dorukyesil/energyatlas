"""Ortak arayüz bileşenleri: başlıklar, KPI şeridi, kategori kartları ve veri tablosu."""

import html
from collections.abc import Sequence

import pandas as pd
import streamlit as st

from src.energyatlas import theme


def sayi(deger: float, ondalik: int = 1) -> str:
    """Sayıyı Türkçe biçimde yazar: 1.234,5 (binlik ayracı nokta, ondalık virgül)."""
    metin = f"{deger:,.{ondalik}f}"
    return metin.replace(",", "§").replace(".", ",").replace("§", ".")


def sayfa_basligi(kategori: str, baslik: str, aciklama: str = "") -> None:
    """Her sayfanın üstündeki kategori etiketi, serif başlık ve açıklama."""
    aciklama_html = f"<p>{html.escape(aciklama)}</p>" if aciklama else ""
    st.markdown(
        f'<div class="ea-sayfa"><div class="ea-eyebrow">{html.escape(kategori)}</div>'
        f"<h1>{html.escape(baslik)}</h1>{aciklama_html}</div>",
        unsafe_allow_html=True,
    )


def bolum(no: str, baslik: str, aciklama: str = "") -> None:
    """Numaralı bölüm başlığı: üstte ince çizgi, küçük numara, serif başlık."""
    aciklama_html = f"<p>{html.escape(aciklama)}</p>" if aciklama else ""
    st.markdown(
        f'<div class="ea-bolum"><span class="ea-no">{html.escape(no)}</span>'
        f"<h2>{html.escape(baslik)}</h2>{aciklama_html}</div>",
        unsafe_allow_html=True,
    )


def kaynak(metin: str) -> None:
    """Grafiğin altına küçük kaynak notu ekler."""
    st.markdown(f'<div class="ea-kaynak">{html.escape(metin)}</div>', unsafe_allow_html=True)


def sparkline(degerler: Sequence[float], renk: str = theme.TURKUAZ, genislik: int = 150, yukseklik: int = 34) -> str:
    """Küçük eğilim çizgisini SVG olarak üretir."""
    seri = [float(d) for d in degerler if d is not None and not pd.isna(d)]
    if len(seri) < 2:
        return ""
    alt, ust = min(seri), max(seri)
    aralik = (ust - alt) or 1.0
    adim = genislik / (len(seri) - 1)
    noktalar = [(i * adim, yukseklik - 3 - (d - alt) / aralik * (yukseklik - 6)) for i, d in enumerate(seri)]
    yol = " ".join(f"{x:.1f},{y:.1f}" for x, y in noktalar)
    son_x, son_y = noktalar[-1]
    return (
        f'<svg width="{genislik}" height="{yukseklik}" viewBox="0 0 {genislik} {yukseklik}" xmlns="http://www.w3.org/2000/svg">'
        f'<polyline points="{yol}" fill="none" stroke="{renk}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{son_x:.1f}" cy="{son_y:.1f}" r="2.4" fill="{renk}"/></svg>'
    )


def kpi_serit(ogeler: list[dict]) -> None:
    """Mini eğilim çizgili gösterge şeridi.

    Her öğe: etiket, deger, birim (isteğe bağlı), alt (isteğe bağlı), ton ("p", "n" veya ""), seri (isteğe bağlı).
    """
    parcalar = []
    for o in ogeler:
        birim = f"<small>{html.escape(o['birim'])}</small>" if o.get("birim") else ""
        alt = f'<div class="a {o.get("ton", "")}">{html.escape(o["alt"])}</div>' if o.get("alt") else ""
        renk = theme.PAS if o.get("ton") == "n" else theme.TURKUAZ
        cizgi = sparkline(o["seri"], renk) if o.get("seri") else ""
        parcalar.append(
            f'<div><div class="e">{html.escape(o["etiket"])}</div>'
            f'<div class="d">{html.escape(str(o["deger"]))}{birim}</div>{alt}{cizgi}</div>'
        )
    st.markdown(f'<div class="ea-serit">{"".join(parcalar)}</div>', unsafe_allow_html=True)


def kategori_karti(ikon: str, baslik: str, aciklama: str, sayfalar: list[tuple[str, str, str]]) -> None:
    """Ana sayfadaki kategori kartı. Her sayfa için (dosya yolu, etiket, ikon) verilir."""
    with st.container(border=True):
        st.markdown(
            f'<span class="ea-kart-isaret"></span><div style="font-size:1.5rem">{ikon}</div>'
            f'<div class="ea-kart-baslik">{html.escape(baslik)}</div>'
            f'<div class="ea-kart-aciklama">{html.escape(aciklama)}</div>',
            unsafe_allow_html=True,
        )
        for yol, etiket, sayfa_ikonu in sayfalar:
            st.page_link(yol, label=etiket, icon=sayfa_ikonu)


def segment(secenekler: list[str], anahtar: str, varsayilan: str | None = None) -> str:
    """Grafik görünümünü değiştiren segment düğmesi. Her zaman bir seçim döndürür."""
    varsayilan = varsayilan or secenekler[0]
    secim = st.segmented_control(
        "Görünüm", secenekler, default=varsayilan, key=anahtar, label_visibility="collapsed"
    )
    return secim or varsayilan


# Her tablonun kaynağı (CSV dosya adına göre). Kaynak belirtilmezse buradan alınır.
TABLO_KAYNAKLARI = {
    "kurulu_guc.csv": "TEİAŞ. Sunum grafiklerinden okunmuştur.",
    "uretim.csv": "TEİAŞ. Sunum grafiklerinden okunmuştur.",
    "tuketim.csv": "TEİAŞ. Sunum grafiklerinden okunmuştur.",
    "kisi_basina.csv": "OECD ve dünya ortalamaları. Sunum grafiklerinden okunmuştur.",
    "depolama_sirketler.csv": "Sunum grafiklerinden okunmuştur (depolamalı proje verileri).",
    "depolama_on_lisans.csv": "EPDK, depolama ön lisans bitiş tarihleri.",
    "isletmedeki_depolama.csv": "EPDK, işletmedeki depolama lisanslı projeler.",
    "iletim.csv": "TEİAŞ ve Enerji ve Tabii Kaynaklar Bakanlığı. Sunum grafiklerinden okunmuştur.",
    "hedefler.csv": "Enerji ve Tabii Kaynaklar Bakanlığı: 2028 Stratejik Plan, 2035 Ulusal Enerji Planı ve Yol Haritası.",
    "ptf.csv": "EPİAŞ. Sunum grafiklerinden okunmuştur.",
    "epdk_tarifeleri.csv": "EPDK, elektrik faturalarına esas tarife tabloları (4 Nisan 2026).",
    "yekdem_fiyat.csv": "EPİAŞ ve sunum grafiklerinden okunmuştur.",
    "yekdem_duyuru.csv": "EPİAŞ, Kayıt ve Uzlaştırma duyuruları.",
    "ulke_gunes.csv": "IEA Renewables 2025 (Türkiye: TEİAŞ, 2025 yıl sonu).",
    "dunya_gunes.csv": "IEA World Energy Outlook 2025.",
    "kuresel_yatirim.csv": "Küresel enerji yatırım verileri. Sunum grafiklerinden okunmuştur.",
    "bolgesel_gunes_yatirim.csv": "Küresel güneş yatırım verileri. Sunum grafiklerinden okunmuştur.",
}


def veri_tablosu(df: pd.DataFrame, baslik: str = "Veri tablosu", dosya: str = "veri.csv", kaynak: str = "") -> None:
    """Tabloyu açılır bölümde gösterir. Üstünde kaynak notu ve CSV indirme düğmesi bulunur."""
    kaynak = kaynak or TABLO_KAYNAKLARI.get(dosya, "")
    with st.expander(baslik):
        if kaynak:
            st.caption(f"Kaynak: {kaynak}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "CSV olarak indir",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=dosya,
            mime="text/csv",
        )
