"""Sunum (PowerPoint) üretimi.

Slayt düzeni, KYB eğitim sunumunun seçilmiş bölümlerini izler: kapak, yasal çekince,
içerik ve seçilen konu slaytları. İçerik ve sayılar Enerji Atlası veri katmanından
(src/energyatlas/data.py) hesaplanır. Grafikler PowerPoint'in kendi grafik nesneleridir,
böylece sunumda düzenlenebilir. Streamlit'e bağımlı değildir.
"""

from __future__ import annotations

import io
from datetime import date

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from src.energyatlas import charts, data, theme

KAGIT = theme.KAGIT
KART = theme.KAGIT_KART
KAGIT_2 = theme.KAGIT_2
CIZGI = theme.CIZGI
METIN = theme.METIN
SOLUK = theme.SOLUK
MUREKKEP = theme.MUREKKEP
TURKUAZ = theme.TURKUAZ
PAS = theme.PAS
OKRA = theme.OKRA
ZEYTIN = theme.ZEYTIN
CELIK = theme.CELIK
GRI = theme.GRI
BEYAZ = "#FFFFFF"
ACIK_MAVI = "#DCE7F3"
SERI_RENK = [MUREKKEP, TURKUAZ, OKRA, PAS, ZEYTIN, CELIK, GRI, theme.ADACAYI]
STAKLI = {XL_CHART_TYPE.COLUMN_STACKED_100, XL_CHART_TYPE.COLUMN_STACKED, XL_CHART_TYPE.BAR_STACKED}

YASAL = [
    "Bu sunumda yer alan her türlü bilgi, açıklama, değerlendirme, hesaplama, örnek, vaka çalışması, cevap anahtarı, senaryo, varsayım, oran, fiyat, tarife, tutar, projeksiyon, grafik ve tablo Türkiye Kalkınma ve Yatırım Bankası A.Ş. (“Kalkınma Yatırım Bankası”) tarafından münhasıran genel bilgilendirme ve eğitim amaçlarıyla hazırlanmıştır. Sunumda yer alan hiçbir içerik; herhangi bir kişi, kurum, yatırım, proje veya finansman işlemi bakımından hukuki, mali, vergisel, teknik veya düzenleyici danışmanlık, yatırım danışmanlığı, kredi tahsis görüşü, değerleme görüşü veya sair profesyonel görüş niteliğinde olmadığı gibi herhangi bir vaat, taahhüt, garanti, temsil, teklif, öneri veya getiri beklentisi olarak da yorumlanamaz.",
    "Sunum kapsamında kullanılan tüm sayısal değerler, oranlar, fiyatlar, tarifeler, üretim ve tüketim miktarları, PTF ve YEKDEM değerleri, enflasyon ve benzeri makroekonomik varsayımlar, gelir tahminleri, projeksiyonlar ve diğer hesaplamalar, aksi açıkça belirtilmedikçe, yalnızca eğitim amacıyla oluşturulmuş örneklerdir. Söz konusu değer ve hesaplamalar herhangi bir gerçek yatırımın, projenin, tesisin, şirketin veya finansman işleminin mevcut ya da gelecekteki performansını yansıtmaz veya garanti etmez. Varsayımlara dayalı tahmin ve projeksiyonlar belirsizlik içerir; gerçekleşen sonuçlar sunumda kullanılan varsayım ve projeksiyonlardan önemli ölçüde farklılaşabilir. Geçmiş dönem verileri veya gerçekleşmeleri, gelecekteki sonuçların göstergesi veya garantisi değildir.",
    "Sunumda yer alan vaka çalışmaları, örnek çözümler, cevap anahtarları ve hesaplama yöntemleri, yalnızca eğitim konularının anlaşılmasını kolaylaştırmak amacıyla hazırlanmıştır. Bunlar, herhangi bir gerçek tesis, yatırım veya işlem bakımından uygulanması gereken kesin yöntem, hukuki görüş, düzenleyici yorum, kredi kararı veya değerleme sonucu olarak kabul edilmemelidir.",
    "Elektrik piyasasına ilişkin kanunlar, yönetmelikler, tebliğler, ikincil düzenlemeler, kurul kararları, tarifeler, fiyatlandırma ve mahsuplaşma esasları, YEKDEM uygulamaları, piyasa işletim kuralları ve diğer ilgili düzenlemeler sık aralıklarla değişebilmekte; bunların yorumu ve uygulaması da yetkili idari veya yargısal mercilerin kararları ve uygulamaları doğrultusunda zaman içerisinde farklılaşabilmektedir. Bu nedenle sunumda yer alan bilgilerin güncelliği ve uygulanabilirliği her kullanım, değerlendirme ve karar alma süreci öncesinde yeniden ve bağımsız olarak kontrol edilmelidir.",
    "İlgili mevzuat, tarife, kurul kararı ve resmi kurum uygulamalarının güncel halleri düzenli olarak takip edilmeli; yalnızca bu sunumda yer alan bilgi, oran, varsayım, örnek veya hesaplamalara dayanılmamalıdır. Sunum içeriği ile yürürlükteki mevzuat, resmi düzenleme, kurul kararı, tarife veya yetkili kurumların güncel uygulamaları arasında herhangi bir farklılık veya çelişki bulunması halinde, yürürlükteki resmi düzenlemeler ve yetkili mercilerin güncel karar ve uygulamaları esas alınmalıdır.",
    "Belirli bir düzenlemenin somut bir projeye uygulanması; tesisin bağlantı ve kullanım şekli, tüketim ve üretim tesisi arasındaki ilişki, ölçüm noktası, bağlantı ve/veya dağıtım bölgesi, tesisin devreye giriş tarihi, üretim lisansı veya lisanssız üretim statüsü, başvuru ve kabul süreçleri, ilgili abone grubu, üretim türü, tüketim geçmişi ve somut olayın diğer teknik ve hukuki özelliklerine göre farklılık gösterebilir. Bu nedenle sunumdaki genel açıklama ve örneklerden hareketle belirli bir proje hakkında doğrudan sonuç çıkarılmamalıdır.",
    "Herhangi bir yatırım, kredi, finansman, değerleme, gelir projeksiyonu veya benzeri karar alınmadan önce; ilgili tarihte yürürlükte bulunan kanun, yönetmelik, tebliğ, kurul kararı, tarife ve diğer düzenlemeler ile Enerji Piyasası Düzenleme Kurumu (EPDK), Enerji Piyasaları İşletme A.Ş. (EPİAŞ), Türkiye Elektrik İletim A.Ş. (TEİAŞ), ilgili dağıtım şirketleri, görevli tedarik şirketleri ve diğer yetkili kurum ve kuruluşların güncel resmi düzenleme, karar, duyuru ve uygulamalarının ayrıca incelenmesi ve somut olayın gerektirdiği hallerde bağımsız hukuk, mali, teknik ve/veya sektör uzmanlarından görüş alınması gerekir. Sunumda yer alan bilgiler tek başına herhangi bir işlem veya kararın dayanağını oluşturmamalıdır.",
    "Kalkınma Yatırım Bankası, sunumda yer alan bilgilerin doğruluğu, güncelliği, yeterliliği, belirli bir amaca uygunluğu veya eksiksizliği konusunda açık veya zımni herhangi bir beyan, garanti veya taahhütte bulunmamaktadır. Sunumun hazırlandığı tarih sonrasında meydana gelebilecek mevzuat, düzenleme, tarife, kurul kararı, piyasa koşulu, fiyat, uygulama veya yorum değişikliklerinin sunuma yansıtılması ya da sunumun güncel tutulması konusunda Kalkınma Yatırım Bankası’nın herhangi bir yükümlülüğü bulunmamaktadır. Kalkınma Yatırım Bankası, sunumda yer alan bilgileri önceden bildirimde bulunmaksızın doğrulama, düzeltme, güncelleme, tamamlama, değiştirme veya sunumdan çıkarma hakkını saklı tutar.",
    "Sunumda yer alan bilgi, açıklama ve örneklere dayanılarak gerçekleştirilen veya gerçekleştirilmeyen herhangi bir işlem, yatırım, kredi, finansman, değerleme veya sair karar ile bunların doğrudan veya dolaylı sonuçlarından; ortaya çıkabilecek zarar, kayıp, gelir veya kâr kaybı, fırsat maliyeti, üçüncü kişi talebi veya sair sonuçlardan, uygulanabilir mevzuatın izin verdiği ölçüde, Kalkınma Yatırım Bankası, yöneticileri, çalışanları ve sunumun hazırlanmasına katkıda bulunan kişiler sorumlu tutulamaz.",
    "Sunumda yer alan yorum ve değerlendirmeler, aksi açıkça belirtilmedikçe, Kalkınma Yatırım Bankası açısından bağlayıcı bir hukuki görüş, düzenleyici yorum, kredi tahsis kararı, değerleme sonucu veya herhangi bir kamu kurumu ya da düzenleyici otoritenin görüşünün aktarımı niteliğinde değildir.",
    "Bu sunum ve içeriğinde yer alan her türlü metin, bilgi, veri, tablo, grafik, hesaplama, görsel, yöntem, vaka çalışması ve diğer materyal Kalkınma Yatırım Bankası’nın önceden verilmiş yazılı izni olmaksızın kısmen veya tamamen üçüncü kişilerle paylaşılamaz; çoğaltılamaz, dağıtılamaz, yayımlanamaz, başka bir sunum veya çalışmaya aktarılamaz, kamuya açıklanamaz veya başka herhangi bir amaçla kullanılamaz.",
]

