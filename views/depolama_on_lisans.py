"""Depolamalı GES ve RES ön lisansları: bitiş yılları ve bölgesel yoğunluk."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Depolama ve yatırımlar",
    "Depolama ön lisansları",
    "Depolamalı GES ve RES ön lisanslarının bitiş yılına göre dağılımı ve bölgesel yoğunluğu.",
)

df = data.depolama_on_lisans()
toplam = df.groupby("teknoloji")[["proje_adedi", "kapasite_mwe"]].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("GES proje adedi", f"{toplam.loc['GES', 'proje_adedi']:.0f}")
c2.metric("GES kapasitesi", f"{ui.sayi(toplam.loc['GES', 'kapasite_mwe'], 0)} MWe")
c3.metric("RES proje adedi", f"{toplam.loc['RES', 'proje_adedi']:.0f}")
c4.metric("RES kapasitesi", f"{ui.sayi(toplam.loc['RES', 'kapasite_mwe'], 0)} MWe")

ui.bolum("01", "Bitiş tarihleri", "Ön lisans bitiş yılına göre depolamalı kapasite (MWe). Üzerine gelerek proje adedini görün.")
st.plotly_chart(charts.on_lisans_yillik(df, "Bitiş yılına göre depolamalı kapasite (MWe)"), use_container_width=True)
ui.kaynak("Yıllık satırların toplamı, kaynaktaki toplam değerden birkaç MWe farklı olabilir (yuvarlama).")

st.markdown(
    """
- EPDK, ön lisans süresi içinde proje ilerlemesini göstermeyen şirketlerin **süre uzatma taleplerini reddediyor**
  ve bu ön lisansları sonlandırıyor veya iptal ediyor.
- **Mücbir sebep** veya izin süreçlerindeki aksamalar nedeniyle EPDK **süre uzatımı** yapabiliyor.
"""
)

ui.bolum("02", "Bölgesel yoğunluk", "Ön lisans başvurularının il bazında yoğunluğu.")
b1, b2 = st.columns(2)
with b1:
    st.markdown("**GES ve depolama**")
    st.markdown("Başvurular özellikle **İç Anadolu** bölgesinde yoğunlaşmıştır. Güney ve Akdeniz kıyısındaki bazı illerde de belirgin bir yoğunluk görülmektedir.")
with b2:
    st.markdown("**RES ve depolama**")
    st.markdown("Başvurular büyük ölçüde **Marmara ve Trakya** bölgesinde yoğunlaşmıştır.")
st.info(
    "Bölgesel yoğunluk şu an haritalardan elde edilen niteliksel bilgidir. İl bazında etkileşimli harita için "
    "ön lisans başvurularının sayısal listesi (EPDK kaynağı) gerekir."
)

ui.veri_tablosu(df, "Veri tablosu", "depolama_on_lisans.csv")
