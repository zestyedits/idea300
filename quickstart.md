# 🚀 Quick Start Guide

Get Session Architect running in **5 minutes**!

## Prerequisites

- Python 3.10+ installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Installation Steps

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/idea300.git
cd idea300
```

### 2. Run Setup Script

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 3. Add Your API Key

Open `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Run the App

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate     # Windows

# Start the server
python planner.py
```

### 5. Open in Browser

Navigate to: **http://localhost:5000**

## First Use

1. Click **Sign Up**
2. Create an account (gets 3 free generations)
3. Go to **Generator**
4. Try a template or enter your own scenario
5. Click **Generate Session Plan**

## Troubleshooting

**Port already in use?**
```bash
# Change port in .env
FLASK_PORT=8000
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**OpenAI API error?**
- Check your API key is correct
- Verify you have credits at platform.openai.com
- Ensure no extra spaces in .env file

## Next Steps

- [Read full documentation](README.md)
- [Deploy to production](DEPLOYMENT.md)
- [Contribute](CONTRIBUTING.md)

## Need Help?

- 📧 Email: support@sessionarchitect.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/idea300/issues)

---

**You're all set! Start generating evidence-based session plans.** 🎉