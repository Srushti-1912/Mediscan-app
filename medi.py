import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import random
import os
from groq import Groq

st.set_page_config(page_title="MediScan AI", page_icon="🏥", layout="wide")

# ─────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────
LANG = {
    "English": {
        "title": "Daily Health Check-in","sleep": "Sleep hours last night",
        "mood": "Mood today (1=very low, 5=great)","symptoms": "Symptoms",
        "meds": "Medication taken today?","meal": "Time of last meal",
        "notes": "Notes (optional)","submit": "Submit",
        "yes": "Yes","no": "No","none": "No medication",
        "sym_display": ["Fever","Headache","Cough","Fatigue","Nausea","Dizziness","Chest pain"],
        "sym_to_eng": {"Fever":"Fever","Headache":"Headache","Cough":"Cough","Fatigue":"Fatigue",
                       "Nausea":"Nausea","Dizziness":"Dizziness","Chest pain":"Chest pain"},
        "saved": "Entry saved!","nlp_hint": "Or describe how you feel in your own words...",
        "nlp_btn": "Auto-detect symptoms","checkin_time": "Check-in time",
    },
    "Hindi": {
        "title": "दैनिक स्वास्थ्य जांच","sleep": "कल रात की नींद (घंटे)",
        "mood": "आज का मूड (1=बहुत खराब, 5=बहुत अच्छा)","symptoms": "लक्षण चुनें",
        "meds": "आज दवाई ली?","meal": "अंतिम भोजन का समय",
        "notes": "नोट्स (वैकल्पिक)","submit": "जमा करें",
        "yes": "हाँ","no": "नहीं","none": "दवाई नहीं",
        "sym_display": ["बुखार","सिरदर्द","खांसी","थकान","मतली","चक्कर","सीने में दर्द"],
        "sym_to_eng": {"बुखार":"Fever","सिरदर्द":"Headache","खांसी":"Cough","थकान":"Fatigue",
                       "मतली":"Nausea","चक्कर":"Dizziness","सीने में दर्द":"Chest pain"},
        "saved": "डेटा सहेजा गया!","nlp_hint": "अपनी तकलीफ अपने शब्दों में लिखें...",
        "nlp_btn": "लक्षण स्वचालित पहचानें","checkin_time": "जांच का समय",
    },
    "Kannada": {
        "title": "ದೈನಂದಿನ ಆರೋಗ್ಯ ತಪಾಸಣೆ","sleep": "ನಿನ್ನೆ ರಾತ್ರಿ ನಿದ್ರೆ (ಗಂಟೆಗಳು)",
        "mood": "ಇಂದಿನ ಮನಸ್ಥಿತಿ (1=ತುಂಬಾ ಕೆಟ್ಟ, 5=ತುಂಬಾ ಒಳ್ಳೆಯದು)","symptoms": "ರೋಗಲಕ್ಷಣಗಳನ್ನು ಆರಿಸಿ",
        "meds": "ಇಂದು ಔಷಧ ತೆಗೆದುಕೊಂಡಿದ್ದೀರಾ?","meal": "ಕೊನೆಯ ಊಟದ ಸಮಯ",
        "notes": "ಟಿಪ್ಪಣಿಗಳು (ಐಚ್ಛಿಕ)","submit": "ಸಲ್ಲಿಸು",
        "yes": "ಹೌದು","no": "ಇಲ್ಲ","none": "ಔಷಧವಿಲ್ಲ",
        "sym_display": ["ಜ್ವರ","ತಲೆನೋವು","ಕೆಮ್ಮು","ಆಯಾಸ","ವಾಕರಿಕೆ","ತಲೆತಿರುಗುವಿಕೆ","ಎದೆ ನೋವು"],
        "sym_to_eng": {"ಜ್ವರ":"Fever","ತಲೆನೋವು":"Headache","ಕೆಮ್ಮು":"Cough","ಆಯಾಸ":"Fatigue",
                       "ವಾಕರಿಕೆ":"Nausea","ತಲೆತಿರುಗುವಿಕೆ":"Dizziness","ಎದೆ ನೋವು":"Chest pain"},
        "saved": "ದಾಖಲೆ ಉಳಿಸಲಾಗಿದೆ!","nlp_hint": "ನಿಮ್ಮ ಭಾವನೆಯನ್ನು ನಿಮ್ಮ ಮಾತುಗಳಲ್ಲಿ ವಿವರಿಸಿ...",
        "nlp_btn": "ಲಕ್ಷಣಗಳನ್ನು ಪತ್ತೆ ಮಾಡಿ","checkin_time": "ತಪಾಸಣೆ ಸಮಯ",
    },
    "Tamil": {
        "title": "தினசரி உடல்நல சோதனை","sleep": "நேற்று இரவு தூக்கம் (மணிநேரம்)",
        "mood": "இன்றைய மனநிலை (1=மிகவும் மோசம், 5=மிகவும் நல்லது)","symptoms": "அறிகுறிகளை தேர்ந்தெடுக்கவும்",
        "meds": "இன்று மருந்து எடுத்தீர்களா?","meal": "கடைசி உணவு நேரம்",
        "notes": "குறிப்புகள் (விருப்பத்தேர்வு)","submit": "சமர்ப்பிக்கவும்",
        "yes": "ஆம்","no": "இல்லை","none": "மருந்தில்லை",
        "sym_display": ["காய்ச்சல்","தலைவலி","இருமல்","சோர்வு","குமட்டல்","தலைச்சுற்றல்","மார்பு வலி"],
        "sym_to_eng": {"காய்ச்சல்":"Fever","தலைவலி":"Headache","இருமல்":"Cough","சோர்வு":"Fatigue",
                       "குமட்டல்":"Nausea","தலைச்சுற்றல்":"Dizziness","மார்பு வலி":"Chest pain"},
        "saved": "தரவு சேமிக்கப்பட்டது!","nlp_hint": "உங்கள் உணர்வை உங்கள் வார்த்தைகளில் விவரிக்கவும்...",
        "nlp_btn": "அறிகுறிகளை கண்டறியவும்","checkin_time": "சோதனை நேரம்",
    },
}

