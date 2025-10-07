# Session Architect 🧠

**AI-Powered Session Planning for Mental Health Professionals**

Session Architect is a web application that helps licensed mental health clinicians generate evidence-based, structured therapy session plans in seconds. Built by clinicians, for clinicians.

---

## 🌟 Features

- **Multi-Modality Support**: CBT, DBT, ACT, EMDR, IFS, Person-Centered, and 15+ therapeutic approaches
- **Professional Lens Customization**: Tailor outputs to match your clinical perspective (Social Worker, Psychologist, Psychiatrist, LMFT, Counselor)
- **Three Output Styles**: Professional (documentation), Balanced (session prep), Creative (psychoeducation)
- **Quick Templates**: Pre-built scenarios for common presenting concerns
- **Progress Note Generation**: Convert session plans to DAP or SOAP notes
- **Export Options**: PDF, DAP, SOAP formats
- **Evidence-Based**: All recommendations cite research and clinical sources

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/idea300.git
   cd idea300
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   python planner.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here
FLASK_SECRET_KEY=generate-with-secrets-token-hex-32

# Optional
FLASK_DEBUG=True
FLASK_PORT=5000
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

---

## 📁 Project Structure

```
idea300/
├── planner.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── static/
│   └── style.css          # Application styles
├── templates/
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── dashboard.html     # User dashboard
│   ├── generator.html     # Session generator
│   ├── history.html       # Generation history
│   ├── billing.html       # Billing management
│   ├── faq.html          # FAQ page
│   ├── personalize.html  # Settings page
│   ├── 404.html          # Error pages
│   └── 500.html
└── README.md
```

---

## 🎯 Usage

### Generating a Session Plan

1. **Log in** or create an account (free trial: 3 generations)
2. Navigate to **Generator**
3. Enter client presenting concern (de-identified)
4. Select therapeutic modality
5. Choose output tone (Professional/Balanced/Creative)
6. Click **Generate Session Plan**

### Using Quick Templates

Click any template in the sidebar to auto-fill the form with a pre-built scenario.

### Changing Professional Lens

1. Go to **Dashboard**
2. Click **Change Lens**
3. Select your clinical profession
4. All future generations will reflect your perspective

### Exporting Plans

After generating a plan:
- **Copy to Clipboard**: Quick copy for pasting into EHR
- **Export PDF**: Download as formatted PDF
- **Export DAP/SOAP**: Convert to progress note format

---

## 🏗️ Architecture

### Tech Stack

- **Backend**: Flask (Python web framework)
- **AI Engine**: OpenAI GPT-4o
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Markdown**: For rich text formatting
- **Session Management**: Flask sessions

### Core Components

1. **Professional Lens System**: Tailors AI output to match clinical discipline
2. **Structured Parsing**: Converts AI output into organized sections
3. **Template System**: Pre-built clinical scenarios
4. **Progress Note Generator**: Converts plans to documentation formats

---

## 🔐 Security & Privacy

### HIPAA Compliance Considerations

⚠️ **IMPORTANT**: This tool is for **session planning**, not client documentation.

- **DO NOT** enter Protected Health Information (PHI)
- **DO NOT** use real client names or identifying details
- Always de-identify scenarios (e.g., "Adult client, age ~30s")
- Use general descriptions only

### Best Practices

1. **De-identification**: Remove all identifying details
2. **General Scenarios**: Focus on presenting problems, not individuals
3. **Local Storage**: Keep sensitive notes offline
4. **Secure Connection**: Always use HTTPS in production

---

## 🚧 Development Roadmap

### Current Version (v1.0)

- ✅ Core session plan generation
- ✅ Multi-modality support
- ✅ Professional lens customization
- ✅ Quick templates
- ✅ DAP/SOAP note generation

### Planned Features (v2.0)

- [ ] PDF export implementation (WeasyPrint)
- [ ] User authentication with password hashing
- [ ] Database integration (PostgreSQL)
- [ ] Session history persistence
- [ ] Stripe billing integration
- [ ] Email notifications
- [ ] Rate limiting
- [ ] Advanced filtering and search

### Future Enhancements

- [ ] Custom template creation
- [ ] Collaborative workspaces
- [ ] Treatment plan tracking
- [ ] Mobile app (iOS/Android)
- [ ] API for third-party integrations

---

## 🛠️ Deployment

### Development

```bash
python planner.py
```

### Production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 planner:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "planner:app"]
```

### Platform Recommendations

- **Heroku**: Easy deployment with buildpacks
- **Render**: Modern platform with free tier
- **DigitalOcean App Platform**: Scalable and affordable
- **AWS Elastic Beanstalk**: Enterprise-grade
- **Railway**: Simple deployment with GitHub integration

---

## 📊 API Usage & Costs

### OpenAI API Costs (Approximate)

- **GPT-4o**: ~$0.05-0.10 per session plan generation
- **Average Plan**: 2,000-3,000 tokens output
- **Monthly Estimate**: $15-30 for 200-300 generations

### Rate Limits

- Default: No rate limiting (implement in production)
- Recommended: 50 generations per user per day

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Landing page loads correctly
- [ ] User can sign up and log in
- [ ] Session plan generates successfully
- [ ] All modalities work (CBT, DBT, ACT, etc.)
- [ ] All professional lenses work
- [ ] Templates auto-fill form correctly
- [ ] DAP/SOAP notes generate
- [ ] Copy to clipboard functions
- [ ] Responsive design on mobile

### Test Scenarios

```python
# Example test case
Topic: "Adult experiencing panic attacks in crowded spaces"
Modality: "CBT"
Tone: "Balanced"
Expected: Structured plan with cognitive restructuring techniques
```

---

## 🤝 Contributing

We welcome contributions from the clinical and developer community!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide for Python
- Add docstrings to functions
- Test thoroughly before submitting
- Update README if adding features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**Clinical Responsibility**: This tool provides suggestions for session planning based on evidence-based practices. All clinical decisions remain the sole responsibility of the licensed clinician. Always use professional judgment, consider individual client needs, and adhere to ethical guidelines and scope of practice.

**Not a Substitute**: This tool does not replace:
- Clinical supervision
- Professional training
- Peer consultation
- Ongoing education
- Direct client assessment

**Accuracy**: While we strive for accuracy, AI-generated content may contain errors. Always verify recommendations against clinical literature and best practices.

---

## 📞 Support

### Documentation

- **Full Documentation**: [docs.sessionarchitect.com](https://docs.sessionarchitect.com)
- **Video Tutorials**: [YouTube Channel](https://youtube.com/@sessionarchitect)

### Community

- **Discord**: [Join our community](https://discord.gg/sessionarchitect)
- **Email**: support@sessionarchitect.com

### Bug Reports

Found a bug? [Open an issue](https://github.com/yourusername/idea300/issues)

---

## 🙏 Acknowledgments

- **OpenAI**: For GPT-4o API
- **Flask Community**: For excellent web framework
- **Clinical Advisors**: Licensed therapists who provided feedback
- **Beta Testers**: Early users who helped refine features

---

## 📈 Changelog

### Version 1.0.0 (2025-10-06)

- Initial release
- Core session plan generation
- 15+ therapeutic modalities
- 5 professional lenses
- DAP/SOAP note generation
- Quick templates
- Responsive design

---

**Built with ❤️ by clinicians, for clinicians**

*Helping therapists spend less time planning and more time healing.*