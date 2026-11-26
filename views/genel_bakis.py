"""Ana sayfa: özet göstergeler ve bölüm kartları."""

import streamlit as st

from src.energyatlas import charts, data, ui

kurulu = data.kurulu_guc().set_index("donem")
uretim = data.uretim().set_index("donem")
tuketim = data.tuketim().set_index("donem")

ui.hero(
    "Enerji Atlası",
    "Türkiye ve dünya elektrik sektörü: kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler tek yerde.",
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kurulu güç (2026 9A)", f"{kurulu.loc['2026 9A', 'toplam_gw']:.1f} GW")
c2.metric("Yenilenebilir üretim payı (2026 9A)", f"%{100 - uretim.loc['2026 9A', 'termik_pct']:.0f}")
c3.metric("Brüt tüketim (2025)", f"{tuketim.loc['2025', 'tuketim_twh']:.0f} TWh")
c4.metric("Güneş payı (kurulu güç, 2026 9A)", f"%{kurulu.loc['2026 9A', 'gunes_pct']:.0f}")

st.subheader("Bölümler")
kart_listesi = [
    ("⚡", "Kapasite ve üretim", ["Kaynaklara göre kurulu güç", "Kaynaklara göre üretim", "Brüt elektrik tüketimi", "Kişi başına tüketim"]),
    ("🔋", "Yenilenebilir ve depolama", ["Devam eden yatırımlar", "Depolama ve şebeke ilişkisi", "Depolama ön lisansları", "Ön lisans bitiş tarihleri", "İşletmedeki depolama projeleri"]),
    ("💲", "Fiyatlar ve tarifeler", ["PTF (piyasa takas fiyatı)", "EPDK elektrik tarifeleri", "YEKDEM fiyatlandırması", "YEKDEM duyuruları"]),
    ("🎯", "Altyapı ve hedefler", ["Elektrik iletim ağı", "Piyasa hedefleri"]),
    ("🌍", "Dünya ve karşılaştırma", ["Dünya kurulu güç", "Dünyada güneş payı", "Ülkeler: güneş kurulu gücü", "Küresel enerji yatırımları"]),
]
for i in range(0, len(kart_listesi), 3):
    satir = st.columns(3)
    for kolon, (ikon, baslik, maddeler) in zip(satir, kart_listesi[i:i + 3]):
        with kolon:
            ui.kart(ikon, baslik, maddeler)
    st.write("")

st.subheader("Toplam kurulu güç gelişimi")
st.plotly_chart(
    charts.toplam_cubuk(data.kurulu_guc(), "toplam_gw", "Toplam kurulu güç (GW)", "GW"),
    use_container_width=True,
)
