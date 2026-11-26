"""Plotly grafik üreticileri. Streamlit'e bağımlı değildir, böylece test edilebilir."""

import pandas as pd
import plotly.graph_objects as go

RENKLER = {
    "Termik": "#1f2937",
    "Güneş": "#f5b400",
    "Rüzgar": "#2a7f62",
    "Diğer Yenilenebilir": "#b8c2cc",
    "Toplam": "#1f4e79",
    "Türkiye": "#c8102e",
    "OECD": "#1f4e79",
    "Dünya": "#6b7280",
}

KAYNAK_KOLONLARI = {
    "Termik": "termik_pct",
    "Güneş": "gunes_pct",
    "Rüzgar": "ruzgar_pct",
    "Diğer Yenilenebilir": "diger_ye_pct",
}


def _duzenle(fig: go.Figure, baslik: str, y_baslik: str) -> go.Figure:
    fig.update_layout(
        title=baslik,
        yaxis_title=y_baslik,
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified",
    )
    return fig


def toplam_cubuk(df: pd.DataFrame, deger: str, baslik: str, y_baslik: str) -> go.Figure:
    """Dönem bazında toplam değerleri gösteren sütun grafiği."""
    fig = go.Figure(
        go.Bar(
            x=df["donem"],
            y=df[deger],
            marker_color=RENKLER["Toplam"],
            text=df[deger],
            texttemplate="%{text:,.1f}",
            textposition="outside",
            hovertemplate="%{x}: %{y:,.1f}<extra></extra>",
        )
    )
    return _duzenle(fig, baslik, y_baslik)


def pay_yiginli_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Kaynak paylarını (%) yığılmış sütunlarla gösterir."""
    fig = go.Figure()
    for etiket, kolon in KAYNAK_KOLONLARI.items():
        fig.add_trace(
            go.Bar(
                name=etiket,
                x=df["donem"],
                y=df[kolon],
                marker_color=RENKLER[etiket],
                hovertemplate=f"{etiket}: %{{y}}%<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100])
    return _duzenle(fig, baslik, "Pay (%)")


def tuketim_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Tüketim (TWh) sütun grafiği. Olay etiketleri hover'da gösterilir."""
    etiketler = df["olay"].fillna("")
    fig = go.Figure(
        go.Bar(
            x=df["donem"],
            y=df["tuketim_twh"],
            marker_color=RENKLER["Toplam"],
            text=df["tuketim_twh"],
            texttemplate="%{text:,.0f}",
            textposition="outside",
            customdata=etiketler,
            hovertemplate="%{x}: %{y:,.0f} TWh<br>%{customdata}<extra></extra>",
        )
    )
    return _duzenle(fig, baslik, "TWh")


def kisi_basina_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Kişi başına tüketimi karşılaştıran yatay çubuk grafiği."""
    renkler = [RENKLER.get(k, RENKLER["Toplam"]) for k in df["kaynak"]]
    fig = go.Figure(
        go.Bar(
            x=df["kwh_kisi"],
            y=df["kaynak"],
            orientation="h",
            marker_color=renkler,
            text=df["kwh_kisi"],
            texttemplate="%{text:,.0f} kWh",
            textposition="outside",
        )
    )
    fig.update_layout(
        title=baslik,
        template="plotly_white",
        xaxis_title="kWh / kişi",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=40, t=60, b=10),
    )
    return fig


def hedef_karsilastirma(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Toplam kurulu güç hedeflerini senaryolara göre karşılaştırır."""
    senaryolar = {
        "2025 gerçekleşen": "gerceklesen_2025_gw",
        "2028 Stratejik Plan": "hedef_2028_stratejik_plan_gw",
        "2035 Ulusal Enerji Planı": "hedef_2035_ulusal_enerji_plani_gw",
        "2035 YE Yol Haritası": "hedef_2035_yenilenebilir_yol_haritasi_gw",
    }
    satir = df.set_index("kaynak")
    fig = go.Figure()
    for kaynak in ["Güneş", "Rüzgar", "Toplam Termik"]:
        if kaynak not in satir.index:
            continue
        fig.add_trace(
            go.Bar(
                name=kaynak,
                x=list(senaryolar.keys()),
                y=[satir.loc[kaynak, kolon] for kolon in senaryolar.values()],
                marker_color=RENKLER.get(kaynak.replace("Toplam ", ""), "#6b7280"),
                hovertemplate=f"{kaynak}: %{{y:,.1f}} GW<extra></extra>",
            )
        )
    fig.update_layout(barmode="group")
    return _duzenle(fig, baslik, "GW")


def pay_halkasi(etiketler: list[str], degerler: list[float], baslik: str) -> go.Figure:
    """Tek bir senaryo için kaynak payını halka grafikle gösterir."""
    fig = go.Figure(
        go.Pie(
            labels=etiketler,
            values=degerler,
            hole=0.55,
            marker=dict(colors=[RENKLER.get(e, "#9ca3af") for e in etiketler]),
            hovertemplate="%{label}: %{value:,.1f} GW (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(title=baslik, template="plotly_white", margin=dict(l=10, r=10, t=60, b=10))
    return fig
