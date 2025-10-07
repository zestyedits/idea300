import os
import markdown
import re
from datetime import datetime

from openai import OpenAI
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-secret-key-in-production')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Professional lens instructions for different clinical perspectives
PROFESSION_INSTRUCTIONS = {
    "Psychiatrist": """Adopt the perspective of a board-certified Psychiatrist (MD/DO). 
    Emphasize: DSM-5-TR diagnostic criteria, neurobiological mechanisms, psychopharmacological considerations, 
    differential diagnosis, and risk assessment. Maintain medical precision and objectivity suitable for 
    clinical documentation.""",
    
    "Psychologist": """Adopt the perspective of a Licensed Clinical Psychologist (PhD/PsyD).
    Emphasize: Evidence-based psychological theories, empirically supported treatments, measurable therapeutic 
    outcomes, comprehensive assessment, and research-backed interventions. Link all recommendations to 
    underlying psychological principles.""",
    
    "Social Worker": """Adopt the perspective of a Licensed Clinical Social Worker (LCSW/LICSW).
    Emphasize: Biopsychosocial assessment, person-in-environment perspective, strengths-based approach, 
    cultural humility, social determinants of health, community resources, and systemic factors. 
    Highlight client resilience and support networks.""",
    
    "LMFT": """Adopt the perspective of a Licensed Marriage and Family Therapist (LMFT).
    Emphasize: Systemic and relational frameworks, interactional patterns, family dynamics, attachment styles, 
    communication processes, and relational context. Even for individual work, consider the client's 
    relational ecosystem.""",
    
    "Counselor": """Adopt the perspective of a Licensed Professional Counselor (LPC/LCPC).
    Emphasize: Wellness model, developmental perspective, multicultural competence, client empowerment, 
    holistic growth, preventive approaches, and skill development. Maintain a collaborative, 
    client-centered stance."""
}

# Master system prompt for session generation
MASTER_PROMPT = """You are an expert clinical supervisor with 20+ years of experience across multiple 
therapeutic modalities. Your knowledge base draws from peer-reviewed research, seminal clinical texts, 
and evidence-based practice guidelines.

{profession_lens}

Your role is to provide comprehensive, structured session plans that clinicians can immediately implement. 

CRITICAL OUTPUT FORMAT:
Structure your entire response using these exact section tags. Each section must be wrapped as shown:

[SECTION:Session Title]
A clear, descriptive title (e.g., "Managing Social Anxiety Through Graded Exposure")
[/SECTION]

[SECTION:Therapeutic Goal]
One specific, measurable, achievable goal for this 50-minute session (e.g., "Client will identify three cognitive distortions contributing to social anxiety and practice one reframing technique").
[/SECTION]

[SECTION:Clinical Conceptualization]
Briefly explain how the chosen modality conceptualizes this presenting problem (2-3 sentences). Reference the theoretical model.
[/SECTION]

[SECTION:Modalities & Techniques]
List the primary therapeutic approach and specific evidence-based techniques being employed (e.g., "CBT using cognitive restructuring, Socratic questioning, and behavioral experiments").
[/SECTION]

[SECTION:Session Structure (Step-by-Step)]
Provide a detailed breakdown of the 50-minute session:
1. Check-in & agenda setting (5 min)
2. Review homework/bridge from last session (5-10 min)
3. Main intervention phase 1 (15 min)
4. Main intervention phase 2 (10 min)
5. Skill practice or in-session activity (10 min)
6. Homework assignment & recap (5-10 min)
[/SECTION]

[SECTION:Clinician Prompts & Activities]
Provide 5-8 specific, open-ended questions or prompts the clinician can use, along with brief descriptions 
of any structured activities. For specialized techniques, cite the source (e.g., "Downward Arrow Technique - Burns, 1980").

Example format:
- "What thoughts went through your mind in that moment?"
- "On a scale of 0-10, how much do you believe that thought right now?"
- Activity: Thought Record Exercise (Beck, 1976) - Client identifies triggering situation, automatic thoughts, emotions, and evidence for/against the thought.
[/SECTION]

[SECTION:Homework or Between-Session Tasks]
Suggest ONE clear, actionable homework assignment that directly reinforces the session's skill or insight. 
Make it specific and measurable (e.g., "Track three situations where you notice catastrophic thinking using the ABC worksheet. Bring completed worksheet to next session.").
[/SECTION]

[SECTION:Protective Factors & Strengths]
Identify 2-3 client strengths, resources, or protective factors the clinician should acknowledge and 
reinforce during the session (e.g., "Strong family support system, high motivation for change, previous 
successful coping with similar challenges").
[/SECTION]

[SECTION:Clinical Rationale]
In 3-4 sentences, justify why this intervention approach is appropriate for the presenting problem. 
Reference its evidence base and expected mechanisms of change. End with a key citation in (Author, Year) format.

Example: "Exposure-based interventions are the gold standard for anxiety disorders, with robust evidence 
showing sustained symptom reduction through extinction learning and inhibitory conditioning. Graded exposure 
allows the client to build distress tolerance systematically while disconfirming feared outcomes. 
Meta-analyses show large effect sizes (d=1.1) for exposure therapy in social anxiety (Hofmann & Smits, 2008)."
[/SECTION]

QUALITY STANDARDS:
- All recommendations must be evidence-based and ethically sound
- Language should be professional yet accessible
- Include specific clinical examples where appropriate
- Cite sources for specialized techniques
- Ensure cultural sensitivity and trauma-informed approach
- Consider safety and risk factors
"""

