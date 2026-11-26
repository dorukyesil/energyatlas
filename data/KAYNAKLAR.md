# Veri kaynakları ve notlar

Bu dosyadaki değerler, portal ekibinin sağladığı grafik görsellerinden okunarak girilmiştir.
Yayın öncesi her değer resmi kaynaktan (TEİAŞ, EPDK, EPİAŞ, Enerji ve Tabii Kaynaklar Bakanlığı) doğrulanmalıdır.

| Dosya | İçerik | Notlar |
|---|---|---|
| `kurulu_guc.csv` | Kaynaklara göre kurulu güç (GW) ve pay (%) | 2016 güneş payı görselde yazılı değil, boş bırakıldı. Pay toplamları yuvarlama nedeniyle 100 dışında olabilir. |
| `uretim.csv` | Kaynaklara göre brüt üretim (TWh) ve pay (%) | 2016-2018 güneş payı görselde yazılı değil, boş bırakıldı. |
| `tuketim.csv` | Brüt elektrik tüketimi (TWh) | 2025 H1 ve 2026 H1 yarıyıl verileri. |
| `kisi_basina.csv` | Kişi başına tüketim (kWh) | OECD ortalaması 38 ülke için. |
| `hedefler.csv` | Kurulu güç hedefleri (GW) | 2028 ve 2035 hedefleri. Yol haritasındaki `*` dipnotu görselde açıklanmadığı için not olarak eklenmedi. |

Bazı dönemler 9A (ocak-eylül) ve H1 (ilk yarı) olarak ayrı gösterilir; yıllık değerlerle doğrudan karşılaştırılmamalıdır.

## Eklenen veriler (6-9. bölümler)

| Dosya | İçerik | Notlar |
|---|---|---|
| `devam_eden_yatirim.csv` | Depolamalı RES+GES (26,9 GW) ve YEKA 2025-2026 (6,2 GW) | Toplam 33,1 GW görselden. |
| `depolama_kapasite.csv` | Depolamalı santral devreye giriş yılı ve güneş/rüzgar payı | 2023: 21,5 GW, 2024: 4,9 GW, 2025: 0,5 GW. |
| `depolama_sirketler.csv` | Kalyon, ENTEK, Aksa, Enerjisa depolamalı proje kapasiteleri (MW) | Enerjisa projeleri Enerjisa Grubu dahilinde gösterilmektedir. |
| `iletim.csv` | AC hattı, trafo merkezi, HVDC hedefleri, 28 milyar USD yatırım | 2025 HVDC değerleri görselde yok. |
| `baglantilar.csv` | Sınır bağlantıları (8 ülke) | Görseldeki ülke listesi. |

Ön lisans haritaları (9. bölüm) yalnızca görsel yoğunluk içerir. Sayısal il listesi için EPDK kaynağı gerekir.

## Eklenen veriler (10-13. bölümler)

| Dosya | İçerik | Notlar |
|---|---|---|
| `depolama_on_lisans.csv` | Depolamalı GES ve RES ön lisans bitiş yılı, proje adedi, kapasite (MWe) | Toplam GES 10.555 MWe, RES 16.399 MWe (görseldeki toplamlar). Yıllık satırların toplamı birkaç MWe farklı çıkabilir (yuvarlama). |
| `isletmedeki_depolama.csv` | İşletmedeki depolama lisanslı 10 tesis, MWh ve MWe | Toplam 419,5 MWh, 388,5 MWe. Kontrol grubu bilgisi görseldeki dipnottan alındı. |
| `tarife.csv` | EPDK tek zamanlı ve çok zamanlı enerji bedelleri (kr/kWh) | 4 Nisan 2026 itibarıyla, vergiler hariç. Dağıtım bedelleri ve reaktif enerji bedelleri eklenmedi. Kaynak: EPDK, elektrik faturalarına esas tarife tabloları. |
| `ptf.csv` | Piyasa takas fiyatı, USD/MWh (2016-2026 9A) | Görseldeki yıllık değerler. |

## Eklenen veriler (14-18. bölümler)

| Dosya | İçerik | Notlar |
|---|---|---|
| `yekdem_fiyat.csv` | Güneş ve elektrik depolama YEKDEM taban, 2025 ortalama, tavan ve PTF (USD/MWh) | Görselden okundu. |
| `yekdem_formul.csv` | YEKDEM formül ağırlıkları (ÜFE, TÜFE, Dolar/TL, Euro/TL) | 10 yıl (2021-2030), her ay güncellenir. |
| `yekdem_yerli_katki.csv` | Yerli katkı: güneş 15,39 USD/MWh (5 yıl), elektrik depolama 20,54 USD/MWh (10 yıl) | Azami tutarlar, %100 yerli aksam varsayımıyla. |
| `yekdem_duyuru.csv` | EPİAŞ duyurusu: 12 kaynak için Ağustos, Eylül, Ekim 2026 fiyat ve yerli akşam desteği | Birim TL kr/kWh. Kaynak: EPİAŞ, 01.07.2021-31.12.2030 YEK belgeli tesis fiyatları. |
| `dunya_kurulu_guc.csv` | Dünya toplam kurulu güç ve güneş (GW), 2010-2050 | Değerler IEA World Energy Outlook 2025 görselinden. 2010 güneş değeri (40 GW) görselde etiketli. Diğer yenilenebilir değerler yalnızca etiketli olduğu için eklenmedi. |
| `dunya_gunes_payi.csv` | Güneşin toplam ve yenilenebilir kurulu güç içindeki payı (%) | Görselden okundu. |
| `ulke_gunes_2024.csv` (eski, artık kullanılmıyor) | Ülkelerin güneş kurulu gücü (GW) | Türkiye 2025 yıl sonu (TEİAŞ), diğerleri 2024. |

