import streamlit as st
import pdfplumber
import openai
import pandas as pd
import json
import time

# Set page config
st.set_page_config(
    page_title="The SEO Works AI Bot",  
    page_icon="https://www.seoworks.co.uk/wp-content/themes/seoworks/assets/images/fav.png", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# Secure API Key Retrieval
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Retrieve key securely
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Function to interact with OpenAI API
def call_openai_api(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a Google Ads performance analyst."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Sidebar for file upload & help info
st.sidebar.header("Upload your PDF here")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf"])

st.sidebar.markdown("""
---
### How to Use:
1️⃣ Upload a **Google Ads Report (PDF)**  
2️⃣ AI will extract & analyse the data  
3️⃣ You can **refine the insights** using additional prompts  
""")

if uploaded_file:
    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully ({uploaded_file.size/1024:.2f} KB)")

    # Extract text from PDF
    with pdfplumber.open(uploaded_file) as pdf:
        raw_text = pdf.pages[1].extract_text() if len(pdf.pages) > 1 else None

    if raw_text:
        with st.expander("📜 View Extracted Text (Page 2)", expanded=False):
            st.text_area("Raw Text from PDF:", raw_text, height=200)

        # AI data extraction
        st.subheader("🔍 Extracting Performance Metrics...")
        extraction_prompt = f"""
        Extract key performance metrics from this unstructured text and return a JSON array.
        Metrics: Clicks, Conversions, Goal Conversion Rate, Cost, Cost per Conversion, 
        Average CPC, Impressions, CTR, All Conversion Value, ROAS, Search Impression Share.
        
        Text:
        {raw_text}

        Respond only with JSON format.
        """
        structured_data = call_openai_api(extraction_prompt)

        if structured_data:
            try:
                df = pd.DataFrame(json.loads(structured_data))
            except json.JSONDecodeError:
                st.error("⚠️ AI returned invalid data. Try another PDF.")
                st.stop()

            st.subheader("📊 Extracted Performance Metrics")
            st.table(df.style.set_properties(**{'text-align': 'left'}))  

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")

            # AI Analysis with Loading Progress
            st.subheader("📈 AI Analysis & Recommendations")
            with st.spinner("🚀 Generating insights..."):
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent + 1)

                table_text = df.to_string(index=False)
                analysis_prompt = f"""
                Analyze the following PPC performance data and provide insights.
                Identify trends and explain performance changes in a clear, professional tone.

                {table_text}

                Avoid jargon and unnecessary complexity. Use UK English. No greetings or sign-offs.
                """
                analysis_result = call_openai_api(analysis_prompt)
                st.write(analysis_result)

            # Refinement section
            st.markdown("""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px;">
                    <h4>Refine AI Analysis</h4>
                </div>
            """, unsafe_allow_html=True)

            user_prompt = st.text_area("Enter additional instructions for AI:", key="user_input")

            if st.button("Improve Analysis"):
                if user_prompt.strip():
                    with st.spinner("🔄 Updating analysis with user input..."):
                        refine_prompt = f"""
                        The user provided additional instructions to refine the analysis.
                        Original analysis:
                        {analysis_result}

                        User request:
                        "{user_prompt}"

                        Provide an improved analysis based on this feedback.
                        """
                        refined_response = call_openai_api(refine_prompt)
                        st.subheader("🔄 Updated AI Analysis")
                        st.write(refined_response)

                        st.subheader("✏️ Further Refinements")
                        user_prompt = st.text_area("Enter additional refinements:", key="further_input")
                else:
                    st.warning("⚠️ Please enter instructions before submitting.")

        else:
            st.error("⚠️ AI extraction failed. Please try a different PDF.")

    else:
        st.error("⚠️ No text found on page 2. Try uploading a different PDF.")
