"""Ana sayfa: öne çıkan gösterge, gösterge şeridi ve kategori kartları."""

import streamlit as st

from src.energyatlas import charts, data, ui

kurulu = data.kurulu_guc()
uretim = data.uretim()
tuketim = data.tuketim()
ptf = data.ptf()
kurulu_yillik = data.tam_yillar(kurulu)
son_9a = kurulu.set_index("donem").loc["2026 9A"]

sol, sag = st.columns([5, 6], gap="large")
with sol:
    st.markdown(
        f"""<div class="ea-eyebrow">Türkiye elektrik sektörü verileri</div>
<div class="ea-hero-baslik">Enerji Atlası</div>
<div class="ea-hero-etiket">Toplam kurulu güç · 2026 9A</div>
<div class="ea-hero-no">{ui.sayi(son_9a['toplam_gw'])}<small>GW</small></div>
<div class="ea-hero-not">Kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler tek yerde.
Sol menüden bir kategori seçin veya aşağıdaki bölümlere göz atın.</div>""",
        unsafe_allow_html=True,
    )
with sag:
    st.plotly_chart(
        charts.cizgi_alan(kurulu_yillik, "donem", "toplam_gw", "Toplam kurulu güç (GW)", "GW", "GW"),
        use_container_width=True,
    )

uretim_yillik = data.tam_yillar(uretim)
tuketim_yillik = data.tam_yillar(tuketim)
ptf_yillik = data.tam_yillar(ptf)
ye_payi = 100 - uretim.set_index("donem").loc["2026 9A", "termik_pct"]
ye_payi_seri = (100 - uretim_yillik["termik_pct"]).tolist()
ptf_son = ptf.set_index("donem")

ui.kpi_serit(
    [
        {
            "etiket": "Kurulu güç, yıllık",
            "deger": ui.sayi(kurulu_yillik["toplam_gw"].iloc[-1]),
            "birim": "GW",
            "alt": f"2016: {ui.sayi(kurulu_yillik['toplam_gw'].iloc[0])} GW",
            "ton": "p",
            "seri": kurulu_yillik["toplam_gw"].tolist(),
        },
        {
            "etiket": "Yenilenebilir üretim payı (2026 9A)",
            "deger": ui.sayi(ye_payi, 0),
            "birim": "%",
            "alt": f"2016: %{ui.sayi(ye_payi_seri[0], 0)}",
            "ton": "p",
            "seri": ye_payi_seri,
        },
        {
            "etiket": "Brüt tüketim, yıllık",
            "deger": ui.sayi(tuketim_yillik["tuketim_twh"].iloc[-1], 0),
            "birim": "TWh",
            "alt": f"2016: {ui.sayi(tuketim_yillik['tuketim_twh'].iloc[0], 0)} TWh",
            "ton": "p",
            "seri": tuketim_yillik["tuketim_twh"].tolist(),
        },
        {
            "etiket": "PTF, yıllık ortalama",
            "deger": ui.sayi(ptf_yillik["ptf_usd_mwh"].iloc[-1], 0),
            "birim": "USD/MWh",
            "alt": f"2026 9A: {ui.sayi(ptf_son.loc['2026 9A', 'ptf_usd_mwh'], 0)} USD/MWh",
            "ton": "n",
            "seri": ptf_yillik["ptf_usd_mwh"].tolist(),
        },
    ]
)
ui.kaynak("Mini grafikler 2016-2025 tam yıl değerlerini gösterir. 9A: ocak-eylül dönemi.")

ui.bolum("01", "Bölümler", "Kategorilere göre düzenlenmiş sayfalar. Başlıklara tıklayarak ilgili sayfaya geçebilirsiniz.")

kartlar = [
    ("⚡", "Elektrik sistemi", "Kurulu güç, üretim ve tüketimin 2016'dan bugüne gelişimi.", [
        ("views/kurulu_guc.py", "Kaynaklara göre kurulu güç", "⚡"),
        ("views/uretim.py", "Kaynaklara göre üretim", "🏭"),
        ("views/tuketim.py", "Brüt elektrik tüketimi", "📈"),
        ("views/kisi_basina.py", "Kişi başına tüketim", "👥"),
    ]),
    ("🔋", "Depolama ve yatırımlar", "Depolamalı santraller, ön lisanslar ve işletmedeki projeler.", [
        ("views/devam_eden_yatirimlar.py", "Devam eden yatırımlar", "🏗️"),
        ("views/depolama_sebeke.py", "Depolama ve şebeke", "🔋"),
        ("views/depolama_on_lisans.py", "Depolama ön lisansları", "📅"),
        ("views/isletmedeki_depolama.py", "İşletmedeki depolama", "🏭"),
    ]),
    ("💲", "Fiyatlar ve tarifeler", "Piyasa takas fiyatı, EPDK tarifeleri ve YEKDEM.", [
        ("views/ptf.py", "Piyasa takas fiyatı (PTF)", "💹"),
        ("views/epdk_tarifeleri.py", "EPDK elektrik tarifeleri", "💡"),
        ("views/yekdem.py", "YEKDEM", "⚖️"),
    ]),
    ("🎯", "Altyapı ve hedefler", "İletim ağı yatırımları ve piyasa hedefleri.", [
        ("views/iletim_agi.py", "Elektrik iletim ağı", "🔌"),
        ("views/piyasa_hedefleri.py", "Piyasa hedefleri", "🎯"),
    ]),
    ("🌍", "Dünya ve karşılaştırma", "Küresel güneş kapasitesi, ülkeler ve yatırımlar.", [
        ("views/dunya_gunes.py", "Dünya güneş kapasitesi", "☀️"),
        ("views/ulke_karsilastirma.py", "Ülke karşılaştırması", "🗺️"),
        ("views/kuresel_yatirimlar.py", "Küresel enerji yatırımları", "💰"),
    ]),
    ("🌍", "Dünya enerji görünümü", "IEA WEO 2026: enerji arzı, elektrik, emisyonlar, talep ve bölgeler.", [
        ("views/weo_enerji_arz.py", "Birincil enerji arzı", "🌍"),
        ("views/weo_elektrik.py", "Elektrik üretimi ve kapasite", "⚡"),
        ("views/weo_emisyon.py", "CO2 emisyonları", "🌫️"),
        ("views/weo_talep_ekonomi.py", "Enerji talebi ve ekonomi", "🏭"),
        ("views/weo_teknoloji.py", "Hidrojen ve karbon yakalama", "🧪"),
        ("views/weo_bolgesel.py", "Bölgesel karşılaştırma", "🗺️"),
    ]),
    ("📘", "Hakkında", "Veri kaynakları, kısaltmalar ve kullanım notları.", [
        ("views/hakkinda.py", "Hakkında ve veri notları", "📘"),
    ]),
]
for i in range(0, len(kartlar), 3):
    for kolon, (ikon, baslik, aciklama, sayfalar) in zip(st.columns(3, gap="medium"), kartlar[i:i + 3]):
        with kolon:
            ui.kategori_karti(ikon, baslik, aciklama, sayfalar)
