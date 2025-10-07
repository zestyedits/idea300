import os
import markdown
import re
import secrets
from datetime import datetime
from functools import wraps

from openai import OpenAI
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

PROFESSION_INSTRUCTIONS = {
    "Psychiatrist": """Adopt the perspective of a board-certified Psychiatrist (MD/DO). 
    Emphasize DSM-5-TR diagnostic criteria, neurobiological mechanisms, psychopharmacological considerations, 
    differential diagnosis, and risk assessment. Maintain medical precision and objectivity suitable for 
    clinical documentation. Consider medication interactions and contraindications when relevant.""",
    
    "Psychologist": """Adopt the perspective of a Licensed Clinical Psychologist (PhD/PsyD).
    Emphasize evidence-based psychological theories, empirically supported treatments, measurable therapeutic 
    outcomes, comprehensive psychological assessment, and research-backed interventions. Link all recommendations 
    to underlying psychological principles and cite relevant research when appropriate.""",
    
    "Social Worker": """Adopt the perspective of a Licensed Clinical Social Worker (LCSW/LICSW).
    Emphasize biopsychosocial assessment, person-in-environment perspective, strengths-based approach, 
    cultural humility, social determinants of health, community resources, and systemic factors. 
    Highlight client resilience, support networks, and advocacy opportunities.""",
    
    "LMFT": """Adopt the perspective of a Licensed Marriage and Family Therapist (LMFT).
    Emphasize systemic and relational frameworks, interactional patterns, family dynamics, attachment styles, 
    communication processes, and relational context. Even for individual work, conceptualize the client within 
    their relational ecosystem and family-of-origin patterns.""",
    
    "Counselor": """Adopt the perspective of a Licensed Professional Counselor (LPC/LCPC).
    Emphasize wellness model, developmental perspective, multicultural competence, client empowerment, 
    holistic growth, preventive approaches, and skill development. Maintain a collaborative, 
    client-centered stance that honors client autonomy and self-determination."""
}

