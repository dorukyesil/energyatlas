"""Türkiye brüt elektrik tüketimi (TWh), 2016-2026."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Elektrik sistemi",
    "Brüt elektrik tüketimi",
    "Türkiye brüt elektrik tüketimi ve yıllık değişimi. Grafikteki noktaların üzerine gelerek olayları görebilirsiniz.",
)

df = data.tuketim()
yillik = data.tam_yillar(df)
ilk, son = yillik.iloc[0], yillik.iloc[-1]
yillik_artis = ((son["tuketim_twh"] / ilk["tuketim_twh"]) ** (1 / (len(yillik) - 1)) - 1) * 100
h1_2025 = df[df["donem"] == "2025 H1"]["tuketim_twh"].iloc[0]
h1_2026 = df[df["donem"] == "2026 H1"]["tuketim_twh"].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("2025 tüketimi", f"{ui.sayi(son['tuketim_twh'], 0)} TWh")
c2.metric("2016-2025 yıllık ortalama artış", f"%{ui.sayi(yillik_artis)}")
c3.metric("2026 ilk yarı", f"{ui.sayi(h1_2026, 0)} TWh", f"{(h1_2026 / h1_2025 - 1) * 100:+.1f}% (2025 ilk yarıya göre)".replace(".", ","))

ui.bolum("01", "Gelişim", "Düzey veya yıllık değişim görünümü.")
gorunum = ui.segment(["Düzey (TWh)", "Yıllık değişim (%)"], "tuketim_gorunum")
if gorunum == "Düzey (TWh)":
    st.plotly_chart(charts.tuketim_cubuk(df, "Türkiye brüt elektrik tüketimi (TWh)"), use_container_width=True)
else:
    degisim = data.yillik_degisim(df, "tuketim_twh")
    st.plotly_chart(charts.yillik_degisim_cubuk(degisim, "donem", "degisim_pct", "Brüt tüketim: yıllık değişim"), use_container_width=True)
ui.kaynak("Veri: sunum grafiklerinden okunmuştur. H1: ilk yarı dönemi, yıllık değerlerle doğrudan karşılaştırılmamalıdır.")

ui.bolum("02", "Öne çıkan olaylar")
for _, satir in df[df["olay"].notna()].iterrows():
    st.markdown(f"- **{satir['donem']}:** {satir['olay']} ({ui.sayi(satir['tuketim_twh'], 0)} TWh)")

ui.veri_tablosu(df, "Veri tablosu", "tuketim.csv")
