"""YEKDEM: taban/tavan fiyatlar, formül, yerli katkı ve EPİAŞ aylık duyuruları."""

import plotly.express as px
import streamlit as st

from src.energyatlas import charts, data, theme, ui


def render() -> None:
    fiyat = data.yekdem_fiyat()
    formul = data.yekdem_formul()
    katki = data.yekdem_yerli_katki().set_index("teknoloji")
    duyuru = data.yekdem_duyuru()
    ptf_2025 = float(fiyat[fiyat["gosterge"].str.startswith("PTF")]["usd_mwh"].iloc[0])

    c1, c2, c3 = st.columns(3)
    c1.metric("Güneş YEKDEM (2025 ortalaması)", "56,6 USD/MWh", f"{56.6 - ptf_2025:+.1f} USD (PTF'e göre)".replace(".", ","), delta_color="off")
    c2.metric("Elektrik depolama YEKDEM (2025 ortalaması)", "66,8 USD/MWh", f"{66.8 - ptf_2025:+.1f} USD (PTF'e göre)".replace(".", ","), delta_color="off")
    c3.metric("2025 ortalama PTF", f"{ui.sayi(ptf_2025)} USD/MWh")

    sekme_fiyat, sekme_duyuru = st.tabs(["Fiyat aralığı ve formül", "EPİAŞ aylık duyuruları"])

    with sekme_fiyat:
        ui.bolum("01", "Taban, ortalama ve tavan", "USD/MWh. Gri sütun 2025 ortalama PTF'dir.")
        g1, g2 = st.columns(2)
        for kolon, teknoloji, renk in [(g1, "Güneş", "#D9A21B"), (g2, "Elektrik Depolama", theme.MUREKKEP)]:
            alt = fiyat[fiyat["teknoloji"] == teknoloji]
            with kolon:
                st.plotly_chart(
                    charts.deger_cubuk(alt["gosterge"].tolist(), alt["usd_mwh"].tolist(), [renk, renk, renk, theme.ADACAYI], f"{teknoloji} YEKDEM (USD/MWh)", "USD/MWh"),
                    use_container_width=True,
                )

        ui.bolum("02", "Formül ve süre", "10 yıl (2021-2030). Her ay güncellenir.")
        st.plotly_chart(
            charts.deger_cubuk(
                formul["bilesen"].tolist(), formul["agirlik_pct"].tolist(),
                [theme.MUREKKEP, theme.TURKUAZ, "#D9A21B", theme.PAS], "Formül bileşenlerinin ağırlığı (%)", "%", sablon="%{text:.0f}%",
            ),
            use_container_width=True,
        )

        ui.bolum("03", "Yerli katkı")
        y1, y2 = st.columns(2)
        y1.metric("Güneş yerli katkı", f"{ui.sayi(katki.loc['Güneş', 'yerli_katki_usd_mwh'], 2)} USD/MWh", f"{katki.loc['Güneş', 'sure_yil']} yıl", delta_color="off")
        y2.metric("Elektrik depolama yerli katkı", f"{ui.sayi(katki.loc['Elektrik Depolama', 'yerli_katki_usd_mwh'], 2)} USD/MWh", f"{katki.loc['Elektrik Depolama', 'sure_yil']} yıl", delta_color="off")
        ui.kaynak("Yerli katkı fiyatı, %100 yerli aksam kullanılması halinde alınabilecek azami tutarları gösterir.")
        ui.veri_tablosu(fiyat, "Veri tablosu", "yekdem_fiyat.csv")

    with sekme_duyuru:
        ui.bolum(
            "01", "Aylık fiyatlar",
            "01.07.2021 - 31.12.2030 arasında işletmeye girecek YEK belgeli tesisler için uygulanacak fiyatlar. Birim: TL kr/kWh.",
        )
        donemler = sorted(duyuru["donem"].unique())
        secim = st.selectbox("Dönem", options=donemler, index=len(donemler) - 1, format_func=lambda d: f"{d[-2:]}.{d[:4]}")
        alt = duyuru[duyuru["donem"] == secim].sort_values("fiyat_kr_kwh", ascending=False)
        en_yuksek, en_dusuk = alt.iloc[0], alt.iloc[-1]
        gunes = alt[alt["kaynak"] == "Güneş Enerjisine Dayalı Üretim Tesisi"].iloc[0]

        d1, d2, d3 = st.columns(3)
        d1.metric("En yüksek fiyat", f"{ui.sayi(en_yuksek['fiyat_kr_kwh'], 2)} kr/kWh", en_yuksek["kaynak"], delta_color="off")
        d2.metric("En düşük fiyat", f"{ui.sayi(en_dusuk['fiyat_kr_kwh'], 2)} kr/kWh", en_dusuk["kaynak"], delta_color="off")
        d3.metric("Güneş fiyatı", f"{ui.sayi(gunes['fiyat_kr_kwh'], 2)} kr/kWh", f"yerli akşam desteği {ui.sayi(gunes['yerli_aksam_kr_kwh'], 2)}", delta_color="off")

        fig = px.bar(alt, x="fiyat_kr_kwh", y="kaynak", orientation="h", labels={"fiyat_kr_kwh": "Fiyat (TL kr/kWh)", "kaynak": ""}, text="fiyat_kr_kwh")
        fig.update_traces(marker_color=theme.MUREKKEP, texttemplate="%{text:,.2f}", textposition="outside")
        fig.update_layout(template=theme.SABLON, yaxis=dict(autorange="reversed"), height=520, bargap=0.5, margin=dict(l=10, r=50, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        ui.bolum("02", "Aylara göre karşılaştırma", "Koyu renk daha yüksek fiyattır.")
        matris = duyuru.pivot(index="kaynak", columns="donem", values="fiyat_kr_kwh")
        matris.columns = [f"{d[-2:]}.{d[:4]}" for d in matris.columns]
        isi = charts.isi_haritasi(matris, "Kaynak ve aya göre YEKDEM fiyatı (TL kr/kWh)", "turkuaz", "%{z:,.0f}", "kr/kWh")
        isi.update_layout(height=520, margin=dict(l=10, r=10, t=56, b=10))
        st.plotly_chart(isi, use_container_width=True)
        ui.kaynak("Kaynak: EPİAŞ, Kayıt ve Uzlaştırma duyuruları.")

        ui.veri_tablosu(duyuru, "Tam tablo", "yekdem_duyuru.csv")