# DAP Note Generation Prompt
DAP_NOTE_PROMPT = """You are a clinical documentation specialist. Based on the session plan provided, 
generate a professional DAP (Data, Assessment, Plan) progress note suitable for clinical records.

Format the note as follows:

**DATA (Subjective & Objective Observations)**
- Client's presenting concerns and reported symptoms
- Observable behaviors, affect, and engagement level
- Relevant session content

**ASSESSMENT (Clinical Analysis)**
- Progress toward treatment goals
- Client's response to interventions
- Clinical impressions and any changes in presentation

**PLAN (Next Steps)**
- Continued treatment approach
- Homework assigned
- Next session focus
- Any referrals or follow-up actions

Keep the tone professional, concise, and suitable for clinical documentation. Avoid overly detailed 
descriptions—focus on clinically relevant information. Use standard clinical terminology."""

# SOAP Note Generation Prompt
SOAP_NOTE_PROMPT = """You are a clinical documentation specialist. Based on the session plan provided, 
generate a professional SOAP (Subjective, Objective, Assessment, Plan) progress note.

Format the note as follows:

**SUBJECTIVE**
- Client's self-reported symptoms, concerns, and experiences
- Direct quotes when relevant
- Client's perspective on progress

**OBJECTIVE**
- Observable data: affect, behavior, appearance
- Mental status observations
- Session attendance and engagement

**ASSESSMENT**
- Clinical impression of client's current status
- Progress toward treatment goals
- Response to interventions
- Risk assessment if relevant

**PLAN**
- Continued therapeutic approach
- Specific interventions for next session
- Homework or between-session tasks
- Frequency of sessions
- Any referrals needed

Maintain professional clinical language appropriate for medical records."""

# Style-specific instructions
STYLE_INSTRUCTIONS = {
    "professional": """Adopt a formal, clinical tone suitable for professional documentation and 
    peer consultation. Use precise clinical terminology, maintain objectivity, and structure content 
    for maximum clarity. This style is ideal for case presentations and supervision.""",
    
    "balanced": """Adopt a warm yet professional tone suitable for a clinician's personal session 
    preparation notes. Balance clinical precision with accessible language. Include practical tips 
    and conversational flow while maintaining therapeutic integrity.""",
    
    "creative": """Adopt an engaging, psychoeducational tone suitable for teaching or explaining 
    concepts to clients. Use metaphors, analogies, and vivid descriptions while remaining clinically 
    accurate. This style helps clinicians think creatively about presenting interventions."""
}


