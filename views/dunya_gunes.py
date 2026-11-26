"""Dünya güneş kapasitesi ve üretimi: IEA WEO 2026 senaryolarına göre."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya ve karşılaştırma",
    "Dünya güneş kapasitesi",
    "IEA World Energy Outlook 2026. Senaryoyu seçerek güneşin dünya kapasitesi ve üretimindeki yerini inceleyin.",
)

ham = data.weo_dunya()
senaryolar = {
    "Mevcut politikalar": "Current Policies Scenario",
    "Belirlenmiş politikalar": "Stated Policies Scenario",
    "Net sıfır (2050)": "Net Zero Emissions by 2050 Scenario",
}
secim = ui.segment(list(senaryolar.keys()), "dunya_senaryo")
kod = senaryolar[secim]

gecmis = ham[(ham["senaryo"] == "Historical") & (ham["gosterge"] == "Kurulu güç (GW)")]
gelecek = ham[(ham["senaryo"] == kod) & (ham["gosterge"] == "Kurulu güç (GW)")]
kapasite = pd.concat([gecmis, gelecek])
pivot = kapasite.pivot_table(index="yil", columns="kaynak", values="deger").reset_index()
pivot = pivot[pivot["yil"].isin([2010, 2024, 2025, 2035, 2040, 2050])]
pivot["Güneş pay (%)"] = pivot["Solar PV"] / pivot["Total"] * 100

son_gecmis = pivot[pivot["yil"] == 2025].iloc[0]
son_senaryo = pivot[pivot["yil"] == 2050].iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Dünya güneş kapasitesi (2025)", f"{ui.sayi(son_gecmis['Solar PV'], 0)} GW")
c2.metric("Güneş payı (2025)", f"%{ui.sayi(son_gecmis['Güneş pay (%)'], 0)}")
c3.metric(f"Güneş kapasitesi (2050, {secim.lower()})", f"{ui.sayi(son_senaryo['Solar PV'], 0)} GW")
c4.metric("Güneş payı (2050)", f"%{ui.sayi(son_senaryo['Güneş pay (%)'], 0)}")

ui.bolum("01", "Kapasite", "Toplam kurulu güç ve güneş kapasitesi, GW. 2010, 2024 ve 2025 gerçekleşen; sonrası seçilen senaryo.")
st.plotly_chart(
    charts.dunya_kurulu_cubuk(
        pivot.rename(columns={"yil": "donem", "Total": "toplam_gw", "Solar PV": "gunes_gw"}).assign(donem=lambda d: d["donem"].astype(str)),
        f"Dünya toplam kurulu güç ve güneş, {secim.lower()} (GW)",
    ),
    use_container_width=True,
)

ui.bolum("02", "Güneşin payı", "Güneşin toplam kurulu güç içindeki payı, %.")
st.plotly_chart(
    charts.toplam_cubuk(
        pivot.assign(donem=pivot["yil"].astype(str), pay=pivot["Güneş pay (%)"].round(1)),
        "pay", "Güneşin toplam kurulu güç içindeki payı (%)", "%",
    ),
    use_container_width=True,
)

ui.bolum("03", "Üretim", "Güneş elektrik üretimi, TWh (seçilen senaryo).")
uretim = ham[(ham["gosterge"] == "Elektrik üretimi (TWh)") & (ham["kaynak"] == "Solar PV") & (ham["senaryo"].isin(["Historical", kod]))]
uretim = uretim[uretim["yil"].isin([2010, 2024, 2025, 2035, 2040, 2050])].sort_values("yil")
st.plotly_chart(
    charts.toplam_cubuk(uretim.assign(donem=uretim["yil"].astype(str)), "deger", "Dünya güneş elektrik üretimi (TWh)", "TWh"),
    use_container_width=True,
)
ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A ücretsiz veri seti. 2010-2025 gerçekleşen; sonraki yıllar seçilen senaryodur.")

ui.veri_tablosu(ham, "Veri tablosu (tüm senaryolar)", "weo_dunya.csv")