# Slayt sırası. Anahtarlar aşağıdaki BUILDERS sözlüğündeki fonksiyonlara karşılık gelir.
# KYB taslağındaki slayt no'ları parantez içinde: 1 kapak, 2 yasal, 3 içerik, 5–6, 8–32, 46 (7 hariç).
PLAN = [
    "kapak", "yasal", "icerik",                                   # 1, 2, 3
    "kurulu", "uretim", "tuketim", "talep",                       # 5, 6, 8, 9
    "hedef_zaman", "hedef_grafik", "devam", "iletim", "sebeke",   # 10–14
    "kullanim", "onlisans_grafik", "onlisans_harita",             # 15–17
    "onlisans_tablo", "isletmede",                                # 18–19
    "bol_fiyat", "yekdem_1", "yekdem_2", "tarife_1", "tarife_2",  # 20–24
    "ptf", "yekdem_formul", "yekdem_duyuru",                      # 25–27
    "bol_guncel", "vizyon_1", "vizyon_2", "tahsis", "hibrit",     # 28–32
    "yonetmelik",                                                 # 46
]


def _rgb(hex_renk: str) -> RGBColor:
    h = hex_renk.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _sayi(deger: float, ondalik: int = 1) -> str:
    return f"{deger:,.{ondalik}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- yardımcı çizim öğeleri

def _yazi(sl, x, y, w, h, satirlar, hizala=PP_ALIGN.LEFT, dikey=MSO_ANCHOR.TOP):
    """satirlar: (metin, boyut, kalın, renk, serif) demetlerinden oluşan liste."""
    kutu = sl.shapes.add_textbox(x, y, w, h)
    tf = kutu.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = dikey
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, (metin, boyut, kalin, renk, serif) in enumerate(satirlar):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = hizala
        p.space_after = Pt(max(boyut * 0.5, 4))
        r = p.add_run()
        r.text = metin
        f = r.font
        f.size = Pt(boyut)
        f.bold = kalin
        f.name = "Georgia" if serif else "Calibri"
        f.color.rgb = _rgb(renk)
    return kutu


