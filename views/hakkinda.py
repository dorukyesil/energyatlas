"""Hakkında: amaç, veri kaynakları ve kullanım notları."""

import streamlit as st

from src.energyatlas import ui

ui.hero("Hakkında", "Bu portal ne içerir, veriler nereden geliyor ve nelere dikkat edilmeli.")

st.subheader("Amaç")
st.markdown(
    "Enerji Atlası, Türkiye ve dünya elektrik sektörüne ait temel göstergeleri tek bir yerde, "
    "anlaşılır grafiklerle sunar. Yatırımcılar, araştırmacılar ve sektörle ilgilenen herkes için hazırlanmıştır."
)

st.subheader("Veri kaynakları")
st.markdown(
    """
- **TEİAŞ:** Kurulu güç, üretim, tüketim, iletim ağı
- **EPDK:** Elektrik tarifeleri, ön lisans bilgileri, depolama lisansları
- **EPİAŞ:** Piyasa takas fiyatı (PTF), YEKDEM duyuruları
- **IEA (Uluslararası Enerji Ajansı):** Dünya kurulu güç ve güneş verileri
- **Enerji ve Tabii Kaynaklar Bakanlığı:** Stratejik plan ve yol haritası hedefleri
- **Küresel yatırım verileri:** Yenilenebilir enerji yatırım eğilimleri
"""
)

st.subheader("Kullanım notları")
st.info(
    "Bazı değerler resmi raporların grafiklerinden okunarak girilmiştir. Yayın öncesi ve karar "
    "vermeden önce ilgili resmi kaynaktan doğrulanmalıdır. Ayrıntılı kaynak notları proje deposundaki "
    "`data/KAYNAKLAR.md` dosyasında yer alır."
)
st.markdown(
    """
- **9A** ocak-eylül, **H1** ilk yarı dönemini ifade eder. Bu değerler yıllık değerlerle doğrudan karşılaştırılmamalıdır.
- **GW / MW / MWh:** Güç ve enerji birimleri. 1 GW = 1.000 MW.
- **kr/kWh:** Kuruş cinsinden birim fiyat. 100 kr = 1 TL.
- **PTF:** Piyasa takas fiyatı. **YEKDEM:** Yenilenebilir enerji kaynaklarının destekleme mekanizması.
"""
)
