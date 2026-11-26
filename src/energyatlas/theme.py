"""Görsel tema: renk paleti, Plotly şablonu ve Streamlit CSS'i.

Tasarım dili: sıcak kağıt zemin, koyu mürekkep mavisi çizgiler, serif başlıklar,
ince ayraçlar ve sakin renkler. Tüm sayfalar ve grafikler renkleri bu dosyadan alır.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Zemin ve metin
KAGIT = "#F4F0E8"
KAGIT_2 = "#ECE6DA"
KAGIT_KART = "#FBF9F4"
CIZGI = "#D9D2C3"
METIN = "#2B2B2B"
SOLUK = "#7A7468"

# Ana renkler
MUREKKEP = "#1B3A57"
TURKUAZ = "#1F6670"
PAS = "#B4432A"
OKRA = "#B9801F"
ZEYTIN = "#5B6B2F"
ADACAYI = "#A9B8B5"
CELIK = "#6C8CA6"

# Geriye dönük uyumluluk için eski adlar
LACIVERT = MUREKKEP
KEHRIBAR = OKRA
MERCAN = PAS
ARDUVAZ = "#4A4A48"
MAVI = CELIK
GRI = "#8A8578"
ACIK_GRI = ADACAYI
ZEMIN = KAGIT

# Kaynak renkleri (grafikler arasında tutarlı kullanılır)
KAYNAK_RENK = {
    "Termik": "#4A4A48",
    "Güneş": "#D9A21B",
    "Rüzgar": TURKUAZ,
    "Diğer Yenilenebilir": ADACAYI,
    "Hidro": CELIK,
    "Jeotermal": "#8B5CF6",
    "Rüzgar + jeotermal": TURKUAZ,
    "Toplam": MUREKKEP,
    "Türkiye": PAS,
    "OECD": CELIK,
    "Dünya": "#8A8578",
}

SERI_RENKLERI = [MUREKKEP, TURKUAZ, OKRA, PAS, CELIK, ZEYTIN, "#8A8578", ADACAYI]

# Sapma (negatif-pozitif) ve sıralı renk skalaları
SAPMA_SKALA = [[0.0, PAS], [0.5, "#EFEAE0"], [1.0, TURKUAZ]]
SIRALI_TURKUAZ = [[0.0, "#EFEAE0"], [1.0, TURKUAZ]]
SIRALI_PAS = [[0.0, "#F1E7DA"], [1.0, PAS]]

SABLON = "enerji"
SERIF = "'Newsreader', 'Source Serif 4', Georgia, 'Times New Roman', serif"
SANS = "'Inter', 'Segoe UI', system-ui, sans-serif"


def _sablon_olustur() -> go.layout.Template:
    sablon = go.layout.Template()
    sablon.layout = go.Layout(
        font=dict(family=SANS, size=12, color="#4A4A48"),
        title=dict(font=dict(family="Georgia, serif", size=17, color=MUREKKEP), x=0.0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=SERI_RENKLERI,
        separators=",.",
        xaxis=dict(showgrid=False, linecolor=CIZGI, ticks="", zeroline=False, tickfont=dict(color=SOLUK)),
        yaxis=dict(gridcolor="#E7E1D3", griddash="dot", linecolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(color=SOLUK)),
        legend=dict(orientation="h", y=-0.2, x=0, bgcolor="rgba(0,0,0,0)", font=dict(color=SOLUK)),
        hoverlabel=dict(bgcolor=KAGIT_KART, bordercolor=CIZGI, font=dict(color=METIN, family=SANS)),
        bargap=0.45,
        margin=dict(l=10, r=10, t=56, b=10),
    )
    return sablon


pio.templates[SABLON] = _sablon_olustur()

CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap');

  html, body, [class*="css"] {{ font-family: {SANS}; color: {METIN}; }}
  .stApp {{ background: {KAGIT}; }}
  .block-container {{ padding-top: 4.2rem; padding-bottom: 4rem; max-width: 1200px; }}

  h1, h2, h3, h4 {{ font-family: {SERIF}; color: {MUREKKEP}; font-weight: 500; letter-spacing: -0.01em; }}
  h1 {{ font-size: 2.6rem; line-height: 1.1; }}
  h2 {{ font-size: 1.7rem; }}
  h3 {{ font-size: 1.3rem; }}
  [data-testid="stCaptionContainer"] {{ color: {SOLUK}; }}

  /* Üstbilgi ve bölüm başlıkları */
  .ea-eyebrow {{ font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: {TURKUAZ}; font-weight: 600; margin-bottom: 0.4rem; }}
  .ea-sayfa h1 {{ margin: 0 0 0.4rem 0; font-size: 2.8rem; }}
  .ea-sayfa p {{ color: {SOLUK}; margin: 0; max-width: 760px; font-size: 1.02rem; line-height: 1.55; }}
  .ea-bolum {{ border-top: 1px solid {MUREKKEP}; margin-top: 2.4rem; padding-top: 0.7rem; }}
  .ea-bolum .ea-no {{ font-family: ui-monospace, 'SFMono-Regular', Menlo, monospace; font-size: 0.7rem; color: {PAS}; }}
  .ea-bolum h2 {{ margin: 0.15rem 0 0.25rem 0; }}
  .ea-bolum p {{ color: {SOLUK}; margin: 0 0 0.6rem 0; max-width: 760px; line-height: 1.55; font-size: 0.95rem; }}
  .ea-kaynak {{ color: #9A9484; font-size: 0.8rem; margin: -0.2rem 0 1rem 0; }}

  /* Göstergeler (st.metric) */
  [data-testid="stMetric"] {{
    background: transparent; border: none; border-top: 1px solid {CIZGI};
    border-radius: 0; padding: 0.7rem 0 0.4rem 0; box-shadow: none;
  }}
  [data-testid="stMetricLabel"] p {{ color: {SOLUK}; font-size: 0.8rem; font-weight: 500; white-space: normal; line-height: 1.3; }}
  [data-testid="stMetricValue"] {{ font-family: {SERIF}; color: {MUREKKEP}; font-weight: 400; font-size: 2.1rem; white-space: normal; line-height: 1.15; }}

  [data-testid="stMetricDelta"] svg {{ display: none; }}
  [data-testid="stMetricDelta"] > div {{ font-size: 0.82rem; }}

  /* Grafikler: düz, çerçevesiz */
  [data-testid="stPlotlyChart"] {{ background: transparent; border: none; padding: 0; margin-bottom: 0.6rem; }}

  /* Kartlar */
  [data-testid="stVerticalBlockBorderWrapper"]:has(.ea-kart-isaret):not(:has([data-testid="stVerticalBlockBorderWrapper"])) {{
    background: {KAGIT_KART}; border: 1px solid {CIZGI}; border-radius: 10px; min-height: 360px;
  }}
  .ea-kart-baslik {{ font-family: {SERIF}; font-size: 1.35rem; color: {MUREKKEP}; margin: 0.1rem 0 0.2rem 0; }}
  .ea-kart-madde {{ color: #4A4A48; font-size: 0.9rem; line-height: 1.55; }}
  .ea-kart-aciklama {{ color: {SOLUK}; font-size: 0.88rem; margin-bottom: 0.5rem; line-height: 1.45; }}
  [data-testid="stPageLink"] a {{ padding: 0.15rem 0; }}

  /* Ana sayfa */
  .ea-hero-no {{ font-family: {SERIF}; color: {TURKUAZ}; font-size: 5.2rem; line-height: 1; margin: 0.4rem 0 0.2rem 0; }}
  .ea-hero-no small {{ font-size: 1.6rem; color: {SOLUK}; margin-left: 0.35rem; }}
  .ea-hero-etiket {{ font-weight: 600; font-size: 0.9rem; color: {MUREKKEP}; }}
  .ea-hero-not {{ color: {SOLUK}; font-size: 0.85rem; margin-top: 0.3rem; }}
  .ea-hero-baslik {{ font-family: {SERIF}; font-size: 4.2rem; color: {MUREKKEP}; line-height: 1.02; margin: 0.2rem 0 0.4rem 0; font-weight: 500; letter-spacing: -0.02em; }}

  /* KPI şeridi */
  .ea-serit {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); border-top: 1px solid {MUREKKEP}; margin: 1.4rem 0 0.4rem 0; }}
  .ea-serit > div {{ padding: 0.9rem 0.9rem 0.8rem 0.9rem; border-right: 1px solid {CIZGI}; }}
  .ea-serit > div:last-child {{ border-right: none; }}
  .ea-serit .e {{ color: {SOLUK}; font-size: 0.78rem; }}
  .ea-serit .d {{ font-family: {SERIF}; font-size: 2rem; color: {MUREKKEP}; line-height: 1.15; margin: 0.15rem 0; }}
  .ea-serit .d small {{ font-size: 0.95rem; color: {SOLUK}; margin-left: 0.2rem; }}
  .ea-serit .a {{ font-size: 0.78rem; color: {SOLUK}; }}
  .ea-serit .a.p {{ color: {TURKUAZ}; }}
  .ea-serit .a.n {{ color: {PAS}; }}
  .ea-serit svg {{ display: block; margin-top: 0.4rem; }}

  /* Kenar çubuğu */
  [data-testid="stSidebar"] {{ background: {KAGIT_2}; border-right: 1px solid {CIZGI}; }}
  [data-testid="stSidebarNavLink"] {{ border-radius: 8px; }}

  [data-testid="stAlert"] {{ border-radius: 10px; }}
  [data-testid="stExpander"] {{ border: 1px solid {CIZGI}; border-radius: 10px; background: {KAGIT_KART}; }}
  #MainMenu, footer {{ visibility: hidden; }}
</style>
"""


def uygula() -> None:
    """Her sayfa çalıştırmasında temayı ve CSS'i uygular."""
    pio.templates.default = SABLON
    st.markdown(CSS, unsafe_allow_html=True)