def _dikdortgen(sl, x, y, w, h, dolgu, cizgi=None, sekil=MSO_SHAPE.RECTANGLE):
    s = sl.shapes.add_shape(sekil, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = _rgb(dolgu)
    if cizgi:
        s.line.color.rgb = _rgb(cizgi)
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def _maddeler(sl, x, y, w, h, maddeler, boyut=14):
    return _yazi(sl, x, y, w, h, [(f"•  {m}", boyut, False, METIN, False) for m in maddeler])


def _kart(sl, x, y, w, h, baslik, govde=(), renk=TURKUAZ, vurgu=None, govde_boyut=13):
    _dikdortgen(sl, x, y, w, h, KART, cizgi=CIZGI)
    _dikdortgen(sl, x, y, Inches(0.07), h, renk)
    satirlar = [(baslik, 15, True, renk, False)]
    if vurgu:
        satirlar.append((vurgu, 24, False, MUREKKEP, True))
    satirlar += [(g, govde_boyut, False, METIN, False) for g in govde]
    _yazi(sl, x + Inches(0.22), y + Inches(0.14), w - Inches(0.36), h - Inches(0.22), satirlar)


def _gosterge(sl, x, y, w, etiket, deger, not_="", renk=MUREKKEP):
    _yazi(sl, x, y, w, Inches(0.35), [(etiket, 12, False, SOLUK, False)])
    _yazi(sl, x, y + Inches(0.3), w, Inches(0.7), [(deger, 30, False, renk, True)])
    if not_:
        _yazi(sl, x, y + Inches(0.98), w, Inches(0.6), [(not_, 11, False, SOLUK, False)])


def _grafik(sl, x, y, w, h, tur, kategoriler, seriler, fmt="0", etiket_fmt=None,
            renkler=None, lejant=True, bosluk=60, nokta_renk=None):
    veri = CategoryChartData()
    veri.categories = [str(k) for k in kategoriler]
    for ad, degerler in seriler:
        veri.add_series(ad, [None if pd.isna(d) else float(d) for d in degerler], number_format=fmt)
    ch = sl.shapes.add_chart(tur, x, y, w, h, veri).chart
    ch.has_title = False
    ch.font.size = Pt(11)
    ch.font.name = "Calibri"
    ch.font.color.rgb = _rgb(METIN)
    ch.has_legend = lejant and len(seriler) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(11)
    plot = ch.plots[0]
    plot.gap_width = bosluk
    stakli = tur in STAKLI
    if stakli:
        plot.overlap = 100
    renkler = renkler or SERI_RENK
    for i, ser in enumerate(plot.series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = _rgb(renkler[i % len(renkler)])
        ser.format.line.fill.background()
    if nokta_renk:
        for idx, renk in nokta_renk.items():
            pt = plot.series[0].points[idx]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = _rgb(renk)
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = etiket_fmt or fmt
    dl.number_format_is_linked = False
    dl.font.size = Pt(10)
    dl.font.color.rgb = _rgb(BEYAZ if stakli else METIN)
    dl.position = XL_LABEL_POSITION.CENTER if stakli else XL_LABEL_POSITION.OUTSIDE_END
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = _rgb(CIZGI)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(10)
    va.tick_labels.font.color.rgb = _rgb(SOLUK)
    va.tick_labels.number_format = fmt
    va.tick_labels.number_format_is_linked = False
    ca = ch.category_axis
    ca.tick_labels.font.size = Pt(10)
    ca.format.line.color.rgb = _rgb(CIZGI)
    return ch


def _halka(sl, x, y, w, h, kategoriler, degerler, renkler):
    veri = CategoryChartData()
    veri.categories = [str(k) for k in kategoriler]
    veri.add_series("Ağırlık", [float(d) for d in degerler], number_format="0")
    ch = sl.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, w, h, veri).chart
    ch.has_title = False
    ch.font.size = Pt(11)
    ch.font.name = "Calibri"
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.RIGHT
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(12)
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = '0"%"'
    dl.number_format_is_linked = False
    dl.font.size = Pt(13)
    dl.font.bold = True
    dl.font.color.rgb = _rgb(BEYAZ)
    for i, pt in enumerate(plot.series[0].points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = _rgb(renkler[i % len(renkler)])
    return ch


def _tablo(sl, x, y, genislikler, basliklar, satirlar, satir_yuk=0.4, boyut=12, metin_sutun=1):
    tum = [basliklar] + satirlar
    gf = sl.shapes.add_table(len(tum), len(basliklar), x, y,
                             Inches(sum(genislikler)), Inches(satir_yuk * len(tum)))
    tbl = gf.table
    for i, g in enumerate(genislikler):
        tbl.columns[i].width = Inches(g)
    for r, satir in enumerate(tum):
        tbl.rows[r].height = Inches(satir_yuk)
        baslik_mi = r == 0
        for c, deger in enumerate(satir):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _rgb(MUREKKEP if baslik_mi else (KART if r % 2 else KAGIT_2))
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c < metin_sutun else PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = str(deger)
            run.font.size = Pt(boyut)
            run.font.bold = baslik_mi
            run.font.name = "Calibri"
            run.font.color.rgb = _rgb(BEYAZ if baslik_mi else METIN)
    return gf


def _resim(sl, x, y, w, fig, genislik_px=900, yukseklik_px=560):
    fig.update_layout(template=theme.SABLON, paper_bgcolor="white", plot_bgcolor="white",
                      title=None, margin=dict(l=0, r=0, t=0, b=0))
    png = fig.to_image(format="png", width=genislik_px, height=yukseklik_px, scale=1)
    sl.shapes.add_picture(io.BytesIO(png), x, y, width=w)


def _arka(sl, renk):
    bg = sl.background.fill
    bg.solid()
    bg.fore_color.rgb = _rgb(renk)


def _bos(prs, renk):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _arka(sl, renk)
    return sl


def _sayfa(prs, baslik, alt, kaynak, no):
    """Standart içerik slaytı: başlık, alt başlık, kaynak satırı ve sayfa no."""
    sl = _bos(prs, KAGIT)
    _dikdortgen(sl, Inches(0.6), Inches(0.42), Inches(0.55), Inches(0.06), TURKUAZ)
    boyut = 28 if len(baslik) <= 52 else 24
    _yazi(sl, Inches(0.6), Inches(0.55), Inches(12.1), Inches(0.75), [(baslik, boyut, False, MUREKKEP, True)])
    if alt:
        _yazi(sl, Inches(0.6), Inches(1.25), Inches(12.1), Inches(0.4), [(alt, 14, False, SOLUK, False)])
    _dikdortgen(sl, Inches(0.6), Inches(6.88), Inches(12.13), Inches(0.012), CIZGI)
    _yazi(sl, Inches(0.6), Inches(6.95), Inches(9.3), Inches(0.35),
          [((f"Kaynak: {kaynak}" if kaynak else "Enerji Atlası"), 9, False, SOLUK, False)])
    _yazi(sl, Inches(9.6), Inches(6.95), Inches(3.13), Inches(0.35),
          [(f"{no}   ·   © 2026 Kalkınma Yatırım Bankası", 9, False, SOLUK, False)], hizala=PP_ALIGN.RIGHT)
    return sl


def _bolum_slayti(prs, no, numara, baslik, alt):
    sl = _bos(prs, MUREKKEP)
    _yazi(sl, Inches(0.9), Inches(2.2), Inches(11.5), Inches(0.5),
          [(f"BÖLÜM {numara}", 14, True, ACIK_MAVI, False)])
    _dikdortgen(sl, Inches(0.9), Inches(2.8), Inches(0.9), Inches(0.06), OKRA)
    _yazi(sl, Inches(0.9), Inches(3.05), Inches(11.5), Inches(1.6), [(baslik, 40, False, BEYAZ, True)])
    _yazi(sl, Inches(0.9), Inches(4.7), Inches(11.5), Inches(0.6), [(alt, 18, False, ACIK_MAVI, False)])
    _yazi(sl, Inches(9.0), Inches(6.95), Inches(3.73), Inches(0.35),
          [(f"{no}   ·   © 2026 Kalkınma Yatırım Bankası", 9, False, "#B9C9D9", False)], hizala=PP_ALIGN.RIGHT)


# ---------------------------------------------------------------- veri hazırlığı

def _veri() -> dict:
    """Slaytların kullandığı tüm değerleri tek seferde hesaplar."""
    v: dict = {}

    ytbs = data.teias_ytbs()
    v["ytbs_toplam"] = float(ytbs["kurulu_guc_gw"].sum())
    v["ytbs_yen"] = float(ytbs.query("grup != 'Termik'")["kurulu_guc_gw"].sum())
    v["ytbs_tarih"] = pd.to_datetime(ytbs["tarih"].iloc[0]).strftime("%d.%m.%Y")
    v["yen_pay"] = v["ytbs_yen"] / v["ytbs_toplam"] * 100

    kurulu = data.kurulu_guc()
    kurulu["donem"] = kurulu["donem"].astype(str)
    v["kurulu"] = kurulu.set_index("donem")

    uretim = data.uretim()
    uretim["donem"] = uretim["donem"].astype(str)
    v["uretim"] = uretim.set_index("donem")

    tuk = data.tam_yillar(data.tuketim()).copy()
    tuk["donem"] = tuk["donem"].astype(str)
    v["tuk"] = tuk
    aylik = data.teias_aylik()
    o26 = aylik[(aylik["yil"] == 2026) & (aylik["ay_no"] <= 10)]
    o25 = aylik[(aylik["yil"] == 2025) & (aylik["ay_no"] <= 10)]
    v["tuk26"] = float(o26["gross_demand"].sum()) / 1000
    v["tuk25"] = float(o25["gross_demand"].sum()) / 1000
    v["tuketim_notlari"] = data.tuketim().dropna(subset=["olay"])

    ptf = data.ptf().copy()
    ptf["donem"] = ptf["donem"].astype(str)
    v["ptf"] = ptf.set_index("donem")["ptf_usd_mwh"]

    v["hedef"] = data.hedefler().set_index("kaynak")
    v["on"] = data.depolama_on_lisans()
    v["onlisans_ham"] = data.epdk_onlisans()
    v["iletim"] = data.iletim()
    v["tarife"] = data.tarife()
    v["yekdem_fiyat"] = data.yekdem_fiyat()
    v["yekdem_duyuru"] = data.yekdem_duyuru()
    v["yekdem_formul"] = data.yekdem_formul()
    v["yekdem_katki"] = data.yekdem_yerli_katki()
    v["isletmede"] = data.isletmedeki_depolama()
    v["devam"] = data.devam_eden_yatirim()
    return v


# ---------------------------------------------------------------- slayt üreticileri

def s_kapak(prs, no, v, sayfa):
    sl = _bos(prs, MUREKKEP)
    _yazi(sl, Inches(0.9), Inches(1.9), Inches(11.5), Inches(0.5),
          [("WB–DSPV (Distributed Solar Photovoltaic)  ·  Stage 2", 14, True, ACIK_MAVI, False)])
    _dikdortgen(sl, Inches(0.9), Inches(2.5), Inches(0.9), Inches(0.06), OKRA)
    _yazi(sl, Inches(0.9), Inches(2.75), Inches(11.5), Inches(1.9),
          [("Elektrik Piyasası ve Lisanssız Güneş Santralleri Mevzuat Eğitimi", 42, False, BEYAZ, True)])
    _yazi(sl, Inches(0.9), Inches(4.85), Inches(11.5), Inches(0.6),
          [("Enerji Atlası verileriyle güncellenmiş sürüm", 20, False, ACIK_MAVI, False)])
    _yazi(sl, Inches(0.9), Inches(6.45), Inches(8.0), Inches(0.5),
          [(f"Veri tarihi: {v['ytbs_tarih']} (TEİAŞ YTBS)  ·  Hazırlanma: {date.today():%d.%m.%Y}",
            12, False, ACIK_MAVI, False)])
    _yazi(sl, Inches(8.9), Inches(6.95), Inches(3.9), Inches(0.35),
          [("© 2026 Kalkınma Yatırım Bankası  ·  Tüm hakları saklıdır", 9, False, "#B9C9D9", False)],
          hizala=PP_ALIGN.RIGHT)


def s_yasal(prs, no, v, sayfa):
    sl = _sayfa(prs, "Yasal çekince ve önemli not", "", "Türkiye Kalkınma ve Yatırım Bankası A.Ş.", no)
    yarim = (len(YASAL) + 1) // 2
    _yazi(sl, Inches(0.6), Inches(1.4), Inches(5.9), Inches(5.4),
          [(p, 8.5, False, METIN, False) for p in YASAL[:yarim]])
    _yazi(sl, Inches(6.85), Inches(1.4), Inches(5.9), Inches(5.4),
          [(p, 8.5, False, METIN, False) for p in YASAL[yarim:]])


def s_icerik(prs, no, v, sayfa):
    sl = _sayfa(prs, "İçerik", "", "", no)
    satirlar = [
        ("01", "Türkiye elektrik piyasası",
         "Kurulu güç, üretim, tüketim, hedefler, devam eden yatırımlar, iletim ağı ve depolama (ön lisanslar, işletmedeki tesisler).",
         sayfa["kurulu"]),
        ("02", "Yenilenebilir enerji santralleri için fiyatlandırma mekanizmaları",
         "PTF, EPDK tarifeleri, YEKDEM formülü, yerli katkı ve EPİAŞ duyuruları.", sayfa["bol_fiyat"]),
        ("03", "Güncel gelişmeler ve beklentiler",
         "2026 vizyonu, lisanssız kapasite tahsisi ve hibrit kapasite düzenlemeleri.", sayfa["bol_guncel"]),
        ("04", "Lisanssız üretim ve mevzuat",
         "2 Nisan 2026 yönetmelik değişikliği: mahsuplaşma, depolama, güç sınırları ve yaptırımlar.",
         sayfa["yonetmelik"]),
    ]
    for i, (no_s, baslik, aciklama, sayfa_no) in enumerate(satirlar):
        y = Inches(1.75 + i * 1.22)
        _yazi(sl, Inches(0.6), y, Inches(1.0), Inches(0.6), [(no_s, 26, False, TURKUAZ, True)])
        _yazi(sl, Inches(1.7), y, Inches(9.6), Inches(0.5), [(baslik, 20, False, MUREKKEP, True)])
        _yazi(sl, Inches(1.7), y + Inches(0.5), Inches(9.6), Inches(0.5), [(aciklama, 13, False, SOLUK, False)])
        _yazi(sl, Inches(11.4), y, Inches(1.33), Inches(0.5),
              [(str(sayfa_no), 20, False, MUREKKEP, True)], hizala=PP_ALIGN.RIGHT)
        if i < len(satirlar) - 1:
            _dikdortgen(sl, Inches(0.6), y + Inches(1.05), Inches(12.13), Inches(0.01), CIZGI)


def s_kurulu(prs, no, v, sayfa):
    k = v["kurulu"]
    donemler = [str(y) for y in range(2016, 2026)] + ["2026 9A"]
    sl = _sayfa(prs, "Kurulu güç: yenilenebilir payı yükseliyor",
                "Kaynaklara göre kurulu güç payı, 2016–2026 9A (%)",
                "TEİAŞ kurulu güç (2026 9A); YTBS (" + v["ytbs_tarih"] + ")", no)
    seriler = [
        ("Termik", k.loc[donemler, "termik_pct"]),
        ("Güneş", k.loc[donemler, "gunes_pct"].fillna(0)),
        ("Rüzgar", k.loc[donemler, "ruzgar_pct"]),
        ("Diğer yenilenebilir", k.loc[donemler, "diger_ye_pct"]),
    ]
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_STACKED_100,
            donemler, seriler, fmt='0"%"', etiket_fmt='0"%";;;', renkler=[GRI, OKRA, CELIK, TURKUAZ], bosluk=45)
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Toplam kurulu güç (YTBS)",
              f"{_sayi(v['ytbs_toplam'])} GW", f"{v['ytbs_tarih']} itibarıyla")
    _gosterge(sl, Inches(8.6), Inches(3.35), Inches(4.1), "Yenilenebilir pay",
              f"%{_sayi(v['yen_pay'], 0)}", f"{_sayi(v['ytbs_yen'])} GW yenilenebilir kurulu güç")
    _maddeler(sl, Inches(8.6), Inches(4.85), Inches(4.1), Inches(1.9), [
        f"2016'da %{_sayi(100 - k.loc['2016', 'termik_pct'], 0)} olan yenilenebilir payı 2026 9A'da %{_sayi(100 - k.loc['2026 9A', 'termik_pct'], 0)}'e yükseldi.",
        f"Güneş payı 2025'te %{_sayi(k.loc['2025', 'gunes_pct'], 0)}, 2026 9A'da %{_sayi(k.loc['2026 9A', 'gunes_pct'], 0)}.",
    ], 13)


