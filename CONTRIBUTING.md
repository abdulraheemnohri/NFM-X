# NFM-X Contributing Guide

## How to Contribute to NFM-X

We welcome contributions from the community!

### Reporting Issues

- Check existing issues before creating new ones
- Provide clear steps to reproduce the issue
- Include error messages and screenshots if applicable
- Specify your environment (OS, Python version, Node.js version, etc.)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

#### Backend Development

```bash
# Clone the repository
git clone https://github.com/abdulraheemnohri/NFM-X.git
cd NFM-X

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Start development server
cd backend
python -m app.main
```

#### Frontend Development

```bash
cd NFM-X/frontend
npm install
npm start
```

### Project Structure

```
NFM-X/
├── backend/              # FastAPI server
├── sdk/                 # Client SDKs
├── cli/                 # Command-line interface
├── frontend/            # React dashboard
└── docs/                # Documentation
```

### Contribution Guidelines

- Follow PEP 8 for Python code
- Use consistent indentation (4 spaces)
- Include docstrings and comments
- Add Urdu comments for key functionality
- Add tests for new features
- Update documentation

### License

By contributing to NFM-X, you agree that your contributions will be licensed under the MIT License.

---

## Urdu: NFM-X کنٹریبیوٹنگ گائڈ

### کیسے کنٹریبیوٹ کریں

ہمارا خیرمقدم ہے! آپ مندرجہ ذیل طریقوں سے کنٹریبیوٹ کر سکتے ہیں:

### مسائل رپورٹ کریں

- نئے مسائل بنانے سے پہلے موجودہ مسائل چیک کریں
- مسئلہ کو دوبارہ بنانے کے واضح مراحل فراہم کریں

### پل ری کوئسٹ

1. ریپوزٹری فورک کریں
2. فیچر برانچ بنائیں
3. اپنی تبدیلیاں کمٹ کریں
4. برانچ پر پوش کریں
5. پل ری کوئسٹ کھولیں

### ڈویلپمنٹ سیٹ اپ

بیک اینڈ اور فرنٹ اینڈ ڈویلپمنٹ کے لیے گائڈ دیکھیں

### پراجیکٹ ساخت

- Python کوڈ کے لیے PEP 8 کا پابند رہیں
- اردو کمنٹس شامل کریں
- ٹیسٹ شامل کریں

### لائسنس

NFM-X MIT لائسنس کے تحت ہے