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


def sparkline(degerler: Sequence[float], yillar: Sequence[str] | None = None, renk: str = theme.TURKUAZ,
              birim: str = "", ondalik: int = 1, genislik: int = 150, yukseklik: int = 34) -> str:
    """Küçük eğilim çizgisi (SVG). Her noktanın üzerine gelindiğinde yıl ve değer görünür."""
    seri = [(i, float(d)) for i, d in enumerate(degerler) if d is not None and not pd.isna(d)]
    if len(seri) < 2:
        return ""
    vals = [d for _, d in seri]
    alt, ust = min(vals), max(vals)
    aralik = (ust - alt) or 1.0
    adim = genislik / (len(degerler) - 1)
    noktalar = [(idx * adim, yukseklik - 3 - (d - alt) / aralik * (yukseklik - 6), d, idx) for idx, d in seri]
    yol = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in noktalar)
    son_x, son_y, _, _ = noktalar[-1]
    parcalar = [f'<svg class="ea-spark" width="{genislik}" height="{yukseklik}" viewBox="0 0 {genislik} {yukseklik}" xmlns="http://www.w3.org/2000/svg">',
                f'<polyline points="{yol}" fill="none" stroke="{renk}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>',
                f'<circle cx="{son_x:.1f}" cy="{son_y:.1f}" r="2.4" fill="{renk}"/>']
    for x, y, d, idx in noktalar:
        yil = yillar[idx] if yillar and idx < len(yillar) else ""
        etiket = f"{yil}: {sayi(d, ondalik)}{(' ' + birim) if birim else ''}"
        parcalar.append(f'<g class="ea-nokta"><circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="transparent"/>'
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{renk}" class="ea-nokta-isaret"/>'
                        f'<text x="{min(max(x, 40), genislik - 40):.1f}" y="{max(y - 7, 9):.1f}" text-anchor="middle" class="ea-ipucu">{html.escape(etiket)}</text></g>')
    parcalar.append("</svg>")
    return "".join(parcalar)


def kpi_serit(ogeler: list[dict]) -> None:
    """Mini eğilim çizgili gösterge şeridi.

    Her öğe: etiket, deger, birim (isteğe bağlı), alt (isteğe bağlı), ton ("p", "n" veya ""),
    seri ve yillar (mini grafik), ondalik (mini grafik ondalık sayısı).
    """
    parcalar = []
    for o in ogeler:
        birim = f"<small>{html.escape(o['birim'])}</small>" if o.get("birim") else ""
        alt = f'<div class="a {o.get("ton", "")}">{html.escape(o["alt"])}</div>' if o.get("alt") else ""
        renk = theme.PAS if o.get("ton") == "n" else theme.TURKUAZ
        cizgi = sparkline(o["seri"], o.get("yillar"), renk, o.get("birim", ""), o.get("ondalik", 1)) if o.get("seri") else ""
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


def teias_notu(*anahtarlar: str, ek: str = "") -> None:
    """TEİAŞ veri setinin resmi tablo adı ve yayın tarihiyle kaynak notu yazar."""
    from src.energyatlas import data

    kaynaklar = data.teias_kaynak()
    parcalar = []
    for a in anahtarlar:
        k = kaynaklar.get(a, {})
        ad = k.get("dosya") or "TEİAŞ"
        tarih = (k.get("yayin_tarihi") or "")[:10]
        parcalar.append(f"{ad}" + (f" (yayın: {tarih[8:10]}.{tarih[5:7]}.{tarih[:4]})" if tarih else ""))
    metin = "Kaynak: TEİAŞ, " + "; ".join(dict.fromkeys(parcalar)) + "."
    if ek:
        metin += " " + ek
    kaynak(metin)


