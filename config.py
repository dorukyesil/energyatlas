"""Uygulama ayarları.

Değerler ortam değişkenlerinden okunur; verilmezse proje içindeki varsayılanlar kullanılır.
Bu sayede aynı kod yerelde, Streamlit Cloud'da veya kendi sunucunuzda değişiklik gerektirmeden çalışır.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = Path(os.environ.get("ENERJI_DATA_DIR", PROJECT_ROOT / "data"))

APP_TITLE = os.environ.get("ENERJI_APP_TITLE", "Enerji Atlası")