MASTER_PROMPT = """You are an expert clinical supervisor with 20+ years of experience across multiple 
therapeutic modalities. Your knowledge base draws from peer-reviewed research, seminal clinical texts, 
and evidence-based practice guidelines. You prioritize ethical practice, cultural competence, and 
trauma-informed care in all recommendations.

{profession_lens}

Your role is to provide comprehensive, structured session plans that clinicians can immediately implement 
with real clients. All recommendations must be ethical, evidence-based, and clinically sound.

CRITICAL OUTPUT FORMAT:
Structure your entire response using these exact section tags. Each section must be wrapped as shown:

[SECTION:Session Title]
A clear, descriptive title that captures the session's focus (e.g., "Managing Social Anxiety Through Graded Exposure and Cognitive Restructuring")
[/SECTION]

[SECTION:Therapeutic Goal]
One specific, measurable, achievable goal for this 50-minute session. Use SMART criteria when possible 
(e.g., "Client will identify three cognitive distortions contributing to social anxiety and practice 
cognitive restructuring on one scenario using the Dysfunctional Thought Record").
[/SECTION]

[SECTION:Clinical Conceptualization]
In 2-4 sentences, explain how the chosen modality conceptualizes this presenting problem. Reference the 
theoretical model and key mechanisms of change (e.g., "From a CBT perspective, social anxiety is maintained 
by overestimation of threat, safety behaviors that prevent disconfirmation of feared outcomes, and negative 
self-focused attention that amplifies distress").
[/SECTION]

[SECTION:Modalities & Techniques]
List the primary therapeutic approach and specific evidence-based techniques being employed. Be precise 
(e.g., "Cognitive Behavioral Therapy (CBT) using: Socratic questioning, cognitive restructuring via 
Dysfunctional Thought Record, behavioral experiment design, and in-session exposure practice").
[/SECTION]

[SECTION:Session Structure (Step-by-Step)]
Provide a detailed breakdown of the 50-minute session with approximate time allocations:
1. **Check-in & Agenda Setting (5 min)** - Brief description
2. **Homework Review & Bridge from Last Session (5-10 min)** - What to review
3. **Main Intervention Phase 1 (15 min)** - Core technique or psychoeducation
4. **Main Intervention Phase 2 (10 min)** - Application or practice
5. **Skill Practice or In-Session Activity (10 min)** - Hands-on work
6. **Homework Assignment & Session Summary (5-10 min)** - Consolidation and next steps
[/SECTION]

[SECTION:Clinician Prompts & Activities]
Provide 6-10 specific, open-ended questions or prompts the clinician can use verbatim, along with 
brief descriptions of structured activities. For specialized techniques, cite the original source.

Format examples:
- **Opening Prompt:** "What's been the most challenging situation for you this week?"
- **Socratic Question:** "What evidence do you have that supports this thought? What evidence contradicts it?"
- **Scaling Question:** "On a scale of 0-10, how much do you believe [thought] right now? Let's explore that."
- **Activity: Thought Record Exercise (Beck, 1976)** - Client identifies triggering situation, automatic 
  thoughts, emotions, evidence for/against the thought, and develops balanced alternative thought.
[/SECTION]

[SECTION:Homework or Between-Session Tasks]
Suggest ONE clear, specific, actionable homework assignment that directly reinforces the session's skill 
or insight. Make it measurable and feasible. Include:
- What to do
- How often or when
- What to track or bring back
Example: "Complete a Thought Record each day when you notice social anxiety (aim for 3-5 records). 
Bring completed worksheets to next session for review."
[/SECTION]

[SECTION:Protective Factors & Strengths]
Identify 2-4 client strengths, resources, or protective factors the clinician should explicitly acknowledge 
and reinforce during the session. Be specific (e.g., "Strong social support from partner, demonstrated 
resilience in past challenges, high insight and motivation for change, stable employment and housing").
[/SECTION]

[SECTION:Clinical Rationale]
In 3-5 sentences, justify why this intervention approach is appropriate for the presenting problem. 
Reference its evidence base, expected mechanisms of change, and outcome research. End with 1-2 key 
citations in (Author, Year) or (Author et al., Year) format.

Example: "Cognitive restructuring is a core CBT technique with robust empirical support for anxiety 
disorders. By identifying and challenging maladaptive thought patterns, clients learn to evaluate thoughts 
more objectively rather than accepting them as facts. This process reduces emotional reactivity and 
behavioral avoidance. Meta-analyses consistently show large effect sizes (d=0.9-1.2) for CBT in social 
anxiety disorder, with gains maintained at follow-up (Hofmann & Smits, 2008; Mayo-Wilson et al., 2014)."
[/SECTION]

[SECTION:Risk Considerations & Contraindications]
Briefly note any safety concerns, red flags to monitor, or situations where this approach should be 
modified or contraindicated (e.g., "Monitor for increased suicidal ideation during exposure work. If 
client reports active SI with plan/intent, pause intervention and conduct safety assessment. Exposure 
work may need to be slowed for clients with severe dissociation or unprocessed trauma").
[/SECTION]

[SECTION:Cultural Considerations]
Address how cultural factors, identity, and context should inform intervention delivery (e.g., "Consider 
how collectivist values may influence client's view of 'assertiveness.' Explore cultural norms around 
emotional expression. Ensure exposure hierarchy accounts for culturally-relevant social situations").
[/SECTION]

QUALITY STANDARDS:
- All recommendations must be evidence-based, ethical, and clinically sound
- Use professional yet accessible language
- Include specific clinical examples and concrete techniques
- Cite sources for specialized interventions
- Ensure cultural humility and trauma-informed approach throughout
- Consider safety, risk factors, and contraindications
- Respect client autonomy and informed consent
- Acknowledge limitations and when to refer
"""

STYLE_INSTRUCTIONS = {
    "professional": """Adopt a formal, clinical tone suitable for professional documentation, 
    case presentations, and peer consultation. Use precise clinical terminology, maintain strict 
    objectivity, and structure content for maximum clarity. This style is ideal for supervision 
    notes, treatment planning documentation, and case conference presentations. Minimize narrative 
    elements and prioritize clinical precision.""",
    
    "balanced": """Adopt a warm yet professional tone suitable for a clinician's personal session 
    preparation notes. Balance clinical precision with accessible, conversational language. Include 
    practical implementation tips and maintain therapeutic authenticity. This style bridges formal 
    documentation and clinical practice, making complex concepts immediately usable while preserving 
    professional integrity.""",
    
    "creative": """Adopt an engaging, psychoeducational tone suitable for teaching concepts to clients 
    or creating client-friendly handouts. Use metaphors, analogies, and vivid descriptions to illuminate 
    therapeutic principles while remaining clinically accurate. This style helps clinicians think 
    creatively about presenting interventions in ways that resonate emotionally while maintaining 
    evidence-based foundations."""
}

