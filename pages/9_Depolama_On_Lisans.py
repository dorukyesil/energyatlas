"""Elektrik depolama ve GES/RES için ön lisans başvuruları (bölgesel yoğunluk)."""

import streamlit as st

from config import APP_TITLE

st.set_page_config(page_title=f"Ön Lisanslar | {APP_TITLE}", layout="wide")
st.title("Elektrik Depolama Ön Lisansları")
st.caption("Ön lisans başvurularının bölgesel yoğunluğu.")

st.markdown(
    """
Aşağıdaki haritalar, GES ve RES ile birlikte enerji depolama için yapılan **ön lisans başvurularının**
il bazında yoğunluğunu gösterir. Renk koyulaştıkça başvuru yoğunluğu artmaktadır.
"""
)

c1, c2 = st.columns(2)
with c1:
    st.subheader("GES ve depolama")
    st.markdown(
        "Başvurular özellikle **İç Anadolu** bölgesinde yoğunlaşmıştır. Güney ve Akdeniz kıyısındaki "
        "bazı illerde de belirgin bir yoğunluk görülmektedir."
    )
with c2:
    st.subheader("RES ve depolama")
    st.markdown(
        "Başvurular büyük ölçüde **Marmara ve Trakya** bölgesinde yoğunlaşmıştır. Rüzgar potansiyelinin "
        "yüksek olduğu bu bölgeler başvuruların merkezidir."
    )

st.info(
    "Bu sayfa şu an görsel haritalardan elde edilen niteliksel bilgiyi içerir. Haritanın il bazında "
    "etkileşimli hale getirilmesi için ön lisans başvurularının sayısal listesi (EPDK kaynağı) gerekir. "
    "Bu veri hazır olduğunda harita ve il bazında tablo eklenecektir."
)
