"""Kaynaklara göre Türkiye elektrik kurulu gücü (GW), 2016-2026."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Elektrik sistemi",
    "Kaynaklara göre kurulu güç",
    "Türkiye elektrik kurulu gücü ve kaynak paylarının 2016'dan bugüne gelişimi.",
)

df = data.kurulu_guc()
son = df[df["donem"] == "2026 9A"].iloc[0]
ilk = df[df["donem"] == "2016"].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam kurulu güç (2026 9A)", f"{ui.sayi(son['toplam_gw'])} GW", f"{son['toplam_gw'] - ilk['toplam_gw']:+.1f} GW (2016'dan beri)".replace(".", ","))
c2.metric("Güneş payı (2026 9A)", f"%{ui.sayi(son['gunes_pct'], 0)}")
c3.metric("Rüzgar payı (2026 9A)", f"%{ui.sayi(son['ruzgar_pct'], 0)}")
c4.metric("Termik payı (2026 9A)", f"%{ui.sayi(son['termik_pct'], 0)}", f"{son['termik_pct'] - ilk['termik_pct']:+.0f} puan (2016'ya göre)", delta_color="inverse")

ui.bolum("01", "Gelişim", "Görünümü değiştirerek toplam kapasiteyi veya kaynak paylarını inceleyin.")
gorunum = ui.segment(["Toplam (GW)", "Kaynak payı (%)", "Isı haritası"], "kurulu_guc_gorunum")
if gorunum == "Toplam (GW)":
    st.plotly_chart(charts.toplam_cubuk(df, "toplam_gw", "Toplam kurulu güç (GW)", "GW"), use_container_width=True)
elif gorunum == "Kaynak payı (%)":
    st.plotly_chart(charts.pay_yiginli_cubuk(df, "Kaynaklara göre kurulu güç payı (%)"), use_container_width=True)
else:
    matris = df.set_index("donem")[["termik_pct", "gunes_pct", "ruzgar_pct", "diger_ye_pct"]].T
    matris.index = ["Termik", "Güneş", "Rüzgar", "Diğer yenilenebilir"]
    st.plotly_chart(
        charts.isi_haritasi(matris, "Kaynak payı ısı haritası (%)", "turkuaz", "%{z:,.0f}", "%"),
        use_container_width=True,
    )
ui.kaynak("Veri: sunum grafiklerinden okunmuştur. 9A: ocak-eylül. Pay toplamları yuvarlama nedeniyle %100'den sapabilir. 2016 güneş payı kaynakta belirtilmemiştir.")

ui.bolum("02", "Yıllık artış", "Toplam kurulu gücün bir önceki yıla göre değişimi.")
yillik = data.yillik_degisim(df, "toplam_gw")
st.plotly_chart(charts.yillik_degisim_cubuk(yillik, "donem", "degisim_pct", "Toplam kurulu güç: yıllık değişim"), use_container_width=True)

ui.veri_tablosu(df, "Veri tablosu", "kurulu_guc.csv")
