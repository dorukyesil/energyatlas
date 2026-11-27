# Sunum üretimi (veri kitabı + sabit şablon)

Bu klasör, kullanıcının verdiği **Enerji Sektörü sunumunu** veri kitabındaki güncel sayılarla yeniden üretir.
Sunumun biçimi (yerleşim, renk, yazı tipi, şekiller) **hiç değişmez**; yalnızca sayılar, grafik değerleri,
tablo hücreleri ve çubuk uzunlukları güncellenir.

| Dosya | Görev |
|---|---|
| `sablon/Enerji_Sektoru_Sunum_sablon.pptx` | Sabit şablon (kullanıcının sunumu). Değiştirilmez. |
| `veri/Piyasa_Veri_Kitabi.xlsx` | **Tek veri kaynağı.** Yeni veriler bu kitaba eklenir; formüller korunur. |
| `uret.py` | Kitabı LibreOffice ile hesaplatır, Kontrol sayfasını denetler, sunumu doldurur. |
| `karsilastir.py` | İki sunumu metin, tablo, grafik ve geometri bakımından karşılaştırır. |
| `cikti/` | Üretilen sunumlar (git'e girmez). |

## Sunum istendiğinde

1. Kitapta güncellenecek yeni veri varsa **kitaba ekle** (aşağıya bak), ilgili parametreleri güncelle.
2. `python sunum/uret.py` komutunu çalıştır. Çıktı: `sunum/cikti/Enerji_Sektoru_Sunum_<yıl>-<ay>.pptx`.
3. Üretilen sunumu kullanıcıya ver; güncellenen kitabı da ver ve depoya commit'le.

`uret.py`, kitaptaki **Kontrol** sayfasında UYARI varsa sunumu üretmez (`--zorla` ile atlanır; yalnızca kullanıcı
isterse). Şablonda beklenen bir şekil, metin deseni ya da grafik bulunamazsa `UretimHatasi` ile durur; sessizce
yanlış sunum üretilmez.

## Kitaba nasıl ekleme yapılır

Kitap formüllüdür: `Girdi_*` sayfaları elle girilen veridir, `S2…S5`, `D1…D8` sayfaları formüllerle hesaplanır.
openpyxl ile **formüllü dosya** yüklenip (data_only kullanılmadan) düzenlenir ve kaydedilir; bu yol sunum
sonucunu değiştirmez (test edildi). Kitabın `Kullanim`, `Kullanim_Elk` ve `Kullanim_Depo` sayfalarındaki kurallar geçerlidir:

- **Her ay:** `Girdi_Aylik`'e yeni ayın satırı (TEİAŞ aylık, GWh), `Girdi_Kurulu`'ya yeni ay sonu sütunu
  (YTBS, MW), `Parametre_Elk`'te Rapor ayı ve Kurulu güç tarihi.
- **EPDK listeleri:** `Girdi_Onlisans` ve `Girdi_Lisans`'a listeler, `Parametre_Depo`'da Veri tarihi.
- **YEKDEM / PTF:** `Girdi_Yekdem`, `Girdi_YekdemSabit`, `Girdi_PtfEski`.
- Renk kuralı: mavi yazı elle girilen sayı, yeşil başka sayfadan bağ, siyah formül, sarı dolgu elle güncellenecek hücre.

Elle kalanlar (kitabın `Kullanim` sayfasında): slayt 3 harita görselleri, sahiplik dipnotu, formül ağırlıkları,
PTF 2016-2018 ve 9 aylık sütunları, 2016-2024 üretim payları (`Girdi_Gecmis`, sarı hücreler).
Yeni yıla girerken şablona yıllık sütun eklemek gerekir (elle); `uret.py` bu durumda açık bir hata verir.

## Bilinen tek bilinçli fark

Slayt 2'deki `Oval 85` içindeki görünmeyen artık metin (`%59`), şablonda güncel olmayan bir değerdi; üretimde
güncel yenilenebilir payla (`%63`) aynı yapılır. Test bunu bilinen fark olarak kabul eder.
