"""İşletmedeki depolama: EPDK lisanslı tesislerinden işletmede olan depolama kapasiteleri."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Depolama ve yatırımlar",
    "İşletmedeki depolama projeleri",
    "EPDK lisanslı tesislerden işletmede olan depolama kapasiteleri. Sıralama MWh'ye göre yapılmıştır.",
)

ham = data.epdk_lisans()
df = ham[ham["isletmedeki_depolama_mwh"] > 0].copy()
df = df.rename(columns={"isletmedeki_depolama_mwh": "kapasite_mwh", "isletmedeki_depolama_mwe": "guc_mwe"})
df = df.sort_values("kapasite_mwh", ascending=False).reset_index(drop=True)
ozet = df.groupby("tesis_turu")[["kapasite_mwh", "guc_mwe"]].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam depolama kapasitesi", f"{ui.sayi(df['kapasite_mwh'].sum())} MWh")
c2.metric("Toplam depolama gücü", f"{ui.sayi(df['guc_mwe'].sum())} MWe")
c3.metric("İşletmedeki tesis sayısı", len(df))
c4.metric("Güneş / rüzgar", f"{int((df['tesis_turu'] == 'Güneş').sum())} / {int((df['tesis_turu'] == 'Rüzgar').sum())}")

ui.bolum("01", "Şirketlere göre kapasite", "İşletmedeki depolama kapasitesi, MWh.")
st.plotly_chart(charts.isletmedeki_cubuk(df, "Tesislere göre işletmedeki depolama kapasitesi (MWh)"), use_container_width=True)

ui.bolum("02", "Güç ve süre", "Baloncuk boyutu kapasiteyi gösterir. Süre, kapasite bölü güçtür: tesis tam güçte kaç saat enerji verebilir.")
st.plotly_chart(charts.depolama_kabarcik(df, "Depolama gücü ve süresi"), use_container_width=True)
ui.kaynak("Süre = kapasite (MWh) / güç (MWe). Yatay eksen logaritmik ölçektir.")

ui.bolum("03", "Teknolojiye göre özet")
o1, o2 = st.columns(2)
if "Güneş" in ozet.index:
    o1.metric("Güneş (GES)", f"{ui.sayi(ozet.loc['Güneş', 'kapasite_mwh'])} MWh", f"{ui.sayi(ozet.loc['Güneş', 'guc_mwe'])} MWe toplam güç", delta_color="off")
if "Rüzgar" in ozet.index:
    o2.metric("Rüzgar (RES)", f"{ui.sayi(ozet.loc['Rüzgar', 'kapasite_mwh'])} MWh", f"{ui.sayi(ozet.loc['Rüzgar', 'guc_mwe'])} MWe toplam güç", delta_color="off")
ui.kaynak("Kaynak: EPDK, lisanslı üretim tesisleri listesi.")

ui.veri_tablosu(df[["lisans_sahibi", "tesis_adi", "il", "tesis_turu", "kapasite_mwh", "guc_mwe"]], "Tablo", "epdk_lisans.csv")
