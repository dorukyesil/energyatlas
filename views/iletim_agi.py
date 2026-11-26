"""Türkiye elektrik iletim ağı: 2025 durumu, 2035 hedefleri ve sınır bağlantıları."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Altyapı ve hedefler",
    "Elektrik iletim ağı",
    "AC (alternatif akım) şebekesi ve HVDC (yüksek gerilim doğru akım) hedefleri.",
)

iletim = data.iletim()
YATIRIM = "Yatırım ihtiyacı (2035'e kadar)"


def deger(gosterge: str, yil: str) -> float:
    satir = iletim[(iletim["gosterge"] == gosterge) & (iletim["yil"].astype(str) == yil)]
    return float(satir["deger"].iloc[0])


c1, c2, c3 = st.columns(3)
c1.metric("AC hattı (2025)", f"{ui.sayi(deger('AC hattı', '2025'), 0)} km", f"2035 hedefi: {ui.sayi(deger('AC hattı', '2035'), 0)} km", delta_color="off")
c2.metric("Trafo merkezi (2025)", f"{ui.sayi(deger('Trafo merkezi', '2025'), 0)}", f"2035 hedefi: {ui.sayi(deger('Trafo merkezi', '2035'), 0)}", delta_color="off")
c3.metric("Yatırım ihtiyacı (2035'e kadar)", f"{ui.sayi(deger(YATIRIM, '2035'), 0)} milyar USD")

ui.bolum("01", "2035 HVDC hedefleri", "Uzun mesafede düşük kayıpla yüksek kapasiteli iletim sağlayan doğru akım koridorları.")
h1, h2, h3 = st.columns(3)
h1.metric("HVDC koridoru", f"{ui.sayi(deger('HVDC koridor kapasitesi', '2035'), 0)} GW")
h2.metric("HVDC hattı", f"{ui.sayi(deger('HVDC hattı', '2035'), 0)} km")
h3.metric("HVDC çevirici merkezi", f"{ui.sayi(deger('HVDC çevirici merkezi', '2035'), 0)}")

ui.bolum("02", "2025 ve 2035 AC şebeke hedefleri")
ac_tablo = iletim[iletim["gosterge"].isin(["AC hattı", "Trafo merkezi"])].copy()
ac_tablo["yil"] = ac_tablo["yil"].astype(str)
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(
        charts.iki_donem_karsilastirma(ac_tablo[ac_tablo["gosterge"] == "AC hattı"], "gosterge", "yil", "deger", "AC hattı (km)", "km"),
        use_container_width=True,
    )
with g2:
    st.plotly_chart(
        charts.iki_donem_karsilastirma(ac_tablo[ac_tablo["gosterge"] == "Trafo merkezi"], "gosterge", "yil", "deger", "Trafo merkezi sayısı", "adet"),
        use_container_width=True,
    )

ui.bolum("03", "Sınır bağlantıları", "Türkiye'nin elektrik ağı sekiz komşu ülkeyle bağlantılıdır.")
baglanti = data.baglantilar()
for bolge in baglanti["komsu_bolge"].unique():
    ulkeler = baglanti[baglanti["komsu_bolge"] == bolge]["ulke"].tolist()
    st.markdown(f"- **{bolge}:** {', '.join(ulkeler)}")

st.info(
    "**AC (Alternatif Akım):** Üretimden dağıtıma kadar mevcut şebekede kullanılan, yönü düzenli aralıklarla değişen akım türüdür.\n\n"
    "**HVDC (Yüksek Gerilim Doğru Akım):** Özellikle uzun mesafelerde, düşük kayıpla ve yüksek kapasiteyle iletim sağlayan doğru akım teknolojisidir."
)

ui.veri_tablosu(iletim, "Veri tablosu", "iletim.csv")