Dünya güneş kapasitesi 2024 değeri (2.164 GW) ile ülke kartındaki toplam görsel tutarlıdır.

## Eklenen veriler (19. bölüm)

| Dosya | İçerik | Notlar |
|---|---|---|
| `kuresel_yatirim.csv` | Küresel toplam enerji, temiz enerji ve güneş yatırımları (milyar USD), 2015-2025 | Görselden okundu. 2015-2025 YBBO: toplam %2,0, temiz %5,9, güneş %12,0 (görseldeki değerlerle tutarlı). |
| `gunes_yatirim_bolge.csv` | Bölgelere göre küresel güneş yatırımları: Asya ve Pasifik, Kuzey Amerika, Avrupa | Yalnızca etiketli bölgeler yazıldı. Diğer bölgeler (Afrika, Merkez ve Güney Amerika, Orta Doğu, Avrasya) toplamdan hesaplanır, sayfada "hesaplanan" olarak işaretli. |

Toplam güneş değeri (441 milyar USD 2025) iki görselde aynıdır, kodda test edilmiştir.

## Kaynak dosyalarından içe aktarılan veriler (kaynak dosya sürümü: Kasım 2026)

Bu veriler `scripts/import_kaynak_verileri.py` ile üretilir. Yeniden üretmek için:
`PYTHONPATH=. python scripts/import_kaynak_verileri.py <kaynak_klasörü>`

| Dosya | Kaynak | İçerik | Not |
|---|---|---|---|
| `epdk_lisans.csv` | EPDK, lisanslı üretim tesisleri listesi | 164 tesis, kurulu güç, depolama, işletmedeki depolama | Kişisel iletişim bilgileri çıkarıldı. |
| `epdk_onlisans.csv` | EPDK, ön lisanslı üretim tesisleri listesi | 502 tesis, bitiş tarihleri, kurulu güç, depolama | Görselden okunan eski değerlerden (530 proje) farklı; liste güncel olduğu için bu esas alınır. |
| `weo_dunya.csv` | IEA World Energy Outlook 2026, Annex A ücretsiz veri seti (dünya) | Kurulu güç (GW) ve elektrik üretimi (TWh), senaryolar: Gerçekleşen, Mevcut politikalar, Belirlenmiş politikalar, Net sıfır (2050) | Güneş 2024: 2.190 GW, 2025: 2.823 GW. Önceki görsel değerleri (2.164 GW) farklı bir sürümdendir. Türkiye ayrı bir kırılım olarak yok. |

Referans: IEA, World Energy Outlook 2025 raporu (PDF). Senaryo tanımları ve politika notları için kullanılmıştır.
| `yatirim_bolge.csv` | IEA, World Energy Investment 2025 veri dosyası | Dünya, ileri ekonomiler, gelişmekte olan ekonomiler (Çin dahil), Çin, bölgeler; 2015-2025; milyar USD (2024 sabit fiyat, MER). Önceki görsel değerleriyle birebir uyumludur. Türkiye, "Europe" grubunda yer alır, ayrı kırılım yoktur. |

## IEA WEO 2026 (dünya ve bölgesel veriler)

`weo_2026.csv` dosyası, Annex A ücretsiz veri setinin dünya ve bölge kırılımlarını tek tabloda toplar.
Kapsam: Dünya ve 15 bölge (Afrika, Asya Pasifik, Brezilya, Orta ve Güney Amerika, Çin, Avrasya, Avrupa, Avrupa Birliği, Hindistan,
Japonya, Orta Doğu, Kuzey Amerika, Rusya, Güneydoğu Asya, ABD). Senaryolar: Gerçekleşen (2010, 2024, 2025), Mevcut politikalar,
Belirlenmiş politikalar, Net sıfır (2050); senaryo yılları 2035, 2040, 2050.
Kategoriler: enerji arzı ve son tüketim, elektrik üretimi ve kapasite, CO2 emisyonları, GSYH ve nüfus, enerji yoğunluğu,
sanayi malzeme üretimi, hidrojen, CCUS ve doğrudan hava yakalama.
Not: Bölgeler birbirini kapsayabilir (ör. Kuzey Amerika ve ABD). Dünya toplamına uluslararası bunkerler dahildir.
Türkiye, WEO bölgesel kırılımında ayrı yer almaz (Avrupa veya Orta Doğu gruplarında değildir).

Ülke ve bölge karşılaştırma sayfası artık `weo_2026.csv` (güneş PV üretimi) verisini kullanır. Türkiye değeri TEİAŞ kurulu güç ve güneş payından hesaplanır.
