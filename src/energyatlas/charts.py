"""Plotly grafik üreticileri. Streamlit'e bağımlı değildir, böylece test edilebilir."""

import pandas as pd
import plotly.graph_objects as go

from src.energyatlas.theme import KAYNAK_RENK, SABLON, SAPMA_SKALA, SIRALI_PAS, SIRALI_TURKUAZ
from src.energyatlas.theme import PAS as PAS
from src.energyatlas.theme import TURKUAZ
from src.energyatlas.theme import PAS as theme_renk_negatif
from src.energyatlas.theme import TURKUAZ as theme_renk_pozitif

RENKLER = KAYNAK_RENK

KAYNAK_KOLONLARI = {
    "Termik": "termik_pct",
    "Güneş": "gunes_pct",
    "Rüzgar": "ruzgar_pct",
    "Diğer Yenilenebilir": "diger_ye_pct",
}


def _duzenle(fig: go.Figure, baslik: str, y_baslik: str) -> go.Figure:
    # Az sayıda kategori varsa tüm etiketleri göster (ör. her yıl)
    if fig.data and fig.data[0].type == "bar" and getattr(fig.data[0], "orientation", "v") != "h":
        kategoriler = list(dict.fromkeys(str(v) for v in fig.data[0].x))
        if 0 < len(kategoriler) <= 14:
            fig.update_xaxes(type="category", tickmode="array", tickvals=kategoriler, ticktext=kategoriler, tickangle=0)
    fig.update_layout(
        title=baslik,
        yaxis_title=y_baslik,
        template=SABLON,
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
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title=baslik,
        template=SABLON,
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
                marker_color=RENKLER.get(kaynak.replace("Toplam ", ""), "#8A8578"),
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
            sort=False,
            marker=dict(colors=[RENKLER.get(e, "#A9B8B5") for e in etiketler]),
            hovertemplate="%{label}: %{value:,.1f} GW (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(title=baslik, template=SABLON, margin=dict(l=10, r=10, t=60, b=10))
    return fig


def sirket_yigin_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Şirketlerin depolamalı GES ve RES kapasitelerini (MW) yığılmış gösterir."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Güneş (GES)",
            x=df["sirket"],
            y=df["ges_mw"],
            marker_color=RENKLER["Güneş"],
            hovertemplate="GES: %{y:,.0f} MW<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Rüzgar (RES)",
            x=df["sirket"],
            y=df["res_mw"],
            marker_color=RENKLER["Rüzgar"],
            hovertemplate="RES: %{y:,.0f} MW<extra></extra>",
        )
    )
    fig.update_layout(barmode="stack")
    return _duzenle(fig, baslik, "MW")


