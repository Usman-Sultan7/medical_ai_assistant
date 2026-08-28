import streamlit as st
from src.config import OPENAI_API_KEY, GENDER_OPTIONS, DURATION_OPTIONS, LANGUAGE_OPTIONS, SYMPTOMS_LIST, MEDICAL_DISCLAIMER
from src.cache_manager import initialize_cache
from src.chains import get_llm, generate_assessment, stream_narrative
from src.utils import safe_parse_json

import streamlit as st

# 1. Check if the user has already entered their API key in this session
if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False

if not st.session_state.api_key_entered:
    # --- BEAUTIFUL AUTHENTICATION SCREEN ---
    
    # Center-aligned headers using HTML/Markdown
    st.markdown(
        """
        <h1 style='text-align: center;'>🩺 MediGuide AI</h1>
        <p style='text-align: center; color: #666666; font-size: 18px;'>
            AI-Powered Medical Symptom Assessment & Patient Guidance
        </p>
        <br><br>
        """, 
        unsafe_allow_html=True
    )
    
    # Use columns to create a centered "card" in the middle of the screen
    # The ratio [1, 1.5, 1] means the middle column is slightly wider than the edges
    left_spacer, center_column, right_spacer = st.columns([1, 1.5, 1])
    
    with center_column:
        st.markdown("### 🔐 Enter OpenAI API Key")
        
        # The input field
        user_key = st.text_input(
            label="OpenAI API Key",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed" # Hides the small label since we have the big heading
        )
        
        st.caption("Your API key is used strictly for this session and is not saved.")
        
        # The prominent continue button
        if st.button("Continue ➔", type="primary", use_container_width=True):
            if user_key.startswith("sk-"): # Basic validation
                st.session_state.api_key = user_key
                st.session_state.api_key_entered = True
                st.rerun() # Instantly refresh the page to show the main app
            else:
                st.error("Please enter a valid OpenAI API key (starts with 'sk-').")
                
    # Stop the rest of the app from running until this screen is passed
    st.stop()

# ==========================================
# --- MAIN DASHBOARD INTERFACE GOES HERE ---
# ==========================================
# (Everything below this line only runs AFTER they click Continue)

# You can access the key anywhere below using: st.session_state.api_key

st.sidebar.title("MediGuide Settings")
st.sidebar.success("API Key Provided!")
# ... the rest of your app code ...

with st.sidebar:
    st.title("MediGuide AI")
    st.warning(MEDICAL_DISCLAIMER)
    
    # REPLACED LINE: Pull the key from the landing page instead of asking again
    api_key = st.session_state.api_key 
    
    cache_type = st.radio("Cache Type", ["InMemoryCache", "SQLiteCache"])
    language = st.selectbox("Language", LANGUAGE_OPTIONS)
    
if not api_key:
    st.info("👈 Please enter your OpenAI API Key in the sidebar to access the assessment form.")
    st.stop()

# 3. Main Form
st.title("Patient Symptom Assessment")
st.error(MEDICAL_DISCLAIMER)

with st.form("patient_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.text_input("Age", "0")
        gender = st.selectbox("Gender", GENDER_OPTIONS)
        duration = st.selectbox("Duration of Symptoms", DURATION_OPTIONS)
    with col2:
        symptoms = st.multiselect("Symptoms", SYMPTOMS_LIST)
        severity = st.slider("Severity", 1, 10, 5)
    
    conditions = st.text_area("Existing Medical Conditions")
    medications = st.text_area("Current Medications")
    notes = st.text_area("Additional Notes")
    
    submitted = st.form_submit_button("Analyze Symptoms")

# 4. Processing and Output
if submitted:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not symptoms:
        st.error("Please select at least one symptom.")
    else:
        initialize_cache(cache_type)
        llm = get_llm(api_key)
        
        inputs = {
            "age": age, "gender": gender, "symptoms": ", ".join(symptoms),
            "duration": duration, "severity": severity,
            "conditions": conditions or "None", "medications": medications or "None",
            "notes": notes or "None", "language": language
        }
        
        st.divider()
        st.subheader("Live Guidance Narrative")
        # Streaming text live to the UI
        st.write_stream(stream_narrative(llm, inputs))
        
        st.divider()
        st.subheader("Structured Assessment Dashboard")
        
        with st.spinner("Analyzing structured data..."):
            raw_json = generate_assessment(llm, inputs)
            data = safe_parse_json(raw_json)
        
        # Displaying the parsed JSON data
        urgency = data.get("urgency_level", "UNKNOWN").upper()
        if urgency == "LOW":
            st.success(f"Urgency Level: {urgency}")
        elif urgency == "EMERGENCY":
            st.error(f"🚨 Urgency Level: {urgency} - SEEK IMMEDIATE HELP")
        else:
            st.warning(f"Urgency Level: {urgency}")
            
        st.metric(label="Summary", value="Patient Profile", delta=f"Severity: {severity}/10")
        st.write(data.get("summary", ""))
        
        # Tabs for clean layout
        tab1, tab2, tab3 = st.tabs(["Possible Conditions", "Next Steps", "Questions for Doctor"])
        
        with tab1:
            for condition in data.get("possible_conditions", []):
                with st.expander(condition.get("name", "Condition")):
                    st.write(condition.get("reason", ""))
        with tab2:
            for step in data.get("recommended_next_steps", []):
                st.write(f"- {step}")
        with tab3:
            for question in data.get("questions_for_doctor", []):
                st.write(f"- {question}")
                
        if data.get("warning_signs"):
            st.error("### Warning Signs")
            for sign in data.get("warning_signs", []):
                st.write(f"- {sign}")