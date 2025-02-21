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


# Custom CSS for styling
st.markdown("""
    <style>
        .block-container { padding: 2rem 5rem; }
        div.stButton > button { width: 100%; font-size: 16px; padding: 10px; }
        div.stDownloadButton > button { background-color: #28a745; color: white; font-size: 16px; border-radius: 5px; padding: 10px; }
        div.stTextArea > textarea { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# Header with SEO Works Logo
col1, col2, col3 = st.columns([1,2,1])

with col2:  
    st.image("resources/SeoWorksLogo-Dark.png", use_container_width=True)
    st.markdown('<div style="text-align: center; font-size:26px;"><strong>The SEO Works Ad Analyser</strong></div>', unsafe_allow_html=True)

# Sidebar for file upload & quick help
st.sidebar.header("Upload your PDF here")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf"])

st.sidebar.markdown("""
---
### How to Use:
1️⃣ Upload a **Google Ads Report (PDF)**  
2️⃣ AI will extract & analyse the data  
3️⃣ You can **refine the insights** using additional prompts  
""")

# Secure API Key Retrieval
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

# Set OpenAI API key securely
openai.api_key = OPENAI_API_KEY


# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return pdf.pages[1].extract_text() if len(pdf.pages) > 1 else None

# Function to send text to ChatGPT API and structure the extracted data
def chatgpt_extraction(raw_text):
    prompt = f"""
    Extract key performance metrics from the following unstructured text. 
    Present them in a structured JSON format with fields: "Metric", "Value", and "Change (%)".
    
    Only include metrics related to PPC performance such as:
    - Clicks, Conversions, Goal Conversion Rate, Cost, Cost per Conversion, 
    - Average CPC, Impressions, CTR, All Conversion Value, 
    - Search Impression Share, ROAS, Average Purchase Revenue

    Ensure the JSON output is a valid array.

    Text:
    {raw_text}

    Respond only with the JSON output and no additional text.
    """

    response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[{"role": "system", "content": "You are a Google Ads performance analyst."},
              {"role": "user", "content": prompt}]
)

    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return None

# Function to analyze extracted data using GPT-4
def chatgpt_analysis(table_text):
    analysis_prompt = f"""
    You are a Google Ads expert. Here is a table containing key Google Ads performance metrics:

    {table_text}

    Generate a summary report with key trends and insights. Ensure a friendly but professional tone.
    Write in UK English and avoid jargon, complex word choices, and emojis.

    Do not use any greetings (e.g., Hello) or sign-offs (e.g., Best regards).
    """

    response = openai.OpenAI(api_key).chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a Google Ads performance analyst."},
                  {"role": "user", "content": analysis_prompt}]
    )

    return response.choices[0].message.content

# Main UI
if uploaded_file:
    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully ({uploaded_file.size/1024:.2f} KB)")

    # Extract text from PDF
    raw_text = extract_pdf_text(uploaded_file)

    if raw_text:
        with st.expander("📜 View Extracted Text (Page 2)", expanded=False):
            st.text_area("Raw Text from PDF:", raw_text, height=200)

        # AI data extraction
        st.subheader("🔍 Extracting Performance Metrics...")
        structured_data = chatgpt_extraction(raw_text)

        if structured_data:
            df = pd.DataFrame(structured_data)

            st.subheader("📊 Extracted Performance Metrics")
            st.table(df.style.set_properties(**{'text-align': 'left'}))  # Improved table display

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")

            table_text = df.to_string(index=False)

            # AI Analysis with Loading Progress
            st.subheader("📈 AI Analysis & Recommendations")
            with st.spinner("🚀 Generating insights..."):
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent + 1)

                analysis_result = chatgpt_analysis(table_text)
                st.write(analysis_result)

            # Refinement section with styled container
            st.markdown("""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px;">
                    <h4>Refine AI Analysis</h4>
                </div>
            """, unsafe_allow_html=True)

            user_prompt = st.text_area("Enter additional instructions or requests for AI:", key="user_input")

            st.markdown("""
                <style>
                    div.stButton > button { background-color: #004085; color: white; font-size: 16px; border-radius: 5px; padding: 10px; }
                </style>
            """, unsafe_allow_html=True)

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

                        refined_response = chatgpt_analysis(refine_prompt)
                        st.subheader("🔄 Updated AI Analysis")
                        st.write(refined_response)

                        st.subheader("✏️ Further Refinements")
                        user_prompt = st.text_area("Enter additional refinements:", key="further_input")
                else:
                    st.warning("⚠️ Please enter some instructions before submitting.")

        else:
            st.error("⚠️ AI extraction failed. Please try a different PDF.")

    else:
        st.error("⚠️ No text found on page 2. Try uploading a different PDF.")

