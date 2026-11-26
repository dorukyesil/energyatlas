"""Ülke ve bölge karşılaştırması: güneş PV elektrik üretimi (IEA WEO 2026)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


# Bu bölgeler, ayrı çubuk olarak gösterilen bölgeler içinde zaten yer alır. Üst üste binmemesi için çıkarılır.
KAPSAYAN_BOLGELER = {"European Union": "Avrupa", "United States": "Kuzey Amerika", "Russia": "Avrasya", "Brazil": "Orta ve Güney Amerika"}
ASYA_ALT_BOLGELER = ["China", "India", "Japan", "Southeast Asia"]


def _ayrik_bolgeler(df):
    """Asya Pasifik'ten alt bölgeleri (Çin, Hindistan, Japonya, GD Asya) düşer; kalanı 'diğer' olarak ayırır.
    Avrupa Birliği, ABD ve Rusya ilgili bölgelerin içinde olduğu için ayrı gösterilmez."""
    parcalar = []
    for _, grup in df.groupby("senaryo"):
        grup = grup[~grup["kapsam"].isin(KAPSAYAN_BOLGELER)].copy()
        ap = grup.loc[grup["kapsam"] == "Asia Pacific", "deger"]
        if not ap.empty:
            alt = grup.loc[grup["kapsam"].isin(ASYA_ALT_BOLGELER), "deger"].sum()
            satir = grup[grup["kapsam"] == "Asia Pacific"].copy()
            satir["kapsam"] = "Asia Pacific (diğer)"
            satir["deger"] = ap.iloc[0] - alt
            grup = grup[grup["kapsam"] != "Asia Pacific"]
            grup = pd.concat([grup, satir])
        parcalar.append(grup)
    return pd.concat(parcalar) if parcalar else df


def render() -> None:
    df = data.weo_tum()
    senaryo = ui.segment(data.WEO_SENARYOLAR, "ulke_senaryo")
    yil = st.segmented_control("Yıl", [2025, 2035, 2040, 2050], default=2025, key="ulke_yil") or 2025

    secim = df[
        (df.kategori == "Energy") & (df.akis == "Electricity generation") & (df.urun == "Solar PV")
        & (df.yil == yil) & (df.senaryo.isin(["Gerçekleşen", senaryo])) & (df.kapsam != "Dünya")
    ].copy()
    secim = _ayrik_bolgeler(secim)
    secim["bolge"] = secim["kapsam"].map(lambda k: "Asya Pasifik (diğer)" if k == "Asia Pacific (diğer)" else data.weo_etiket(k))
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

    ui.bolum("01", "Güneş PV üretimi karşılaştırması", "TWh. Çubuklar birbirini kapsamaz: Asya Pasifik'ten Çin, Hindistan, Japonya ve Güneydoğu Asya çıkarılmış, Avrupa Birliği, ABD, Rusya ve Brezilya ayrı gösterilmemiştir.")
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