def yillik_pay_cubuk(df: pd.DataFrame, donem: str, baslik: str) -> go.Figure:
    """Devreye giriş yılına göre güneş ve rüzgar paylarını (%) gösterir."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Güneş",
            x=df[donem],
            y=df["gunes_pct"],
            marker_color=RENKLER["Güneş"],
            text=df["gunes_pct"],
            texttemplate="%{text}%",
            hovertemplate="Güneş: %{y}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Rüzgar",
            x=df[donem],
            y=df["ruzgar_pct"],
            marker_color=RENKLER["Rüzgar"],
            text=df["ruzgar_pct"],
            texttemplate="%{text}%",
            hovertemplate="Rüzgar: %{y}%<extra></extra>",
        )
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100])
    return _duzenle(fig, baslik, "Pay (%)")


def iki_donem_karsilastirma(df: pd.DataFrame, kategori: str, donem: str, deger: str, baslik: str, birim: str) -> go.Figure:
    """Gösterge bazında iki yıl (örn. 2025 ve 2035) değerlerini yan yana gösterir."""
    fig = go.Figure()
    for yil, renk in [("2025", "#A9B8B5"), ("2035", RENKLER["Toplam"])]:
        alt = df[df[donem].astype(str) == yil]
        fig.add_trace(
            go.Bar(
                name=yil,
                x=alt[kategori],
                y=alt[deger],
                marker_color=renk,
                text=alt[deger],
                texttemplate="%{text:,.0f}",
                textposition="outside",
                hovertemplate=f"{yil}: %{{y:,.0f}} {birim}<extra></extra>",
            )
        )
    fig.update_layout(barmode="group")
    return _duzenle(fig, baslik, birim)


def sematik_profil(saat: list[int], talep: list[float], termik: list[float], ruzgar: list[float], gunes: list[float], depolama: list[float], baslik: str) -> go.Figure:
    """Şematik günlük profil. Gerçek veri değildir; kavramı göstermek için kullanılır."""
    fig = go.Figure()
    for isim, seri, renk in [
        ("Termik (baz yük)", termik, RENKLER["Termik"]),
        ("Rüzgar", ruzgar, RENKLER["Rüzgar"]),
        ("Güneş", gunes, RENKLER["Güneş"]),
        ("Depolama (boşaltma)", depolama, "#1B3A57"),
    ]:
        fig.add_trace(go.Scatter(name=isim, x=saat, y=seri, mode="lines", line=dict(color=renk, width=2), stackgroup=None))
    fig.add_trace(go.Scatter(name="Elektrik talebi", x=saat, y=talep, mode="lines", line=dict(color="#B4432A", width=3, dash="dot")))
    fig.update_xaxes(title="Saat", dtick=3)
    return _duzenle(fig, baslik, "Göreli güç (şematik)")


def on_lisans_yillik(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Ön lisans bitiş yılına göre kapasiteyi (MWe) teknolojiye göre gruplar."""
    fig = go.Figure()
    for teknoloji, renk in [("GES", RENKLER["Güneş"]), ("RES", RENKLER["Rüzgar"])]:
        alt = df[df["teknoloji"] == teknoloji]
        fig.add_trace(
            go.Bar(
                name="Depolamalı " + teknoloji,
                x=alt["bitis_yili"].astype(str),
                y=alt["kapasite_mwe"],
                marker_color=renk,
                hovertemplate=teknoloji + ": %{y:,.0f} MWe<br>%{customdata} proje<extra></extra>",
                customdata=alt["proje_adedi"],
            )
        )
    fig.update_layout(barmode="group")
    return _duzenle(fig, baslik, "Kapasite (MWe)")


def isletmedeki_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """İşletmedeki depolama kapasitesini (MWh) şirketlere göre yatay çubukla gösterir."""
    renkler = [RENKLER["Güneş"] if t == "Güneş" else RENKLER["Rüzgar"] for t in df["tesis_turu"]]
    fig = go.Figure(
        go.Bar(
            x=df["kapasite_mwh"],
            y=df["lisans_sahibi"],
            orientation="h",
            marker_color=renkler,
            text=df["kapasite_mwh"],
            texttemplate="%{text:,.1f} MWh",
            textposition="outside",
            cliponaxis=False,
            customdata=df["guc_mwe"],
            hovertemplate="%{y}<br>Kapasite: %{x:,.1f} MWh<br>Güç: %{customdata:,.1f} MWe<extra></extra>",
        )
    )
    fig.update_layout(
        title=baslik,
        template=SABLON,
        xaxis_title="MWh",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=60, t=60, b=10),
    )
    return fig


