# NFM-X V4 - اردو دستاویزات

## تعارف

NFM-X ایک Open Source Memory Management System ہے جو آپ کو اپنی تمام معلومات کو محفوظ، منظم، اور تلاش کرنے کی سہولت فراہم کرتا ہے۔

## خصوصیات

### Core خصوصیات
- میموری اسٹوریج: ٹیکسٹ، دستاویزات، امیجز
- ایڈوانسڈ سرچ: پورا ٹیکسٹ سرچ
- OCR پروسیسنگ: PDFs، امیجز سے ٹیکسٹ نکالنا
- گراف ریلیشنز: میموریز کے درمیان کنکشنز
- ورژن کنٹرول: چینجز کو ٹریک کریں
- سنک اینڈ بیکپ: خودکار سنک

### V4 نئی خصوصیات
- بہتر OCR انجن: کئی بیک اینڈز
- بیچ پروسیسنگ: کئی دستاویزات ایک ساتھ
- دستاویز مینجمنٹ: مکمل CRUD
- Structured Data Extraction: ٹیبلز، کی-ویلیو
- خودکار کمپریشن: شیڈول کے ساتھ
- ٹکراؤ حل: خودکار اور مینوئل
- پٹرن سرچ: ریگیکس پٹرنز
- ہنر سسٹم: کسٹم ہنر کو چلائیں
- MCP تصدیق: API کی چابیوں کا انتظام
- تفصیلی ہیلتھ چیک: سسٹم مانیٹرنگ
- ریٹ لیمٹ: API ریٹ لیمٹ
- فائل لاگنگ: مکمل لاگنگ

## انسٹالیشن

### Backend

```bash
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X
pip install -r requirements.txt
cp .env.example .env
python -m backend.app.main
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API رفرنس

### V4 اینڈ پوائنٹس

- GET /api/health - ہیلتھ چیک
- GET /api/ocr/config - OCR ترتیبات
- GET /api/documents - دستاویزات کی فہرست
- GET /api/conflicts - ٹکراؤ کی فہرست
- GET /api/patterns - پٹرنز کی فہرست
- GET /api/skills - ہنر کی فہرست
- GET /api/mcp/config - MCP ترتیبات

## ڈاٹا بیس ماڈلز

- Memory: میموری اسٹوریج
- User: صارفین
- Conflict: ٹکراؤ
- Document: دستاویزات
- Pattern: پٹرنز
- Skill: ہنر
- APIKey: API چابیاں

## ٹیسٹنگ

```bash
pytest
pytest -v
pytest --cov=backend/app
```

## ڈپلائمنٹ

Docker کے ساتھ:

```bash
docker-compose up -d
```

## پروبلم حل کرنا

### ڈاٹا بیس انیشیلائز کریں:
```bash
python -c "from backend.app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### پورٹ آزاد کریں:
```bash
lsof -i :8000
kill -9 <PID>
```

## ورژن ہسٹری

- 4.0.0: V4 تمام فیچرز
- 3.0.0: V3 فیچرز
- 2.0.0: V2 فیچرز
- 1.0.0: Core فیچرز

## رابطہ

- ایمل: abdulraheemnohri@gmail.com
- GitHub: https://github.com/abdulraheemnohri/NFM-X

---

**آخری اپ ڈیٹ**: 3 اگست 2026
**ورژن**: 4.0.0
