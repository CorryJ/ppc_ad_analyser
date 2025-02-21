import streamlit as st
import pdfplumber
import openai
import pandas as pd
import json
# Setting page title and header
st.set_page_config(page_title="The SEO Works AI Bot",  
st.set_page_config(page_title="The SEO Works Google Ad Report analyser",  
                   page_icon="https://www.seoworks.co.uk/wp-content/themes/seoworks/assets/images/fav.png", 
                   layout="centered",initial_sidebar_state="collapsed")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.header("")
   
with col2:
    st.header("")
    st.image("resources/SeoWorksLogo-Dark.png")
with col3:
    st.header("")
st.markdown('<div style="text-align: center; font-size:24px;"><strong>The SEO Works Ad analyser<strong></div>', unsafe_allow_html=True)
# Initialise OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# Define banned words list
banned_words = "Everest, Matterhorn, levate, juncture, moreover, landscape, utilise, maze, labyrinth, cusp, hurdles, bustling, harnessing, unveiling the power,\
       realm, depicted, demystify, insurmountable, new era, poised, unravel, entanglement, unprecedented, eerie connection, unliving, \
       beacon, unleash, delve, enrich, multifaceted, elevate, discover, supercharge, unlock, unleash, tailored, elegant, delve, dive, \
       ever-evolving, pride, realm,  meticulously, grappling, superior, weighing,  merely, picture, architect, adventure, journey, embark , \
       navigate, navigation, navigating, enchanting, world, dazzle, tapestry, in this blog, in this article, dive-in, in today's, right place, \
        let's get started, imagine this, picture this, consider this, just explore"
# Function to extract text from page 2 of the PDF
def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        if len(pdf.pages) > 1:  # Ensure at least 2 pages exist
            return pdf.pages[1].extract_text()
        else:
            return None
# Function to send text to ChatGPT API and structure the extracted data
def chatgpt_extraction(raw_text):
    prompt = f"""
    Extract key performance metrics from the following unstructured text. 
    Present them in a structured JSON format with fields: "Metric", "Value", and "Change (%)".
    
    Only include metrics related to PPC performance such as:
    - Clicks
    - Conversions
    - Goal Conversion Rate
    - Cost
    - Cost per Conversion
    - Average CPC
    - Impressions
    - CTR
    - All Conversion Value
    - Search Impression Share
    - Return on Ad Spend (ROAS)
    - Average Purchase Revenue
    Ensure the JSON output is a valid array.
    Text:
    {raw_text}
    Respond only with the JSON output and no additional text.
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a data extraction assistant."},
                  {"role": "user", "content": prompt}]
    )
    # Extract JSON output
    structured_data = response.choices[0].message.content.strip()
    # Ensure JSON format
    try:
        return json.loads(structured_data)
    except json.JSONDecodeError:
        return None
# Function to analyze extracted data using GPT-4
def chatgpt_analysis(table_text):
    analysis_prompt = f"""
    You are a Google Ads expert. Here is a table containing key Google Ads performance metrics:
    {table_text}
    Please provide a summary of the table and recommendations to improve performance. 
    Write in UK English at all times (e.g., humanise instead of humanize, colour instead of color). 
    Avoid jargon and unnecessarily complex word choices. Clarity is crucial. 
    Do not use emojis or exclamation marks. 
    You MUST NOT include any of the following words in the response:
    {banned_words}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a Google Ads performance analyst."},
                  {"role": "user", "content": analysis_prompt}]
    )
    return response.choices[0].message.content
# Streamlit UI
st.title("AI-Powered PDF Performance Report Extractor & Analysis")
# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file:
    raw_text = extract_pdf_text(uploaded_file)
    if raw_text:
        st.subheader("Extracted Text (Page 2)")
        st.text_area("Raw Text from PDF:", raw_text, height=200)
        # Call ChatGPT API to structure the extracted data
        st.subheader("Structured Data Extraction in Progress...")
        structured_data = chatgpt_extraction(raw_text)
        if structured_data:
            # Convert JSON response to Pandas DataFrame
            df = pd.DataFrame(structured_data)
            # Display structured table
            st.subheader("Extracted Performance Metrics")
            st.dataframe(df)
            # Provide CSV download option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")
            # Convert table to plain text for AI analysis
            table_text = df.to_string(index=False)
            # Run AI analysis
            st.subheader("AI Analysis & Recommendations")
            with st.spinner("Analysing table with AI..."):
                analysis_result = chatgpt_analysis(table_text)
                st.write(analysis_result)
        else:
            st.error("Failed to extract structured data from the ChatGPT API. Please check the output.")
    else:
        st.error("Could not extract text from page 2.")