DAP_NOTE_PROMPT = """You are a clinical documentation specialist creating progress notes for 
electronic health records. Generate a professional DAP (Data, Assessment, Plan) note based on 
the session plan provided.

Format requirements:

**DATA (Subjective & Objective Observations)**
- Client's self-reported concerns, symptoms, and experiences
- Observable presentation: affect, mood, behavior, engagement
- Key session content and interventions provided
- Client's response to interventions

**ASSESSMENT (Clinical Analysis)**
- Progress toward treatment goals (reference specific goals)
- Client's response to interventions and therapeutic process
- Clinical impressions and any changes in presentation
- Strengths and barriers to progress
- Current risk level if relevant

**PLAN (Next Steps)**
- Continued treatment approach and modality
- Specific interventions planned for next session
- Homework or between-session tasks assigned
- Any referrals, consultations, or follow-up actions needed
- Next session scheduled date/time

Standards:
- Use professional, concise clinical language
- Focus on clinically relevant, billable content
- Avoid excessive detail—prioritize what matters for treatment planning
- Use standard clinical terminology and abbreviations appropriately
- Ensure note supports medical necessity
- Maintain HIPAA compliance (no identifying details beyond what's clinically necessary)
"""

SOAP_NOTE_PROMPT = """You are a clinical documentation specialist creating progress notes for 
medical/clinical records. Generate a professional SOAP (Subjective, Objective, Assessment, Plan) 
note based on the session plan provided.

Format requirements:

**SUBJECTIVE**
- Client's self-reported symptoms, concerns, and experiences
- Relevant quotes (if applicable)
- Client's perception of progress and challenges
- Changes since last session

**OBJECTIVE**
- Observable data: affect, mood, appearance, behavior
- Mental Status Exam observations (orientation, memory, attention, insight, judgment)
- Session attendance and level of engagement
- Psychometric data if relevant

**ASSESSMENT**
- Clinical diagnosis or working diagnosis (if applicable)
- Clinical impression of current status and functioning
- Progress toward treatment goals with specific indicators
- Response to current interventions
- Risk assessment (SI/HI/AVH if relevant)
- Functional impairment level

**PLAN**
- Continued treatment approach and theoretical orientation
- Specific interventions for next session
- Homework or between-session practice assigned
- Frequency and modality of future sessions
- Referrals, consultations, or coordination of care needed
- Any medication considerations (for prescribers)
- Target date for treatment plan review

Standards:
- Use medical-model clinical language appropriate for interdisciplinary records
- Include DSM-5-TR terminology where appropriate
- Structure for billing and insurance documentation
- Support medical necessity clearly
- Ensure clarity for other treatment team members
- Maintain professional objectivity
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def generate_session_plan(topic, modality, style, profession):
    """Generate a structured session plan using OpenAI API."""
    lens = PROFESSION_INSTRUCTIONS.get(profession, PROFESSION_INSTRUCTIONS["Counselor"])
    system_prompt = MASTER_PROMPT.format(profession_lens=lens)
    style_instruction = STYLE_INSTRUCTIONS.get(style.lower(), STYLE_INSTRUCTIONS["balanced"])
    
    user_message = f"""Create a {modality} session plan for the following client scenario:

{topic}

STYLE REQUIREMENT: {style_instruction}

CRITICAL: Structure your response using the [SECTION:Title]...[/SECTION] format for ALL sections."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        app.logger.error(f"OpenAI API error: {str(e)}")
        return f"<p style='color: #dc3545;'>Error generating session plan: {str(e)}</p>"