def s_uretim(prs, no, v, sayfa):
    u = v["uretim"]
    donemler = [str(y) for y in range(2016, 2026)] + ["2026 9A"]
    sl = _sayfa(prs, "Elektrik üretiminde yenilenebilir payı",
                "Kaynaklara göre brüt üretim payı, 2016–2026 9A (%)", "TEİAŞ üretim verileri", no)
    seriler = [
        ("Termik", u.loc[donemler, "termik_pct"]),
        ("Güneş", u.loc[donemler, "gunes_pct"].fillna(0)),
        ("Rüzgar", u.loc[donemler, "ruzgar_pct"]),
        ("Diğer yenilenebilir", u.loc[donemler, "diger_ye_pct"]),
    ]
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_STACKED_100,
            donemler, seriler, fmt='0"%"', etiket_fmt='0"%";;;', renkler=[GRI, OKRA, CELIK, TURKUAZ], bosluk=45)
    yen_2026 = 100 - u.loc["2026 9A", "termik_pct"]
    yen_2016 = 100 - u.loc["2016", "termik_pct"]
    twh_2026 = float(u.loc["2026 9A", "toplam_twh"])
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Yenilenebilir pay, 2026 9A",
              f"%{_sayi(yen_2026, 0)}", f"2016'da %{_sayi(yen_2016, 0)}")
    _gosterge(sl, Inches(8.6), Inches(3.35), Inches(4.1), "2026 Ocak–Eylül üretim",
              f"{_sayi(twh_2026, 0)} TWh", f"Yenilenebilir yaklaşık {_sayi(twh_2026 * yen_2026 / 100, 0)} TWh")
    _maddeler(sl, Inches(8.6), Inches(4.85), Inches(4.1), Inches(1.9), [
        "Termik payı 2026 9A'da %40'a geriledi; hidro, rüzgar ve güneş üretimi arttı.",
        "Pay ve üretim miktarı her dönemde TEİAŞ aylık verilerinden hesaplanır.",
    ], 13)


def s_tuketim(prs, no, v, sayfa):
    t = v["tuk"]
    sl = _sayfa(prs, "Brüt elektrik tüketimi", "Türkiye brüt elektrik tüketimi, 2016–2025 (TWh)",
                "TEİAŞ; Enerji Atlası tüketim verisi", no)
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_CLUSTERED,
            t["donem"].tolist(), [("Brüt tüketim (TWh)", t["tuketim_twh"])], fmt="0", renkler=[MUREKKEP], bosluk=55)
    son = float(t["tuketim_twh"].iloc[-1])
    degisim = (v["tuk26"] / v["tuk25"] - 1) * 100
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Brüt tüketim, 2025",
              f"{_sayi(son, 0)} TWh", "2016'dan bu yana artış sürüyor")
    _gosterge(sl, Inches(8.6), Inches(3.35), Inches(4.1), "2026 Ocak–Ekim",
              f"{_sayi(v['tuk26'], 0)} TWh",
              f"2025 aynı dönem {_sayi(v['tuk25'], 0)} TWh ({'+' if degisim >= 0 else ''}{_sayi(degisim, 1)}%)")
    notlar = [f"{r['donem']}: {r['olay']}" for _, r in v["tuketim_notlari"].iterrows()]
    notlar.append("Ekonomik büyüme ve elektrikli araçların yaygınlaşması tüketimin artmasını sürdürecek.")
    _maddeler(sl, Inches(8.6), Inches(4.85), Inches(4.1), Inches(1.9), notlar, 12)


def s_talep(prs, no, v, sayfa):
    sl = _sayfa(prs, "Elektrik tüketimini etkileyen faktörler",
                "KYB eğitim sunumundaki faktörlerin gruplandırılmış hali", "KYB eğitim sunumu", no)
    gruplar = [
        ("Talebi artıran", TURKUAZ, ["Ekonomik büyüme ve sanayi gelişimi", "Elektrikli araçlar",
                                     "Elektrikli ısıtma sistemleri", "Elektrifikasyon süreci",
                                     "Nüfus artışı ve refah seviyesi"]),
        ("Talebi sınırlayan", PAS, ["Ekonomik durgunluk", "Verimlilik yatırımları",
                                    "Verimli cihazlar", "Şebeke kayıplarının azaltılması"]),
        ("Yük profili ve politika", OKRA, ["Tüketim saatleri ve yük profili", "Teknoloji tüketimi",
                                           "Yeni teknolojiler", "Teşvikler ve fatura destekleri"]),
    ]
    genislik = Inches(3.9)
    for i, (baslik, renk, maddeler) in enumerate(gruplar):
        x = Inches(0.6) + i * (genislik + Inches(0.215))
        _kart(sl, x, Inches(1.9), genislik, Inches(3.9), baslik, [f"•  {m}" for m in maddeler], renk=renk,
              govde_boyut=14)


def s_hedef_zaman(prs, no, v, sayfa):
    h = v["hedef"]
    sl = _sayfa(prs, "Hedefler: planlardan gerçekleşmeye", "Kurulu güç hedeflerinin zaman çizgisi",
                "Enerji ve Tabii Kaynaklar Bakanlığı; Enerji Atlası Hedefler ve vizyon sayfası", no)
    _dikdortgen(sl, Inches(1.0), Inches(3.46), Inches(11.3), Inches(0.03), CIZGI)
    olaylar = [
        ("2023 Ocak", "Ulusal Enerji Planı", "2035 hedeflerinin ilk kez yayımlandığı plan (2020–2035)."),
        ("2024 Ekim", "2035 Yenilenebilir Enerji Yol Haritası", "120 GW rüzgar ve güneş hedefi, COP29'da ilan edildi."),
        ("2024 Kasım", "2024–2028 Stratejik Planı",
         f"2028 hedefi: {_sayi(h.loc['Toplam', 'hedef_2028_stratejik_plan_gw'], 0)} GW toplam kurulu güç, 10 GW batarya."),
        ("2025 yıl sonu", "Gerçekleşen",
         f"Kurulu güç {_sayi(h.loc['Toplam', 'gerceklesen_2025_gw'])} GW; güneş {_sayi(h.loc['Güneş', 'gerceklesen_2025_gw'])} GW, rüzgar {_sayi(h.loc['Rüzgar', 'gerceklesen_2025_gw'])} GW."),
    ]
    for i, (tarih, baslik, aciklama) in enumerate(olaylar):
        cx = 1.5 + i * 3.4
        _daire = _dikdortgen(sl, Inches(cx - 0.15), Inches(3.33), Inches(0.3), Inches(0.3), TURKUAZ,
                             sekil=MSO_SHAPE.OVAL)
        _yazi(sl, Inches(cx - 1.5), Inches(2.5), Inches(3.0), Inches(0.5),
              [(tarih, 16, True, TURKUAZ, False)], hizala=PP_ALIGN.CENTER)
        _yazi(sl, Inches(cx - 1.5), Inches(3.95), Inches(3.0), Inches(0.8),
              [(baslik, 16, False, MUREKKEP, True)], hizala=PP_ALIGN.CENTER)
        _yazi(sl, Inches(cx - 1.5), Inches(4.85), Inches(3.0), Inches(1.4),
              [(aciklama, 12, False, METIN, False)], hizala=PP_ALIGN.CENTER)


def s_hedef_grafik(prs, no, v, sayfa):
    h = v["hedef"]
    sl = _sayfa(prs, "Kurulu güç hedefleri: 2028 ve 2035",
                "Toplam yenilenebilir ve termik kurulu güç (GW)",
                "Enerji ve Tabii Kaynaklar Bakanlığı; TEİAŞ (2025 gerçekleşen)", no)
    kategoriler = ["2025 gerçekleşen", "2028 Stratejik Plan", "2035 Ulusal Enerji Planı", "2035 Yenilenebilir Yol Haritası"]
    seriler = [
        ("Toplam yenilenebilir", [h.loc["Toplam Yenilenebilir", c] for c in
                                 ["gerceklesen_2025_gw", "hedef_2028_stratejik_plan_gw",
                                  "hedef_2035_ulusal_enerji_plani_gw", "hedef_2035_yenilenebilir_yol_haritasi_gw"]]),
        ("Toplam termik", [h.loc["Toplam Termik", c] for c in
                           ["gerceklesen_2025_gw", "hedef_2028_stratejik_plan_gw",
                            "hedef_2035_ulusal_enerji_plani_gw", "hedef_2035_yenilenebilir_yol_haritasi_gw"]]),
    ]
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_CLUSTERED,
            kategoriler, seriler, fmt="0", renkler=[TURKUAZ, GRI], bosluk=70)
    yol = float(h.loc["Güneş", "hedef_2035_yenilenebilir_yol_haritasi_gw"]) + float(h.loc["Rüzgar", "hedef_2035_yenilenebilir_yol_haritasi_gw"])
    tuketim_2035 = h.loc["Elektrik Tüketimi (TWh)", "hedef_2035_ulusal_enerji_plani_gw"]
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "2035 yol haritası: güneş + rüzgar",
              f"{_sayi(yol, 0)} GW", "Toplam yenilenebilir 160 GW")
    _maddeler(sl, Inches(8.6), Inches(3.5), Inches(4.1), Inches(3.2), [
        f"2028 batarya hedefi: {_sayi(h.loc['Batarya', 'hedef_2028_stratejik_plan_gw'], 0)} GW.",
        f"2025'te {_sayi(h.loc['Elektrik Tüketimi (TWh)', 'gerceklesen_2025_gw'])} TWh olan tüketimin Ulusal Enerji Planı'ndaki 2035 hedefi {_sayi(tuketim_2035)} TWh.",
        "Termik kapasitenin 2035'e kadar 67–70 GW düzeyinde kalması öngörülüyor.",
    ], 13)


