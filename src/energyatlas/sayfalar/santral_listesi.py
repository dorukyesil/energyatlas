"""EPDK santral listesi: lisanslı ve ön lisanslı üretim tesisleri, il ve tür filtreleri."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    sekme_lisans, sekme_onlisans = st.tabs(["Lisanslı tesisler", "Ön lisanslı tesisler"])


    def bolum(df, anahtar: str, aciklama: str):
        tur = ui.segment(["Tümü", "Güneş", "Rüzgar"], f"{anahtar}_tur")
        il_secenekleri = ["Tüm iller"] + sorted(df["il"].dropna().unique().tolist())
        il = st.selectbox("İl", il_secenekleri, key=f"{anahtar}_il")

        alt = df.copy()
        if tur != "Tümü":
            alt = alt[alt["tesis_turu"] == tur]
        if il != "Tüm iller":
            alt = alt[alt["il"] == il]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tesis sayısı", f"{len(alt)}")
        c2.metric("Kurulu güç", f"{ui.sayi(alt['kurulu_mwe'].sum(), 0)} MWe")
        c3.metric("Depolama kapasitesi", f"{ui.sayi(alt['depolama_mwh'].sum(), 0)} MWh")
        c4.metric("İl sayısı", f"{alt['il'].nunique()}")

        ui.bolum("01", "İllere göre kurulu güç", aciklama)
        il_toplam = (
            alt.groupby("il", as_index=False)["kurulu_mwe"].sum().sort_values("kurulu_mwe", ascending=False).head(15)
        )
        if il_toplam.empty:
            st.info("Seçilen filtrelerde tesis yok.")
        else:
            st.plotly_chart(charts.il_cubuk(il_toplam, "En büyük 15 il (kurulu güç, MWe)"), use_container_width=True)

        ui.bolum("02", "Tesis listesi", "Tabloyu filtreleyebilir, sıralayabilir ve CSV olarak indirebilirsiniz.")
        goster = alt[["lisans_sahibi", "tesis_adi", "il", "ilce", "tesis_turu", "kurulu_mwe", "depolama_mwh", "bitis"]].rename(
            columns={
                "lisans_sahibi": "Lisans sahibi", "tesis_adi": "Tesis", "il": "İl", "ilce": "İlçe",
                "tesis_turu": "Tür", "kurulu_mwe": "Kurulu güç (MWe)", "depolama_mwh": "Depolama (MWh)", "bitis": "Bitiş tarihi",
            }
        )
        st.dataframe(goster.sort_values("Kurulu güç (MWe)", ascending=False), use_container_width=True, hide_index=True)
        st.download_button(
            "Filtrelenmiş listeyi indir (CSV)",
            data=goster.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"epdk_{anahtar}.csv",
            mime="text/csv",
        )


    with sekme_lisans:
        bolum(data.epdk_lisans(), "lisans", "Lisanslı tesislerin il bazında kurulu gücü.")
        ui.kaynak("Kaynak: EPDK, lisanslı üretim tesisleri listesi. Kişisel iletişim bilgileri gösterilmez.")

    with sekme_onlisans:
        bolum(data.epdk_onlisans(), "onlisans", "Ön lisanslı tesislerin il bazında kurulu gücü.")
        ui.kaynak("Kaynak: EPDK, ön lisanslı üretim tesisleri listesi. Kişisel iletişim bilgileri gösterilmez.")
