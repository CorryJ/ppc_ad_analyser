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
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Secure API Key Retrieval
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

# Initialize OpenAI client (Latest API version)
client = openai.Client(api_key=OPENAI_API_KEY)

# Define banned words list
banned_words = "Everest, Matterhorn, levate, juncture, moreover, landscape, utilise, maze, labyrinth, cusp, hurdles, bustling, harnessing, unveiling the power,\
       realm, depicted, demystify, insurmountable, new era, poised, unravel, entanglement, unprecedented, eerie connection, unliving, \
       beacon, unleash, delve, enrich, multifaceted, elevate, discover, supercharge, unlock, unleash, tailored, elegant, delve, dive, \
       ever-evolving, pride, realm, meticulously, grappling, superior, weighing, merely, picture, architect, adventure, journey, embark, \
       navigate, navigation, navigating, enchanting, world, dazzle, tapestry, in this blog, in this article, dive-in, in today's, right place, \
       let's get started, imagine this, picture this, consider this, just explore"

# Custom CSS for styling
st.markdown("""
    <style>
        .block-container { padding: 2rem 5rem; }
        div.stButton > button { width: 100%; font-size: 16px; padding: 10px; }
        div.stDownloadButton > button { background-color: #28a745; color: white; font-size: 16px; border-radius: 5px; padding: 10px; }
        div.stTextArea > textarea { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# Improve Header Layout
col1, col2, col3 = st.columns([1,2,1])  # Adjust column widths

with col2:  
    st.image("resources/SeoWorksLogo-Dark.png", use_column_width=True)  # Auto-resize image
    st.markdown('<div style="text-align: center; font-size:26px;"><strong>The SEO Works Ad Analyser</strong></div>', unsafe_allow_html=True)

# Use Sidebar for PDF Upload
st.sidebar.header("Upload your PDF here")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf"])
st.sidebar.markdown("""
---
### How to Use:
1️⃣ Upload a **Google Ads Report (PDF)**  
2️⃣ AI will extract & analyse the data  
3️⃣ You can **refine the insights** using additional prompts  
""")


# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return pdf.pages[1].extract_text() if len(pdf.pages) > 1 else None

# Function to call OpenAI API
def call_openai_api(prompt, model="gpt-4-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a data extraction assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ OpenAI API error: {str(e)}")
        return None

# Initialize session state for storing analysis
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

if uploaded_file:
    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully ({uploaded_file.size/1024:.2f} KB)")

    raw_text = extract_pdf_text(uploaded_file)

    if raw_text:
        with st.expander("📜 View Extracted Text (Page 2)", expanded=False):
            st.text_area("Raw Text from PDF:", raw_text, height=200)

        # AI data extraction
        st.subheader("🔍 Extracting Performance Metrics...")
        extraction_prompt = f"""
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
        structured_data = call_openai_api(extraction_prompt)

        if structured_data:
            df = pd.DataFrame(json.loads(structured_data))
            st.subheader("📊 Extracted Performance Metrics")
            st.table(df.style.set_properties(**{'text-align': 'left'}))

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")

            # AI Analysis
            st.subheader("📈 AI Analysis & Recommendations")
            with st.spinner("🚀 Generating insights..."):
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent + 1)
            if st.session_state.analysis_result == "":
                analysis_prompt = f"""
                You are a Google Ads expert. Here is a table containing key Google Ads performance metrics:

                {df.to_string(index=False)}

                Generate a summary report for my PPC account with the following metrics below attached. Identify key trends and provide insights. 
                Expand on any performance trends and insights. Ensure the tone of voice is friendly but not informal. Speak about the report like you manage the PPC / Google Ads account.
                Write in UK English at all times. Avoid jargon and unnecessarily complex word choices. Clarity is crucial. 
                Do not use emojis or exclamation marks. 
                Do not use any greetings (e.g., Hello) or sign-offs (e.g., Best regards).

                You MUST NOT include any of the following words in the response:
                {banned_words}
                """
                st.session_state.analysis_result = call_openai_api(analysis_prompt, model="gpt-4o")

            st.write(st.session_state.analysis_result)

            # Refinement section
            st.markdown("""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px;">
                    <h4>Refine AI Analysis</h4>
                </div>
            """, unsafe_allow_html=True)


           # st.subheader("✏️ Refine AI Analysis")
            user_prompt = st.text_area("Enter additional instructions for AI:", key="user_input")

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
                        {st.session_state.analysis_result}

                        User request:
                        "{user_prompt}"

                        Provide an improved analysis based on this feedback.
                        """
                        st.session_state.analysis_result = call_openai_api(refine_prompt, model="gpt-4o")
                        st.rerun()  # Refresh the page to display new results
                else:
                    st.warning("⚠️ Please enter some instructions before submitting.")

        else:
            st.error("⚠️ AI returned invalid data. Please try again.")

    else:
        st.error("⚠️ No text found on page 2. Try uploading a different PDF.")

