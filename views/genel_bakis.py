"""Ana sayfa: özet göstergeler, veri güncelleme, sunum indirme ve konu kartları."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, export, guncelleme, ptf_analiz as pa, ui

kurulu = data.kurulu_guc()
uretim = data.uretim()
tuketim = data.tuketim()
kurulu_yillik = data.teias_kurulu_guc()[["donem", "toplam_gw", "yil"]]
son_9a = {"toplam_gw": data.teias_ytbs()["kurulu_guc_gw"].sum(), "yenilenebilir_gw": data.teias_ytbs().query("grup != 'Termik'")["kurulu_guc_gw"].sum()}


@st.cache_data(show_spinner="Sunum hazırlanıyor…")
def _sunum_bytes(surum: str) -> bytes:
    """Sunum dosyasını üretir. `surum` (son güncelleme zamanı) değiştiğinde yeniden üretilir."""
    return export.ozet_sunum_bytes()


ui.hero(
    "Enerji Atlası",
    "Türkiye ve dünya elektrik sektörü: kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler tek yerde.",
)

ust1, ust2, ust3 = st.columns([3, 1.2, 1.4])
with ust1:
    st.caption(f"Son güncelleme: {guncelleme.son_guncelleme_metni()}")
with ust2:
    if st.button("Verileri güncelle", use_container_width=True, help="Veri dosyalarını yeniden okur ve sunumu yeniler."):
        st.cache_data.clear()
        data.yenile()
        guncelleme.guncelle()
        st.rerun()
with ust3:
    st.download_button(
        "Sunumu indir (.pptx)",
        data=_sunum_bytes(guncelleme.son_guncelleme_metni()),
        file_name="enerji_atlasi_sunum.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )

sol, sag = st.columns([5, 6], gap="large")
with sol:
    st.markdown(
        f"""<div class="ea-eyebrow">Türkiye elektrik sektörü verileri</div>