def s_devam(prs, no, v, sayfa):
    d = v["devam"]
    proje = d[d["kalem"] != "Toplam"]
    toplam = float(d.loc[d["kalem"] == "Toplam", "gw"].iloc[0])
    sl = _sayfa(prs, "Devam eden yatırımlar", "Yatırım aşamasındaki kurulu güç (GW)",
                "Enerji ve Tabii Kaynaklar Bakanlığı; EPDK ön lisans verisi", no)
    _grafik(sl, Inches(0.6), Inches(1.9), Inches(7.6), Inches(3.8), XL_CHART_TYPE.BAR_CLUSTERED,
            proje["kalem"].tolist()[::-1], [("GW", proje["gw"].tolist()[::-1])], fmt="0.0",
            renkler=[TURKUAZ], bosluk=80)
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Toplam devam eden kapasite", f"{_sayi(toplam)} GW")
    _maddeler(sl, Inches(0.6), Inches(5.9), Inches(12.1), Inches(0.9), [
        "Her yıl 2 GW'lık yeni YEKA yarışması düzenlenmektedir.",
    ], 14)


def s_iletim(prs, no, v, sayfa):
    il = v["iletim"]

    def deger(g, yil):
        satir = il[(il["gosterge"] == g) & (il["yil"] == yil)]
        return None if satir.empty else float(satir["deger"].iloc[0])

    satirlar = []
    for ad, birim in [("AC hattı", "km"), ("Trafo merkezi", "adet"), ("HVDC hattı", "km"),
                      ("HVDC çevirici merkezi", "adet"), ("HVDC koridor kapasitesi", "GW"),
                      ("Yatırım ihtiyacı (2035'e kadar)", "milyar USD")]:
        b = deger(ad, 2025)
        h35 = deger(ad, 2035)
        if ad.startswith("Yatırım"):
            h35 = deger("Yatırım ihtiyacı (2035'e kadar)", 2035)
        satirlar.append([ad, "–" if b is None else _sayi(b, 0), "–" if h35 is None else _sayi(h35, 0), birim])
    sl = _sayfa(prs, "Elektrik iletim ağı ve 2035 hedefleri", "AC genişlemesi ve HVDC koridorları", "TEİAŞ; Enerji ve Tabii Kaynaklar Bakanlığı", no)
    _tablo(sl, Inches(0.6), Inches(1.9), [3.8, 1.6, 1.8, 1.4], ["Gösterge", "2025", "2035 hedefi", "Birim"],
           satirlar, satir_yuk=0.52, boyut=13)
    _maddeler(sl, Inches(9.6), Inches(1.9), Inches(3.1), Inches(4.8), [
        "HVDC, uzun mesafede düşük kayıpla yüksek kapasiteli iletim sağlar.",
        "AC: üretimden dağıtıma kullanılan mevcut alternatif akım sistemi.",
        "HVDC yatırımıyla komşu ülke bağlantıları ve şebeke dijitalizasyonu öne çıkıyor.",
    ], 13)


def s_sebeke(prs, no, v, sayfa):
    k = v["kurulu"]
    sl = _sayfa(prs, "Elektrik şebekesi ve depolama ilişkisi", "Termik payı düştükçe depolama ihtiyacı artıyor",
                "TEİAŞ kurulu güç; KYB eğitim sunumu", no)
    _kart(sl, Inches(0.6), Inches(1.9), Inches(7.6), Inches(3.9), "Neden depolama?", [
        "Baz yük sağlayan termik santrallerin kurulu güç içindeki payı düştükçe talebi rüzgar ve güneş santralleri karşılayacaktır.",
        "Rüzgar ve güneş santrallerinin değişken üretimi nedeniyle talebi dengeleyecek ek araç ve teknolojilere ihtiyaç duyulur.",
        "Depolama, üretim fazlasını talep anında kullanarak şebeke dengesini sağlar.",
    ], renk=TURKUAZ, govde_boyut=15)
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Termik payı, 2016",
              f"%{_sayi(k.loc['2016', 'termik_pct'], 0)}", "Kurulu güç içinde")
    _gosterge(sl, Inches(8.6), Inches(3.6), Inches(4.1), "Termik payı, 2026 9A",
              f"%{_sayi(k.loc['2026 9A', 'termik_pct'], 0)}", "Kurulu güç içinde")


def s_kullanim(prs, no, v, sayfa):
    sl = _sayfa(prs, "Elektrik depolama: kullanım türleri", "Depolama tesislerinin kurulabildiği modeller",
                "EPDK elektrik depolama mevzuatı; KYB eğitim sunumu", no)
    kartlar = [
        ("Müstakil tesis", "Tedarikçi veya toplayıcı lisansı ve en az 2 MW kurulu güç gerekir."),
        ("Üretim tesisine bütünleşik", "Üretim lisansı sahibi tüzel kişiler, lisansta yazan kurulu güce kadar depolama kurabilir."),
        ("Tüketim tesisine bütünleşik", "Şebeke operatörünün onayı, sözleşme gücünün aşılmaması ve aynı ölçüm noktası şartıyla."),
        ("Şebeke işletmecisi tarafından", "Dağıtım şirketleri, fayda-maliyet analiziyle yeni şebeke yatırımından ekonomik olduğunu kanıtlarsa EPDK onayıyla kurabilir."),
        ("Lisanssız üretim tesisleri tarafından", "Üretim-tüketim dengesi için kullanılır; ödeme mekanizmaları sınırlı, optimizasyon odaklıdır."),
    ]
    genislik = Inches(3.9)
    yukseklik = Inches(2.05)
    for i, (baslik, metin) in enumerate(kartlar):
        satir, sutun = (0, i) if i < 3 else (1, i - 3)
        x = Inches(0.6) + sutun * (genislik + Inches(0.215)) + (Inches(1.9) if satir == 1 else 0)
        y = Inches(1.85) + satir * (yukseklik + Inches(0.2))
        _kart(sl, x, y, genislik, yukseklik, baslik, [metin], renk=TURKUAZ if i % 2 == 0 else OKRA, govde_boyut=13)
    _yazi(sl, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.45), [(
        "EPDK, Kasım 2022'de ön lisans başvurularını kabul etmeye başladı; Nisan 2023'te ilk lisansı verdi.",
        13, False, SOLUK, False)])


def s_onlisans_grafik(prs, no, v, sayfa):
    on = v["on"]
    piv = on.pivot_table(index="bitis_yili", columns="teknoloji", values="kapasite_mwe", aggfunc="sum").fillna(0)
    toplam_gw = on["kapasite_mwe"].sum() / 1000
    sayi = int(on["proje_adedi"].sum())
    sl = _sayfa(prs, "Depolamalı ön lisanslar", "Bitiş yılına göre depolamalı GES ve RES kapasitesi (MWe)",
                "EPDK ön lisans listesi", no)
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_STACKED,
            [str(y) for y in piv.index], [("GES", piv["GES"]), ("RES", piv["RES"])],
            fmt="#,##0", renkler=[OKRA, TURKUAZ], bosluk=55)
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Depolamalı santral kapasitesi",
              f"{_sayi(toplam_gw)} GW", f"{sayi} ön lisans (GES + RES)")
    _maddeler(sl, Inches(8.6), Inches(3.5), Inches(4.1), Inches(3.2), [
        "Depolamalı RES'lerin toplam ön lisans kapasitesi GES'lerin üzerindedir.",
        "En büyük kapasite 2027 bitiş yılında toplanıyor.",
    ], 13)


def s_onlisans_harita(prs, no, v, sayfa):
    ham = v["onlisans_ham"].copy()
    ham["ad_key"] = ham["il"].map(data.il_anahtari)
    sl = _sayfa(prs, "Ön lisanslar: il bazında dağılım", "GES ve RES ön lisanslarının kurulu güç dağılımı (MWe)",
                "EPDK ön lisans listesi; Türkiye il sınırları", no)
    for i, (tur, ad, renk) in enumerate([("Güneş", "GES ön lisansları", "#D9A21B"),
                                         ("Rüzgar", "RES ön lisansları", "#13A89E")]):
        x = Inches(0.6) + i * Inches(6.2)
        _yazi(sl, x, Inches(1.8), Inches(5.9), Inches(0.4), [(ad, 15, True, MUREKKEP, False)])
        df = ham[ham["tesis_turu"] == tur].groupby("ad_key", as_index=False)["kurulu_mwe"].sum()
        fig = charts.tr_harita(df, "kurulu_mwe", "", renk, "MWe")
        _resim(sl, x, Inches(2.25), Inches(5.9), fig, 900, 560)
    _yazi(sl, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.45), [(
        "GES ağırlıklı olarak iç kesimlerde, RES ise kuzeybatıda yoğunlaşıyor.", 13, False, METIN, False)])


