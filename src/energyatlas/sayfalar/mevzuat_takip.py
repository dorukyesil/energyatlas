"""Mevzuat takibi: son yayımlananlar ve kanun teklifleri durumu."""

import pandas as pd
import streamlit as st

from src.energyatlas import data, ui


def render() -> None:
    d = data.mevzuat()
    ui.bolum("01", "Son 30 gün", "Son otuz günde yayımlanan enerji ile ilgili metinler.")
    if d.empty:
        st.info("Mevzuat verisi henüz üretilmedi.")
    else:
        son = d["tarih"].max()
        yakin = d[d["tarih"] >= son - pd.Timedelta(days=30)].sort_values("tarih", ascending=False)
        st.caption(f"Veri son tarihi: {son:%d.%m.%Y}. Son 30 günde {len(yakin)} metin.")
        st.dataframe(
            yakin[["tarih", "tur", "baslik", "baglanti"]].rename(columns={"tarih": "Tarih", "tur": "Tür", "baslik": "Başlık", "baglanti": "Bağlantı"}),
            use_container_width=True, hide_index=True,
            column_config={"Bağlantı": st.column_config.LinkColumn("Bağlantı", display_text="Metni aç")},
        )

    ui.bolum("02", "Kanun teklifleri", "TBMM kanun teklifleri henüz bağlanmadı.")
    st.info(
        "TBMM'nin kanun teklifi sorgu sayfası makine tarafından okunabilir bir veri servisi sunmuyor. "
        "Bu bölüm, teklif listesi kaynağı doğrulandığında (ör. sorgu formunun isteklerini izleyen bir çekici) doldurulacaktır."
    )
    ui.kaynak("Kaynak: TBMM Yasama sayfası (tbmm.gov.tr).")
