"""Türkiye elektrik piyasası kurulu güç hedefleri: 2025 gerçekleşen, 2028 ve 2035 hedefleri."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.hedefler()
    satir = df.set_index("kaynak")

    toplam_2025 = satir.loc["Toplam", "gerceklesen_2025_gw"]
    toplam_2028 = satir.loc["Toplam", "hedef_2028_stratejik_plan_gw"]
    toplam_2035 = satir.loc["Toplam", "hedef_2035_yenilenebilir_yol_haritasi_gw"]
    yenilenebilir_2035 = satir.loc["Toplam Yenilenebilir", "hedef_2035_yenilenebilir_yol_haritasi_gw"]
    gunes_ruzgar_2035 = satir.loc["Güneş", "hedef_2035_yenilenebilir_yol_haritasi_gw"] + satir.loc["Rüzgar", "hedef_2035_yenilenebilir_yol_haritasi_gw"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam kurulu güç (2028 hedefi)", f"{ui.sayi(toplam_2028)} GW", f"{toplam_2028 - toplam_2025:+.1f} GW (2025'e göre)".replace(".", ","))
    c2.metric("Toplam kurulu güç (2035 yol haritası)", f"{ui.sayi(toplam_2035)} GW", f"{toplam_2035 - toplam_2025:+.1f} GW (2025'e göre)".replace(".", ","))
    c3.metric("Güneş + rüzgar kapasitesi (2035)", f"{ui.sayi(gunes_ruzgar_2035)} GW", f"yenilenebilir toplam {ui.sayi(yenilenebilir_2035)} GW", delta_color="off")

    ui.bolum("01", "Senaryo karşılaştırması", "Güneş, rüzgar ve termik kurulu güç hedeflerinin senaryolara göre değişimi.")
    st.plotly_chart(charts.hedef_karsilastirma(df, "Senaryolara göre güneş, rüzgar ve termik kurulu güç (GW)"), use_container_width=True)
    ui.kaynak("Yol haritasındaki toplam ve yenilenebilir değerlerin dipnotu (*) kaynakta açıklanmamıştır.")

    ui.bolum("02", "Kaynak payı", "2025, 2028 ve 2035 için toplam kurulu gücün kaynaklara dağılımı. Diğer yenilenebilir, toplamdan hesaplanmıştır.")
    donemler = {
        "2025 gerçekleşen": "gerceklesen_2025_gw",
        "2028 Stratejik Plan": "hedef_2028_stratejik_plan_gw",
        "2035 YE Yol Haritası": "hedef_2035_yenilenebilir_yol_haritasi_gw",
    }
    for kolon, (baslik, kaynak_kolonu) in zip(st.columns(len(donemler)), donemler.items()):
        toplam = satir.loc["Toplam", kaynak_kolonu]
        gunes = satir.loc["Güneş", kaynak_kolonu]
        ruzgar = satir.loc["Rüzgar", kaynak_kolonu]
        termik = satir.loc["Toplam Termik", kaynak_kolonu]
        diger = toplam - gunes - ruzgar - termik
        with kolon:
            st.plotly_chart(
                charts.pay_halkasi(["Güneş", "Rüzgar", "Diğer Yenilenebilir", "Termik"], [gunes, ruzgar, diger, termik], f"{baslik}: {toplam:.0f} GW"),
                use_container_width=True,
            )

    ui.bolum("03", "Elektrik tüketimi hedefi")
    tuketim_2025 = satir.loc["Elektrik Tüketimi (TWh)", "gerceklesen_2025_gw"]
    tuketim_2035 = satir.loc["Elektrik Tüketimi (TWh)", "hedef_2035_ulusal_enerji_plani_gw"]
    st.markdown(
        f"2025'te **{ui.sayi(tuketim_2025)} TWh** olan tüketimin, Ulusal Enerji Planı'na göre 2035'te "
        f"**{ui.sayi(tuketim_2035)} TWh** olması hedefleniyor (yaklaşık %{ui.sayi((tuketim_2035 / tuketim_2025 - 1) * 100, 0)} artış)."
    )

    ui.veri_tablosu(df, "Veri tablosu", "hedefler.csv")