def s_onlisans_tablo(prs, no, v, sayfa):
    on = v["on"]
    sl = _sayfa(prs, "Ön lisans takvimi ve süre riski", "Bitiş yılına göre proje adedi ve kapasite (MWe)",
                "EPDK ön lisans listesi", no)
    yil_2026_oran = {}
    for i, tek in enumerate(["GES", "RES"]):
        s = on[on["teknoloji"] == tek].sort_values("bitis_yili")
        satirlar = [[str(int(r.bitis_yili)), _sayi(r.proje_adedi, 0), _sayi(r.kapasite_mwe, 0)] for r in s.itertuples()]
        satirlar.append(["TOPLAM", _sayi(s["proje_adedi"].sum(), 0), _sayi(s["kapasite_mwe"].sum(), 0)])
        toplam = s["kapasite_mwe"].sum()
        yil_2026_oran[tek] = s.loc[s["bitis_yili"] == 2026, "kapasite_mwe"].sum() / toplam * 100
        x = Inches(0.6) + i * Inches(6.2)
        _yazi(sl, x, Inches(1.8), Inches(5.9), Inches(0.4), [(f"Depolamalı {'GES' if tek == 'GES' else 'RES'}", 15, True, MUREKKEP, False)])
        _tablo(sl, x, Inches(2.25), [1.9, 1.8, 2.2], ["Bitiş yılı", "Proje adedi", "Kapasite (MWe)"],
               satirlar, satir_yuk=0.42, boyut=13)
    _maddeler(sl, Inches(0.6), Inches(5.35), Inches(12.1), Inches(1.4), [
        f"2026'da süresi dolacak kapasite: GES %{_sayi(yil_2026_oran['GES'], 0)}, RES %{_sayi(yil_2026_oran['RES'], 0)}.",
        "EPDK, süre uzatım talebini reddederek ilerlemeyen ön lisansları sonlandırabilir; mücbir sebep veya izin gecikmelerinde uzatma yapılabilir.",
    ], 13)


def s_isletmede(prs, no, v, sayfa):
    isl = v["isletmede"].copy()
    top = isl.sort_values("kapasite_mwh", ascending=False).head(10)
    kategori = [str(a)[:34] for a in top["lisans_sahibi"]][::-1]
    sl = _sayfa(prs, "İşletmedeki depolamalı lisanslı projeler", "Depolama kapasitesi, en büyük 10 tesis (MWh)",
                "EPDK lisans listesi; işletmedeki depolama verisi", no)
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.BAR_CLUSTERED,
            kategori, [("Kapasite (MWh)", top["kapasite_mwh"].tolist()[::-1])], fmt="0.0",
            renkler=[MUREKKEP], bosluk=50)
    turler = isl["tesis_turu"].value_counts()
    kontrol = isl["kontrol_grubu"].dropna().value_counts()
    maddeler = [
        f"Tesis dağılımı: {int(turler.get('Güneş', 0))} güneş, {int(turler.get('Rüzgar', 0))} rüzgar.",
    ]
    if len(kontrol):
        maddeler.append(f"En çok tesis kontrol eden grup: {kontrol.index[0]} ({int(kontrol.iloc[0])} tesis).")
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "Toplam depolama kapasitesi",
              f"{_sayi(isl['kapasite_mwh'].sum())} MWh", f"{len(isl)} lisanslı tesis")
    _gosterge(sl, Inches(8.6), Inches(3.35), Inches(4.1), "Toplam kurulu güç", f"{_sayi(isl['guc_mwe'].sum())} MWe")
    _maddeler(sl, Inches(8.6), Inches(4.85), Inches(4.1), Inches(1.9), maddeler, 13)


def s_yekdem_1(prs, no, v, sayfa):
    sl = _sayfa(prs, "YEKDEM ve yenilenebilir santral mekanizmaları",
                "Lisanslı, YEKA, hibrit, piyasa satışı ve depolama entegreli modeller", "EPİAŞ; EPDK; KYB eğitim sunumu", no)
    kartlar = [
        ("Lisanslı santraller (YEKDEM)", "2021–2030 arasında işletmeye alınanlar, kaynak tipine göre 10–15 yıl TL/MWh bazında destek alır. Enflasyon ve kur güncellemesi %40 ve %60 oranında uygulanır."),
        ("YEKA ihaleleri", "İhale yoluyla tahsis edilir; elektrik alım garantisi sunulabilir."),
        ("Hibrit santraller", "Hibrit santralin kapasitesi, mevcut santralin toplam kurulu gücü ile sınırlıdır."),
        ("Piyasaya satış", "Spot piyasa veya PPA ile satış yapılabilir; YEKDEM süresi içinde ya da bittikten sonra piyasa modeli seçilebilir."),
        ("Depolama entegreli model", "İhaleye girmeden başvuru sırasına göre, EPDK onayıyla lisans alınır; 10 yıl sabit fiyat ve yerli aksam desteği."),
    ]
    for i, (baslik, metin) in enumerate(kartlar):
        _kart(sl, Inches(0.6), Inches(1.85) + i * Inches(1.0), Inches(6.0), Inches(0.95), baslik, [metin],
              renk=TURKUAZ if i % 2 == 0 else OKRA, govde_boyut=11)
    fiyat = v["yekdem_fiyat"].pivot(index="gosterge", columns="teknoloji", values="usd_mwh")
    sira = ["Taban", "2025 Ort.", "Tavan", "PTF (2025 Ort.)"]
    fiyat = fiyat.reindex(sira)
    _yazi(sl, Inches(6.95), Inches(1.85), Inches(5.8), Inches(0.4),
          [("YEKDEM fiyatları (USD/MWh)", 15, True, MUREKKEP, False)])
    _grafik(sl, Inches(6.95), Inches(2.3), Inches(5.8), Inches(4.4), XL_CHART_TYPE.COLUMN_CLUSTERED,
            sira, [("Güneş", fiyat["Güneş"]), ("Elektrik depolama", fiyat["Elektrik Depolama"])],
            fmt="0.0", renkler=[OKRA, TURKUAZ], bosluk=60)


def s_yekdem_2(prs, no, v, sayfa):
    sl = _sayfa(prs, "Lisanssız üretimde mahsuplaşma ve YEKDEM sonrası",
                "Saat bazlı mahsuplaşma ve on yıl sonrasındaki satış kuralları",
                "EPDK; Elektrik Piyasasında Lisanssız Elektrik Üretim Yönetmeliği", no)
    kartlar = [
        ("Saatlik mahsuplaşma", "Üretim ve tüketim dengesi saat bazında hesaplanır. Saatlik mahsuplaşmaya geçiş 1 Mayıs 2026'dır."),
        ("Öz tüketim odaklı model", "Lisanssız üretim modeli öz tüketime odaklanır; fazla üretimin ekonomik değeri sınırlandırılmıştır."),
        ("Eşik üstü üretim", "Belirli eşiklerin üzerindeki üretim YEKDEM kapsamında bedelsiz katkı olarak değerlendirilir."),
        ("On yıl sonra", "Aynı ölçüm noktasındaki tesisler ürettiği enerjinin tamamını satabilir; farklı noktadakiler EPDK kararına göre satış yapar."),
    ]
    for i, (baslik, metin) in enumerate(kartlar):
        satir, sutun = divmod(i, 2)
        _kart(sl, Inches(0.6) + sutun * Inches(6.2), Inches(1.9) + satir * Inches(2.3), Inches(5.9), Inches(2.1),
              baslik, [metin], renk=TURKUAZ if i % 2 == 0 else OKRA, govde_boyut=14)
    _yazi(sl, Inches(0.6), Inches(6.55), Inches(12.1), Inches(0.35), [(
        "Lisanssız tesislerde saatlik mahsuplaşma ve bedelli üretim sınırları 2 Nisan 2026 değişikliğiyle düzenlenmiştir (bkz. son slayt).",
        11, False, SOLUK, False)])


def s_tarife_1(prs, no, v, sayfa):
    t = v["tarife"]
    og = t[t["baglanti"] == "OG Çift Terim"].dropna(subset=["gunduz"])
    sl = _sayfa(prs, "EPDK elektrik tarifeleri: zamana göre", "OG çift terim, gruplara göre tarife (kr/kWh)",
                "EPDK elektrik faturalarına esas tarife tabloları", no)
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_CLUSTERED,
            og["grup"].tolist(),
            [("Gündüz", og["gunduz"]), ("Puant", og["puant"]), ("Gece", og["gece"])],
            fmt="0", renkler=[TURKUAZ, PAS, MUREKKEP], bosluk=60)
    _maddeler(sl, Inches(8.6), Inches(1.95), Inches(4.1), Inches(4.8), [
        "Birim: kr/kWh. Tarifeler EPDK tarafından belirli periyotlarda güncellenir.",
        "Puant saat tarifesi her grupta en yüksek, gece tarifesi en düşük olandır.",
        "Lisanssız üretimde ihtiyaç fazlası gelirinin hesabında, tesisin bağlantı tipi ve abone grubundaki tek zamanlı tarife kullanılır.",
    ], 13)


