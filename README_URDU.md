# NFM-X: غیر فراموش قابل ترقی AI میموری

**«ہر چیز یاد رکھیں۔ تبدیلی کو سمجھیں۔ ہمیشہ ترقی کریں۔»**

## 📚 مفہوم

NFM-X ایک **مستقل، ماڈل سے آزاد، لوکل فرسٹ AI میموری پلیٹ فارم** ہے جو AI سسٹمز کو **دائمی، غیر فراموش، خود بخود ترقی کرنے والی میموری** فراہم کرتا ہے۔

## 🎯 مقصد

NFM-X کا مقصد AI سسٹمز کو ایسی میموری فراہم کرنا ہے جو:
- **ہمیشہ یاد رہے** - معلومات کبھی خود بخود مٹ نہیں جاتی
- **ترقی کرتی رہے** - نئی معلومات سے خود بخود بہتر ہوتی ہے
- **ماڈل سے آزاد ہو** - کسی بھی LLM کے ساتھ کام کرے
- **لوکل فرسٹ ہو** - انٹرنیٹ کے بغیر بھی کامل کام کرے

## 🏗️ آرکیٹیکچر

```
USER / APPLICATION
        ↓
   AI AGENT
        ↓
   NFM-X MEMORY LAYER  ← یہ ہمارا سسٹم
        ↓
   LLM / AI MODEL
```

NFM-X **میڈل ویئر لیئر** کی طرح کام کرتا ہے جو خود بخود:
1. متعلقہ میموریز کو تلاش کرتا ہے
2. انہیں AI کے لیے کنٹیکسٹ بناتا ہے
3. نئی تجربات کو کیپچر کرتا ہے
4. میموریز کو ویلڈیٹ اور کلاسیفائی کرتا ہے
5. علم کو وقت کے ساتھ ترقی دیتا ہے
6. غیر تبدیل شدہ تاریخ کو محفوظ رکھتا ہے

## 📦 انسٹالیشن

```bash
# ریپوزٹوری کلون کریں
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X

# ورچوئل انوائرنمنٹ بنائیں
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# ڈپنڈنسیز انسٹال کریں
pip install -r requirements.txt

# NFM-X سرور شروع کریں
python -m backend.app.main
```

سرور `http://localhost:8765` پر شروع ہوگا۔

## 🚀 استعمال

### Python SDK

```python
from nfm import NFMClient

# NFM-X سے کنیکٹ ہوئیں
nfm = NFMClient("http://localhost:8765")

# AI کے لیے کنٹیکسٹ بنائیں
context = nfm.build_context(
    agent_id="my-agent",
    query="اپنا پراجیکٹ جاری رکھیں"
)

# AI سے جواب حاصل کریں (خود بخود میموری کے ساتھ)
response = nfm.ai.chat(
    agent_id="my-agent",
    message="اپنا پراجیکٹ جاری رکھیں"
)

# مینوئل میموری آپریشنز
nfm.learn(
    agent_id="my-agent",
    user_input="اپنا پراجیکٹ جاری رکھیں",
    ai_output=response
)
```

## 🔧 کنفیگریشن

`.env` فائل بنائیں:

```bash
# سرور سیٹنگز
NFM_HOST=0.0.0.0
NFM_PORT=8765
NFM_DEBUG=true

# اسٹوریج
NFM_STORAGE_PATH=./storage
NFM_VECTOR_BACKEND=faiss

# AI پرووائڈر (اختیاری)
NFM_LLM_PROVIDER=ollama
NFM_LLM_MODEL=llama3.2
NFM_LLM_BASE_URL=http://localhost:11434
```

## 📄 لائسنس

یہ پراجیکٹ MIT لائسنس کے تحت لائسنسڈ ہے - تفصیلات کے لیے [LICENSE](LICENSE) فائل دیکھیں۔

---

**NFM-X: AI کے لیے میموری آپریٹنگ سسٹم**

*"AI اپنا ماڈل بدل سکتا ہے۔ AI اپنا علم بدل سکتا ہے۔ AI اپنی مہارت بہتر کر سکتا ہے۔ AI اپنے عقائد کو درست کر سکتا ہے۔ لیکن اس کی تاریخی میموری کبھی خود بخود کھو نہیں جاتی۔"*