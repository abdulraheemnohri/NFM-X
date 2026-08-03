# NFM-X V1.5 دستاویزات - اردو

## 📚 جدول مطالب

1. [تعارف](#تعارف)
2. [انسٹالیشن اور سیٹ اپ](#انسٹالیشن-اور-سیٹ-اپ)
3. [ترتیبات](#ترتیبات)
4. [API رفرنس](#api-رفرنس)
5. [خاصیتیں](#خاصیتیں)
6. [ڈاٹا بیس ماڈلز](#ڈاٹا-بیس-ماڈلز)
7. [استعمال کے نمونے](#استعمال-کے-نمونے)
8. [ٹیسٹنگ](#ٹیسٹنگ)
9. [مائیگریشن گائیڈ](#مائیگریشن-گائیڈ)

---

## تعارف

NFM-X V1.5 بنیادی مموری مینجمنٹ سسٹم متعارف کراتا ہے۔ یہ ورژن مندرجہ ذیل خصوصیات کے ساتھ آتا ہے:

- بنیادی مموری CRUD آپریشنز - مموری بنائیں، پڑھیں، اپ ڈیٹ کریں، مٹائیں
- سادہ سرچ فنکشنلٹی - مموریوں میں تلاش کریں
- گراف پر مبنی رشتے - مموریوں کے درمیان تعلقات دیکھیں
- ٹکراؤ ڈٹیکشن - متضاد مموریوں کا پتا لگائیں
- شوائد اور تجزیات - استعمال کے اعداد و شمار

---

## انسٹالیشن اور سیٹ اپ

### ضروریات

- Python 3.8 یا اس سے اوپر
- FastAPI
- SQLAlchemy
- SQLite

### بیک اینڈ سیٹ اپ

```bash
# ریپوزٹری کلون کریں
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X

# ورچوئل ماحول بنائیں
python -m venv venv
source venv/bin/activate

# ڈپنڈنسیز انسٹال کریں
pip install -r requirements.txt

# ڈیٹا بیس ابتدائی کریں
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"

# بیک اینڈ چلائیں
python -m backend.app.main
```

---

## ترتیبات

### ماحولیاتی متغیرات

```env
NFM_APP_NAME=NFM-X
NFM_APP_VERSION=1.5.0
NFM_DEBUG=True
NFM_ENVIRONMENT=development
NFM_DATABASE_URL=sqlite+aiosqlite:///./nfm.db
NFM_DATABASE_ECHO=False
NFM_DATABASE_POOL_SIZE=5
NFM_DATABASE_MAX_OVERFLOW=10
```

---

## API رفرنس

### مموری API اینڈ پوائنٹس

| طریقہ | اینڈ پوائنٹ | وصف |
|-------|-------------|------|
| GET | /api/v1/memories | تمام مموریوں کی فہرست |
| GET | /api/v1/memories/{id} | مخصوص مموری حاصل کریں |
| POST | /api/v1/memories | نیا مموری بنائیں |
| PUT | /api/v1/memories/{id} | مموری اپ ڈیٹ کریں |
| DELETE | /api/v1/memories/{id} | مموری مٹائیں |

### سرچ API اینڈ پوائنٹس

| طریقہ | اینڈ پوائنٹ | وصف |
|-------|-------------|------|
| GET | /api/v1/search | مموریوں میں تلاش کریں |
| POST | /api/v1/search | پیشرفتہ تلاش |

### گراف API اینڈ پوائنٹس

| طریقہ | اینڈ پوائنٹ | وصف |
|-------|-------------|------|
| GET | /api/v1/graph | مموری گراف حاصل کریں |

### شوائد API اینڈ پوائنٹس

| طریقہ | اینڈ پوائنٹ | وصف |
|-------|-------------|------|
| GET | /api/v1/stats | شوائد حاصل کریں |

### ٹکراؤ API اینڈ پوائنٹس

| طریقہ | اینڈ پوائنٹ | وصف |
|-------|-------------|------|
| GET | /api/v1/conflicts | ٹکراؤ کی فہرست |
| POST | /api/v1/conflicts/resolve | ٹکراؤ حل کریں |

---

## خصوصیات

### مموری مینجمنٹ
- مموری بنائیں، پڑھیں، اپ ڈیٹ کریں، مٹائیں
- میٹا ڈیٹا سپورٹ
- ٹیگنگ سسٹم

### سرچ
- مکمل ٹیکسٹ سرچ
- ٹیگز اور تاریخوں کے ذریعے فلٹر

### گراف
- کنکشنز کو وژولائز کریں
- رشتوں میں نیویگیٹ کریں

### ٹکراؤ
- خودکار ڈٹیکشن
- دستی حل

### شوائد
- مموری میٹرکس
- استعمال کے اعداد

---

## ڈیٹا بیس ماڈلز

### مموری ماڈل

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from backend.app.database import Base

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(200))
    tags = Column(String(500))
    metadata = Column(Text)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, index=True)
    parent_id = Column(Integer, index=True)
```

### ٹکراؤ ماڈل

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.app.database import Base

class Conflict(Base):
    __tablename__ = "conflicts"
    id = Column(Integer, primary_key=True, index=True)
    memory_id_1 = Column(Integer, index=True)
    memory_id_2 = Column(Integer, index=True)
    conflict_type = Column(String(50))
    description = Column(Text)
    severity = Column(Float, default=0.5)
    status = Column(String(20), default="unresolved")
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## استعمال کے نمونے

### مموری بنانا

```bash
curl -X POST "http://localhost:8000/api/v1/memories"   -H "Content-Type: application/json"   -d '{"content": "میری پہلی مموری", "title": "پہلی مموری", "tags": "ٹیسٹ"}'
```

### تلاش کرنا

```bash
curl -X GET "http://localhost:8000/api/v1/search?q=پہلی"
```

---

## ٹیسٹنگ

```bash
pytest backend/app/tests/ -v
```

---

## مائیگریشن گائیڈ

V1.5 پوری طرح V1.0 کے ساتھ متوازی ہے۔ کوئی بریکنگ چینج نہیں۔

---

## چینج لاگ

### V1.5.0 (2026-08-03)
- بنیادی مموری آپریشنز شامل کیے
- سرچ فنکشنلٹی نافذ کی
- گراف رشتے شامل کیے
- ٹکراؤ ڈٹیکشن متعارف کراتی
- شوائد شامل کی

### V1.0.0 (2026-01-01)
- ابتدائی ریلیز

---

## لائسنس

MIT لائسنس - کاپی رائٹ (c) 2026 عبدالرحیم نوحاری

---

## سپورٹ

- GitHub: [https://github.com/abdulraheemnohari/NFM-X](https://github.com/abdulraheemnohari/NFM-X)

---

*آخری اپ ڈیٹ: 3 اگست 2026*