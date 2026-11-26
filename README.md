# Enerji Atlası

Türkiye ve dünya elektrik sektörünü kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler üzerinden
gösteren Streamlit tabanlı web portalı.

## Bölümler

| Kategori | Sayfalar |
|---|---|
| Genel | Genel Bakış, Hakkında |
| Kapasite ve üretim | Kurulu güç, üretim, brüt tüketim, kişi başına tüketim |
| Yenilenebilir ve depolama | Devam eden yatırımlar, depolama ve şebeke, depolama ön lisansları, ön lisans tarihleri, işletmedeki depolama |
| Fiyatlar ve tarifeler | PTF, EPDK tarifeleri, YEKDEM, YEKDEM duyuruları |
| Altyapı ve hedefler | Elektrik iletim ağı, piyasa hedefleri |
| Dünya ve karşılaştırma | Dünya kurulu güç, dünyada güneş payı, ülke karşılaştırması, küresel yatırımlar |

## Proje yapısı

```
app.py              Giriş noktası: tema, gezinme menüsü ve kategoriler
views/              Her sayfa bir dosya
src/energyatlas/
  theme.py          Renk paleti, Plotly şablonu, CSS
  ui.py             Ortak bileşenler (başlık, kart, veri tablosu + CSV indirme)
  charts.py         Grafik üreticileri (Streamlit'ten bağımsız)
  data.py           Veri okuma katmanı
data/               CSV veri dosyaları ve KAYNAKLAR.md (kaynak notları)
config.py           Ayarlar (ortam değişkenleri)
tests/              Testler
```

## Kurulum ve çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testler

```bash
pytest
```

## Ayarlar

| Ortam değişkeni    | Varsayılan      | Açıklama                  |
|--------------------|-----------------|---------------------------|
| `ENERJI_DATA_DIR`  | `<proje>/data`  | Veri dosyalarının klasörü |
| `ENERJI_APP_TITLE` | `Enerji Atlası` | Uygulama başlığı          |

## Streamlit Community Cloud'a dağıtım

1. Depo herkese açık olmalı.
2. [share.streamlit.io](https://share.streamlit.io) adresinde GitHub ile giriş yapın ve **Create app** deyin.
3. Ayarlar:
   - Repository: `dorukyesil/energyatlas`
   - Branch: `claude/energyatlas-portal` (veya birleştirildikten sonra `main`)
   - Main file path: `app.py`
4. Python sürümünü 3.11 veya 3.12 olarak seçin.

Veriler depoda CSV olarak tutulur, dağıtım için ayrıca bir gizli anahtar gerekmez.

## Veri notları

Veriler resmi raporlardan ve kurum duyurularından alınmıştır. Bazı değerler grafiklerden okunmuştur.
Kullanmadan önce `data/KAYNAKLAR.md` dosyasındaki notlara bakın ve resmi kaynaktan doğrulayın.
