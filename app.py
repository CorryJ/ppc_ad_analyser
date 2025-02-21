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

# Initialize OpenAI client
client = openai.Client(api_key=OPENAI_API_KEY)

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return pdf.pages[1].extract_text() if len(pdf.pages) > 1 else None

# Function to call OpenAI API and enforce JSON response
def call_openai_api(prompt, model="gpt-4-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a data extraction assistant. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        response_format="json"  # Ensures JSON output
    )

    raw_response = response.choices[0].message.content

    # Debugging: Print raw response in case of error
    print("Raw OpenAI Response:", raw_response)

    # Ensure response is valid JSON
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        st.error("⚠️ AI returned invalid JSON. Try again or check the extracted text.")
        return None

# Main UI
st.sidebar.header("Upload your PDF here")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf"])

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
        Respond only with a JSON array of objects, no other text.

        Example format:
        [
            {{"Metric": "Clicks", "Value": "1200", "Change (%)": "+10%"}},
            {{"Metric": "Conversions", "Value": "50", "Change (%)": "-5%"}}
        ]

        Text:
        {raw_text}
        """
        structured_data = call_openai_api(extraction_prompt)

        if structured_data:
            try:
                df = pd.DataFrame(structured_data)
                st.subheader("📊 Extracted Performance Metrics")
                st.table(df)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Extracted Data as CSV", csv, "extracted_data.csv", "text/csv")

                # AI Analysis
                st.subheader("📈 AI Analysis & Recommendations")
                analysis_prompt = f"""
                Analyze the following PPC performance data and provide insights.

                {df.to_string(index=False)}

                Keep the response clear, professional, and in UK English.
                """
                analysis_result = call_openai_api(analysis_prompt, model="gpt-4o")
                st.write(analysis_result)

            except Exception as e:
                st.error(f"⚠️ Error processing AI response: {str(e)}")
        else:
            st.error("⚠️ AI returned invalid data. Please try again.")

    else:
        st.error("⚠️ No text found on page 2. Try uploading a different PDF.")