def parse_structured_plan(text_plan):
    """Parse the structured text plan into sections with titles and HTML content."""
    sections = []
    pattern = r"\[SECTION:(.*?)\](.*?)\[/SECTION\]"
    matches = re.findall(pattern, text_plan, re.DOTALL | re.IGNORECASE)
    
    for title, content in matches:
        title = title.strip()
        content_html = markdown.markdown(
            content.strip(),
            extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
        )
        sections.append({"title": title, "content": content_html})
    
    return sections


def render_plan_html(sections):
    """Convert parsed sections into formatted HTML for display."""
    if not sections:
        return "<p class='muted'>No plan content generated. Please try again.</p>"
    
    html_parts = ['<div class="plan-document">']
    
    for idx, section in enumerate(sections):
        section_class = "plan-section"
        if idx == 0:
            section_class += " first-section"
        
        html_parts.append(f'''
        <div class="{section_class}">
            <h2 class="section-title">{section['title']}</h2>
            <div class="section-content">{section['content']}</div>
        </div>
        ''')
    
    html_parts.append('</div>')
    return "\n".join(html_parts)


def generate_progress_note(session_plan_text, note_type="dap"):
    """Generate a progress note (DAP or SOAP) from a session plan."""
    prompt = DAP_NOTE_PROMPT if note_type.lower() == "dap" else SOAP_NOTE_PROMPT
    
    user_message = f"""Based on this session plan, generate a {note_type.upper()} progress note:

{session_plan_text}

Format professionally and concisely. Focus on clinically relevant documentation."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=2000
        )
        note_content = response.choices[0].message.content
        return markdown.markdown(note_content, extensions=['tables', 'nl2br'])
    except Exception as e:
        app.logger.error(f"Error generating {note_type.upper()} note: {str(e)}")
        return f"<p style='color: #dc3545;'>Error generating {note_type.upper()} note: {str(e)}</p>"


# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        # TODO: Implement real authentication against database
        # For now, mock authentication
        if email and password:
            session['logged_in'] = True
            session['name'] = "Dr. Alex Chen"
            session['email'] = email
            session['profession'] = session.get('profession', 'Counselor')
            session['user_id'] = f"user_{secrets.token_hex(8)}"
            session['credits'] = 50
            session['plans_generated'] = 0
            
            flash('Welcome back! Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Please enter both email and password.', 'error')
    
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User signup."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        # TODO: Implement real user creation with password hashing
        # For now, mock account creation
        if name and email and password:
            session['logged_in'] = True
            session['name'] = name
            session['email'] = email
            session['profession'] = 'Counselor'  # Default
            session['user_id'] = f"user_{secrets.token_hex(8)}"
            session['credits'] = 3  # Free trial credits
            session['plans_generated'] = 0
            session['member_since'] = datetime.now().strftime("%B %Y")
            
            flash('Account created successfully! You have 3 free plan generations.', 'success')
            return redirect(url_for('personalize'))  # Direct to profession selection
        else:
            flash('Please fill out all fields.', 'error')
    
    return render_template("signup.html")


@app.route("/logout")
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route("/faq")
def faq():
    """Frequently asked questions - public page."""
    return render_template("faq.html")


# ============================================================================
# PROTECTED ROUTES
# ============================================================================

@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard."""
    user_data = {
        "name": session.get('name', 'Clinician'),
        "profession": session.get('profession', 'Not Set'),
        "email": session.get('email', 'user@example.com'),
        "credits": session.get('credits', 0),
        "plans_generated": session.get('plans_generated', 0),
        "plan_tier": "Pro" if session.get('credits', 0) > 10 else "Free",
        "member_since": session.get('member_since', 'October 2025')
    }
    
    return render_template("dashboard.html", user=user_data)