def s_tarife_2(prs, no, v, sayfa):
    t = v["tarife"]
    secim = t[t["grup"].str.contains("Sanayi|Mesken", regex=True)].head(8)

    def f(x):
        return "–" if pd.isna(x) else _sayi(x, 2)

    satirlar = [[r.baglanti, r.grup, f(r.tek_zamanli), f(r.gunduz), f(r.puant), f(r.gece)] for r in secim.itertuples()]
    sl = _sayfa(prs, "EPDK tarifeleri ve ihtiyaç fazlası geliri", "Seçilmiş grupların tarifeleri (kr/kWh)",
                "EPDK elektrik faturalarına esas tarife tabloları", no)
    _tablo(sl, Inches(0.6), Inches(1.85), [2.2, 3.0, 1.9, 1.7, 1.7, 1.6],
           ["Bağlantı", "Grup", "Tek zamanlı", "Gündüz", "Puant", "Gece"], satirlar, satir_yuk=0.36, boyut=12,
           metin_sutun=2)
    _maddeler(sl, Inches(0.6), Inches(5.35), Inches(12.1), Inches(1.4), [
        "AG: alçak gerilim, OG: orta gerilim.",
        "Tarifeler, lisanssız ihtiyaç fazlası enerjisinin gelir hesabında kullanılır ve EPDK tarafından değerlendirilerek değiştirilir.",
    ], 13)


def s_ptf(prs, no, v, sayfa):
    p = v["ptf"]
    donemler = [str(y) for y in range(2016, 2026)] + ["2026 9A"]
    cagr = ((p["2025"] / p["2016"]) ** (1 / 9) - 1) * 100
    sl = _sayfa(prs, "Piyasa takas fiyatı (PTF)", "Yıllık ortalama PTF, USD/MWh (2016–2026 9A)",
                "EPİAŞ; Enerji Atlası PTF verisi", no)
    zirve_idx = donemler.index("2022")
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(7.6), Inches(4.9), XL_CHART_TYPE.COLUMN_CLUSTERED,
            donemler, [("PTF (USD/MWh)", p.loc[donemler])], fmt="0", renkler=[MUREKKEP], bosluk=55,
            nokta_renk={zirve_idx: PAS, len(donemler) - 1: TURKUAZ})
    _gosterge(sl, Inches(8.6), Inches(1.9), Inches(4.1), "2016–2025 bileşik yıllık artış (USD)",
              f"%{_sayi(cagr, 1)}", "Dolar bazında ortalama artış")
    _gosterge(sl, Inches(8.6), Inches(3.35), Inches(4.1), "2022 zirvesi", f"{_sayi(p['2022'], 0)} USD/MWh")
    fark = (p["2026 9A"] / p["2025 9A"] - 1) * 100
    _maddeler(sl, Inches(8.6), Inches(4.85), Inches(4.1), Inches(1.9), [
        f"2026 9A ({_sayi(p['2026 9A'], 0)} USD) 2025 9A'ya göre %{_sayi(abs(fark), 0)} düşük.",
        "Aşırı yağışlarla hidroelektrik üretimi yükseldiğinde fiyatlar baskılanır.",
    ], 13)


def s_yekdem_formul(prs, no, v, sayfa):
    f = v["yekdem_formul"]
    k = v["yekdem_katki"]
    sl = _sayfa(prs, "YEKDEM formülü ve yerli katkı", "Fiyat güncelleme ağırlıkları ve yerli katkı tutarları",
                "EPİAŞ; EPDK", no)
    _yazi(sl, Inches(0.6), Inches(1.8), Inches(5.9), Inches(0.4), [("Güncelleme ağırlıkları (%)", 15, True, MUREKKEP, False)])
    _halka(sl, Inches(0.6), Inches(2.25), Inches(5.9), Inches(4.4), f["bilesen"].tolist(), f["agirlik_pct"].tolist(),
           [MUREKKEP, TURKUAZ, OKRA, PAS])
    _yazi(sl, Inches(6.95), Inches(1.8), Inches(5.8), Inches(0.4), [("Yerli katkı fiyatı (USD/MWh)", 15, True, MUREKKEP, False)])
    _grafik(sl, Inches(6.95), Inches(2.25), Inches(5.8), Inches(3.4), XL_CHART_TYPE.COLUMN_CLUSTERED,
            [f"{r.teknoloji} ({int(r.sure_yil)} yıl)" for r in k.itertuples()],
            [("Yerli katkı", k["yerli_katki_usd_mwh"])], fmt="0.00", renkler=[TURKUAZ], bosluk=90, lejant=False)
    _yazi(sl, Inches(6.95), Inches(5.75), Inches(5.8), Inches(0.9), [(
        "Tutarlar %100 yerli aksam kullanımı varsayımıyla hesaplanan azami değerlerdir.", 11, False, SOLUK, False)])


def s_yekdem_duyuru(prs, no, v, sayfa):
    d = v["yekdem_duyuru"]
    son = d["donem"].max()
    gun = d[d["donem"] == son].sort_values("fiyat_kr_kwh", ascending=False)
    sl = _sayfa(prs, "EPİAŞ YEKDEM duyuruları", f"Kaynak tipine göre fiyat, {son} dönemi (kr/kWh)",
                "EPİAŞ YEKDEM duyuruları (2021–2030 dönemi tesisleri)", no)
    _grafik(sl, Inches(0.6), Inches(1.85), Inches(8.0), Inches(4.95), XL_CHART_TYPE.BAR_CLUSTERED,
            [str(a)[:60] for a in gun["kaynak"]][::-1], [("Fiyat (kr/kWh)", gun["fiyat_kr_kwh"].tolist()[::-1])],
            fmt="0", renkler=[OKRA], bosluk=45)
    en_yuksek = gun.iloc[0]
    _maddeler(sl, Inches(8.9), Inches(1.95), Inches(3.8), Inches(4.8), [
        f"Duyurular {d['donem'].min()} – {son} dönemlerini kapsar.",
        f"En yüksek fiyat: {en_yuksek['kaynak'].split(' Üretim')[0]} ({_sayi(en_yuksek['fiyat_kr_kwh'], 2)} kr/kWh).",
        f"Yerli aksam desteği, aynı kaynakta {_sayi(en_yuksek['yerli_aksam_kr_kwh'], 2)} kr/kWh.",
    ], 13)


def s_vizyon_1(prs, no, v, sayfa):
    sl = _sayfa(prs, "Enerjide 2026 vizyonu (1/2)", "Lisanssız, depolama ve güneş yatırımlarına ilişkin duyurular",
                "ETKB; T.C. İletişim Başkanlığı; KYB eğitim sunumu", no)
    kartlar = [
        ("Öz tüketim GES", "Yaklaşık 3.500 MW kapasite öz tüketim projelerine tahsis edildi; sanayi ve stratejik sektörler öncelikli."),
        ("DEKA modeli", "Depolama Kaynak Alanı (DEKA) modelinin, YEKA benzeri bir yapıyla 2026'da planlandığı duyuruldu."),
        ("ACWA Power: 5 GW güneş", "Sivas ve Karaman Taşeli'de toplam 5 GW için satın alma anlaşması imzalandı; ilk etap 2 GW."),
        ("Depolama: 2.000 MW", "2026 içinde 2.000 MW enerji depolama yatırımının hayata geçirilmesi planlanıyor."),
        ("Yüzer GES: 3.000 MW", "Özel sektör veya EÜAŞ eliyle yaklaşık 3.000 MW yüzer GES'in en kısa sürede hayata geçirilmesi hedefleniyor."),
    ]
    genislik = Inches(3.9)
    for i, (baslik, metin) in enumerate(kartlar):
        satir, sutun = (0, i) if i < 3 else (1, i - 3)
        x = Inches(0.6) + sutun * (genislik + Inches(0.215)) + (Inches(2.0) if satir == 1 else 0)
        _kart(sl, x, Inches(1.85) + satir * Inches(2.45), genislik, Inches(2.25), baslik, [metin],
              renk=TURKUAZ if i % 2 == 0 else OKRA, govde_boyut=13)


def s_vizyon_2(prs, no, v, sayfa):
    sl = _sayfa(prs, "Enerjide 2026 vizyonu (2/2)", "Rüzgar, hibrit, nükleer ve doğal gaz gelişmeleri",
                "ETKB; T.C. İletişim Başkanlığı; KYB eğitim sunumu", no)
    _yazi(sl, Inches(0.6), Inches(1.8), Inches(5.6), Inches(0.4), [("2026 hibrit kapasite tahsisi (MW)", 15, True, MUREKKEP, False)])
    _grafik(sl, Inches(0.6), Inches(2.25), Inches(5.6), Inches(3.9), XL_CHART_TYPE.COLUMN_CLUSTERED,
            ["Hidroelektrik (HES)", "Diğer"], [("MW", [1300, 200])], fmt="#,##0", renkler=[TURKUAZ], bosluk=80, lejant=False)
    _yazi(sl, Inches(0.6), Inches(6.25), Inches(5.6), Inches(0.5), [(
        "Toplam 1.500 MW başvuruya açıldı; diğer 200 MW, toplamdan HES payının çıkarılmasıyla hesaplandı.", 10, False, SOLUK, False)])
    kartlar = [
        ("Deniz üstü rüzgar YEKA", "2026'da ilk ihale yapılacak; 2035'te toplam kapasitenin 5 GW'a ulaşması hedefleniyor."),
        ("Lisanssız depolama", "10 yılı dolan lisanssız santrallerin depolama sistemleriyle entegre edilerek sistemde tutulması planlanıyor."),
        ("Yeni nükleer ve SMR", "Akkuyu'nun ardından Sinop ve Trakya'da yeni nükleer santraller; SMR yatırımları değerlendiriliyor."),
        ("Doğal gaz santralleri", "ENKA'nın 850 MW doğal gaz yatırımının ardından Oyak Grubu'nun da yatırım yapabileceği belirtildi."),
    ]
    for i, (baslik, metin) in enumerate(kartlar):
        _kart(sl, Inches(6.7), Inches(1.85) + i * Inches(1.2), Inches(6.0), Inches(1.05), baslik, [metin],
              renk=TURKUAZ if i % 2 == 0 else OKRA, govde_boyut=12)


