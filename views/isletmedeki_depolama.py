"""İşletmedeki depolama lisanslı projeler: şirketler ve tesis dağılımı."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Depolama ve yatırımlar",
    "İşletmedeki depolama projeleri",
    "İşletmeye alınmış depolama tesisleri. Sıralama işletmedeki kapasiteye göre yapılmıştır.",
)

df = data.isletmedeki_depolama().sort_values("kapasite_mwh", ascending=False).reset_index(drop=True)
ozet = df.groupby("tesis_turu")[["kapasite_mwh", "guc_mwe"]].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam depolama kapasitesi", f"{ui.sayi(df['kapasite_mwh'].sum())} MWh")
c2.metric("Toplam depolama gücü", f"{ui.sayi(df['guc_mwe'].sum())} MWe")
c3.metric("Şirket sayısı", len(df))
c4.metric("Güneş / rüzgar tesisi", f"{int((df['tesis_turu'] == 'Güneş').sum())} / {int((df['tesis_turu'] == 'Rüzgar').sum())}")

ui.bolum("01", "Şirketlere göre kapasite", "İşletmedeki depolama kapasitesi, MWh.")
st.plotly_chart(charts.isletmedeki_cubuk(df, "Şirketlere göre işletmedeki depolama kapasitesi (MWh)"), use_container_width=True)

ui.bolum("02", "Güç ve süre", "Baloncuk boyutu kapasiteyi gösterir. Süre, kapasite bölü güçtür: tesis tam güçte kaç saat enerji verebilir.")
st.plotly_chart(charts.depolama_kabarcik(df, "Depolama gücü ve süresi"), use_container_width=True)
ui.kaynak("Süre = kapasite (MWh) / güç (MWe). Yatay eksen logaritmik ölçektir.")

ui.bolum("03", "Teknolojiye göre özet")
o1, o2 = st.columns(2)
o1.metric("Güneş (GES)", f"{ui.sayi(ozet.loc['Güneş', 'kapasite_mwh'])} MWh", f"{ui.sayi(ozet.loc['Güneş', 'guc_mwe'])} MWe toplam güç", delta_color="off")
o2.metric("Rüzgar (RES)", f"{ui.sayi(ozet.loc['Rüzgar', 'kapasite_mwh'])} MWh", f"{ui.sayi(ozet.loc['Rüzgar', 'guc_mwe'])} MWe toplam güç", delta_color="off")
ui.kaynak(
    "Not: Erguvan, Soma ve Meltem Enerji, Polat Holding'in kontrolündedir. İğdır Hoşhaber Elektrik, Kazancı Holding "
    "(Kazancı ailesi) kontrolündedir. Oze Enerji, Gündüzkanat ailesi/grubu kontrolündedir. Artuklu GES Elektrik, Egesa mülkiyetindedir."
)

ui.veri_tablosu(df, "Tablo", "isletmedeki_depolama.csv")
