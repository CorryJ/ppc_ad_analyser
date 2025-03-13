import streamlit as st
import pdfplumber
import openai
import pandas as pd
import json
import time

# Set page config
st.set_page_config(
    page_title="The SEO Works Google Ads Analyser",  
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
        div.stButton > button { width: 100%; font-size: 16px; padding: 10px; background-color: #007BFF; color: white; border-radius: 5px; }
        div.stDownloadButton > button { background-color: #28a745; color: white; font-size: 16px; border-radius: 5px; padding: 10px; }
        div.stTextArea > textarea { font-size: 14px; }
        .custom-box { background-color: #f9f9f9; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Header with SEO Works Logo
col1, col2, col3 = st.columns([1,2,1])
with col2:  
    st.image("resources/SeoWorksLogo-Dark.png", use_container_width=True)
    st.markdown('<div style="text-align: center; font-size:26px;"><strong>The SEO Works Ad Analyser</strong></div>', unsafe_allow_html=True)

# Sidebar for file upload
st.sidebar.header("📂 Upload your PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

st.sidebar.markdown("""
---
### ℹ️ How to Use:
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

# Initialize session state for storing analysis history
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []  # Stores all versions of analysis

if uploaded_file:
    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully ({uploaded_file.size/1024:.2f} KB)")

    raw_text = extract_pdf_text(uploaded_file)

    if raw_text:
        with st.expander("📜 View Extracted Text (Page 2)", expanded=False):
            st.text_area("Raw Text from PDF:", raw_text, height=200)

        # AI Data Extraction
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
            st.dataframe(df)  # Improved styling for tables

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")

            # Generate Initial Analysis if none exists
            if not st.session_state.analysis_history:
                analysis_prompt = f"""
                You are an online paid advertising expert who manages ad campaigns on behalf of your client. Generate a summary report for your client's PPC 
                account with the following metrics provided in the below table:

                {df.to_string(index=False)}

                Identify key trends and provide insights. Expand on any performance trends and insights. 
                Can you split out the summary into 3 sections - Traffic & Cost, Engagement, Conversions. 
                Then provide a section on Key Takeaways & Next Steps.

                Write in a personal style. Ensure the tone of voice is friendly but not informal. 
                Write in the present perfect tense, for example rather than "The number of clicks has increased by 6.4%" say "We've seen a significant increase in traffic, with clicks up by 6.4%". 
                Overall we want the analysis to make it seem as though it's 'our' account. This is because when we talk about it, it's our work so the responsibility and performance is on our shoulders.
                Keep the tone professional but approachable, without excessive formality or technical jargon.
                Ensure all content is written in UK English(e.g., humanise instead of humanize, colour instead of color) and does not include greetings or sign-offs.
                Do not use emojis or exclamation marks. 
                
                You MUST NOT include any of the following words in the response:
                {banned_words}
                """
                first_analysis = call_openai_api(analysis_prompt, model="gpt-4-turbo")
                if first_analysis:
                    st.session_state.analysis_history.append(first_analysis)

            # Display All Versions of Analysis
            for i, analysis in enumerate(st.session_state.analysis_history):
                st.markdown(f"<h1>📜 Analysis Version {i+1}</h1>", unsafe_allow_html=True)
                st.write(analysis)

                # Refinement Section for Each Analysis Version
                st.markdown('<div class="custom-box"><h4>🔧 Refine This Analysis</h4></div>', unsafe_allow_html=True)
                user_prompt = st.text_area(f"Enter refinements for Version {i+1}:", key=f"user_input_{i}")

                # Blue Button for Refining Each Version
                if st.button(f"Improve Analysis Version {i+1}", key=f"refine_button_{i}"):
                    if user_prompt.strip():
                        with st.spinner("🔄 Generating refined analysis..."):
                            refine_prompt = f"""
                            The user provided additional instructions to refine the analysis.
                            Original analysis:
                            {analysis}

                            User request:
                            "{user_prompt}"

                            Provide an improved analysis based on this feedback.
                            """
                            new_analysis = call_openai_api(refine_prompt, model="gpt-4-turbo")
                            if new_analysis:
                                st.session_state.analysis_history.append(new_analysis)

                        st.rerun()  # Refresh the page to display new results
                    else:
                        st.warning("⚠️ Please enter some instructions before submitting.")

        else:
            st.error("⚠️ AI returned invalid data. Please try again.")

    else:
        st.error("⚠️ No text found on page 2. Try uploading a different PDF.")