SYM_MAP = {
    "fever":"Fever","temperature":"Fever","hot":"Fever","headache":"Headache","head pain":"Headache",
    "migraine":"Headache","cough":"Cough","coughing":"Cough","fatigue":"Fatigue","tired":"Fatigue",
    "exhausted":"Fatigue","weak":"Fatigue","nausea":"Nausea","nauseous":"Nausea","vomit":"Nausea",
    "dizzy":"Dizziness","dizziness":"Dizziness","chest":"Chest pain","chest pain":"Chest pain",
    "बुखार":"Fever","सिरदर्द":"Headache","थकान":"Fatigue","खांसी":"Cough",
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "health_logs":[],"alerts":[],"chat_history":[],
    "user_baseline":{},"demo_mode":False,
    "user_name":"","caregiver_email":"",
    "caregiver_notified":[],"language":"English",
    "user_age":25,"conditions":[],"gender":"Male",
    "nlp_detected":[],"sos_triggered":False,
    "api_key":"","custom_condition":"",
    "logged_in":False,"role":None,
    "patient_profile":{},"doctor_profile":{},
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

DEMO_LOGS = [
    {"sleep":7,"mood":4,"symptoms":[],"notes":"Felt great","time":"08:00","date":(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d"),"meds_taken":True,"last_meal":"07:30"},
    {"sleep":6,"mood":3,"symptoms":["Headache"],"notes":"Mild headache","time":"09:00","date":(datetime.now()-timedelta(days=5)).strftime("%Y-%m-%d"),"meds_taken":True,"last_meal":"08:00"},
    {"sleep":5,"mood":3,"symptoms":["Headache","Fatigue"],"notes":"Stressful day","time":"10:00","date":(datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d"),"meds_taken":False,"last_meal":"12:00"},
    {"sleep":4,"mood":2,"symptoms":["Fatigue","Cough"],"notes":"Very tired","time":"08:30","date":(datetime.now()-timedelta(days=3)).strftime("%Y-%m-%d"),"meds_taken":False,"last_meal":"09:00"},
    {"sleep":4,"mood":2,"symptoms":["Fever","Fatigue","Headache"],"notes":"Feeling sick","time":"09:00","date":(datetime.now()-timedelta(days=2)).strftime("%Y-%m-%d"),"meds_taken":True,"last_meal":"10:00"},
    {"sleep":5,"mood":2,"symptoms":["Fever","Cough"],"notes":"Still unwell","time":"08:00","date":(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d"),"meds_taken":True,"last_meal":"08:30"},
    {"sleep":6,"mood":3,"symptoms":["Cough"],"notes":"Slightly better","time":"08:00","date":datetime.now().strftime("%Y-%m-%d"),"meds_taken":True,"last_meal":"07:45"},
]

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.stApp{background:#0a0f1e;color:#e0e6f0}
.main .block-container{padding-top:1.5rem}
[data-testid="stSidebar"]{background:#0d1528;border-right:1px solid #1e2d4a}
.stMetric{background:#0d1528;border:1px solid #1e2d4a;border-radius:12px;padding:1rem}
.stMetric label{color:#7a92b5!important;font-size:12px!important}
.stMetric [data-testid="stMetricValue"]{color:#e0e6f0!important}
div[data-testid="stForm"]{background:#0d1528;border:1px solid #1e2d4a;border-radius:16px;padding:1.5rem}
.stButton>button{background:#1a4db5;color:white;border:none;border-radius:8px;font-weight:600;padding:0.5rem 1.2rem}
.stButton>button:hover{background:#1e5cd4}
.stMultiSelect>div{background:#0d1528!important;border:1px solid #1e2d4a!important}
.stTextArea>div>textarea{background:#0d1528!important;border:1px solid #1e2d4a!important;color:#e0e6f0!important}
.stTextInput>div>div>input{background:#0d1528!important;border:1px solid #1e2d4a!important;color:#e0e6f0!important}
.stSelectbox>div>div{background:#0d1528!important}
h1,h2,h3{color:#e0e6f0!important}
.stMarkdown{color:#c0cce0}
.chat-msg-user{background:#1a2d4d;border-radius:12px 12px 2px 12px;padding:10px 14px;margin:6px 0;text-align:right}
.chat-msg-ai{background:#0d1e38;border:1px solid #1e3a5a;border-radius:12px 12px 12px 2px;padding:10px 14px;margin:6px 0}
.sos-box{background:#7f0000;border:2px solid #e74c3c;border-radius:16px;padding:1.5rem;text-align:center;margin:1rem 0}
.streak-box{background:#1a3a1a;border:1px solid #2ecc71;border-radius:10px;padding:0.75rem 1rem;display:inline-block}
.login-card{background:#0d1528;border:1px solid #1e2d4a;border-radius:16px;padding:2rem;max-width:480px;margin:0 auto}
.role-card{background:#0d1528;border:2px solid #1e2d4a;border-radius:16px;padding:2rem;text-align:center;cursor:pointer;transition:border-color 0.2s}
.role-card:hover{border-color:#4C9BE8}
.role-icon{font-size:48px;margin-bottom:1rem}
.doctor-badge{background:#1a3a5a;border:1px solid #4C9BE8;border-radius:8px;padding:4px 10px;font-size:11px;color:#4C9BE8;display:inline-block;margin-bottom:8px}
.patient-badge{background:#1a3a1a;border:1px solid #2ecc71;border-radius:8px;padding:4px 10px;font-size:11px;color:#2ecc71;display:inline-block;margin-bottom:8px}
.health-plan-box{background:#0d1e38;border:1px solid #1e3a5a;border-radius:12px;padding:1.2rem;color:#c0cce0;line-height:1.6;font-size:14px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def extract_symptoms_nlp(text):
    text_lower = text.lower()
    found = set()
    for keyword,symptom in SYM_MAP.items():
        if keyword in text_lower: found.add(symptom)
    return list(found)

def compute_streak(logs):
    if not logs: return 0
    dates = sorted(set(e.get("date","") for e in logs if e.get("date")),reverse=True)
    if not dates: return 0
    streak = 1
    for i in range(1,len(dates)):
        d1=datetime.strptime(dates[i-1],"%Y-%m-%d"); d2=datetime.strptime(dates[i],"%Y-%m-%d")
        if (d1-d2).days==1: streak+=1
        else: break
    return streak

def get_time_weight(log_time):
    try: hour=int(str(log_time).split(":")[0])
    except: hour=9
    if 6<=hour<10: return {"Fatigue":1.8,"Headache":1.2,"Fever":1.5,"Cough":1.0}
    elif 10<=hour<18: return {"Fatigue":1.0,"Headache":1.0,"Fever":1.3,"Cough":1.0}
    else: return {"Fatigue":0.7,"Headache":0.9,"Fever":1.2,"Cough":1.0}

def compute_baseline(logs):
    if len(logs)<3: return {"avg_sleep":7,"avg_mood":3}
    first_half=logs[:max(3,len(logs)//2)]
    return {"avg_sleep":round(sum(e["sleep"] for e in first_half)/len(first_half),1),
            "avg_mood":round(sum(e["mood"] for e in first_half)/len(first_half),1)}

def detect_correlations(logs):
    if len(logs)<4: return []
    findings=[]
    for i in range(2,len(logs)):
        prev2,prev1,curr=logs[i-2],logs[i-1],logs[i]
        if prev2["sleep"]<5 and "Headache" in curr.get("symptoms",[]): findings.append("Poor sleep 2 days ago correlates with today's headache")
        if prev1["mood"]<=2 and curr["sleep"]<5: findings.append("Low mood yesterday may be causing poor sleep today")
        if "Fever" in prev1.get("symptoms",[]) and "Fatigue" in curr.get("symptoms",[]): findings.append("Fatigue today likely linked to yesterday's fever")
    return list(set(findings))

def compute_recovery(logs):
    if len(logs)<2: return None
    recent=logs[-min(7,len(logs)):]
    scores=[max(0,min(100,100-(7-e["sleep"])*5-(3-e["mood"])*10-len(e.get("symptoms",[]))*10)) for e in recent]
    if len(scores)>=2 and scores[-1]>scores[0]: trend,pct="improving",round((scores[-1]-scores[0])/max(1,abs(scores[0]))*100)
    elif len(scores)>=2 and scores[-1]<scores[0]: trend,pct="declining",round((scores[0]-scores[-1])/max(1,abs(scores[0]))*100)
    else: trend,pct="stable",0
    return {"scores":scores,"trend":trend,"pct":pct,"latest":scores[-1]}

def analyze_health(data):
    risk,insights,risk_factors,symptom_count=0,[],[],0
    sleep_values,mood_values=[],[]
    baseline=compute_baseline(data)
    for entry in data:
        sleep_values.append(entry["sleep"]); mood_values.append(entry["mood"])
        symptom_count+=len(entry.get("symptoms",[]))
    if len(sleep_values)>=3 and sleep_values[-1]<sleep_values[-2]<sleep_values[-3]:
        risk+=25; insights.append("Consistent decline in sleep pattern detected")
        risk_factors.append(("Sleep decline",25,"Sleeping less each day for 3+ days"))
    if len(mood_values)>=3 and mood_values[-1]<mood_values[-2]<mood_values[-3]:
        risk+=20; insights.append("Mood deterioration trend observed")
        risk_factors.append(("Mood decline",20,"Mood dropped 3 days in a row"))
    for entry in data:
        tw=get_time_weight(entry.get("time","09:00"))
        if entry["sleep"]<baseline["avg_sleep"]-1.5:
            risk+=15; risk_factors.append(("Below-baseline sleep",15,f"Slept {entry['sleep']}h vs usual {baseline['avg_sleep']}h"))
        if entry["mood"]<baseline["avg_mood"]-1:
            risk+=15; risk_factors.append(("Below-baseline mood",15,f"Mood {entry['mood']}/5 vs usual {baseline['avg_mood']}/5"))
        for sym,base_pts in [("Fever",25),("Headache",10),("Fatigue",20),("Cough",5)]:
            if sym in entry.get("symptoms",[]):
                pts=int(base_pts*tw.get(sym,1.0)); risk+=pts
                risk_factors.append((sym,pts,f"{sym} reported"))
                if sym=="Fever": insights.append("Fever detected - possible infection risk")
                if sym=="Fatigue": insights.append("Fatigue indicates possible burnout")
        if not entry.get("meds_taken",True): risk+=8; risk_factors.append(("Missed medication",8,"Medication not taken"))
    if symptom_count>=4: risk+=20; insights.append("Multiple recurring symptoms detected"); risk_factors.append(("Symptom overload",20,f"{symptom_count} total symptoms"))
    if any(e["sleep"]<5 for e in data) and any(e["mood"]<=2 for e in data):
        risk+=20; insights.append("Low sleep + low mood suggests stress/burnout"); risk_factors.append(("Stress combo",20,"Sleep<5h AND mood<=2 both present"))
    risk=min(risk,100)
    if len(sleep_values)>=3 and len(mood_values)>=3:
        st_val=sleep_values[-1]-sleep_values[-3]; mt=mood_values[-1]-mood_values[-3]
        pred=min(risk+(10 if st_val<-1 else 0)+(10 if mt<-1 else 0),100)
        if pred>risk+5: tomorrow="WARNING: Likely to worsen - trends suggest higher risk tomorrow"
        elif pred<risk-5: tomorrow="GOOD: Trending to improve - stabilising"
        else: tomorrow="STABLE: No major change expected tomorrow"
    else: tomorrow="INFO: Need 3+ entries for prediction"
    if risk>75: diagnosis,diag_color="HIGH RISK - Possible infection or severe fatigue","#e74c3c"
    elif risk>50: diagnosis,diag_color="MODERATE RISK - Health imbalance detected","#f39c12"
    else: diagnosis,diag_color="LOW RISK - Stable condition","#2ecc71"
    seen=set(); unique_factors=[]
    for f in risk_factors:
        if f[0] not in seen: seen.add(f[0]); unique_factors.append(f)
    return {"risk_score":risk,"health_score":max(0,100-risk),"insights":list(set(insights)),
            "diagnosis":diagnosis,"diag_color":diag_color,"alert":risk>70,
            "tomorrow":tomorrow,"risk_factors":unique_factors,"baseline":baseline}

def call_groq(prompt):
    api_key=st.session_state.get("api_key","").strip() or os.environ.get("GROQ_API_KEY","").strip()
    if not api_key: raise ValueError("No API key. Enter Groq API key in sidebar.")
    client=Groq(api_key=api_key)
    response=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"You are a helpful medical assistant."},{"role":"user","content":prompt}],
        temperature=0.7,max_tokens=500)
    return response.choices[0].message.content

def ask_groq_chat(user_msg,data,result):
    gender=st.session_state.get("gender","Not specified")
    prompt=f"""You are MediScan AI, a compassionate health assistant.
PATIENT DATA:
- Name: {st.session_state.user_name}, Age: {st.session_state.user_age}, Gender: {gender}
- Risk Score: {result['risk_score']}/100
- Diagnosis: {result['diagnosis']}
- Insights: {', '.join(result.get('insights',[]))}
- Sleep trend: {[e['sleep'] for e in data]}
- Mood trend: {[e['mood'] for e in data]}
- Symptoms: {list(set(s for e in data for s in e.get('symptoms',[])))}
- Conditions: {', '.join(st.session_state.conditions) or 'None'}
USER QUESTION: {user_msg}
Answer clearly and helpfully in 3-4 sentences. Never diagnose."""
    return call_groq(prompt)

def generate_doctor_note(data,result):
    gender=st.session_state.get("gender","Not specified")
    logs_str="\n".join(f"Day {i+1} ({e.get('date','')}): Sleep={e['sleep']}h, Mood={e['mood']}/5, Symptoms={', '.join(e.get('symptoms',[])) or 'none'}, Meds={'taken' if e.get('meds_taken',True) else 'missed'}" for i,e in enumerate(data[-7:]))
    prompt=f"""Write a formal clinical doctor visit summary note.
Patient: {st.session_state.user_name}, Age {st.session_state.user_age}, Gender: {gender}
Conditions: {', '.join(st.session_state.conditions) or 'None'}
Risk Score: {result['risk_score']}/100 — {result['diagnosis']}
Health Log:\n{logs_str}
Write in professional medical language, third person, under 200 words."""
    return call_groq(prompt)

# ─────────────────────────────────────────────
# GENERATE HEALTH PLAN (fixed location — before it is called in Dashboard)
# ─────────────────────────────────────────────
def generate_health_plan(data, result):
    gender = st.session_state.get("gender", "Not specified")
    conditions = ', '.join(st.session_state.conditions) or 'None'
    symptoms = list(set(s for e in data for s in e.get('symptoms', [])))
    prompt = f"""You are an intelligent health assistant.

Patient condition:
- Name: {st.session_state.user_name}, Age: {st.session_state.user_age}, Gender: {gender}
- Existing conditions: {conditions}
- Risk Score: {result['risk_score']}/100
- Diagnosis: {result['diagnosis']}
- Current Symptoms: {symptoms}
- Sleep trend (last {len(data)} days): {[e['sleep'] for e in data]}
- Mood trend (last {len(data)} days): {[e['mood'] for e in data]}

Based on the above patient data, create a PERSONALISED and COMPLETE simple health plan with:

1. 🥗 Diet Tips (2-3 specific points based on symptoms)
2. 🏃 Exercise Tips (2-3 points suitable for current condition)
3. 😴 Sleep Tips (1-2 points to improve sleep)
4. 🧠 Mental Health Tips (1-2 points based on mood trend)
5. ⚠️ When to See a Doctor (1-2 warning signs to watch for)

Keep it:
- Very simple and practical
- Short bullet points
- Easy to follow in daily life
- Personalised to this patient's data
- No medical diagnosis, only wellness advice

Format clearly with headings and bullet points."""
    return call_groq(prompt)

def draw_radar(data):
    logs=data[-7:]; n=len(logs)
    sleep_score=min(100,round(sum(e["sleep"] for e in logs)/n/8*100))
    mood_score=min(100,round(sum(e["mood"] for e in logs)/n/5*100))
    sym_free=max(0,100-round(sum(len(e.get("symptoms",[])) for e in logs)/n*20))
    med_score=round(sum(1 for e in logs if e.get("meds_taken",True))/n*100)
    consistency=min(100,round(compute_streak(data)/7*100))
    categories=["Sleep","Mood","Symptom-free","Medication","Consistency"]
    values=[sleep_score,mood_score,sym_free,med_score,consistency]
    N=len(categories); angles=[n_/N*2*np.pi for n_ in range(N)]+[0]; vals=values+[values[0]]
    fig,ax=plt.subplots(figsize=(5,5),subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0a0f1e"); ax.set_facecolor("#0d1528")
    ax.plot(angles,vals,color="#4C9BE8",linewidth=2); ax.fill(angles,vals,color="#4C9BE8",alpha=0.25)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(categories,color="#e0e6f0",fontsize=10)
    ax.set_yticks([20,40,60,80,100]); ax.set_yticklabels(["20","40","60","80","100"],color="#7a92b5",fontsize=7)
    ax.tick_params(colors="#7a92b5"); ax.spines["polar"].set_color("#1e2d4a"); ax.grid(color="#1e2d4a",linewidth=0.8)
    plt.title("Wellness Radar",color="#e0e6f0",fontsize=12,pad=15); plt.tight_layout()
    return fig,{"Sleep":sleep_score,"Mood":mood_score,"Symptom-free":sym_free,"Medication":med_score,"Consistency":consistency}

def draw_recovery(recovery):
    scores=recovery["scores"]; fig,ax=plt.subplots(figsize=(7,2.5))
    fig.patch.set_facecolor("#0a0f1e"); ax.set_facecolor("#0d1528")
    x=list(range(1,len(scores)+1))
    cl=["#2ecc71" if s>=60 else "#f39c12" if s>=40 else "#e74c3c" for s in scores]
    for i in range(len(x)-1): ax.plot(x[i:i+2],scores[i:i+2],color=cl[i],linewidth=3)
    ax.scatter(x,scores,color=cl,s=60,zorder=5); ax.fill_between(x,scores,alpha=0.1,color="#4C9BE8")
    ax.set_ylim(0,105); ax.tick_params(colors="#7a92b5")
    for sp in ax.spines.values(): sp.set_edgecolor("#1e2d4a")
    ax.axhline(60,color="#2ecc71",linestyle="--",alpha=0.3,linewidth=1); ax.text(len(x)+0.1,61,"Stable",color="#2ecc71",fontsize=8)
    plt.title("Recovery Tracker",color="#e0e6f0",fontsize=11,pad=8); plt.tight_layout()
    return fig

def draw_risk_breakdown(risk_factors):
    if not risk_factors: return None
    names=[f[0] for f in risk_factors[:7]]; scores=[f[1] for f in risk_factors[:7]]
    colors=["#e74c3c" if s>=20 else "#f39c12" if s>=10 else "#3498db" for s in scores]
    fig,ax=plt.subplots(figsize=(7,max(2.5,len(names)*0.55)))
    fig.patch.set_facecolor("#0a0f1e"); ax.set_facecolor("#0d1528")
    bars=ax.barh(names,scores,color=colors,height=0.55); ax.set_xlim(0,max(scores)*1.35)
    for bar,score in zip(bars,scores):
        ax.text(bar.get_width()+0.5,bar.get_y()+bar.get_height()/2,f"+{score}",va="center",color="#e0e6f0",fontsize=9)
    ax.tick_params(colors="#7a92b5",labelsize=9); ax.invert_yaxis()
    for sp in ax.spines.values(): sp.set_edgecolor("#1e2d4a")
    plt.title("Why am I at risk?",color="#e0e6f0",fontsize=11,pad=8); plt.tight_layout()
    return fig

def draw_heatmap(data):
    hours=list(range(6,24))
    days=[(datetime.now()-timedelta(days=i)).strftime("%a %d") for i in range(min(7,len(data))-1,-1,-1)]
    matrix=np.zeros((len(days),len(hours)))
    for i,entry in enumerate(data[-7:]):
        base=0
        if entry["sleep"]<5: base+=30
        if entry["mood"]<=2: base+=20
        if "Fever" in entry.get("symptoms",[]): base+=30
        if "Fatigue" in entry.get("symptoms",[]): base+=20
        if "Headache" in entry.get("symptoms",[]): base+=10
        for j,h in enumerate(hours):
            f=1.3 if 6<=h<9 else 0.8 if 12<=h<14 else 1.1 if 18<=h<22 else 0.9
            matrix[i][j]=min(100,base*f*random.uniform(0.88,1.12))
    fig,ax=plt.subplots(figsize=(10,3))
    fig.patch.set_facecolor("#0a0f1e"); ax.set_facecolor("#0a0f1e")
    im=ax.imshow(matrix,aspect="auto",cmap=plt.cm.get_cmap("RdYlGn_r"),vmin=0,vmax=100)
    ax.set_xticks(range(len(hours))); ax.set_xticklabels([f"{h}:00" for h in hours],fontsize=8,color="#7a92b5",rotation=45)
    ax.set_yticks(range(len(days))); ax.set_yticklabels(days,fontsize=9,color="#7a92b5")
    ax.tick_params(colors="#7a92b5")
    for sp in ax.spines.values(): sp.set_edgecolor("#1e2d4a")
    cb=plt.colorbar(im,ax=ax,pad=0.01); cb.ax.tick_params(colors="#7a92b5",labelsize=8); cb.set_label("Risk",color="#7a92b5",fontsize=9)
    plt.title("24-Hour Risk Heatmap",color="#e0e6f0",fontsize=11,pad=8); plt.tight_layout()
    return fig

def clean(text):
    return "".join(ch if ord(ch)<128 else "?" for ch in text)

def generate_report(data,result):
    sep="="*54; line="-"*54
    streak=compute_streak(data); recovery=compute_recovery(data); corr=detect_correlations(data)
    gender=st.session_state.get("gender","Not specified")
    lines=[sep,"          MEDISCAN AI - HEALTH REPORT",sep,
           f"  Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
           f"  Patient    : {st.session_state.user_name}",
           f"  Age        : {st.session_state.user_age}",
           f"  Gender     : {gender}",
           f"  Conditions : {', '.join(st.session_state.conditions) or 'None'}",
           f"  Log streak : {streak} day(s)",line,"  SUMMARY",line,
           f"  Risk Score   : {result['risk_score']} / 100",
           f"  Health Score : {result['health_score']} / 100",
           f"  Diagnosis    : {result['diagnosis']}",
           f"  Forecast     : {result['tomorrow']}",
           f"  Baseline     : Sleep {result['baseline']['avg_sleep']}h | Mood {result['baseline']['avg_mood']}/5"]
    if recovery: lines.append(f"  Recovery     : {recovery['trend'].upper()} ({recovery['pct']}% change)")
    lines+=[" ",line,"  AI INSIGHTS",line]
    for i in result["insights"]: lines.append(f"  * {clean(i)}")
    if corr: lines+=[" ",line,"  CORRELATIONS DETECTED",line]; [lines.append(f"  * {clean(c)}") for c in corr]
    lines+=[" ",line,"  RISK FACTOR BREAKDOWN",line,f"  {'Factor':<30} | Pts | Reason","  "+"-"*50]
    for name,pts,reason in result["risk_factors"]: lines.append(f"  {name[:28]:<30} | +{pts:3d} | {clean(reason)}")
    lines+=[" ",line,"  DAILY LOG HISTORY",line,f"  {'Day':<4} {'Date':<12} {'Sleep':<7} {'Mood':<6} {'Meds':<5} Symptoms","  "+"-"*52]
    for idx,e in enumerate(data,1):
        syms=", ".join(e.get("symptoms",[])) or "None"; meds="Yes" if e.get("meds_taken",True) else "No"
        lines.append(f"  {idx:<4} {e.get('date',''):<12} {str(e['sleep'])+'h':<7} {str(e['mood'])+'/5':<6} {meds:<5} {syms}")
    lines+=[" ",sep,"  Share this report with your doctor.","  MediScan AI does not replace medical advice.",sep]
    return "\n".join(lines)

# ═══════════════════════════════════════════════
# LOGIN / REGISTER PAGES
# ═══════════════════════════════════════════════
if not st.session_state.logged_in:

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
        <div style="font-size:48px;margin-bottom:0.5rem">🏥</div>
        <h1 style="color:#e0e6f0;font-size:32px;margin:0">MediScan AI</h1>
        <p style="color:#7a92b5;margin-top:8px">Context-Aware Health Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

    if "login_role" not in st.session_state:
        st.session_state.login_role = None

    if st.session_state.login_role is None:
        st.markdown("<h3 style='text-align:center;color:#e0e6f0;margin-bottom:1.5rem'>Who are you?</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div style="background:#0d1528;border:2px solid #2ecc71;border-radius:16px;padding:2rem;text-align:center;">
                <div style="font-size:52px;margin-bottom:0.75rem">🧑‍⚕️</div>
                <div style="background:#1a3a1a;border:1px solid #2ecc71;border-radius:8px;padding:4px 10px;font-size:11px;color:#2ecc71;display:inline-block;margin-bottom:8px">PATIENT</div>
                <h3 style="color:#e0e6f0;margin:8px 0">I am a Patient</h3>
                <p style="color:#7a92b5;font-size:13px">Log symptoms, track health, get AI insights</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Patient", use_container_width=True, key="btn_patient"):
                st.session_state.login_role = "patient"
                st.rerun()

        with col2:
            st.markdown("""
            <div style="background:#0d1528;border:2px solid #4C9BE8;border-radius:16px;padding:2rem;text-align:center;">
                <div style="font-size:52px;margin-bottom:0.75rem">👨‍⚕️</div>
                <div style="background:#1a3a5a;border:1px solid #4C9BE8;border-radius:8px;padding:4px 10px;font-size:11px;color:#4C9BE8;display:inline-block;margin-bottom:8px">DOCTOR</div>
                <h3 style="color:#e0e6f0;margin:8px 0">I am a Doctor</h3>
                <p style="color:#7a92b5;font-size:13px">View patient alerts, generate clinical notes</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Doctor", use_container_width=True, key="btn_doctor"):
                st.session_state.login_role = "doctor"
                st.rerun()

    elif st.session_state.login_role == "patient":
        st.markdown("<h3 style='text-align:center;color:#e0e6f0;margin-bottom:1.5rem'>🧑‍⚕️ Patient Registration</h3>", unsafe_allow_html=True)

        col_center, = [st.columns([1,2,1])[1]]
        with col_center:
            with st.form("patient_login_form"):
                st.markdown('<p style="color:#2ecc71;font-weight:600;margin-bottom:1rem">Personal Information</p>', unsafe_allow_html=True)

                full_name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
                email     = st.text_input("Email Address *", placeholder="e.g. priya@email.com")

                c1, c2 = st.columns(2)
                with c1:
                    age = st.number_input("Age *", min_value=1, max_value=120, value=25)
                with c2:
                    gender = st.radio("Gender *", ["Male","Female","Other"], horizontal=True)

                phone = st.text_input("Phone Number", placeholder="+91 XXXXX XXXXX")

                st.markdown('<p style="color:#2ecc71;font-weight:600;margin:1rem 0 0.5rem">Medical Information</p>', unsafe_allow_html=True)

                CONDITION_LIST=["Diabetes","Hypertension","Asthma","Heart disease","Thyroid","Cancer","Kidney disease","Liver disease"]
                conditions = st.multiselect("Existing conditions", CONDITION_LIST)
                custom_cond = st.text_input("Other condition (not in list)", placeholder="e.g. Lupus, Crohn's disease...")
                caregiver_email = st.text_input("Emergency contact email", placeholder="caregiver@email.com")
                blood_group = st.selectbox("Blood Group", ["Not specified","A+","A-","B+","B-","AB+","AB-","O+","O-"])

                st.markdown('<p style="color:#2ecc71;font-weight:600;margin:1rem 0 0.5rem">Preferences</p>', unsafe_allow_html=True)
                language = st.selectbox("Preferred Language", list(LANG.keys()))

                submitted = st.form_submit_button("Register & Enter →", use_container_width=True)

            if submitted:
                if not full_name.strip() or not email.strip():
                    st.error("Please fill in Name and Email.")
                else:
                    all_conditions = conditions.copy()
                    if custom_cond.strip(): all_conditions.append(custom_cond.strip())
                    st.session_state.logged_in = True
                    st.session_state.role = "patient"
                    st.session_state.user_name = full_name.strip()
                    st.session_state.user_age = age
                    st.session_state.gender = gender
                    st.session_state.conditions = all_conditions
                    st.session_state.caregiver_email = caregiver_email
                    st.session_state.language = language
                    st.session_state.custom_condition = custom_cond
                    st.session_state.patient_profile = {
                        "name": full_name.strip(), "email": email.strip(),
                        "age": age, "gender": gender, "phone": phone,
                        "conditions": all_conditions, "blood_group": blood_group,
                        "caregiver_email": caregiver_email, "language": language,
                    }
                    st.rerun()

        if st.button("← Back"):
            st.session_state.login_role = None
            st.rerun()

    elif st.session_state.login_role == "doctor":
        st.markdown("<h3 style='text-align:center;color:#e0e6f0;margin-bottom:1.5rem'>👨‍⚕️ Doctor Registration</h3>", unsafe_allow_html=True)

        col_center, = [st.columns([1,2,1])[1]]
        with col_center:
            with st.form("doctor_login_form"):
                st.markdown('<p style="color:#4C9BE8;font-weight:600;margin-bottom:1rem">Personal Information</p>', unsafe_allow_html=True)

                full_name  = st.text_input("Full Name *", placeholder="e.g. Dr. Ravi Kumar")
                email      = st.text_input("Email Address *", placeholder="e.g. dr.ravi@hospital.com")

                c1, c2 = st.columns(2)
                with c1:
                    age = st.number_input("Age", min_value=25, max_value=80, value=35)
                with c2:
                    gender = st.radio("Gender", ["Male","Female","Other"], horizontal=True)

                phone = st.text_input("Phone Number", placeholder="+91 XXXXX XXXXX")

                st.markdown('<p style="color:#4C9BE8;font-weight:600;margin:1rem 0 0.5rem">Professional Information</p>', unsafe_allow_html=True)

                specialization = st.selectbox("Specialization *", [
                    "General Physician","Cardiologist","Neurologist","Endocrinologist",
                    "Pulmonologist","Gastroenterologist","Oncologist","Nephrologist",
                    "Psychiatrist","Dermatologist","Orthopedist","Pediatrician","Other"
                ])
                other_spec = st.text_input("Other specialization (if not listed)", placeholder="e.g. Sports Medicine")

                hospital    = st.text_input("Hospital / Clinic Name *", placeholder="e.g. Apollo Hospital, Bengaluru")
                reg_number  = st.text_input("Medical Registration Number *", placeholder="e.g. MCI-12345")
                experience  = st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
                consult_fee = st.text_input("Consultation Fee (INR)", placeholder="e.g. 500")

                st.markdown('<p style="color:#4C9BE8;font-weight:600;margin:1rem 0 0.5rem">Availability</p>', unsafe_allow_html=True)
                available_days = st.multiselect("Available Days", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                    default=["Monday","Tuesday","Wednesday","Thursday","Friday"])
                consult_hours = st.text_input("Consultation Hours", placeholder="e.g. 9:00 AM - 5:00 PM")

                submitted = st.form_submit_button("Register & Enter →", use_container_width=True)

            if submitted:
                if not full_name.strip() or not email.strip() or not hospital.strip() or not reg_number.strip():
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    final_spec = other_spec.strip() if other_spec.strip() and specialization == "Other" else specialization
                    st.session_state.logged_in = True
                    st.session_state.role = "doctor"
                    st.session_state.user_name = full_name.strip()
                    st.session_state.user_age = age
                    st.session_state.gender = gender
                    st.session_state.doctor_profile = {
                        "name": full_name.strip(), "email": email.strip(),
                        "age": age, "gender": gender, "phone": phone,
                        "specialization": final_spec, "hospital": hospital.strip(),
                        "reg_number": reg_number.strip(), "experience": experience,
                        "consult_fee": consult_fee, "available_days": available_days,
                        "consult_hours": consult_hours,
                    }
                    st.rerun()

        if st.button("← Back"):
            st.session_state.login_role = None
            st.rerun()

    st.stop()

# ═══════════════════════════════════════════════
# MAIN APP (after login)
# ═══════════════════════════════════════════════

# ── SIDEBAR ──
st.sidebar.markdown("## MediScan AI")
st.sidebar.markdown("---")

role = st.session_state.role
profile = st.session_state.doctor_profile if role=="doctor" else st.session_state.patient_profile
if role == "doctor":
    st.sidebar.markdown(f'<div style="background:#1a3a5a;border:1px solid #4C9BE8;border-radius:10px;padding:10px 14px;margin-bottom:8px"><div style="color:#4C9BE8;font-size:11px;font-weight:600">DOCTOR</div><div style="color:#e0e6f0;font-weight:600">{profile.get("name","")}</div><div style="color:#7a92b5;font-size:12px">{profile.get("specialization","")}</div><div style="color:#7a92b5;font-size:11px">{profile.get("hospital","")}</div></div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<div style="background:#1a3a1a;border:1px solid #2ecc71;border-radius:10px;padding:10px 14px;margin-bottom:8px"><div style="color:#2ecc71;font-size:11px;font-weight:600">PATIENT</div><div style="color:#e0e6f0;font-weight:600">{profile.get("name","")}</div><div style="color:#7a92b5;font-size:12px">Age {profile.get("age","")} · {profile.get("gender","")}</div><div style="color:#7a92b5;font-size:11px">{profile.get("email","")}</div></div>', unsafe_allow_html=True)

if st.sidebar.button("Load Demo Data"):
    st.session_state.health_logs=DEMO_LOGS.copy(); st.session_state.demo_mode=True
    st.sidebar.success("Demo data loaded!")
if st.session_state.demo_mode: st.sidebar.success("Demo mode active")

if role == "patient":
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Language / भाषा / ಭಾಷೆ**")
    st.session_state.language=st.sidebar.selectbox("Language",list(LANG.keys()),
        index=list(LANG.keys()).index(st.session_state.language),label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("**API Settings**")
api_input=st.sidebar.text_input("Groq API Key",value=st.session_state.api_key,type="password",placeholder="gsk_...")
if api_input.strip(): st.session_state.api_key=api_input.strip()
if st.session_state.api_key or os.environ.get("GROQ_API_KEY",""):
    st.sidebar.success("Groq API key set ✓")
else:
    st.sidebar.warning("Enter Groq API key for AI features")

if st.session_state.health_logs:
    streak=compute_streak(st.session_state.health_logs)
    if streak>=3: st.sidebar.markdown(f'<div class="streak-box">🔥 {streak}-day streak!</div>',unsafe_allow_html=True)
    elif streak>0: st.sidebar.info(f"Day {streak} streak — keep going!")

st.sidebar.markdown("---")
if st.session_state.health_logs:
    st.sidebar.metric("Entries",len(st.session_state.health_logs))
    if st.sidebar.button("Clear all data"):
        for k in ["health_logs","alerts","chat_history","caregiver_notified"]:
            st.session_state[k]=[]
        st.session_state.demo_mode=False; st.rerun()

if st.sidebar.button("🚪 Logout"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

if role == "doctor":
    page=st.sidebar.radio("Navigate",["Doctor Panel","Doctor Tools","Risk Heatmap"])
else:
    page=st.sidebar.radio("Navigate",[
        "Daily Check-in","Dashboard","Risk Heatmap",
        "AI Health Chat","Doctor Tools","Doctor Panel","SOS Emergency"])

T=LANG[st.session_state.language]

# ══════════════════════════════════════
# PAGE: DAILY CHECK-IN (patient only)
# ══════════════════════════════════════
if page=="Daily Check-in":
    st.title(f"📋 {T['title']}")
    st.markdown(f"Hello **{st.session_state.user_name}** ({st.session_state.gender}, Age {st.session_state.user_age})")
    st.markdown("---")
    nlp_text=st.text_area(T["nlp_hint"],height=70,key="nlp_input")
    if st.button(T["nlp_btn"]):
        detected=extract_symptoms_nlp(nlp_text)
        if detected:
            st.session_state.nlp_detected=detected
            detected_display=[disp for eng in detected for disp,e in T["sym_to_eng"].items() if e==eng]
            st.success(f"Detected: {', '.join(detected_display or detected)}")
        else: st.info("No symptoms detected — fill in manually below.")
    st.markdown("---")
    nlp_defaults_display=[disp for eng_sym in st.session_state.nlp_detected for disp,eng in T["sym_to_eng"].items() if eng==eng_sym]
    with st.form("health_form"):
        c1,c2=st.columns(2)
        with c1:
            sleep=st.slider(T["sleep"],0,12,7)
            mood=st.slider(T["mood"],1,5,3)
            log_time=st.time_input(T["checkin_time"],value=datetime.now().time())
        with c2:
            valid_defaults=[s for s in nlp_defaults_display if s in T["sym_display"]]
            symptoms_display=st.multiselect(T["symptoms"],T["sym_display"],default=valid_defaults)
            meds_ans=st.radio(T["meds"],[T["yes"],T["no"],T["none"]],horizontal=True)
            last_meal=st.text_input(T["meal"],"08:00")
        notes=st.text_area(T["notes"],height=70)
        submitted=st.form_submit_button(T["submit"])
    if submitted:
        symptoms_english=[T["sym_to_eng"].get(s,s) for s in symptoms_display]
        entry={"sleep":sleep,"mood":mood,"symptoms":symptoms_english,"symptoms_display":symptoms_display,
               "meds_taken":meds_ans==T["yes"],"last_meal":last_meal,"notes":notes,
               "time":str(log_time)[:5],"date":datetime.now().strftime("%Y-%m-%d"),"language":st.session_state.language}
        st.session_state.health_logs.append(entry); st.session_state.nlp_detected=[]
        st.success(f"✅ {T['saved']} (Entry #{len(st.session_state.health_logs)})")
        if len(st.session_state.health_logs)>=2:
            r=analyze_health(st.session_state.health_logs)
            if r["risk_score"]>70: st.error(f"High risk detected ({r['risk_score']}/100) — check Dashboard.")

# ══════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════
elif page=="Dashboard":
    st.title("📊 Health Dashboard"); st.markdown("---")
    data=st.session_state.health_logs
    if not data: st.warning("No data — log entries or load Demo Data from sidebar."); st.stop()

    result=analyze_health(data); df=pd.DataFrame(data)
    streak=compute_streak(data); recovery=compute_recovery(data); corrs=detect_correlations(data)

    if streak>=3:
        st.markdown(f'<div class="streak-box">🔥 {streak}-day check-in streak!</div><br>',unsafe_allow_html=True)

    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Risk Score",f"{result['risk_score']}/100")
    c2.metric("Health Score",f"{result['health_score']}/100")
    c3.metric("Entries",len(data))
    c4.metric("Avg Sleep",f"{round(sum(e['sleep'] for e in data)/len(data),1)}h")
    c5.metric("Streak",f"{streak} days")

    st.markdown("---")

    col_d,col_f=st.columns(2)
    with col_d:
        st.subheader("Diagnosis")
        color=result.get("diag_color","#aaa")
        st.markdown(f'<div style="background:{color}22;border-left:4px solid {color};padding:10px 14px;border-radius:4px;color:#e0e6f0;">{result["diagnosis"]}</div>',unsafe_allow_html=True)

    with col_f:
        st.subheader("Tomorrow's Forecast")
        st.warning(result["tomorrow"])

    st.caption(f"Baseline: Sleep {result['baseline']['avg_sleep']}h | Mood {result['baseline']['avg_mood']}/5")

    st.markdown("---")

    if result["insights"]:
        st.subheader("AI Insights")
        for i in result["insights"]:
            st.write(f"• {i}")

    # ── SMART HEALTH PLAN ──
    st.markdown("---")
    st.subheader("🧠 Smart Health Plan")
    st.markdown("*Personalised wellness tips based on your health data*")

    if st.session_state.api_key or os.environ.get("GROQ_API_KEY",""):
        if st.button("🔄 Generate My Health Plan", key="gen_plan_btn"):
            with st.spinner("Generating your personalised health plan..."):
                try:
                    plan = generate_health_plan(data, result)
                    st.session_state["health_plan_cache"] = plan
                except Exception as e:
                    st.error(f"Error generating plan: {e}")

        if "health_plan_cache" in st.session_state and st.session_state["health_plan_cache"]:
            formatted_plan = st.session_state["health_plan_cache"].replace("\n", "<br>")
            st.markdown(f'<div class="health-plan-box">{formatted_plan}</div>', unsafe_allow_html=True)
        else:
            st.info("Click the button above to generate your personalised health plan.")
    else:
        st.info("Enter Groq API key in sidebar to get your AI-powered health plan.")

# ══════════════════════════════════════
# PAGE: RISK HEATMAP
# ══════════════════════════════════════
elif page=="Risk Heatmap":
    st.title("🔥 24-Hour Risk Heatmap"); st.markdown("---")
    data=st.session_state.health_logs
    if not data: st.warning("No data yet."); st.stop()
    fig=draw_heatmap(data); st.pyplot(fig); plt.close(fig)
    st.markdown("**Red** = high risk | **Yellow** = moderate | **Green** = low risk")

# ══════════════════════════════════════
# PAGE: AI HEALTH CHAT
# ══════════════════════════════════════
elif page=="AI Health Chat":
    st.title("🤖 AI Health Chat"); st.markdown("---")
    data=st.session_state.health_logs
    if not data: st.warning("Log health data first."); st.stop()
    if not st.session_state.api_key: st.warning("Enter your Groq API key in the sidebar first."); st.stop()
    result=analyze_health(data)
    for msg in st.session_state.chat_history:
        if msg["role"]=="user": st.markdown(f'<div class="chat-msg-user">You: {msg["content"]}</div>',unsafe_allow_html=True)
        else: st.markdown(f'<div class="chat-msg-ai">MediScan AI: {msg["content"]}</div>',unsafe_allow_html=True)
    st.markdown("**Suggested questions:**")
    suggestions=["Why do I feel tired?","What's causing my high risk?","How can I improve my sleep?","Should I see a doctor?","What patterns do you see in my data?"]
    cols=st.columns(len(suggestions))
    for i,sug in enumerate(suggestions):
        if cols[i].button(sug,key=f"sug_{i}"):
            with st.spinner("Thinking..."):
                try:
                    reply=ask_groq_chat(sug,data,result)
                    st.session_state.chat_history.append({"role":"user","content":sug})
                    st.session_state.chat_history.append({"role":"assistant","content":reply})
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    with st.form("chat_form",clear_on_submit=True):
        user_input=st.text_input("Type your question...",placeholder="e.g. Why am I at risk?")
        send=st.form_submit_button("Send")
    if send and user_input.strip():
        with st.spinner("MediScan AI is thinking..."):
            try:
                reply=ask_groq_chat(user_input,data,result)
                st.session_state.chat_history.append({"role":"user","content":user_input})
                st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.chat_history:
        if st.button("Clear chat"): st.session_state.chat_history=[]; st.rerun()

# ══════════════════════════════════════
# PAGE: DOCTOR TOOLS
# ══════════════════════════════════════
elif page=="Doctor Tools":
    st.title("🩺 Doctor Tools"); st.markdown("---")
    if role == "doctor":
        dp = st.session_state.doctor_profile
        st.info(f"Logged in as **Dr. {dp.get('name','')}** — {dp.get('specialization','')} | {dp.get('hospital','')}")
    data=st.session_state.health_logs
    if not data: st.warning("No patient data. Load Demo Data from sidebar."); st.stop()
    if not st.session_state.api_key: st.warning("Enter your Groq API key in the sidebar first."); st.stop()
    result=analyze_health(data)
    st.subheader("AI Doctor Visit Note")
    st.markdown("Generates a professional clinical summary.")
    if st.button("Generate Doctor Note"):
        with st.spinner("Writing clinical summary..."):
            try:
                note=generate_doctor_note(data,result)
                st.markdown(f'<div style="background:#0d1e38;border:1px solid #1e3a5a;border-radius:12px;padding:1.2rem;color:#c0cce0;font-family:monospace;font-size:13px;line-height:1.7;">{note}</div>',unsafe_allow_html=True)
                st.download_button("Download Note (.txt)",data=note.encode("ascii",errors="replace"),
                    file_name=f"DoctorNote_{datetime.now().strftime('%Y%m%d')}.txt",mime="text/plain")
            except Exception as e: st.error(f"Error: {e}")
    st.markdown("---"); st.subheader("Pattern Correlations")
    corrs=detect_correlations(data)
    if corrs:
        for c in corrs: st.info(f"🔗 {c}")
    else: st.success("No notable correlations yet. Log more entries.")

# ══════════════════════════════════════
# PAGE: DOCTOR PANEL
# ══════════════════════════════════════
elif page=="Doctor Panel":
    st.title("👨‍⚕️ Doctor Dashboard"); st.markdown("---")
    if role == "doctor":
        dp = st.session_state.doctor_profile
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Specialization", dp.get("specialization",""))
        c2.metric("Hospital", dp.get("hospital","")[:15]+"..." if len(dp.get("hospital",""))>15 else dp.get("hospital",""))
        c3.metric("Experience", f"{dp.get('experience',0)} yrs")
        c4.metric("Reg. No.", dp.get("reg_number",""))
        st.markdown("---")
    data=st.session_state.health_logs; alerts=st.session_state.alerts
    if data:
        result=analyze_health(data); c1,c2,c3=st.columns(3)
        c1.metric("Patient Risk Score",f"{result['risk_score']}/100")
        c2.metric("Health Score",f"{result['health_score']}/100")
        c3.metric("Entries",len(data)); st.markdown("---")
    if not alerts: st.success("No high-risk alerts. Patient is stable.")
    else:
        st.error(f"{len(alerts)} High-Risk Alert(s)")
        for i,alert in enumerate(alerts):
            with st.expander(f"Alert {i+1} — Risk: {alert['risk_score']}/100 — {alert['date']}",expanded=(i==len(alerts)-1)):
                c1,c2=st.columns(2)
                c1.metric("Risk Score",f"{alert['risk_score']}/100"); c2.write(f"**Status:** {alert['message']}")
                if data and i==len(alerts)-1:
                    r2=analyze_health(data); st.write("**Key concerns:**")
                    for name,pts,reason in r2["risk_factors"][:4]: st.write(f"  • {name}: {reason}")
                    st.write(f"**Forecast:** {r2['tomorrow']}")
                if st.button("Contact Patient",key=f"contact_{i}"): st.success(f"Doctor contacting {st.session_state.user_name}...")
                if st.button("Request More Tests",key=f"tests_{i}"): st.info("Test request logged.")
    if data:
        st.markdown("---"); st.subheader("Full Log History")
        df_show=pd.DataFrame(data)[["date","sleep","mood","symptoms","meds_taken","notes"]].copy()
        df_show["symptoms"]=df_show["symptoms"].apply(lambda x:", ".join(x) if x else "None")
        st.dataframe(df_show,use_container_width=True)

# ══════════════════════════════════════
# PAGE: SOS EMERGENCY
# ══════════════════════════════════════
elif page=="SOS Emergency":
    st.title("🆘 Emergency SOS"); st.markdown("---")
    data=st.session_state.health_logs
    if data:
        result=analyze_health(data); last=data[-1]; syms=", ".join(last.get("symptoms",[])) or "None"
    else:
        result={"risk_score":0,"diagnosis":"No data"}; last={}; syms="Unknown"
    risk_score=result.get("risk_score",0)
    if risk_score<=70:
        st.success(f"Your current risk score is {risk_score}/100 — no emergency alert needed.")
        st.info("SOS activates only when risk score exceeds 70/100.")
        st.markdown("**To test:** Load Demo Data from the sidebar."); st.stop()
    st.error(f"HIGH RISK DETECTED — Risk Score: {risk_score}/100")
    sos_msg=f"""MEDICAL EMERGENCY ALERT
Patient: {st.session_state.user_name}
Age: {st.session_state.user_age}
Gender: {st.session_state.get('gender','Not specified')}
Existing conditions: {', '.join(st.session_state.conditions) or 'None'}

CURRENT HEALTH STATUS:
Risk Score: {result['risk_score']}/100
Diagnosis: {result['diagnosis']}
Last reported symptoms: {syms}
Last check-in: {last.get('date','Unknown')}
Sleep last night: {last.get('sleep','?')}h
Mood: {last.get('mood','?')}/5
Caregiver contact: {st.session_state.caregiver_email or 'Not set'}

PLEASE SEND HELP IMMEDIATELY."""
    st.markdown('<div class="sos-box">',unsafe_allow_html=True)
    st.code(sos_msg)
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("Call 112 (India)",use_container_width=True): st.error("Calling 112 — Emergency Services")
    with c2:
        if st.button("Call 108 (Ambulance)",use_container_width=True): st.error("Calling 108 — Ambulance")
    with c3:
        st.download_button("Copy SOS Message",data=sos_msg.encode("ascii",errors="replace"),
            file_name="SOS_Emergency.txt",mime="text/plain",use_container_width=True)
    st.markdown("---")
    st.warning("This is a demo app. In a real emergency always call your local emergency number directly.")
