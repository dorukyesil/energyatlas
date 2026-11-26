"""Hakkında: amaç, veri kaynakları ve kullanım notları."""

import streamlit as st

from src.energyatlas import ui

ui.sayfa_basligi("Genel", "Hakkında", "Bu portal ne içerir, veriler nereden geliyor ve nelere dikkat edilmeli.")

ui.bolum("01", "Amaç")
st.markdown(
    "Enerji Atlası, Türkiye ve dünya elektrik sektörüne ait temel göstergeleri tek bir yerde, "
    "anlaşılır grafiklerle sunar. Yatırımcılar, araştırmacılar ve sektörle ilgilenen herkes için hazırlanmıştır."
)

ui.bolum("02", "Veri kaynakları")
st.markdown(
    """
- **TEİAŞ:** Kurulu güç, üretim, tüketim, iletim ağı
- **EPDK:** Elektrik tarifeleri, ön lisans bilgileri, depolama lisansları
- **EPİAŞ:** Piyasa takas fiyatı (PTF), YEKDEM duyuruları
- **IEA World Energy Outlook 2026 (Annex A ücretsiz veri seti):** Dünya kurulu güç, üretim ve senaryolar. Yayım: World Energy Outlook 2025 raporu bağlamı için kullanılmıştır.
- **EPDK lisanslı ve ön lisanslı üretim tesisi listeleri:** Santral bazında kurulu güç, depolama ve bitiş tarihleri. Kişisel iletişim bilgileri portala alınmamıştır.
- **Enerji ve Tabii Kaynaklar Bakanlığı:** Stratejik plan ve yol haritası hedefleri
- **Küresel yatırım verileri:** Yenilenebilir enerji yatırım eğilimleri
"""
)

ui.bolum("03", "Kullanım notları")
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
