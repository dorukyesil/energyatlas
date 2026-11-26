"""EPDK elektrik tarifeleri: tek zamanlı ve çok zamanlı enerji bedelleri (4 Nisan 2026 itibarıyla)."""

import plotly.express as px
import streamlit as st

from src.energyatlas import charts, data, theme, ui


def render() -> None:
    df = data.tarife()
    df["grup_etiket"] = df["baglanti"] + " | " + df["grup"]


    def satir(baglanti: str, grup: str) -> float:
        return float(df[(df["baglanti"] == baglanti) & (df["grup"] == grup)]["tek_zamanli"].iloc[0])


    c1, c2, c3 = st.columns(3)
    c1.metric("Mesken (AG, 8 kWh/gün üstü)", f"{ui.sayi(satir('AG Tek Terim', 'Mesken (8 kWh/gün üstü)') / 100, 2)} TL/kWh")
    c2.metric("Sanayi (OG Tek Terim)", f"{ui.sayi(satir('OG Tek Terim', 'Sanayi') / 100, 2)} TL/kWh")
    c3.metric("Aydınlatma (AG Tek Terim)", f"{ui.sayi(satir('AG Tek Terim', 'Aydınlatma') / 100, 2)} TL/kWh")

    ui.bolum("01", "Tek zamanlı enerji bedeli", "Bağlantı türünü seçerek karşılaştırmayı daraltın.")
    secenekler = ["Tümü"] + df["baglanti"].drop_duplicates().tolist()
    secim = ui.segment(secenekler, "epdk_baglanti")
    alt = df if secim == "Tümü" else df[df["baglanti"] == secim]
    fig = px.bar(
        alt.sort_values("tek_zamanli", ascending=False),
        x="tek_zamanli",
        y="grup_etiket",
        orientation="h",
        color="baglanti",
        labels={"tek_zamanli": "kr/kWh", "grup_etiket": "", "baglanti": ""},
        color_discrete_map={
            "İletim Sistemi": theme.GRI,
            "OG Çift Terim": theme.MUREKKEP,
            "OG Tek Terim": theme.TURKUAZ,
            "AG Tek Terim": theme.OKRA,
            "Genel Aydınlatma": theme.PAS,
        },
        text="tek_zamanli",
    )
    fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(template=theme.SABLON, yaxis=dict(autorange="reversed", automargin=True), height=max(260, 34 * len(alt) + 90), bargap=0.45,
                      legend=dict(orientation="h", y=-0.12, x=0), margin=dict(l=10, r=50, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    ui.kaynak("Kaynak: EPDK, elektrik faturalarına esas tarife tabloları. AG: alçak gerilim, OG: orta gerilim.")

    ui.bolum("02", "Çok zamanlı tarifeler", "Gündüz, puant ve gece dilimleri. Koyu renk daha yüksek fiyattır.")
    cok = df[df["gunduz"].notna()].copy()
    matris = cok.set_index("grup_etiket")[["gunduz", "puant", "gece"]]
    matris.columns = ["Gündüz", "Puant", "Gece"]
    fig_isi = charts.isi_haritasi(matris, "Çok zamanlı enerji bedelleri (kr/kWh)", "pas", "%{z:,.0f}", "kr/kWh")
    fig_isi.update_layout(height=max(420, 34 * len(matris)))
    st.plotly_chart(fig_isi, use_container_width=True)
    ui.kaynak("Puant dilimi en pahalı, gece dilimi en ucuz dilimdir.")

    ui.veri_tablosu(df.drop(columns=["grup_etiket"]), "Tam tablo", "epdk_tarifeleri.csv")
