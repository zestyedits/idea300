# Deployment Guide

This guide covers deploying Session Architect to production environments.

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended)

**Pros**: Free tier, automatic HTTPS, easy setup
**Cost**: Free for basic usage

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   ```
   Name: session-architect
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT planner:app
   ```
6. Add environment variables:
   - `OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`
   - `PYTHON_VERSION` = `3.11.0`
7. Click "Create Web Service"

### Option 2: Railway

**Pros**: Simple, modern, good free tier
**Cost**: $5/month after free tier

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables:
   ```bash
   railway variables set OPENAI_API_KEY=sk-...
   railway variables set FLASK_SECRET_KEY=your-key
   ```
5. Deploy: `railway up`

### Option 3: Heroku

**Pros**: Well-documented, mature platform
**Cost**: $7/month minimum

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create session-architect`
4. Add buildpack: `heroku buildpacks:set heroku/python`
5. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=sk-...
   heroku config:set FLASK_SECRET_KEY=your-key
   ```
6. Deploy: `git push heroku main`

### Option 4: DigitalOcean App Platform

**Pros**: Reliable, good performance
**Cost**: $5/month minimum

1. Push code to GitHub
2. Go to DigitalOcean dashboard
3. Create new App
4. Connect GitHub repository
5. Configure build settings
6. Add environment variables
7. Deploy

---

## 📋 Pre-Deployment Checklist

### Security

- [ ] Set strong `FLASK_SECRET_KEY` (use `secrets.token_hex(32)`)
- [ ] Enable HTTPS (most platforms provide this automatically)
- [ ] Set `SESSION_COOKIE_SECURE=True` in production
- [ ] Set `SESSION_COOKIE_HTTPONLY=True`
- [ ] Never commit `.env` files
- [ ] Use environment variables for all secrets
- [ ] Implement rate limiting (recommended)

### Configuration

- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper logging
- [ ] Set up error monitoring (Sentry recommended)
- [ ] Configure database (if using persistence)

### Testing

- [ ] Test all routes in staging
- [ ] Verify OpenAI API calls work
- [ ] Check responsive design on mobile
- [ ] Test with real user scenarios
- [ ] Load test if expecting traffic

---

## 🔧 Production Configuration

### Environment Variables

Required for all deployments:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-production-key

# Flask
FLASK_SECRET_KEY=generate-with-secrets-token-hex-32
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

Optional but recommended:

```bash
# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email (if using notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Procfile (for Heroku/Railway)

Create `Procfile` in project root:

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT planner:app --timeout 120
```

### runtime.txt (for Heroku)

Create `runtime.txt`:

```
python-3.11.7
```

### gunicorn_config.py (Advanced)

Create `gunicorn_config.py` for fine-tuned control:

```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'session-architect'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs instance

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "planner:app", "--timeout", "120"]
```

### docker-compose.yml

For local testing:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Optional: PostgreSQL database
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=session_architect
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t session-architect .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e FLASK_SECRET_KEY=... \
  session-architect

# Using docker-compose
docker-compose up -d
```

---

## 🗄️ Database Setup (Optional)

If you want to persist user data and history:

### PostgreSQL Setup

1. **Create database**:
   ```sql
   CREATE DATABASE session_architect;
   ```

2. **Add to requirements.txt**:
   ```
   Flask-SQLAlchemy==3.1.1
   psycopg2-binary==2.9.9
   ```

3. **Update planner.py**:
   ```python
   from flask_sqlalchemy import SQLAlchemy
   
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   db = SQLAlchemy(app)
   ```

4. **Create models** (add to planner.py):
   ```python
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(120), unique=True, nullable=False)
       password_hash = db.Column(db.String(255), nullable=False)
       profession = db.Column(db.String(50))
       credits = db.Column(db.Integer, default=3)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
   class Generation(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       topic = db.Column(db.Text, nullable=False)
       modality = db.Column(db.String(50))
       tone = db.Column(db.String(20))
       plan_content = db.Column(db.Text)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

---

## 📊 Monitoring & Logging

### Sentry Integration

1. Install: `pip install sentry-sdk[flask]`

2. Add to planner.py:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.flask import FlaskIntegration
   
   sentry_sdk.init(
       dsn=os.environ.get("SENTRY_DSN"),
       integrations=[FlaskIntegration()],
       traces_sample_rate=1.0
   )
   ```

### Logging Setup

Add to planner.py:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # File handler
    file_handler = RotatingFileHandler(
        'logs/session_architect.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Session Architect startup')
```

---

## 🔒 SSL/HTTPS Setup

Most modern platforms (Render, Railway, Heroku) provide automatic HTTPS. For custom deployments:

### Using Nginx (Reverse Proxy)

1. Install Nginx
2. Configure SSL with Let's Encrypt:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 💰 Cost Estimation

### Monthly Costs (Approximate)

**Hosting:**
- Render: Free tier or $7/month
- Railway: Free tier or $5/month
- Heroku: $7/month minimum
- DigitalOcean: $5-12/month

**OpenAI API:**
- GPT-4o: ~$0.05-0.10 per generation
- 200 generations/month: $10-20
- 500 generations/month: $25-50

**Total:** $12-70/month depending on usage

### Cost Optimization

1. **Use GPT-3.5-Turbo** for some operations (cheaper)
2. **Implement caching** for common requests
3. **Set up rate limiting** to prevent abuse
4. **Monitor usage** with OpenAI dashboard

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        # Add your test commands here
        python -m pytest
    
    - name: Deploy to Render
      env:
        RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
      run: |
        # Deploy command for your platform
        curl -X POST "https://api.render.com/deploy/..."
```

---

## 🆘 Troubleshooting

### Common Issues

**Issue**: Application crashes on startup
- Check logs for errors
- Verify environment variables are set
- Ensure Python version matches requirements

**Issue**: OpenAI API errors
- Verify API key is correct
- Check OpenAI service status
- Review API usage limits

**Issue**: Session data not persisting
- Check if using database or sessions
- Verify session cookie settings
- Check for CORS issues

### Health Check Endpoint

Add to planner.py:

```python
@app.route("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })
```

---

## 📞 Support

For deployment help:
- **Documentation**: Read full docs
- **Community**: Join Discord
- **Email**: support@sessionarchitect.com

---

**Ready to deploy?** Follow the platform-specific guide above and your Session Architect instance will be live in minutes!