# NFM-X Testing Guide

## Testing the Complete NFM-X System

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Virtual environment (recommended)

### Backend Testing

#### 1. Install Backend Dependencies

```bash
cd NFM-X
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Start Backend Server

```bash
cd backend
python -m app.main
```

The server will start at `http://localhost:8765`

#### 3. Test Backend API Endpoints

You can test the API using curl or any HTTP client:

```bash
# Health check
curl http://localhost:8765/health

# Get system info
curl http://localhost:8765/info

# Create a test memory
curl -X POST http://localhost:8765/api/memory/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "memory_type": "episodic", "tags": ["test"], "confidence": 0.9}'
```

### Frontend Testing

#### 1. Install Frontend Dependencies

```bash
cd NFM-X/frontend
npm install
```

#### 2. Start Frontend Development Server

```bash
npm start
```

The frontend will start at `http://localhost:3000`

#### 3. Test Frontend Pages

- **Dashboard**: `http://localhost:3000/` - View system statistics and recent activity
- **Memories**: `http://localhost:3000/memories` - List, create, edit, and delete memories
- **Search**: `http://localhost:3000/search` - Search memories with different strategies
- **Graph**: `http://localhost:3000/graph` - Visualize knowledge graph
- **Analytics**: `http://localhost:3000/analytics` - View analytics and charts
- **Settings**: `http://localhost:3000/settings` - Configure API and language settings

### Integration Testing

#### 1. Test Complete Workflow

1. Create a memory using the frontend form
2. Verify it appears in the memories list
3. Search for the memory using different search strategies
4. View the memory in the knowledge graph
5. Check analytics to see the new memory statistics

#### 2. Test API Integration

- Ensure all API endpoints are accessible from the frontend
- Test error handling for invalid inputs
- Test authentication if API key is configured

#### 3. Test Language Support

- Switch between English and Urdu in settings
- Verify all UI elements update correctly
- Test RTL layout for Urdu

---

## Urdu: NFM-X ٹیسٹنگ گائڈ

### شروع کرنے سے پہلے

- Python 3.10+ 
- Node.js 18+
- Git

### بیک اینڈ ٹیسٹنگ

#### 1. بیک اینڈ سرور شروع کریں

```bash
cd NFM-X/backend
python -m app.main
```

سرور http://localhost:8765 پر شروع ہو گا

#### 2. فرنٹ اینڈ ٹیسٹنگ

```bash
cd NFM-X/frontend
npm install
npm start
```

فرنٹ اینڈ http://localhost:3000 پر شروع ہو گا

#### 3. مکمل سسٹم ٹیسٹ کریں

- میموری بنائیں
- میموری سرچ کریں
- گراف دیکھیں
- اینالٹکس چیک کریں
- زبان بدلیں

### مسائل اور حل

- پورٹ پہلے سے استعمال میں ہے: .env فائل میں پورٹ بدلیں
- ڈپینڈنسیز غائب ہیں: pip install -r requirements.txt
- API سے کنکشن نہیں: بیک اینڈ سرور چل رہا ہے کیہ چیک کریں