def generate_session_plan(topic, modality, style, profession):
    """Generate a structured session plan using OpenAI API."""
    
    # Get profession-specific lens
    lens = PROFESSION_INSTRUCTIONS.get(profession, PROFESSION_INSTRUCTIONS["Counselor"])
    
    # Format master prompt with profession lens
    system_prompt = MASTER_PROMPT.format(profession_lens=lens)
    
    # Get style instruction
    style_instruction = STYLE_INSTRUCTIONS.get(style.lower(), STYLE_INSTRUCTIONS["balanced"])
    
    # Construct user message
    user_message = f"""Create a {modality} session plan for the following client scenario:

{topic}

STYLE REQUIREMENT: {style_instruction}

Remember to structure your response using the [SECTION:Title]...[/SECTION] format for all sections."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<p style='color: #dc3545;'>Error generating session plan: {str(e)}</p>"


def parse_structured_plan(text_plan):
    """Parse the structured text plan into sections with titles and HTML content."""
    sections = []
    pattern = r"\[SECTION:(.*?)\](.*?)\[/SECTION\]"
    matches = re.findall(pattern, text_plan, re.DOTALL)
    
    for title, content in matches:
        title = title.strip()
        # Convert markdown to HTML
        content_html = markdown.markdown(
            content.strip(),
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        sections.append({"title": title, "content": content_html})
    
    return sections


def render_plan_html(sections):
    """Convert parsed sections into formatted HTML for display."""
    if not sections:
        return "<p>No plan generated.</p>"
    
    html_parts = []
    for section in sections:
        html_parts.append(f"""
        <div class="plan-section">
            <h2 class="section-title">{section['title']}</h2>
            <div class="section-content">{section['content']}</div>
        </div>
        """)
    
    return "\n".join(html_parts)


def generate_progress_note(session_plan_text, note_type="dap"):
    """Generate a progress note (DAP or SOAP) from a session plan."""
    
    prompt = DAP_NOTE_PROMPT if note_type.lower() == "dap" else SOAP_NOTE_PROMPT
    
    user_message = f"""Based on the following session plan, generate a {note_type.upper()} progress note:

{session_plan_text}

Format the note professionally and concisely."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        note_content = response.choices[0].message.content
        return markdown.markdown(note_content, extensions=['tables', 'nl2br'])
    except Exception as e:
        return f"<p style='color: #dc3545;'>Error generating {note_type.upper()} note: {str(e)}</p>"


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@app.route("/generator", methods=["GET", "POST"])
def generator():
    """Main session generator page."""
    plan_html = None
    output_style = "balanced"
    profession = session.get('profession', 'Counselor')
    
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        modality = request.form.get("modality", "").strip()
        tone = request.form.get("tone", "balanced").strip()
        
        if not topic or not modality:
            plan_html = "<p style='color: #dc3545;'>Please provide both a topic and modality.</p>"
        else:
            # Generate the plan
            generated_plan_text = generate_session_plan(topic, modality, tone, profession)
            
            # Parse into sections
            plan_sections = parse_structured_plan(generated_plan_text)
            
            # Render as HTML
            plan_html = render_plan_html(plan_sections)
            
            # Store in session for regeneration
            session['last_topic'] = topic
            session['last_modality'] = modality
            session['last_tone'] = tone
        
        output_style = tone
    
    return render_template(
        "generator.html",
        plan=plan_html,
        output_style=output_style,
        profession=profession
    )


@app.route("/generate-dap", methods=["POST"])
def generate_dap():
    """API endpoint to generate DAP note from session plan."""
    data = request.get_json()
    session_plan = data.get("plan_text", "")
    
    if not session_plan:
        return jsonify({"error": "No session plan provided."}), 400
    
    dap_note_html = generate_progress_note(session_plan, note_type="dap")
    return jsonify({"dap_note_html": dap_note_html})


@app.route("/generate-soap", methods=["POST"])
def generate_soap():
    """API endpoint to generate SOAP note from session plan."""
    data = request.get_json()
    session_plan = data.get("plan_text", "")
    
    if not session_plan:
        return jsonify({"error": "No session plan provided."}), 400
    
    soap_note_html = generate_progress_note(session_plan, note_type="soap")
    return jsonify({"soap_note_html": soap_note_html})


