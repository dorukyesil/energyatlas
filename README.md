# Enerji Atlası

Enerji sektörüne ilişkin verileri görselleştiren Streamlit tabanlı web portalı.

## Proje yapısı

```
app.py            Giriş sayfası
pages/            Sayfalar: kurulu güç, üretim, tüketim, kişi başına, piyasa hedefleri
src/energyatlas/  Veri okuma ve iş mantığı (Streamlit'e bağımlı değil)
data/             Veri dosyaları (CSV) ve kaynak notları
config.py         Ayarlar (ortam değişkenlerinden okunur)
tests/            Testler
```

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
streamlit run app.py
```

## Testler

```bash
pytest
```

## Ayarlar

| Ortam değişkeni    | Varsayılan            | Açıklama                 |
|--------------------|-----------------------|--------------------------|
| `ENERJI_DATA_DIR`  | `<proje>/data`        | Veri dosyalarının klasörü |
| `ENERJI_APP_TITLE` | `Enerji Atlası`       | Uygulama başlığı         |

> Veriler `data/` klasöründedir. Kaynak ve doğrulama notları için `data/KAYNAKLAR.md` dosyasına bakın.
