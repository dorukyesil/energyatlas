"""Elektrik depolama ile şebeke ve talep arasındaki ilişki (kavramsal anlatım)."""

import numpy as np
import streamlit as st

from src.energyatlas import charts, ui

ui.sayfa_basligi(
    "Depolama ve yatırımlar",
    "Depolama ve şebeke ilişkisi",
    "Bu sayfa kavramı anlatır. Grafikler şematiktir, gerçek veri değildir.",
)

st.markdown(
    """
Elektrik talebi gün içinde değişir. Termik santraller **baz yükü** sürekli karşılar. Rüzgar ve güneş ise
kendi zamanlarında üretir: güneş öğleyin, rüzgar çoğunlukla gece ve sabaha karşı daha güçlüdür.
**Depolama**, fazla üretimi biriktirip talep arttığında şebekeye geri verir. Böylece yenilenebilir
kaynaklar talebe daha iyi uyum sağlar.
"""
)

saat = list(range(24))
gunes = [max(0.0, np.exp(-((s - 13) ** 2) / 12) * 1.0) for s in saat]
ruzgar = [0.5 + 0.15 * np.cos((s - 4) / 24 * 2 * np.pi) for s in saat]
termik = [0.45 + 0.05 * np.sin((s - 6) / 24 * 2 * np.pi) for s in saat]
talep = [0.55 + 0.35 * np.exp(-((s - 19) ** 2) / 18) + 0.15 * np.exp(-((s - 11) ** 2) / 20) for s in saat]
depolama = [max(0.0, (talep[i] - termik[i] - ruzgar[i] - gunes[i]) * 0.9) for i in range(24)]

ui.bolum("01", "Şematik günlük profil", "Talep, kaynaklar ve depolamanın gün içindeki ilişkisi.")
st.plotly_chart(
    charts.sematik_profil(saat, talep, termik, ruzgar, gunes, depolama, "Şematik günlük profil: talep, kaynaklar ve depolama"),
    use_container_width=True,
)
ui.kaynak("Eğriler kavramı göstermek için hesaplanmış örneklerdir, gerçek üretim ve talep verisi değildir.")

ui.bolum("02", "Nasıl çalışır?")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**1. Fazla üretim**")
    st.markdown("Güneş ve rüzgar talebin üzerinde üretim yaptığında fazla enerji depolanır.")
with c2:
    st.markdown("**2. Depolama**")
    st.markdown("Bataryalar veya diğer depolama sistemleri enerjiyi biriktirir.")
with c3:
    st.markdown("**3. Talep anı**")
    st.markdown("Akşam saatlerinde talep arttığında depolanan enerji şebekeye geri verilir.")
