"""Küresel enerji yatırımları: IEA Dünya Enerji Yatırımları 2025 verisi."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya ve karşılaştırma",
    "Küresel enerji yatırımları",
    "IEA Dünya Enerji Yatırımları 2025. Milyar USD (2024 sabit fiyat, MER). Kategori ve bölge seçerek inceleyin.",
)

ham = data.yatirim_bolge()
dunya = ham[ham["bolge"] == "World"]


def seri(kategori: str, bolge: str = "World"):
    return ham[(ham["bolge"] == bolge) & (ham["kategori"] == kategori)].sort_values("yil")


toplam = seri("Toplam")
temiz = seri("Temiz enerji")
gunes = seri("Güneş")
ilk, son = toplam.iloc[0], toplam.iloc[-1]


def cagr(a: float, b: float, n: int = 10) -> float:
    return ((b / a) ** (1 / n) - 1) * 100


c1, c2, c3 = st.columns(3)
c1.metric("Toplam enerji yatırımı (2025)", f"{ui.sayi(son['deger'], 0)} milyar USD",
          f"yıllık ortalama %{ui.sayi(cagr(ilk['deger'], son['deger']))} (2015-2025)", delta_color="off")
c2.metric("Temiz enerji yatırımı (2025)", f"{ui.sayi(seri('Temiz enerji').iloc[-1]['deger'], 0)} milyar USD",
          f"yıllık ortalama %{ui.sayi(cagr(temiz.iloc[0]['deger'], temiz.iloc[-1]['deger']))}", delta_color="off")
c3.metric("Güneş yatırımı (2025)", f"{ui.sayi(gunes.iloc[-1]['deger'], 0)} milyar USD",
          f"yıllık ortalama %{ui.sayi(cagr(gunes.iloc[0]['deger'], gunes.iloc[-1]['deger']))}", delta_color="off")

ui.bolum("01", "Dünya yatırımları", "Seçilen kategorinin yıllara göre dünya yatırımı.")
kategoriler = ["Toplam", "Temiz enerji", "Fosil yakıtlar", "Güneş", "Rüzgar", "Batarya depolama", "Elektrik şebekeleri", "Nükleer", "Enerji verimliliği"]
kategori = st.selectbox("Kategori", kategoriler, index=0, key="kuresel_kategori")
alt = seri(kategori).assign(donem=lambda d: d["yil"].astype(str))
st.plotly_chart(charts.toplam_cubuk(alt, "deger", f"Dünya yatırımları: {kategori} (milyar USD)", "milyar USD"), use_container_width=True)
ui.kaynak("Kaynak: IEA, World Energy Investment 2025 veri dosyası (World sayfası). 2024 sabit fiyat, MER.")

ui.bolum("02", "Bölgeler", "Ayrık bölgeler: ileri ekonomiler, gelişmekte olan ekonomiler (Çin hariç) ve Çin. Bunlar dünya toplamını oluşturur.")
bolgeler = ["İleri ekonomiler", "Gelişmekte olan ekonomiler (çin hariç)", "China"]
yil = st.segmented_control("Yıl", [2015, 2020, 2025], default=2025, key="kuresel_yil") or 2025
kat2 = st.selectbox("Kategori (bölge karşılaştırması)", kategoriler, index=3, key="kuresel_kategori2")
bolge_df = ham[(ham["bolge"].isin(bolgeler)) & (ham["kategori"] == kat2) & (ham["yil"] == yil)]
st.plotly_chart(
    charts.yatay_deger_cubuk(bolge_df, "bolge", "deger", f"{kat2}: bölgelere göre ({yil}, milyar USD)", "milyar USD"),
    use_container_width=True,
)

ui.bolum("03", "Bölgesel zaman serisi", "Ayrık bölgelerin yıllara göre katkısı (kategori: toplam).")
zaman = ham[(ham["bolge"].isin(bolgeler)) & (ham["kategori"] == "Toplam")]
st.plotly_chart(
    charts.yigin_cubuk(zaman, "yil", "bolge", "deger", "Toplam yatırım, bölgelere göre (milyar USD)", "milyar USD"),
    use_container_width=True,
)
ui.kaynak(
    "Not: Türkiye, IEA sınıflandırmasında 'Avrupa' bölgesinde yer alır. Ayrı bir Türkiye değeri bu veri dosyasında yoktur."
)

ui.veri_tablosu(ham, "Veri tablosu (tüm bölge ve kategoriler)", "yatirim_bolge.csv")