def tarife_karsilastirma(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Seçilen gruplar için gündüz, puant, gece tarifelerini gruplu çubukla gösterir."""
    fig = go.Figure()
    for kolon, etiket, renk in [
        ("gunduz", "Gündüz", "#D9A21B"),
        ("puant", "Puant", "#B4432A"),
        ("gece", "Gece", "#1B3A57"),
    ]:
        fig.add_trace(
            go.Bar(
                name=etiket,
                x=df["grup"],
                y=df[kolon],
                marker_color=renk,
                hovertemplate=etiket + ": %{y:,.2f} kr/kWh<extra></extra>",
            )
        )
    fig.update_layout(barmode="group")
    fig = _duzenle(fig, baslik, "kr/kWh")
    fig.update_xaxes(tickangle=-30)
    return fig


def ptf_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """PTF (USD/MWh) yıllık değerleri. 2022 zirvesi vurgulanır."""
    renkler = ["#B4432A" if d == "2022" else RENKLER["Toplam"] for d in df["donem"]]
    fig = go.Figure(
        go.Bar(
            x=df["donem"],
            y=df["ptf_usd_mwh"],
            marker_color=renkler,
            text=df["ptf_usd_mwh"],
            textposition="outside",
            hovertemplate="%{x}: %{y} USD/MWh<extra></extra>",
        )
    )
    return _duzenle(fig, baslik, "USD/MWh")


def deger_cubuk(etiketler: list[str], degerler: list[float], renkler: list[str], baslik: str, y_baslik: str, sablon: str = "%{text:,.1f}") -> go.Figure:
    """Etiket-değer çifti için renkli sütun grafiği."""
    fig = go.Figure(
        go.Bar(
            x=etiketler,
            y=degerler,
            marker_color=renkler,
            text=degerler,
            texttemplate=sablon,
            textposition="outside",
            hovertemplate="%{x}: %{y:,.2f}<extra></extra>",
        )
    )
    return _duzenle(fig, baslik, y_baslik)


def yekdem_cizgi(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Her kaynak için aylık YEKDEM fiyatını (kr/kWh) çizgiyle gösterir."""
    fig = go.Figure()
    for kaynak, alt in df.groupby("kaynak", sort=False):
        fig.add_trace(
            go.Scatter(
                name=kaynak,
                x=alt["donem"],
                y=alt["fiyat_kr_kwh"],
                mode="lines+markers",
                hovertemplate=kaynak + ": %{y:,.2f} kr/kWh<extra></extra>",
            )
        )
    return _duzenle(fig, baslik, "TL kr/kWh")


def dunya_kurulu_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Dünya toplam kurulu güç ve güneş kapasitesini yan yana gösterir."""
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Toplam kapasite", x=df["donem"], y=df["toplam_gw"], marker_color="#8A8578",
                         text=df["toplam_gw"], texttemplate="%{text:,.0f}", textposition="outside"))
    fig.add_trace(go.Bar(name="Güneş", x=df["donem"], y=df["gunes_gw"], marker_color=RENKLER["Güneş"],
                         text=df["gunes_gw"], texttemplate="%{text:,.0f}", textposition="outside"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickformat=",.0f")
    return _duzenle(fig, baslik, "GW")


def dunya_pay_nokta(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Güneşin toplam ve yenilenebilir kurulu güç içindeki payını (%) gösterir."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Güneş / Toplam", x=df["donem"], y=df["gunes_toplam_pct"], mode="lines+markers+text",
                             text=df["gunes_toplam_pct"], texttemplate="%{text}%", textposition="top center",
                             marker=dict(size=10, color="#1B3A57")))
    fig.add_trace(go.Scatter(name="Güneş / Yenilenebilir", x=df["donem"], y=df["gunes_yenilenebilir_pct"], mode="lines+markers+text",
                             text=df["gunes_yenilenebilir_pct"], texttemplate="%{text}%", textposition="top center",
                             marker=dict(size=10, color="#6C8CA6")))
    fig.update_yaxes(range=[0, 80], ticksuffix="%")
    return _duzenle(fig, baslik, "Pay (%)")


def ulke_yatay_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Ülkelerin güneş kurulu gücünü yatay çubukla gösterir; Türkiye vurgulanır."""
    renkler = ["#B4432A" if u == "Türkiye" else RENKLER["Güneş"] for u in df["ulke"]]
    fig = go.Figure(
        go.Bar(
            x=df["gunes_gw"],
            y=df["ulke"],
            orientation="h",
            marker_color=renkler,
            text=df["gunes_gw"],
            texttemplate="%{text:,.0f} GW",
            textposition="outside",
            cliponaxis=False,
            customdata=df["yil_notu"],
            hovertemplate="%{y}: %{x:,.0f} GW<br>%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(title=baslik, template=SABLON, xaxis_title="GW",
                      yaxis=dict(autorange="reversed"), margin=dict(l=10, r=60, t=60, b=10))
    return fig


def kuresel_yatirim_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Toplam enerji, temiz enerji ve güneş yatırımlarını (milyar USD) gruplu gösterir."""
    fig = go.Figure()
    for kolon, etiket, renk in [
        ("toplam_mlrd_usd", "Toplam enerji yatırımları", "#1B3A57"),
        ("temiz_enerji_mlrd_usd", "Temiz enerji yatırımları", "#6C8CA6"),
        ("gunes_mlrd_usd", "Güneş yatırımları", RENKLER["Güneş"]),
    ]:
        fig.add_trace(
            go.Bar(
                name=etiket,
                x=df["yil"].astype(str),
                y=df[kolon],
                marker_color=renk,
                text=df[kolon],
                texttemplate="%{text:,.0f}",
                textposition="outside",
                hovertemplate=etiket + ": %{y:,.0f} milyar USD<extra></extra>",
            )
        )
    fig.update_layout(barmode="group")
    return _duzenle(fig, baslik, "Milyar USD")


def bolge_yigin_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """Bölgelere göre küresel güneş yatırımlarını yığılmış gösterir. Diğer bölgeler toplamdan hesaplanır."""
    diger = df["toplam_mlrd_usd"] - df["asya_pasifik_mlrd_usd"] - df["kuzey_amerika_mlrd_usd"] - df["avrupa_mlrd_usd"]
    fig = go.Figure()
    for etiket, deger, renk in [
        ("Asya ve Pasifik", df["asya_pasifik_mlrd_usd"], "#4A4A48"),
        ("Kuzey Amerika", df["kuzey_amerika_mlrd_usd"], "#6C8CA6"),
        ("Avrupa", df["avrupa_mlrd_usd"], "#A9B8B5"),
        ("Diğer bölgeler (hesaplanan)", diger, "#C9C3B4"),
    ]:
        fig.add_trace(
            go.Bar(
                name=etiket,
                x=df["yil"].astype(str),
                y=deger,
                marker_color=renk,
                hovertemplate=etiket + ": %{y:,.0f} milyar USD<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    return _duzenle(fig, baslik, "Milyar USD")


def cizgi_alan(df: pd.DataFrame, x: str, y: str, baslik: str, y_baslik: str, birim: str = "", hareketli_ortalama: int | None = None) -> go.Figure:
    """Sade çizgi grafik: ince lacivert çizgi, soluk alan, kesikli ortalama ve son değer etiketi."""
    fig = go.Figure()
    yillar = df[x].astype(int) if df[x].astype(str).str.fullmatch(r"\d{4}").all() else df[x].astype(str)
    fig.add_trace(
        go.Scatter(
            x=yillar,
            y=df[y],
            mode="lines+markers",
            line=dict(color=RENKLER["Toplam"], width=2.2),
            marker=dict(size=5, color=RENKLER["Toplam"]),
            fill="tozeroy",
            fillcolor="rgba(27,58,87,0.08)",
            hovertemplate="%{x}: %{y:,.1f} " + birim + "<extra></extra>",
            name="Değer",
        )
    )
    if hareketli_ortalama:
        ort = df[y].rolling(hareketli_ortalama, min_periods=hareketli_ortalama).mean()
        fig.add_trace(
            go.Scatter(
                x=yillar,
                y=ort,
                mode="lines",
                line=dict(color="#4A4A48", width=1.3, dash="dot"),
                name=f"{hareketli_ortalama} dönem ortalaması",
                hovertemplate="%{y:,.1f}<extra>ortalama</extra>",
            )
        )
    son = df.iloc[-1]
    tam_sayi = bool((df[y].dropna() % 1 == 0).all())
    son_metin = f"{son[y]:,.0f}" if tam_sayi else f"{son[y]:,.1f}"
    fig.add_annotation(
        x=int(son[x]) if str(son[x]).isdigit() else str(son[x]), y=son[y], text=f"<b>{son_metin}</b>".replace(",", "§").replace(".", ",").replace("§", "."),
        showarrow=False, xanchor="left", xshift=8, font=dict(color=RENKLER["Toplam"], size=13),
    )
    return _duzenle(fig, baslik, y_baslik)


def yillik_degisim_cubuk(df: pd.DataFrame, x: str, degisim: str, baslik: str) -> go.Figure:
    """Yıllık değişimi (%) artış ve düşüşü farklı renklerde gösteren iki yönlü sütun grafiği."""
    renkler = [theme_renk_pozitif if v >= 0 else theme_renk_negatif for v in df[degisim]]
    fig = go.Figure(
        go.Bar(
            x=df[x].astype(str),
            y=df[degisim],
            marker_color=renkler,
            text=[f"{v:+.1f}%".replace(".", ",") for v in df[degisim]],
            textposition="outside",
            textfont=dict(size=11),
            cliponaxis=False,
            hovertemplate="%{x}: %{y:+,.1f}%<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#8A8578", line_width=1)
    return _duzenle(fig, baslik, "Yıllık değişim (%)")


def isi_haritasi(matris: pd.DataFrame, baslik: str, skala: str = "turkuaz", sablon: str = "%{z:,.1f}", z_baslik: str = "") -> go.Figure:
    """Satır x sütun ısı haritası. skala: 'turkuaz', 'pas' veya 'sapma' (negatif-pozitif)."""
    skalalar = {"turkuaz": SIRALI_TURKUAZ, "pas": SIRALI_PAS, "sapma": SAPMA_SKALA}
    fig = go.Figure(
        go.Heatmap(
            z=matris.values,
            x=[str(c) for c in matris.columns],
            y=[str(i) for i in matris.index],
            colorscale=skalalar[skala],
            xgap=2,
            ygap=2,
            text=matris.values,
            texttemplate=sablon,
            textfont=dict(size=11),
            colorbar=dict(title=z_baslik, thickness=10, len=0.8, outlinewidth=0),
            hovertemplate="%{y}<br>%{x}: %{z:,.1f}<extra></extra>",
            zmid=0 if skala == "sapma" else None,
        )
    )
    fig.update_layout(title=baslik, template=SABLON, yaxis=dict(autorange="reversed", automargin=True), margin=dict(l=10, r=10, t=56, b=10))
    return fig


def depolama_kabarcik(df: pd.DataFrame, baslik: str) -> go.Figure:
    """İşletmedeki depolama tesislerini güç ve süre ekseninde baloncuk olarak gösterir. Baloncuk boyutu kapasitedir."""
    fig = go.Figure()
    for tur, renk in [("Güneş", RENKLER["Güneş"]), ("Rüzgar", RENKLER["Rüzgar"])]:
        alt = df[df["tesis_turu"] == tur]
        sure = alt["kapasite_mwh"] / alt["guc_mwe"]
        fig.add_trace(
            go.Scatter(
                name=tur,
                x=alt["guc_mwe"],
                y=sure,
                mode="markers",
                marker=dict(size=alt["kapasite_mwh"], sizemode="area", sizeref=2.0 * df["kapasite_mwh"].max() / (48.0**2), sizemin=6, color=renk, opacity=0.85, line=dict(color="white", width=1)),
                customdata=alt[["lisans_sahibi", "kapasite_mwh"]],
                hovertemplate="%{customdata[0]}<br>Güç: %{x:,.1f} MWe<br>Süre: %{y:,.2f} saat<br>Kapasite: %{customdata[1]:,.1f} MWh<extra></extra>",
            )
        )
    fig.update_layout(xaxis_title="Depolama gücü (MWe)", yaxis_title="Süre (saat)", xaxis=dict(type="log", tickvals=[4, 7, 10, 20, 30, 50, 100], ticktext=["4", "7", "10", "20", "30", "50", "100"]), title=baslik, template=SABLON)
    return fig


def il_cubuk(df: pd.DataFrame, baslik: str) -> go.Figure:
    """İllere göre kurulu gücü yatay çubukla gösterir (büyükten küçüğe)."""
    fig = go.Figure(
        go.Bar(
            x=df["kurulu_mwe"],
            y=df["il"],
            orientation="h",
            marker_color=RENKLER["Toplam"],
            text=df["kurulu_mwe"],
            texttemplate="%{text:,.0f} MWe",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,.1f} MWe<extra></extra>",
        )
    )
    fig.update_layout(title=baslik, template=SABLON, xaxis_title="MWe", yaxis=dict(autorange="reversed", automargin=True),
                      margin=dict(l=10, r=70, t=60, b=10))
    return fig


def yatay_deger_cubuk(df: pd.DataFrame, etiket: str, deger: str, baslik: str, birim: str) -> go.Figure:
    """Etiket-değer çiftlerini büyükten küçüğe yatay çubukla gösterir."""
    sirali = df.sort_values(deger, ascending=True)
    fig = go.Figure(
        go.Bar(
            x=sirali[deger],
            y=sirali[etiket],
            orientation="h",
            marker_color=RENKLER["Toplam"],
            text=sirali[deger],
            texttemplate="%{text:,.1f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,.1f} " + birim + "<extra></extra>",
        )
    )
    fig.update_layout(title=baslik, template=SABLON, xaxis_title=birim, margin=dict(l=10, r=60, t=60, b=10))
    return fig


def yigin_cubuk(df: pd.DataFrame, x: str, seri: str, deger: str, baslik: str, y_baslik: str) -> go.Figure:
    """Seri bazında yığılmış sütun grafiği (ör. yıllara göre bölge katkıları)."""
    fig = go.Figure()
    for ad, alt in df.groupby(seri, sort=False):
        fig.add_trace(go.Bar(name=str(ad), x=alt[x].astype(str), y=alt[deger], hovertemplate=f"{ad}: %{{y:,.1f}}<extra></extra>"))
    fig.update_layout(barmode="stack")
    return _duzenle(fig, baslik, y_baslik)


def cizgi_coklu(df: pd.DataFrame, x: str, seri: str, deger: str, baslik: str, y_baslik: str) -> go.Figure:
    """Birden çok serinin çizgi grafiği (ör. senaryo ya da kaynak karşılaştırması)."""
    fig = go.Figure()
    for ad, alt in df.groupby(seri, sort=False):
        fig.add_trace(go.Scatter(name=str(ad), x=alt[x], y=alt[deger], mode="lines+markers",
                                 line=dict(width=2.2), marker=dict(size=5),
                                 hovertemplate=f"{ad}: %{{y:,.1f}}<extra></extra>"))
    return _duzenle(fig, baslik, y_baslik)


def gruplu_yatay(df: pd.DataFrame, etiket: str, seri: str, deger: str, baslik: str, birim: str) -> go.Figure:
    """Etiketler (ör. bölgeler) için seri başına yan yana yatay çubuk."""
    fig = go.Figure()
    for ad, alt in df.groupby(seri, sort=False):
        fig.add_trace(go.Bar(name=str(ad), y=alt[etiket], x=alt[deger], orientation="h",
                             hovertemplate=f"{ad} - %{{y}}: %{{x:,.1f}} {birim}<extra></extra>"))
    fig.update_layout(barmode="group", yaxis=dict(autorange="reversed", automargin=True))
    return _duzenle(fig, baslik, birim)


def pay_yigin_genel(df: pd.DataFrame, x: str, kolonlar: dict[str, str], baslik: str, y_baslik: str = "Pay (%)") -> go.Figure:
    """Verilen {etiket: sütun} eşlemesiyle yığılmış pay grafiği. Renkler kaynak etiketinden alınır."""
    fig = go.Figure()
    for etiket, kolon in kolonlar.items():
        fig.add_trace(
            go.Bar(
                name=etiket,
                x=df[x].astype(str),
                y=df[kolon],
                marker_color=RENKLER.get(etiket),
                hovertemplate=f"{etiket}: %{{y:,.1f}}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    return _duzenle(fig, baslik, y_baslik)


def gruplu_cubuk(df: pd.DataFrame, x: str, seri: str, deger: str, baslik: str, y_baslik: str) -> go.Figure:
    """Seri bazında yan yana sütunlar (ör. yıllara göre ithalat ve ihracat)."""
    fig = go.Figure()
    for ad, alt in df.groupby(seri, sort=False):
        fig.add_trace(go.Bar(name=str(ad), x=alt[x].astype(str), y=alt[deger], hovertemplate=f"{ad}: %{{y:,.1f}}<extra></extra>"))
    fig.update_layout(barmode="group")
    return _duzenle(fig, baslik, y_baslik)


def canli_kurulu_guc(yillik: pd.DataFrame, guncel_gw: float, guncel_tarih: pd.Timestamp, baslik: str,
                     yen_yillik: list[float] | None = None, yen_guncel: float | None = None) -> go.Figure:
    """Toplam ve yenilenebilir kurulu güç çizgileri; sonda güncel (YTBS) noktalar. Y ekseni veriye göre daraltılmıştır."""
    x = [str(v) for v in yillik["donem"]]
    y = list(yillik["toplam_gw"])
    etiket = guncel_tarih.strftime("%d.%m.%Y")
    fig = go.Figure()

    def iz(xs, ys, renk, ad, guncel_nokta_metin, kesik=False):
        fig.add_trace(go.Scatter(
            x=xs[:-1], y=ys[:-1], mode="lines+markers", name=ad,
            line=dict(color=renk, width=2.4), marker=dict(size=6, color=renk),
            hovertemplate="%{x}: %{y:,.1f} GW<extra>" + ad + "</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[xs[-2], xs[-1]], y=[ys[-2], ys[-1]], mode="lines+markers+text", name=ad + " (güncel)",
            showlegend=False,
            line=dict(color=PAS if not kesik else renk, width=2, dash="dot"),
            marker=dict(size=[6, 12], color=[renk, PAS], line=dict(color="white", width=2)),
            text=["", f"<b>{guncel_nokta_metin}</b>"], textposition="top center", textfont=dict(color=PAS, size=12),
            hovertemplate="%{x}: %{y:,.1f} GW<extra>" + ad + " (YTBS)</extra>",
        ))

    tr = lambda v: f"{v:,.1f} GW".replace(",", "§").replace(".", ",").replace("§", ".")
    yen_seri = list(yen_yillik) if yen_yillik else None
    tum_y = y + [guncel_gw]
    x_tam = x + ["Güncel"]
    if yen_seri is not None and yen_guncel is not None:
        iz(x_tam, tum_y, RENKLER["Toplam"], "Toplam", tr(guncel_gw))
        iz(x_tam, yen_seri + [yen_guncel], TURKUAZ, "Yenilenebilir", tr(yen_guncel))
        ymin = min(min(y), min(yen_seri)) * 0.9
        ymax = max(guncel_gw, yen_guncel, max(y)) * 1.12
    else:
        iz(x_tam, tum_y, RENKLER["Toplam"], "Toplam", tr(guncel_gw))
        ymin = min(y) * 0.92
        ymax = max(max(y), guncel_gw) * 1.08
    fig.update_xaxes(type="category", tickangle=0)
    fig.update_yaxes(range=[ymin, ymax], ticksuffix="")
    fig.update_layout(height=320, showlegend=yen_seri is not None, margin=dict(l=10, r=20, t=50, b=10),
                      legend=dict(orientation="h", y=-0.15))
    fig.add_annotation(x=1, y=1.12, xref="paper", yref="paper", showarrow=False, xanchor="right",
                       text=f"Güncel: YTBS, {etiket}", font=dict(size=11, color="#7A7468"))
    return _duzenle(fig, baslik, "GW")


def tr_harita(df: pd.DataFrame, deger: str, baslik: str, renk: str, birim: str = "MWe") -> go.Figure:
    """Türkiye il haritası. df: 'ad_key' (il anahtarı) ve `deger` sütunları. Değere göre tek renk tonu."""
    from src.energyatlas import data

    geo = data.tr_il_geojson()
    deger_map = dict(zip(df["ad_key"], df[deger]))
    z = [float(deger_map.get(f["properties"]["ad_key"], 0.0)) for f in geo["features"]]
    konumlar = [f["properties"]["ad_key"] for f in geo["features"]]
    fig = go.Figure(go.Choropleth(
        geojson=geo,
        featureidkey="properties.ad_key",
        locations=konumlar,
        z=z,
        colorscale=[[0.0, "#F1ECE2"], [0.35, _acik(renk)], [1.0, renk]],
        marker_line_color="#FBF9F4",
        marker_line_width=0.6,
        colorbar=dict(title=birim, thickness=10, len=0.6, outlinewidth=0),
        customdata=[f["properties"]["name"] for f in geo["features"]],
        hovertemplate="%{customdata}: %{z:,.0f} " + birim + "<extra></extra>",
    ))
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(title=baslik, template=SABLON, margin=dict(l=0, r=0, t=50, b=0), height=430,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def _acik(hex_renk: str) -> str:
    h = hex_renk.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    k = 0.55
    return f"#{int(r + (255 - r) * k):02X}{int(g + (255 - g) * k):02X}{int(b + (255 - b) * k):02X}"


def isletmedeki_cubuk_genel(df: pd.DataFrame, etiket: str, seri: str, deger: str, baslik: str) -> go.Figure:
    """Şirket bazında yığılmış yatay çubuk: seri (ör. GES/RES) renkleriyle."""
    renk = {"GES": "#D9A21B", "RES": "#13A89E"}
    fig = go.Figure()
    for ad, alt in df.groupby(seri, sort=False):
        alt = alt.sort_values(deger, ascending=True)
        fig.add_trace(go.Bar(name=str(ad), y=alt[etiket], x=alt[deger], orientation="h",
                             marker_color=renk.get(str(ad)), hovertemplate=f"{ad}: %{{x:,.1f}} MWe<extra></extra>"))
    fig.update_layout(barmode="stack", title=baslik, template=SABLON, xaxis_title="MWe",
                      yaxis=dict(automargin=True), margin=dict(l=10, r=20, t=60, b=10))
    return fig
