# ⚡ DineBot Quick Start Guide

Get DineBot up and running in 5 minutes!

## 🎯 Quick Setup (Windows)

### Step 1: Open Command Prompt in Project Folder
```bash
# Navigate to project folder
cd path\to\dinebot
```

### Step 2: Run These Commands
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start backend
cd backend
python app.py
```

### Step 3: Open Frontend
1. Keep the command prompt running
2. Open `frontend/index.html` in your browser
3. Start chatting!

---

## 🎯 Quick Setup (Mac/Linux)

### Step 1: Open Terminal in Project Folder
```bash
# Navigate to project folder
cd path/to/dinebot
```

### Step 2: Run These Commands
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start backend
cd backend
python app.py
```

### Step 3: Open Frontend
1. Keep the terminal running
2. Open `frontend/index.html` in your browser
3. Start chatting!

---

## 🧪 Test if Everything Works

### Test 1: Backend Health Check
Open in browser: `http://localhost:5000`

**Expected:**
```json
{
  "status": "online",
  "message": "DineBot API is running",
  "version": "1.0.0"
}
```

### Test 2: Chat with Bot
In the frontend:
1. Type: "Hi"
2. Type: "Show me the menu"
3. Type: "Tell me about pizza"

All should work! ✅

---

## 🚨 Troubleshooting

### "Command not found: python"
**Solution:** Try `python3` instead of `python`

### "No module named 'flask'"
**Solution:** Make sure virtual environment is activated (see prompt prefix)

### "spaCy model not found"
**Solution:** Run `python -m spacy download en_core_web_sm`

### "Port 5000 already in use"
**Solution:** Edit `backend/app.py` line 124:
```python
app.run(port=5001)  # Change to 5001 or any free port
```

### Frontend not connecting
**Solution:**
1. Check backend is running
2. Verify URL in `frontend/js/chat.js` matches your backend port
3. Try opening index.html with a local server:
   ```bash
   cd frontend
   python -m http.server 8000
   # Then open: http://localhost:8000
   ```

---

## 📝 Sample Queries to Try

**Easy:**
- "Hi"
- "Show menu"
- "What are your timings?"

**Medium:**
- "Tell me about chicken tikka"
- "Show me vegetarian options"
- "What desserts do you have?"

**Advanced:**
- "What vegetarian dishes cost less than 200?"
- "Does pizza contain any dairy?"
- "Show me spicy appetizers"

---

## 🎓 Understanding the Architecture

```
User Types Query
      ↓
Frontend (chat.js)
      ↓
HTTP POST to /api/chat
      ↓
Flask Backend (app.py)
      ↓
NLP Service (intent + entities)
      ↓
Query Service (business logic)
      ↓
Database (SQLite)
      ↓
JSON Response
      ↓
Frontend Display
```

---

## 📂 File You'll Need to Modify

**For Demo Data:**
- `backend/data/sample_data.json` - Add/edit menu items

**For Restaurant Info:**
- `backend/config.py` - Change name, address, hours

**For UI Styling:**
- `frontend/css/style.css` - Colors, fonts, layout

**For NLP Patterns:**
- `backend/services/nlp_service.py` - Intent patterns

---

## 🎬 Ready for Demo?

### Checklist:
- [ ] Backend running without errors
- [ ] Frontend showing welcome message
- [ ] Test all sample queries
- [ ] Know how to explain NLP concepts
- [ ] Have backup (screenshots/video)

### Quick Demo Flow:
1. **Show UI** (30s)
2. **Basic query** - "Show menu" (30s)
3. **Smart search** - "Tell me about pizza" (30s)
4. **Fuzzy match** - Type "piza" (30s)
5. **Filters** - "Vegetarian options" (30s)
6. **Info** - "Your timings?" (30s)
7. **Explain tech** (1min)

**Total: ~4 minutes**

---

## 🆘 Need Help?

### Check These First:
1. All files in correct folders?
2. Virtual environment activated?
3. All dependencies installed?
4. spaCy model downloaded?
5. Backend running on port 5000?
6. Browser console showing errors?

### Common Solutions:
- Restart backend server
- Clear browser cache
- Check firewall/antivirus
- Try different browser
- Re-run installation steps

---

## 🚀 You're All Set!

Your DineBot is ready to impress! 

**Remember:**
- Keep backend terminal open while using
- Use the quick suggestions for fast testing
- Check TESTING_GUIDE.md for comprehensive tests
- Review README.md for detailed documentation

**Good luck with your demo! 💪**