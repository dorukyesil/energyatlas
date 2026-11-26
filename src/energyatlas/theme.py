"""Görsel tema: renk paleti, Plotly şablonu ve Streamlit CSS'i.

Tüm sayfalar ve grafikler bu modülden renk ve stil alır. Renk değiştirmek için
yalnızca bu dosyadaki sabitleri düzenlemek yeterlidir.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Ana palet
LACIVERT = "#0B2545"
TURKUAZ = "#13A89E"
KEHRIBAR = "#F4B942"
MERCAN = "#E76F51"
ARDUVAZ = "#334155"
MAVI = "#3A7CA5"
GRI = "#64748B"
ACIK_GRI = "#CBD5E1"
ZEMIN = "#F8FAFC"

# Kaynak renkleri (grafikler arasında tutarlı kullanılır)
KAYNAK_RENK = {
    "Termik": ARDUVAZ,
    "Güneş": KEHRIBAR,
    "Rüzgar": TURKUAZ,
    "Diğer Yenilenebilir": ACIK_GRI,
    "Toplam": LACIVERT,
    "Türkiye": MERCAN,
    "OECD": MAVI,
    "Dünya": GRI,
}

SERI_RENKLERI = [LACIVERT, TURKUAZ, KEHRIBAR, MERCAN, MAVI, ARDUVAZ, "#8B5CF6", "#94A3B8"]

SABLON = "enerji"


def _sablon_olustur() -> go.layout.Template:
    sablon = go.layout.Template()
    sablon.layout = go.Layout(
        font=dict(family="Inter, 'Segoe UI', system-ui, sans-serif", size=13, color=ARDUVAZ),
        title=dict(font=dict(size=18, color=LACIVERT), x=0.01, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=SERI_RENKLERI,
        xaxis=dict(showgrid=False, linecolor="#E2E8F0", ticks="", zeroline=False),
        yaxis=dict(gridcolor="#EEF2F7", linecolor="rgba(0,0,0,0)", zeroline=False),
        legend=dict(orientation="h", y=-0.18, x=0, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", bordercolor=ACIK_GRI, font=dict(color=ARDUVAZ)),
        bargap=0.35,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return sablon


pio.templates[SABLON] = _sablon_olustur()

CSS = f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }}
  .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }}
  h1 {{ color: {LACIVERT}; font-weight: 800; letter-spacing: -0.02em; }}
  h2, h3 {{ color: {LACIVERT}; font-weight: 700; letter-spacing: -0.01em; }}
  [data-testid="stCaptionContainer"] {{ color: {GRI}; font-size: 0.95rem; }}

  /* KPI kartları */
  [data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-left: 4px solid {TURKUAZ};
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(11,37,69,0.04), 0 4px 14px rgba(11,37,69,0.05);
  }}
  [data-testid="stMetricLabel"] p {{ color: {GRI}; font-weight: 600; font-size: 0.85rem; }}
  [data-testid="stMetricValue"] {{ color: {LACIVERT}; font-weight: 800; font-size: 1.6rem; white-space: normal; line-height: 1.2; }}
  [data-testid="stMetricLabel"] {{ white-space: normal; }}
  [data-testid="stMetricLabel"] p {{ overflow: visible; text-overflow: clip; white-space: normal; line-height: 1.3; }}

  /* Grafik kartları */
  [data-testid="stPlotlyChart"] {{
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 10px 12px 4px 12px;
    box-shadow: 0 1px 2px rgba(11,37,69,0.04);
    margin-bottom: 1rem;
  }}

  /* Bilgi kutuları */
  [data-testid="stAlert"] {{ border-radius: 12px; }}

  /* Kenar çubuğu */
  [data-testid="stSidebar"] {{ background: {ZEMIN}; border-right: 1px solid #E2E8F0; }}
  [data-testid="stSidebarNavLink"] {{ border-radius: 10px; }}

  /* Hero bloğu */
  .ea-hero {{
    background: linear-gradient(135deg, {LACIVERT} 0%, #13406E 60%, {TURKUAZ} 140%);
    color: #ffffff;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 30px rgba(11,37,69,0.18);
  }}
  .ea-hero h1 {{ color: #ffffff; margin: 0 0 6px 0; font-size: 2.1rem; }}
  .ea-hero p {{ color: #DCE7F3; margin: 0; font-size: 1.02rem; }}

  /* Kategori kartları */
  .ea-kart {{
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 250px;
    box-shadow: 0 1px 2px rgba(11,37,69,0.04);
  }}
  .ea-kart .ea-ikon {{ font-size: 1.6rem; }}
  .ea-kart h4 {{ color: {LACIVERT}; margin: 6px 0 6px 0; font-weight: 700; }}
  .ea-kart ul {{ margin: 0; padding-left: 1.1rem; color: {ARDUVAZ}; font-size: 0.93rem; line-height: 1.6; }}

  #MainMenu, footer {{ visibility: hidden; }}
</style>
"""


def uygula() -> None:
    """Her sayfa çalıştırmasında temayı ve CSS'i uygular."""
    pio.templates.default = SABLON
    st.markdown(CSS, unsafe_allow_html=True)