@app.route("/generator", methods=["GET", "POST"])
@login_required
def generator():
    """Main session generator page."""
    plan_html = None
    output_style = "balanced"
    profession = session.get('profession', 'Counselor')
    
    # Check if user has credits
    credits = session.get('credits', 0)
    
    if request.method == "POST":
        if credits <= 0:
            flash('You have no remaining credits. Please upgrade your plan.', 'warning')
            return redirect(url_for('billing'))
        
        topic = request.form.get("topic", "").strip()
        modality = request.form.get("modality", "").strip()
        tone = request.form.get("tone", "balanced").strip()
        
        if not topic or not modality:
            flash('Please provide both a topic and modality.', 'error')
        else:
            # Generate the plan
            generated_plan_text = generate_session_plan(topic, modality, tone, profession)
            
            # Parse into sections
            plan_sections = parse_structured_plan(generated_plan_text)
            
            # Render as HTML
            plan_html = render_plan_html(plan_sections)
            
            # Store in session for regeneration and history
            session['last_topic'] = topic
            session['last_modality'] = modality
            session['last_tone'] = tone
            session['last_plan'] = generated_plan_text
            
            # Deduct credit
            session['credits'] = credits - 1
            session['plans_generated'] = session.get('plans_generated', 0) + 1
            
            flash(f'Plan generated successfully! You have {session["credits"]} credits remaining.', 'success')
        
        output_style = tone
    
    return render_template(
        "generator.html",
        plan=plan_html,
        output_style=output_style,
        profession=profession,
        credits=credits
    )


@app.route("/history")
@login_required
def history():
    """Generation history."""
    # TODO: Fetch from database in production
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
        }
    ]
    
    return render_template("history.html", history=generation_history)


@app.route("/billing")
@login_required
def billing():
    """Billing and subscription management."""
    billing_data = {
        "plan": "Pro Tier" if session.get('credits', 0) > 10 else "Free Trial",
        "price": "$29/month",
        "card": "Visa ending in 4242",
        "next_billing_date": "November 6, 2025",
        "credits_remaining": session.get('credits', 0),
        "credits_used_this_month": session.get('plans_generated', 0)
    }
    
    return render_template("billing.html", billing=billing_data)


@app.route("/personalize", methods=["GET", "POST"])
@login_required
def personalize():
    """User personalization settings."""
    if request.method == "POST":
        profession = request.form.get("profession", "Counselor")
        session['profession'] = profession
        flash(f'Clinical lens updated to {profession}.', 'success')
        return redirect(url_for('dashboard'))
    
    current_profession = session.get('profession', 'Counselor')
    return render_template("personalize.html", current_profession=current_profession)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/generate-dap", methods=["POST"])
@login_required
def api_generate_dap():
    """API endpoint to generate DAP note from session plan."""
    data = request.get_json()
    session_plan = data.get("plan_text", "")
    
    if not session_plan:
        return jsonify({"error": "No session plan provided"}), 400
    
    dap_note_html = generate_progress_note(session_plan, note_type="dap")
    return jsonify({"dap_note_html": dap_note_html})


@app.route("/api/generate-soap", methods=["POST"])
@login_required
def api_generate_soap():
    """API endpoint to generate SOAP note from session plan."""
    data = request.get_json()
    session_plan = data.get("plan_text", "")
    
    if not session_plan:
        return jsonify({"error": "No session plan provided"}), 400
    
    soap_note_html = generate_progress_note(session_plan, note_type="soap")
    return jsonify({"soap_note_html": soap_note_html})


@app.route("/export/<export_type>", methods=["POST"])
@login_required
def export_document(export_type):
    """Handle document exports (PDF, DAP, SOAP)."""
    html_content = request.form.get("html", "")
    
    if not html_content:
        return jsonify({"error": "No content to export"}), 400
    
    # TODO: Implement actual PDF generation using WeasyPrint or similar
    # For now, return placeholder response
    return jsonify({
        "status": "not_implemented",
        "message": f"{export_type.upper()} export coming soon",
        "note": "PDF generation requires WeasyPrint or similar library"
    }), 501


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """404 error handler."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler."""
    app.logger.error(f"Server error: {str(e)}")
    return render_template("500.html"), 500


@app.errorhandler(413)
def request_entity_too_large(e):
    """File too large error handler."""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(request.url)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Validate environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("=" * 60)
        print("WARNING: OPENAI_API_KEY environment variable not set!")
        print("The application will not function without a valid API key.")
        print("=" * 60)
    
    # Set Flask secret key warning
    if app.secret_key == os.environ.get('FLASK_SECRET_KEY'):
        print("Using environment secret key")
    else:
        print("WARNING: Using generated secret key. Set FLASK_SECRET_KEY in production!")
    
    # Run application
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(
        debug=debug_mode,
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000))
    )