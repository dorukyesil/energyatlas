"""Devam eden yatırımlar: EPDK ön lisanslı tesislerden şirket ve teknoloji bazında özet."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    ham = data.epdk_onlisans()
    ham = ham[ham["kurulu_mwe"] > 0].copy()
    lisans = data.epdk_lisans()
    lisans_depolama = lisans[lisans["isletmedeki_depolama_mwh"] > 0]

    toplam_ol = float(ham["kurulu_mwe"].sum())
    ges_ol = float(ham.loc[ham["tesis_turu"] == "Güneş", "kurulu_mwe"].sum())
    res_ol = float(ham.loc[ham["tesis_turu"] == "Rüzgar", "kurulu_mwe"].sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ön lisanslı toplam kurulu güç", f"{ui.sayi(toplam_ol, 0)} MWe")
    c2.metric("GES ön lisans", f"{ui.sayi(ges_ol, 0)} MWe", f"{int((ham['tesis_turu'] == 'Güneş').sum())} tesis", delta_color="off")
    c3.metric("RES ön lisans", f"{ui.sayi(res_ol, 0)} MWe", f"{int((ham['tesis_turu'] == 'Rüzgar').sum())} tesis", delta_color="off")
    c4.metric("Lisanslı tesislerde işletmedeki depolama", f"{ui.sayi(lisans_depolama['isletmedeki_depolama_mwh'].sum(), 0)} MWh", delta_color="off")

    ui.bolum("01", "Şirketlere göre ön lisanslı kapasite", "En büyük 15 şirket, kurulu güç (MWe). Teknolojiye göre ayrılmıştır.")
    sirket = ham.groupby(["lisans_sahibi", "tesis_turu"], as_index=False)["kurulu_mwe"].sum()
    en_buyuk = sirket.groupby("lisans_sahibi")["kurulu_mwe"].sum().nlargest(15).index
    sirket = sirket[sirket["lisans_sahibi"].isin(en_buyuk)].copy()
    sirket["teknoloji"] = sirket["tesis_turu"].map({"Güneş": "GES", "Rüzgar": "RES"})
    st.plotly_chart(charts.isletmedeki_cubuk_genel(sirket, "lisans_sahibi", "teknoloji", "kurulu_mwe", "En büyük 15 şirket (MWe)"), use_container_width=True)

    ui.bolum("02", "Bitiş yılına göre ön lisanslı kapasite", "Ön lisans bitiş yılına göre kurulu güç. Süre dolmadan ilerleme beklenir.")
    ham["bitis_yili"] = pd.to_datetime(ham["bitis"], errors="coerce").dt.year
    yillik = ham.dropna(subset=["bitis_yili"]).groupby(["bitis_yili", "tesis_turu"], as_index=False)["kurulu_mwe"].sum()
    yillik["teknoloji"] = yillik["tesis_turu"].map({"Güneş": "GES", "Rüzgar": "RES"})
    st.plotly_chart(charts.yigin_cubuk(yillik.assign(bitis_yili=yillik["bitis_yili"].astype(int).astype(str)), "bitis_yili", "teknoloji", "kurulu_mwe", "Bitiş yılına göre ön lisanslı kurulu güç (MWe)", "MWe"), use_container_width=True)
    ui.kaynak("Kaynak: EPDK ön lisanslı ve lisanslı üretim tesisleri listeleri.")

    ui.veri_tablosu(sirket[["lisans_sahibi", "teknoloji", "kurulu_mwe"]], "Şirket tablosu", "epdk_onlisans.csv")
