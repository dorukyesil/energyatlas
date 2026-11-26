"""Enerji mevzuatı: Resmî Gazete'de yayımlanan son metinler, filtreler ve bağlantılar."""

import streamlit as st

from src.energyatlas import data, ui


def render() -> None:
    d = data.mevzuat()
    if d.empty:
        st.info("Mevzuat verisi henüz üretilmedi. `scripts/mevzuat_resmi_gazete.py` çalıştırılmalıdır.")
        return

    ui.bolum("01", "Yayımlanan metinler", "Enerjiyle ilgili Resmî Gazete metinleri. Türü, değişiklik olup olmadığını ve anahtar kelimeyi seçerek filtreleyin.")
    c1, c2, c3 = st.columns(3)
    turler = ["Tümü"] + sorted(d["tur"].unique().tolist())
    tur = c1.selectbox("Tür", turler, key="mevzuat_tur")
    yil_aralik = c2.slider("Yıl", int(d["yil"].min()), int(d["yil"].max()), (int(d["yil"].max()) - 1, int(d["yil"].max())), key="mevzuat_yil")
    yalniz_degisiklik = c3.toggle("Yalnızca değişiklikler", value=False, key="mevzuat_degisiklik")
    ara = st.text_input("Başlıkta ara", "", key="mevzuat_ara", placeholder="ör. YEKDEM, depolama, EPDK")

    alt = d[(d["yil"] >= yil_aralik[0]) & (d["yil"] <= yil_aralik[1])]
    if tur != "Tümü":
        alt = alt[alt["tur"] == tur]
    if yalniz_degisiklik:
        alt = alt[alt["degisiklik"]]
    if ara.strip():
        alt = alt[alt["baslik"].str.contains(ara.strip(), case=False, regex=False)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Metin sayısı", f"{len(alt)}")
    m2.metric("Değişiklik içeren", f"{int(alt['degisiklik'].sum())}")
    m3.metric("Yürürlükten kaldırma", f"{int(alt['yururluk_kaldirma'].sum())}")

    gosterim = alt.sort_values("tarih", ascending=False)[["tarih", "tur", "baslik", "degisiklik", "anahtar_kelimeler", "baglanti"]].rename(columns={
        "tarih": "Tarih", "tur": "Tür", "baslik": "Başlık", "degisiklik": "Değişiklik", "anahtar_kelimeler": "Anahtar kelimeler", "baglanti": "Bağlantı"})
    st.dataframe(
        gosterim,
        use_container_width=True,
        hide_index=True,
        column_config={"Bağlantı": st.column_config.LinkColumn("Bağlantı", display_text="Metni aç")},
    )
    st.download_button("Filtrelenmiş listeyi indir (CSV)", data=gosterim.to_csv(index=False).encode("utf-8-sig"),
                       file_name="enerji_mevzuati.csv", mime="text/csv", key="mevzuat_indir")
    ui.kaynak("Kaynak: Resmî Gazete (resmigazete.gov.tr) günlük arşivi. Enerjiyle ilgili başlıklar anahtar kelime eşleşmesiyle seçilmiştir.")
