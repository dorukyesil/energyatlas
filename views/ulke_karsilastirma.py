"""Ülke ve bölge karşılaştırması: güneş PV elektrik üretimi (IEA WEO 2026)."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Ülke ve bölge karşılaştırması: güneş üretimi",
    "IEA WEO 2026'da yer alan ülke ve bölgelerin güneş PV elektrik üretimi (TWh). Senaryo ve yıl seçerek karşılaştırın.",
)

df = data.weo_tum()
senaryo = ui.segment(data.WEO_SENARYOLAR, "ulke_senaryo")
yil = st.segmented_control("Yıl", [2025, 2035, 2040, 2050], default=2025, key="ulke_yil") or 2025

secim = df[
    (df.kategori == "Energy") & (df.akis == "Electricity generation") & (df.urun == "Solar PV")
    & (df.yil == yil) & (df.senaryo.isin(["Gerçekleşen", senaryo])) & (df.kapsam != "Dünya")
].copy()
secim["bolge"] = secim["kapsam"].map(data.weo_etiket)
dunya = df[
    (df.kapsam == "Dünya") & (df.kategori == "Energy") & (df.akis == "Electricity generation") & (df.urun == "Solar PV")
    & (df.yil == yil) & (df.senaryo.isin(["Gerçekleşen", senaryo]))
]

# Türkiye: WEO'da ayrı kırılım yok. TEİAŞ kurulu güç ve güneş payından türetilen kurulu güç.
kurulu = data.kurulu_guc().set_index("donem")
tr_guc_2026 = kurulu.loc["2026 9A", "toplam_gw"] * kurulu.loc["2026 9A", "gunes_pct"] / 100

c1, c2, c3 = st.columns(3)
c1.metric(f"Dünya güneş PV üretimi ({yil})", f"{ui.sayi(dunya['deger'].iloc[0], 0)} TWh" if not dunya.empty else "-")
if not secim.empty:
    lider = secim.sort_values("deger", ascending=False).iloc[0]
    c2.metric("En büyük (bölge)", lider["bolge"], f"{ui.sayi(lider['deger'], 0)} TWh", delta_color="off")
c3.metric("Türkiye kurulu güneş (2026 9A)", f"{ui.sayi(tr_guc_2026, 1)} GW", "TEİAŞ kurulu güç payından türetilmiştir", delta_color="off")

ui.bolum("01", "Güneş PV üretimi karşılaştırması", "Ülke ve bölgeler, TWh. Bölgeler birbirini kapsayabilir (ör. Avrupa Birliği, Avrupa'nın parçasıdır).")
if secim.empty:
    st.info("Bu yıl ve senaryo için veri yok.")
else:
    st.plotly_chart(charts.yatay_deger_cubuk(secim, "bolge", "deger", f"Güneş PV üretimi, {yil} ({senaryo.lower()}, TWh)", "TWh"), use_container_width=True)
ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A ücretsiz veri seti. Türkiye bu veri setinde ayrı yer almaz.")

ui.bolum("02", "Türkiye", "WEO verisinde Türkiye yok. Türkiye'nin güneş kurulu gücü, TEİAŞ toplam kurulu gücü ve güneş payından hesaplanır.")
st.markdown(
    f"2026 9A itibarıyla toplam kurulu güç **{ui.sayi(kurulu.loc['2026 9A', 'toplam_gw'])} GW**, güneş payı **%{ui.sayi(kurulu.loc['2026 9A', 'gunes_pct'], 0)}** "
    f"ile güneş kurulu gücü yaklaşık **{ui.sayi(tr_guc_2026, 1)} GW**'tır. Bu değer, sunum grafiğindeki yuvarlanmış paylardan hesaplanmıştır."
)

ui.veri_tablosu(secim[["kapsam", "senaryo", "yil", "deger", "birim"]], "Veri tablosu", "weo_2026.csv")