@app.route("/export/<export_type>", methods=["POST"])
def export_document(export_type):
    """Handle document exports (PDF, DAP, SOAP)."""
    # This is a placeholder - you'll need to implement actual PDF generation
    # using libraries like WeasyPrint, ReportLab, or pdfkit
    html_content = request.form.get("html", "")
    
    if not html_content:
        return jsonify({"error": "No content to export"}), 400
    
    # For now, return a mock response
    # In production, generate actual PDF and return as file
    return jsonify({
        "message": f"{export_type.upper()} export not yet implemented",
        "note": "Implement PDF generation using WeasyPrint or similar library"
    }), 501


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        # In production, validate credentials against database
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Mock authentication
        session['logged_in'] = True
        session['name'] = "Dr. Alex Chen"
        session['email'] = email
        session['profession'] = "Counselor"
        session['user_id'] = "user_12345"
        
        return redirect(url_for('dashboard'))
    
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User signup."""
    if request.method == "POST":
        # In production, create user account in database
        name = request.form.get("name")
        email = request.form.get("email")
        profession = request.form.get("profession", "Counselor")
        
        # Mock account creation
        session['logged_in'] = True
        session['name'] = name
        session['email'] = email
        session['profession'] = profession
        session['user_id'] = f"user_{datetime.now().timestamp()}"
        
        return redirect(url_for('dashboard'))
    
    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    """User dashboard."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_data = {
        "name": session.get('name', 'Clinician'),
        "profession": session.get('profession', 'Not Set'),
        "email": session.get('email', 'user@example.com'),
        "credits": session.get('credits', 50),
        "plans_generated": session.get('plans_generated', 12),
        "plan_tier": session.get('plan_tier', 'Pro'),
        "member_since": session.get('member_since', 'October 2025')
    }
    
    return render_template("dashboard.html", user=user_data)


@app.route("/billing")
def billing():
    """Billing and subscription management."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    billing_data = {
        "plan": "Pro Tier",
        "price": "$29/month",
        "card": "Visa ending in 4242",
        "next_billing_date": "November 6, 2025",
        "credits_remaining": 50,
        "credits_used_this_month": 12
    }
    
    return render_template("billing.html", billing=billing_data)


@app.route("/history")
def history():
    """Generation history."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # In production, fetch from database
    generation_history = [
        {
            "id": "gen_001",
            "date": "2025-10-05",
            "time": "2:30 PM",
            "topic": "Post-breakup rumination and low mood",
            "modality": "CBT",
            "tone": "Balanced"
        },
        {
            "id": "gen_002",
            "date": "2025-10-04",
            "time": "10:15 AM",
            "topic": "Adolescent school avoidance",
            "modality": "SFBT",
            "tone": "Creative"
        },
        {
            "id": "gen_003",
            "date": "2025-10-02",
            "time": "4:45 PM",
            "topic": "Panic attacks in social settings",
            "modality": "ACT",
            "tone": "Professional"
        },
        {
            "id": "gen_004",
            "date": "2025-10-01",
            "time": "11:00 AM",
            "topic": "Trauma processing from childhood abuse",
            "modality": "EMDR",
            "tone": "Balanced"
        }
    ]
    
    return render_template("history.html", history=generation_history)


@app.route("/faq")
def faq():
    """Frequently asked questions."""
    return render_template("faq.html")


@app.route("/personalize", methods=["GET", "POST"])
def personalize():
    """User personalization settings."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Update user preferences
        session['profession'] = request.form.get("profession", "Counselor")
        session['default_modality'] = request.form.get("default_modality", "")
        session['default_tone'] = request.form.get("default_tone", "balanced")
        
        return redirect(url_for('dashboard'))
    
    current_settings = {
        "profession": session.get('profession', 'Counselor'),
        "default_modality": session.get('default_modality', ''),
        "default_tone": session.get('default_tone', 'balanced')
    }
    
    return render_template("personalize.html", settings=current_settings)


@app.route("/logout")
def logout():
    """User logout."""
    session.clear()
    return redirect(url_for('index'))


@app.route("/api/validate-api-key", methods=["POST"])
def validate_api_key():
    """Validate OpenAI API key."""
    data = request.get_json()
    api_key = data.get("api_key", "")
    
    if not api_key:
        return jsonify({"valid": False, "error": "No API key provided"}), 400
    
    try:
        test_client = OpenAI(api_key=api_key)
        # Simple test call
        test_client.models.list()
        return jsonify({"valid": True, "message": "API key is valid"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 400


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set!")
    
    # Run in debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5000)