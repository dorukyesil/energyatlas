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
