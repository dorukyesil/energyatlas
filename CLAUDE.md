# Kalıcı yönergeler

## Sunum
Kullanıcı "sunumu ver / hazırla" dediğinde `sunum/README.md` iş akışını izle: sunum şablonu
(`sunum/sablon/`) **hiç değişmez**; yalnızca sayılar, grafikler ve tablolar `sunum/veri/Piyasa_Veri_Kitabi.xlsx`
kitabındaki güncel veriden doldurulur (`python sunum/uret.py`). Yeni veri geldikçe **bu kitaba ekleme yap**
(formülleri koru), kitabı commit'le ve güncel kitabı kullanıcıya da ver. Kontrol sayfasında UYARI varsa sunum üretme.
Portaldaki eski `export.py` sunumu bu değildir; kullanıcının istediği sunum şablonlu üretimdir.

## Veri
- TEİAŞ verisi yalnızca MCP/resmi tablolardan alınır; kullanıcının gönderdiği görsellerden sayı okunmaz.
- Yenilenebilir = hidro + jeotermal + rüzgar + güneş + biyokütle ve atık ısı. Termik bu ikisi hariç fosil kaynaklardır.
- Kaynak renkleri `src/energyatlas/theme.py` içindeki `kaynak_rengi` ile sabittir (güneş sarı, rüzgar yeşil, hidro mavi, termik koyu).

## Git
Geliştirme dalı `claude/energyatlas-portal`. Yalnızca kullanıcı isterse `main`'e alınır.