def s_tahsis(prs, no, v, sayfa):
    sl = _sayfa(prs, "Lisanssız santraller için kapasite tahsisi",
                "26 Şubat 2026 tarihli düzenlemeler", "EPDK; KYB eğitim sunumu", no)
    _yazi(sl, Inches(0.6), Inches(1.85), Inches(12.1), Inches(1.2), [(
        "Lisanssız güneş ve rüzgar projeleri için kapasite tahsisi “tükettiğin yerde üret” yaklaşımını izler; aynı sayaç noktasındaki öz tüketimi önceliklendirir ve başvurular bu esasa göre değerlendirilir.",
        16, False, METIN, False)])
    _kart(sl, Inches(0.6), Inches(3.3), Inches(5.9), Inches(3.3), "Öncelik: öz tüketim", [
        "Üretim ve tüketim aynı ölçüm noktasında olmalıdır.",
        "Başvurular, sanayi tesisleri ve stratejik sektörler öncelikli olacak şekilde değerlendirilir.",
    ], renk=TURKUAZ, govde_boyut=14)
    _kart(sl, Inches(6.8), Inches(3.3), Inches(5.9), Inches(3.3), "Maksimum kapasite", [
        "İletim gerilimi seviyesinde şebekeye bağlanacak rüzgar ve güneş kapasitesi 1.500 MWe ile sınırlıdır.",
        "Başvurular bu öncelik esasına göre değerlendirilmektedir.",
    ], renk=OKRA, govde_boyut=14)


def s_hibrit(prs, no, v, sayfa):
    sl = _sayfa(prs, "Hibrit yenilenebilir tesislere bağlantı kapasitesi",
                "EPDK Kurul Kararı, 16 Nisan 2026", "EPDK Kurul Kararı 14482; KYB eğitim sunumu", no)
    _gosterge(sl, Inches(0.6), Inches(1.9), Inches(3.8), "Hibrit kapasite tahsisi", "1.500 MW", "2026 itibarıyla başvuruya açık")
    _gosterge(sl, Inches(4.7), Inches(1.9), Inches(3.8), "Hidroelektrik payı", "1.300 MW", "Tahsisin büyük bölümü")
    _kart(sl, Inches(0.6), Inches(3.6), Inches(3.9), Inches(2.4), "Karar", [
        "EPDK, 16 Nisan 2026 tarihli 14482 sayılı Kurul Kararı ile çok kaynaklı (hibrit) üretim yapısına geçiş için bağlantı kapasitesi çerçevesini belirledi.",
    ], renk=TURKUAZ, govde_boyut=13)
    _kart(sl, Inches(4.7), Inches(3.6), Inches(3.9), Inches(2.4), "Tahsis ilkesi", [
        "Tahsis, mevcut üretim altyapısı ile entegrasyonu esas alır.",
    ], renk=OKRA, govde_boyut=13)
    _kart(sl, Inches(8.8), Inches(3.6), Inches(3.9), Inches(2.4), "Hesaplama", [
        "Kapasite faktörü hesaplarında son 5 yıla ait üretim ve kurulu güç verileri esas alınır.",
    ], renk=ZEYTIN, govde_boyut=13)
    _yazi(sl, Inches(8.6), Inches(1.9), Inches(4.1), Inches(1.2), [(
        "Hibrit tesisler, mevcut santralin kurulu gücü ile sınırlı kapasite alır.", 12, False, SOLUK, False)])


def s_yonetmelik(prs, no, v, sayfa):
    sl = _sayfa(prs, "Lisanssız elektrik üretiminde yeni düzenlemeler",
                "2 Nisan 2026 değişikliği · Resmî Gazete: 33212 · Saatlik mahsuplaşmaya geçiş: 1 Mayıs 2026",
                "EPDK güncel yönetmelik metni; 14531 sayılı Kurul Kararı; EPİAŞ LÜM Kılavuzu", no)
    kartlar = [
        ("Saatlik mahsuplaşma", "1 saat", ["26. madde kapsamındaki üretim ve tüketim EPİAŞ tarafından saatlik mahsuplaştırılır.", "Mesken tesislerinde aylık mahsuplaşma sürer."]),
        ("Depolama entegrasyonu", "Öz tüketim odaklı", ["Üretim tesisinin elektriksel gücüne kadar bütünleşik depolama kurulabilir.", "Depodan verilen miktar ayrılmazsa ihtiyaç fazlasının tamamı bedelsiz kalır."]),
        ("Güç ve üretim sınırları", "2 × elektriksel güç", ["Mekanik güç en fazla elektriksel gücün 2 katı (12.05.2019 sonrası çağrı mektubu alan tesislerde, rüzgar hariç).", "Bedelli üretim limiti: yıllık tüketimin 2 katı; meskenler hariç."]),
        ("Kabul öncesi yaptırım", "60 gün · 3 yıl", ["Çağrı mektubu veya bağlantı anlaşması olmayan tesisin ekipmanı parsel dışına çıkarılır.", "Bu kişiler için 3 yıl yeni başvuru yasağı."]),
        ("Ana ekipmanda üretim tarihi", "Son 5 yıl", ["Panel, invertör, türbin ve batarya gibi ana ekipmanlar son 5 yılda üretilmiş olmalıdır.", "5/1-(a) ve (d) kapsamındaki tesisler istisnadır."]),
        ("Finansman açısından", None, ["Gelir ve borç ödeme projeksiyonları; saatlik üretim–tüketim profili, bedelli üretim limiti ve depolama koşullarıyla güncellenmelidir."]),
    ]
    genislik = Inches(3.91)
    for i, (baslik, vurgu, govde) in enumerate(kartlar):
        satir, sutun = divmod(i, 3)
        _kart(sl, Inches(0.6) + sutun * (genislik + Inches(0.2)), Inches(1.85) + satir * Inches(2.4),
              genislik, Inches(2.25), baslik, govde, renk=TURKUAZ if i % 2 == 0 else OKRA,
              vurgu=vurgu, govde_boyut=12)


BUILDERS = {
    "kapak": s_kapak, "yasal": s_yasal, "icerik": s_icerik,
    "kurulu": s_kurulu, "uretim": s_uretim, "tuketim": s_tuketim, "talep": s_talep,
    "hedef_zaman": s_hedef_zaman, "hedef_grafik": s_hedef_grafik, "devam": s_devam,
    "iletim": s_iletim, "sebeke": s_sebeke, "kullanim": s_kullanim,
    "onlisans_grafik": s_onlisans_grafik, "onlisans_harita": s_onlisans_harita, "onlisans_tablo": s_onlisans_tablo,
    "isletmede": s_isletmede,
    "yekdem_1": s_yekdem_1, "yekdem_2": s_yekdem_2, "tarife_1": s_tarife_1, "tarife_2": s_tarife_2,
    "ptf": s_ptf, "yekdem_formul": s_yekdem_formul, "yekdem_duyuru": s_yekdem_duyuru,
    "vizyon_1": s_vizyon_1, "vizyon_2": s_vizyon_2, "tahsis": s_tahsis, "hibrit": s_hibrit,
    "yonetmelik": s_yonetmelik,
}


def sunum_olustur(v: dict | None = None) -> bytes:
    """Slayt planını (PLAN) çalıştırır ve .pptx dosyasının baytlarını döndürür."""
    v = v or _veri()
    sayfa = {anahtar: i + 1 for i, anahtar in enumerate(PLAN)}
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for i, anahtar in enumerate(PLAN):
        if anahtar == "bol_fiyat":
            _bolum_slayti(prs, i + 1, "2", "Yenilenebilir enerji santralleri için fiyatlandırma mekanizmaları",
                          "PTF, tarifeler, YEKDEM ve EPİAŞ duyuruları")
        elif anahtar == "bol_guncel":
            _bolum_slayti(prs, i + 1, "3", "Güncel gelişmeler ve beklentiler",
                          "2026 vizyonu, lisanssız kapasite tahsisi ve hibrit kapasite")
        else:
            BUILDERS[anahtar](prs, i + 1, v, sayfa)
    cikti = io.BytesIO()
    prs.save(cikti)
    return cikti.getvalue()


def ozet_sunum_bytes() -> bytes:
    """Portaldaki 'Sunumu indir' düğmesi için sunum baytları."""
    return sunum_olustur()