# Her tablonun kaynağı (CSV dosya adına göre). Kaynak belirtilmezse buradan alınır.
TABLO_KAYNAKLARI = {
    "teias_kurulu_guc.csv": "TEİAŞ, kurulu güç tablosu (turkiye-energy-mcp).",
    "teias_uretim.csv": "TEİAŞ, brüt elektrik üretimi tablosu (turkiye-energy-mcp).",
    "teias_talep.csv": "TEİAŞ, talep ve ithalat-ihracat tabloları (turkiye-energy-mcp).",
    "teias_dis_ticaret.csv": "TEİAŞ, ülke bazında ithalat-ihracat (turkiye-energy-mcp).",
    "teias_iletim.csv": "TEİAŞ, iletim istatistikleri (turkiye-energy-mcp).",
    "teias_aylik.csv": "TEİAŞ, aylık enerji istatistikleri (turkiye-energy-mcp).",
    "teias_ytbs_kurulu_guc.csv": "TEİAŞ YTBS, güncel kurulu güç (geçici işletme verisi).",
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
    "epdk_lisans.csv": "EPDK, lisanslı üretim tesisleri listesi (depolamalı santraller).",
    "epdk_onlisans.csv": "EPDK, ön lisanslı üretim tesisleri listesi.",
    "weo_dunya.csv": "IEA World Energy Outlook 2026, Annex A ücretsiz veri seti (dünya).",
    "weo_2026.csv": "IEA World Energy Outlook 2026, Annex A ücretsiz veri seti (dünya ve bölgeler).",
    "yatirim_bolge.csv": "IEA, World Energy Investment 2025 veri dosyası (2024 sabit fiyat, MER).",
}


def veri_tablosu(df: pd.DataFrame, baslik: str = "Veri tablosu", dosya: str = "veri.csv", kaynak: str = "") -> None:
    """Tabloyu açılır bölümde gösterir. Üstünde kaynak notu ve CSV indirme düğmesi bulunur."""
    kaynak = kaynak or TABLO_KAYNAKLARI.get(dosya, "")
    parmak_izi = int(pd.util.hash_pandas_object(df, index=False).sum() % 10**9)
    anahtar = "dl_" + "".join(ch if ch.isalnum() else "_" for ch in f"{dosya}_{baslik}") + f"_{parmak_izi}"
    with st.expander(baslik):
        if kaynak:
            st.caption(f"Kaynak: {kaynak}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "CSV olarak indir",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=dosya,
            mime="text/csv",
            key=anahtar,
        )


def geri_linki() -> None:
    """Alt sayfalardan ana sayfaya dönüş bağlantısı."""
    st.page_link("views/genel_bakis.py", label="← Ana sayfa", icon="🏠")


def kategori_karti_basit(ikon: str, baslik: str, aciklama: str, maddeler: list[str], yol: str, etiket: str) -> None:
    """Ana sayfadaki konu kartı: kısa açıklama, alt başlıklar ve tek bir bağlantı."""
    with st.container(border=True, height=300):
        st.markdown(
            f'<span class="ea-kart-isaret"></span><div style="font-size:1.5rem">{ikon}</div>'
            f'<div class="ea-kart-baslik">{html.escape(baslik)}</div>'
            f'<div class="ea-kart-aciklama">{html.escape(aciklama)}</div>'
            + "".join(f'<div class="ea-kart-madde">· {html.escape(m)}</div>' for m in maddeler),
            unsafe_allow_html=True,
        )
        st.page_link(yol, label=f"{etiket} →")


def hero(baslik: str, aciklama: str) -> None:
    """Ana sayfanın üstündeki başlık bloğu."""
    st.markdown(
        f'<div class="ea-hero"><h1>{html.escape(baslik)}</h1><p>{html.escape(aciklama)}</p></div>',
        unsafe_allow_html=True,
    )


TIMELINE_CSS = """
<style>
.ea-tl { display:grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin: 0.5rem 0 1rem 0; }
.ea-tl > div { background:#FBF9F4; border:1px solid #D9D2C3; border-radius:12px; padding:14px 16px; position:relative; }
.ea-tl > div::before { content:""; position:absolute; top:-6px; left:16px; width:10px; height:10px; border-radius:50%; background:#1F6670; }
.ea-tl .y { font-family: Newsreader, Georgia, serif; font-size:1.7rem; color:#1B3A57; line-height:1; }
.ea-tl .b { font-size:0.85rem; color:#4A4A48; margin-top:6px; line-height:1.4; }
.ea-tl .k { font-size:0.72rem; color:#7A7468; letter-spacing:.06em; text-transform:uppercase; margin-top:8px; }
</style>
"""


def zaman_cizgisi(olaylar: list[tuple[str, str, str]]) -> None:
    """Yatay zaman çizelgesi. Her olay: (yıl/tarih, başlık, açıklama)."""
    kartlar = "".join(
        f'<div><div class="y">{html.escape(y)}</div><div class="b"><b>{html.escape(b)}</b><br>{html.escape(c)}</div></div>'
        for y, b, c in olaylar
    )
    st.markdown(TIMELINE_CSS + f'<div class="ea-tl">{kartlar}</div>', unsafe_allow_html=True)
