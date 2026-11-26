"""Türkiye elektrik iletim ağı: 2025 durumu, 2035 hedefleri ve sınır bağlantıları."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Elektrik İletim Ağı ve Hedefler")
st.caption("AC (alternatif akım) şebekesi ve HVDC (yüksek gerilim doğru akım) hedefleri.")

iletim = data.iletim()


def deger(gosterge: str, yil: str) -> float:
    satir = iletim[(iletim["gosterge"] == gosterge) & (iletim["yil"].astype(str) == yil)]
    return float(satir["deger"].iloc[0])


c1, c2, c3 = st.columns(3)
c1.metric("AC hattı (2025)", f"{deger('AC hattı', '2025'):,.0f} km", f"2035 hedefi: {deger('AC hattı', '2035'):,.0f} km")
c2.metric("Trafo merkezi (2025)", f"{deger('Trafo merkezi', '2025'):,.0f}", f"2035 hedefi: {deger('Trafo merkezi', '2035'):,.0f}")
YATIRIM = "Yatırım ihtiyacı (2035'e kadar)"
c3.metric("Yatırım ihtiyacı (2035'e kadar)", f"{deger(YATIRIM, '2035'):,.0f} milyar USD")

st.subheader("2035 HVDC hedefleri")
h1, h2, h3 = st.columns(3)
h1.metric("HVDC koridoru", f"{deger('HVDC koridor kapasitesi', '2035'):,.0f} GW")
h2.metric("HVDC hattı", f"{deger('HVDC hattı', '2035'):,.0f} km")
h3.metric("HVDC çevirici merkezi", f"{deger('HVDC çevirici merkezi', '2035'):,.0f}")

st.subheader("2025 ve 2035 AC şebeke hedefleri")
ac_tablo = iletim[iletim["gosterge"].isin(["AC hattı", "Trafo merkezi"])].copy()
ac_tablo["yil"] = ac_tablo["yil"].astype(str)
st.plotly_chart(
    charts.iki_donem_karsilastirma(
        ac_tablo[ac_tablo["gosterge"] == "AC hattı"], "gosterge", "yil", "deger", "AC hattı (km)", "km"
    ),
    use_container_width=True,
)
st.plotly_chart(
    charts.iki_donem_karsilastirma(
        ac_tablo[ac_tablo["gosterge"] == "Trafo merkezi"], "gosterge", "yil", "deger", "Trafo merkezi sayısı", "adet"
    ),
    use_container_width=True,
)

st.subheader("Sınır bağlantıları")
baglanti = data.baglantilar()
for bolge in baglanti["komsu_bolge"].unique():
    ulkeler = baglanti[baglanti["komsu_bolge"] == bolge]["ulke"].tolist()
    st.markdown(f"- **{bolge}:** {', '.join(ulkeler)}")

st.info(
    "**AC (Alternatif Akım):** Üretimden dağıtıma kadar mevcut şebekede kullanılan, yönü düzenli aralıklarla değişen akım türüdür.\n\n"
    "**HVDC (Yüksek Gerilim Doğru Akım):** Özellikle uzun mesafelerde, düşük kayıpla ve yüksek kapasiteyle iletim sağlayan doğru akım teknolojisidir."
)

ui.veri_tablosu(iletim, "Veriyi tablo olarak göster")