<div class="ea-hero-etiket">Toplam kurulu güç · güncel (YTBS)</div>
<div class="ea-hero-no">{ui.sayi(son_9a["toplam_gw"])}<small>GW</small></div>
<div class="ea-hero-etiket" style="margin-top:0.6rem">Yenilenebilir kurulu güç · güncel (YTBS)</div>
<div class="ea-hero-no" style="font-size:3.2rem">{ui.sayi(son_9a["yenilenebilir_gw"])}<small>GW · %{ui.sayi(son_9a["yenilenebilir_gw"] / son_9a["toplam_gw"] * 100, 0)}</small></div>
<div class="ea-hero-not">Aşağıdaki konulardan birini seçerek ilgili sayfaya geçin.</div>""",
        unsafe_allow_html=True,
    )
with sag:
    ytbs_toplam = data.teias_ytbs()["kurulu_guc_gw"].sum()
    ytbs_tarih = pd.to_datetime(data.teias_ytbs()["tarih"].iloc[0])
    yen_yillik = data.teias_yenilenebilir()["yenilenebilir_gw"].tolist()
    yen_guncel = float(data.teias_ytbs().query("grup != 'Termik'")["kurulu_guc_gw"].sum())
    termik_yillik = data.teias_kurulu_guc()["termik_gw"].tolist()
    termik_guncel = float(data.teias_ytbs().query("grup == 'Termik'")["kurulu_guc_gw"].sum())
    st.plotly_chart(
        charts.canli_kurulu_guc(kurulu_yillik, ytbs_toplam, ytbs_tarih, "Kurulu güç: toplam, yenilenebilir ve termik (GW)",
                                yen_yillik=yen_yillik, yen_guncel=yen_guncel,
                                termik_yillik=termik_yillik, termik_guncel=termik_guncel),
        use_container_width=True,
    )

ytbs = data.teias_ytbs()
ytbs_toplam = float(ytbs["kurulu_guc_gw"].sum())
ytbs_tarih = pd.to_datetime(ytbs["tarih"].iloc[0]).strftime("%d.%m.%Y")

aylik = data.teias_aylik()
o26 = aylik[(aylik["yil"] == 2026) & (aylik["ay_no"] <= 10)]
o25 = aylik[(aylik["yil"] == 2025) & (aylik["ay_no"] <= 10)]
yen26 = float(o26[["hydro", "wind", "solar", "geothermal"]].sum().sum() / o26["total_generation"].sum() * 100)
tuk26 = float(o26["gross_demand"].sum()) / 1000
tuk25 = float(o25["gross_demand"].sum()) / 1000
tuk_degisim = (tuk26 / tuk25 - 1) * 100

uretim_yillik = data.teias_uretim().copy()
yenilenebilir_yillik = (uretim_yillik["hidro_twh"] + uretim_yillik["ruzgar_jeotermal_twh"] + uretim_yillik["gunes_twh"]) / uretim_yillik["toplam_twh"] * 100
yenilenebilir_seri = yenilenebilir_yillik.tolist() + [yen26]
yenilenebilir_yillar = uretim_yillik["donem"].tolist() + ["2026 Oca-Eki"]

tuketim_yillik = data.teias_talep()
kurulu_seri = kurulu_yillik["toplam_gw"].tolist() + [ytbs_toplam]
kurulu_yillar = kurulu_yillik["donem"].tolist() + ["2026 güncel"]

ptf_yil = pa.yillik(data.ptf_gunluk())
ptf_son_tarih = data.ptf_gunluk()["tarih"].max().strftime("%d.%m")
ptf_seri = ptf_yil["usd"].tolist()
ptf_yillar = ptf_yil["donem"].tolist()
ptf_2026 = float(ptf_yil.loc[ptf_yil["yil"] == ptf_yil["yil"].max(), "usd"].iloc[0])
ptf_2025 = float(ptf_yil.loc[ptf_yil["yil"] == 2025, "usd"].iloc[0])

ui.kpi_serit(
    [
        {"etiket": "Kurulu güç (2026 güncel, YTBS)", "deger": ui.sayi(ytbs_toplam), "birim": "GW",
         "alt": f"TEİAŞ 2025: {ui.sayi(kurulu_yillik['toplam_gw'].iloc[-1])} GW · {ytbs_tarih}", "ton": "p",
         "seri": kurulu_seri, "yillar": kurulu_yillar},
        {"etiket": "Yenilenebilir üretim payı (2026 Ocak-Ekim)", "deger": ui.sayi(yen26, 0), "birim": "%",
         "alt": f"2025 tam yıl: %{ui.sayi(yenilenebilir_yillik.iloc[-1], 0)}", "ton": "p",
         "seri": yenilenebilir_seri, "yillar": yenilenebilir_yillar, "ondalik": 0},
        {"etiket": "Brüt tüketim (2026 Ocak-Ekim)", "deger": ui.sayi(tuk26, 0), "birim": "TWh",
         "alt": f"2025 aynı dönem: {ui.sayi(tuk25, 0)} TWh ({tuk_degisim:+.1f}%)".replace(".", ","), "ton": "p" if tuk_degisim >= 0 else "n",
         "seri": tuketim_yillik["brut_talep_twh"].tolist(), "yillar": tuketim_yillik["donem"].tolist(), "ondalik": 0},
        {"etiket": f"PTF (2026, 1 Oca–{ptf_son_tarih} ortalama)", "deger": ui.sayi(ptf_2026, 0), "birim": "USD/MWh",
         "alt": f"2025 tam yıl: {ui.sayi(ptf_2025, 0)} USD/MWh", "ton": "n",
         "seri": ptf_seri, "yillar": ptf_yillar, "ondalik": 0},
    ]
)
ui.kaynak("Mini grafikler her dönem için en güncel değeri de içerir; noktanın üzerine gelerek yıl ve değeri görebilirsiniz. Parantez içinde dönem yazılıdır. Kurulu güç: YTBS (günlük), diğerleri TEİAŞ/EPİAŞ.")

ui.bolum("01", "Konular", "Her kart bir konu sayfasını açar. Sayfalar kendi içinde sekmelere ayrılmıştır.")

kartlar = [
    ("⚡", "Elektrik piyasası", "Kurulu güç, üretim, tüketim ve depolama.",
     ["Kurulu güç", "Üretim", "Tüketim", "Depolama ve ön lisanslar"],
     "views/elektrik_piyasasi.py", "Elektrik piyasasına git"),
    ("🎯", "Hedefler ve güncel gelişmeler", "Geçmiş ve yeni hedefler, devam eden yatırımlar.",
     ["Hedefler", "Devam eden yatırımlar", "Güncel gelişmeler"],
     "views/hedefler_gelismeler.py", "Hedeflere git"),
    ("☀️", "Lisanssız üretim", "Lisanssız üretimin mevzuatı, gelişimi ve ihtiyaç fazlası hesaplamaları.",
     ["Yakında eklenecek"],
     "views/lisanssiz.py", "Lisanssız üretime git"),
    ("💲", "Fiyatlandırma", "EPDK tarifeleri, piyasa takas fiyatı ve YEKDEM.",
     ["EPDK tarifeleri", "PTF (piyasa takas fiyatı)", "YEKDEM"],
     "views/fiyatlandirma.py", "Fiyatlandırmaya git"),
    ("🌍", "Dünya enerji görünümü", "IEA WEO 2026 verileri: enerji arzı, elektrik, emisyonlar, talep ve teknolojiler.",
     ["Güneş kapasitesi", "Birincil enerji arzı", "Elektrik üretimi ve kapasite", "CO2 emisyonları", "Talep ve ekonomi", "Hidrojen ve CCUS"],
     "views/dunya_enerji.py", "Dünya görünümüne git"),
    ("🗺️", "Dünya karşılaştırma", "Bölgesel karşılaştırma, ülke güneş üretimi ve küresel yatırımlar.",
     ["Bölgesel karşılaştırma", "Ülke ve bölge güneş üretimi", "Küresel enerji yatırımları"],
     "views/dunya_karsilastirma.py", "Karşılaştırmaya git"),
]
for i in range(0, len(kartlar), 3):
    for kolon, (ikon, baslik, aciklama, maddeler, yol, etiket) in zip(st.columns(3, gap="medium"), kartlar[i:i + 3]):
        with kolon:
            ui.kategori_karti_basit(ikon, baslik, aciklama, maddeler, yol, etiket)
    st.write("")

st.page_link("views/hakkinda.py", label="Hakkında ve veri kaynakları →", icon="📘")
