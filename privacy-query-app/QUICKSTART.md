# 🚀 QUICK START GUIDE

**Get Privacy Query Interface running in 5 minutes!**

---

## ⚡ Step 1: Windows/macOS/Linux - Install Requirements

### Windows
```powershell
# Open PowerShell, navigate to project folder
cd privacy-query-app

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install everything
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### macOS/Linux
```bash
cd privacy-query-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## ⚡ Step 2: Start Ollama

**Open a new terminal/command prompt:**

```bash
# Terminal 1: Start Ollama service
ollama serve

# Wait for: "Listening on 127.0.0.1:11434"
```

**Open another terminal for model:**

```bash
# Terminal 2: Download Llama 3 (first time only - takes 10-20 min)
ollama pull llama3

# Wait for download to complete
```

---

## ⚡ Step 3: Run the Flask App

**In your original terminal (with venv activated):**

```bash
# Make sure you're in privacy-query-app folder
# Make sure (venv) shows in your terminal prompt

python app.py

# You should see:
# Running on http://127.0.0.1:5000
```

---

## ⚡ Step 4: Open Browser

Go to: **http://localhost:5000**

---

## ⚡ Step 5: Create Account & Test

1. Click **"Sign up here"**
2. Create account:
   - Username: `testuser`
   - Password: `TestPass123` (min 6 chars)
3. Click **"Create Account"**
4. Login with your credentials
5. Try a query:

```
My name is John Smith, my email is john@example.com, 
I work at Google. What is machine learning?
```

Click **"Submit Query"** and watch it work! 🎉

---

## 🔍 What Happens Every Submission

```
You type query
    ↓
PII detected (names, emails, phone, etc.)
    ↓
Risk score calculated (0-100)
    ↓
Data masked [NAME], [EMAIL], etc.
    ↓
Masked query sent to Llama 3 AI
    ↓
Response received
    ↓
Original values restored in response
    ↓
Results displayed in dashboard
```

---

## 📖 Important Files & Docs

Keep these bookmarked:

| File | Purpose |
|------|---------|
| **README.md** | Complete overview & features |
| **DEPLOYMENT.md** | Detailed setup & troubleshooting |
| **PROJECT_SUMMARY.md** | What's included in the project |
| **app.py** | Main application - READ THE CODE! |

---

## ❌ Troubleshooting Quick Fixes

### *"Cannot connect to Ollama API"*
→ Make sure `ollama serve` is running in Terminal 1

### *"Model 'en_core_web_sm' not found"*
→ Run: `python -m spacy download en_core_web_sm`

### *"Port 5000 already in use"*
→ Close other instances or use: `python app.py --port 5001`

### *"ModuleNotFoundError: flask"*
→ Make sure (venv) is activated. See Step 1 above.

### *"First Ollama request takes forever"*
→ **Normal!** First request loads the 4GB model (2-3 minutes)
→ Subsequent requests much faster (5-15 seconds)

---

## 💡 Pro Tips

- 📝 Check **Query History** tab to view past queries
- 🛡️ Click **How It Works** to understand risk scoring
- 🔒 Your data stays on your machine - never sent to external AI
- 📋 Copy button for easy sharing of results
- 🌙 Page supports dark mode (browser setting)

---

## 🎓 Next Steps

1. **Try different queries** - see what gets detected
2. **Check the code** - read app.py, understand flow
3. **Customize** - adjust risk weights, add more PII types
4. **Share it** - showcase in portfolio/interviews
5. **Deploy** - follow DEPLOYMENT.md for production

---

## 📱 Example Queries to Try

### Safe Query (No PII)
```
What are the latest trends in artificial intelligence?
```
Expected: No PII detected, Risk Score: 0

### Business Email
```
Contact me at john.doe@company.com for the project details.
```
Expected: EMAIL detected, Risk Score: 30

### Full Personal Info
```
My name is Sarah Johnson, email sarah@mail.com, phone +1-555-123-4567,
I live in New York and work at Apple. My Aadhaar is 1234 5678 9012.
```
Expected: Multiple detections, Risk Score: 100+

### Password Leak (Demo)
```
My password is SuperSecure123! and API key is sk_live_abc123
```
Expected: PASSWORD and API_KEY detected, Risk Score: 100

---

## ✅ Checklist

- [ ] Python 3.9+ installed
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] SpaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] Ollama running (`ollama serve`)
- [ ] Llama 3 pulled (`ollama pull llama3`)
- [ ] Flask app running (`python app.py`)
- [ ] Browser opened to http://localhost:5000
- [ ] Account created
- [ ] First query tested

**All checked? You're ready! 🚀**

---

## 🆘 Need Help?

1. **Installation issues?** → Read DEPLOYMENT.md (detailed step-by-step)
2. **How does it work?** → Read README.md (complete guide)
3. **What's in the code?** → Read PROJECT_SUMMARY.md
4. **Code not working?** → Check error message in terminal
5. **Ollama not responding?** → Ensure `ollama serve` is running

---

## 🎉 Congratulations!

You now have a production-quality, privacy-preserving AI interface running locally!

**This project demonstrates:**
- Full-stack web development
- Security best practices
- NLP/AI integration
- Database design
- Modern UI/UX
- API development

Perfect for: Portfolio, interviews, academic projects, or learning!

---

**Happy exploring! 🛡️**

Questions? All answers are in README.md, DEPLOYMENT.md, and the code comments.
