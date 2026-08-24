import streamlit as st
from src.config import OPENAI_API_KEY, GENDER_OPTIONS, DURATION_OPTIONS, LANGUAGE_OPTIONS, SYMPTOMS_LIST, MEDICAL_DISCLAIMER
from src.cache_manager import initialize_cache
from src.chains import get_llm, generate_assessment, stream_narrative
from src.utils import safe_parse_json

# 1. UI Configuration
st.set_page_config(page_title="MediGuide AI", layout="wide")

# 2. Sidebar
with st.sidebar:
    st.title("MediGuide AI")
    st.warning(MEDICAL_DISCLAIMER)
    api_key = st.text_input("OpenAI API Key", value=OPENAI_API_KEY, type="password")
    cache_type = st.radio("Cache Type", ["InMemoryCache", "SQLiteCache"])
    language = st.selectbox("Language", LANGUAGE_OPTIONS)

# 3. Main Form
st.title("Patient Symptom Assessment")
st.error(MEDICAL_DISCLAIMER)

with st.form("patient_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.text_input("Age", "25")
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