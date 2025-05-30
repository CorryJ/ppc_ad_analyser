import streamlit as st
import pdfplumber
import openai
import pandas as pd
import json
import time
import hashlib
from typing import Optional, Dict, Any

# Page configuration
st.set_page_config(
    page_title="The SEO Works Google Ads Analyser",
    # page_icon="📊",
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

banned_words = "Everest, Matterhorn, levate, juncture, moreover, landscape, utilise, maze, labyrinth, cusp, hurdles, bustling, harnessing, unveiling the power,\
       realm, depicted, demystify, insurmountable, new era, poised, unravel, entanglement, unprecedented, eerie connection, unliving, \
       beacon, unleash, delve, enrich, multifaceted, elevate, discover, supercharge, unlock, unleash, tailored, elegant, delve, dive, \
       ever-evolving, pride, realm, meticulously, grappling, superior, weighing, merely, picture, architect, adventure, journey, embark, \
       navigate, navigation, navigating, enchanting, world, dazzle, tapestry, in this blog, in this article, dive-in, in today's, right place, \
       let's get started, imagine this, picture this, consider this, just explore"

# Custom CSS for modern design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* SEO Works Brand Colors - Clean Header Design */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
        border: 2px solid #85bd41;
        box-shadow: 0 4px 20px -4px rgb(133 189 65 / 0.2);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #433D3F;
        margin-bottom: 0.5rem;
        text-shadow: none;
    }
    
    .main-title .highlight {
        color: #85bd41;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: #433D3F;
        font-weight: 400;
        margin-bottom: 1rem;
        opacity: 0.8;
    }
    
    .brand-accent {
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #85bd41, #aadd6a, #f1cc2f);
        margin: 1rem auto 0;
        border-radius: 2px;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(67 61 63 / 0.1), 0 2px 4px -2px rgb(67 61 63 / 0.1);
        border: 1px solid #c9ef9b;
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        background: linear-gradient(135deg, #85bd41, #aadd6a);
        color: white;
        padding: 1rem 1.5rem;
        margin: -1.5rem -1.5rem 1.5rem -1.5rem;
        border-radius: 1rem 1rem 0 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .upload-card .card-header {
        background: linear-gradient(135deg, #85bd41, #bbd14f);
    }
    
    .metrics-card .card-header {
        background: linear-gradient(135deg, #f1cc2f, #ffdf57);
        color: #433D3F;
    }
    
    .analysis-card .card-header {
        background: linear-gradient(135deg, #433D3F, #85bd41);
        color: white;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #c9ef9b, #ffe585);
        border: 1px solid #85bd41;
        border-radius: 0.75rem;
        padding: 1rem;
        transition: all 0.2s ease;
        margin-bottom: 0.75rem;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px -2px rgb(133 189 65 / 0.3);
        transform: translateY(-1px);
        background: linear-gradient(135deg, #aadd6a, #ffdf57);
    }
    
    .metric-name {
        font-weight: 600;
        color: #433D3F;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    .metric-period {
        font-size: 0.75rem;
        color: #433D3F;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #433D3F;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .change-positive {
        color: #85bd41;
        font-weight: 700;
    }
    
    .change-negative {
        color: #433D3F;
        font-weight: 700;
    }
    
    .change-neutral {
        color: #433D3F;
        opacity: 0.6;
    }
    
    /* Analysis content */
    .analysis-content {
        line-height: 1.7;
        color: #433D3F;
    }
    
    .analysis-content h2 {
        color: #433D3F;
        font-weight: 700;
        font-size: 1.25rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #85bd41;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #85bd41, #aadd6a) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px -2px rgb(133 189 65 / 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #aadd6a, #bbd14f) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 16px -4px rgb(133 189 65 / 0.4) !important;
    }
    
    /* Custom refinement button */
    .refine-button {
        background: linear-gradient(135deg, #f1cc2f, #ffdf57) !important;
        color: #433D3F !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* File uploader styling */
    .uploadedfile {
        background: linear-gradient(135deg, #c9ef9b, #aadd6a) !important;
        border: 1px solid #85bd41 !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        color: #433D3F !important;
    }
    
    /* Custom box styling */
    .custom-box {
        background: linear-gradient(135deg, #c9ef9b, #ffe585);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #85bd41;
        color: #433D3F;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .custom-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Utility Functions
def validate_uploaded_file(uploaded_file) -> bool:
    """Validate uploaded file"""
    if not uploaded_file:
        return False
        
    # Check file size (max 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File size too large. Please upload a file smaller than 10MB.")
        return False
        
    # Check file type
    if not uploaded_file.name.lower().endswith('.pdf'):
        st.error("Please upload a PDF file only.")
        return False
        
    return True

def extract_pdf_text(uploaded_file) -> Optional[str]:
    """Extract text from all pages of PDF with improved error handling"""
    if not validate_uploaded_file(uploaded_file):
        return None
        
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            all_text = ""
            pages_processed = 0
            
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text += f"\n--- Page {i+1} ---\n{text}\n"
                        pages_processed += 1
                except Exception as e:
                    st.warning(f"Could not extract text from page {i+1}: {str(e)}")
                    continue
            
            if pages_processed == 0:
                st.error("No readable text found in the PDF. Please ensure the PDF contains text (not just images).")
                return None
                
            st.success(f"Successfully extracted text from {pages_processed} page(s)")
            return all_text.strip()
            
    except Exception as e:
        st.error(f"Failed to process PDF: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_openai_call(prompt_hash: str, prompt: str, model: str = "gpt-4.1") -> Optional[str]:
    """Cached OpenAI API call to avoid repeated requests"""
    return call_openai_api_with_retry(prompt, model)

def call_openai_api_with_retry(prompt: str, model: str = "gpt-4.1", max_retries: int = 3) -> Optional[str]:
    """Call OpenAI API with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent results
                max_tokens=4000
            )
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1
                st.warning(f"Rate limit reached. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            st.error("Rate limit exceeded. Please try again later.")
            return None
            
        except openai.APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                st.warning(f"API error occurred. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            st.error(f"OpenAI API error: {str(e)}")
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                st.warning(f"Unexpected error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    return None

def call_openai_api(prompt: str, model: str = "gpt-4.1") -> Optional[str]:
    """Main OpenAI API call function with caching"""
    # Create hash for caching
    prompt_hash = hashlib.md5(f"{prompt}{model}".encode()).hexdigest()
    return cached_openai_call(prompt_hash, prompt, model)

def parse_structured_data(structured_data: str) -> Optional[pd.DataFrame]:
    """Parse AI response into DataFrame with robust error handling"""
    if not structured_data or not structured_data.strip():
        st.error("No data received from AI analysis.")
        return None
    
    try:
        # Try to find JSON in the response
        structured_data = structured_data.strip()
        
        # Look for JSON array markers
        start_idx = structured_data.find('[')
        end_idx = structured_data.rfind(']') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = structured_data[start_idx:end_idx]
        else:
            json_str = structured_data
        
        data = json.loads(json_str)
        
        # Validate data structure
        if not isinstance(data, list):
            st.error("AI response is not in the expected list format.")
            return None
            
        if len(data) == 0:
            st.warning("No metrics found in the PDF. The document might not contain recognizable performance data.")
            return None
        
        # Validate each item has required fields
        required_fields = ['Metric', 'Value']
        for item in data:
            if not isinstance(item, dict):
                st.error("Invalid data format in AI response.")
                return None
            for field in required_fields:
                if field not in item:
                    st.warning(f"Missing field '{field}' in some metrics. Proceeding with available data.")
        
        df = pd.DataFrame(data)
        
        # Clean and validate DataFrame
        if df.empty:
            st.warning("No valid data could be extracted from the response.")
            return None
            
        return df
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response as JSON: {str(e)}")
        st.text_area("Raw AI Response (for debugging):", structured_data, height=200)
        return None
        
    except Exception as e:
        st.error(f"Unexpected error parsing data: {str(e)}")
        return None

def get_change_class(change_str):
    """Return CSS class based on change direction"""
    if not change_str or str(change_str).lower() in ['null', 'none', '']:
        return 'change-neutral'
    elif str(change_str).startswith('+'):
        return 'change-positive'
    elif str(change_str).startswith('-'):
        return 'change-negative'
    else:
        return 'change-neutral'

def get_change_icon(change_str):
    """Return appropriate icon for change"""
    if not change_str or str(change_str).lower() in ['null', 'none', '']:
        return '●'
    elif str(change_str).startswith('+'):
        return '↗'
    elif str(change_str).startswith('-'):
        return '↘'
    else:
        return '●'

def format_metric_value(value):
    """Format metric values to ensure proper display of currency and percentages"""
    if not value or pd.isna(value):
        return str(value)
    
    value_str = str(value).strip()
    
    # If it already has £ or % symbols, return as is
    if '£' in value_str or '%' in value_str:
        return value_str
    
    # Try to detect if it should be currency or percentage based on common patterns
    # Remove commas for number detection
    clean_value = value_str.replace(',', '')
    
    # Check if it's a pure number that could be formatted
    try:
        num_value = float(clean_value)
        
        # If original value had commas and is > 100, likely currency
        if ',' in value_str and num_value > 100:
            return f"£{value_str}"
        
        # If it's a small decimal (0-5 range), might be a percentage
        if 0 < num_value < 5 and '.' in clean_value:
            return f"{value_str}%"
            
    except ValueError:
        pass
    
    return value_str

def format_change_value(change):
    """Format change values to ensure % symbol is shown"""
    if not change or pd.isna(change) or str(change).lower() in ['null', 'none', '']:
        return ''
    
    change_str = str(change).strip()
    
    # If it already has %, return as is
    if '%' in change_str:
        return change_str
    
    # If it looks like a percentage change, add %
    if change_str.startswith(('+', '-')) and change_str[1:].replace('.', '').isdigit():
        return f"{change_str}%"
    
    return change_str

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">📊 The SEO Works <span class="highlight">Ad Analyser</span></h1>
    <p class="main-subtitle">Transform your PPC reports into actionable insights with AI-powered analysis</p>
    <div class="brand-accent"></div>
</div>
""", unsafe_allow_html=True)

# Sidebar for file upload
st.sidebar.header("📂 Upload your PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

st.sidebar.markdown("""
---
### ℹ️ How to Use:
1️⃣ Upload a **Google Ads Report (PDF)**  
2️⃣ AI will extract & analyse the data  
3️⃣ You can **refine the insights** using additional prompts  

### 💡 Tips:
- Ensure your PDF contains readable text
- Files should be under 10MB
- Multi-page reports are supported
""")

# Main application logic
if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully ({file_size_mb:.2f} MB)")

    # Extract text from PDF
    if st.session_state.extracted_data is None:
        with st.spinner("📄 Processing PDF..."):
            raw_text = extract_pdf_text(uploaded_file)
        
        if raw_text:
            with st.expander("📜 View Extracted Text", expanded=False):
                st.text_area("Raw Text from PDF:", raw_text, height=300)

            # AI Data Extraction
            st.subheader("🔍 Extracting Performance Metrics...")
            
            extraction_prompt = f"""
            Extract ALL performance metrics from the following unstructured text. 
            Present them in a structured JSON format with fields: "Metric", "Value", "Change (%)", and "Period".

            Extract ALL metrics including:
            - Month on Month data: Clicks, Conversions, Goal Conversion Rate, Cost, Cost per Conversion, Average CPC, Impressions, CTR, Search Impression Share, All Conversion Value, ROAS, Average Purchase Revenue
            - Year on Year data: All same metrics as above but for year-over-year comparison
            - Shopify Stats: Total Revenue, Total Sales (both Month on Month and Year on Year)
            - Any other performance metrics found in the document

            Rules:
            1. Return ONLY a valid JSON array
            2. Each object must have "Metric", "Value", and "Period" fields
            3. Include "Change (%)" only if percentage change data is available, otherwise use null
            4. Use "Period" field to indicate if it's "Month on Month", "Year on Year", or "Current Period"
            5. For Shopify stats, clearly indicate the source as "Shopify"
            6. Extract ALL numerical performance data found in the document
            7. Ensure all JSON is properly formatted

            Text:
            {raw_text}

            Respond only with the JSON output and no additional text.
            """
            
            with st.spinner("🤖 AI is analyzing your data..."):
                structured_data = call_openai_api(extraction_prompt)

            if structured_data:
                df = parse_structured_data(structured_data)
                
                if df is not None:
                    st.session_state.extracted_data = df
                    st.success("✅ Data extraction completed successfully!")
                else:
                    st.error("❌ Failed to extract valid data from the PDF.")
            else:
                st.error("❌ AI analysis failed. Please try again.")
        else:
            st.error("❌ Could not extract text from the PDF. Please check the file format.")
    
    # Display extracted data if available
    if st.session_state.extracted_data is not None:
        df = st.session_state.extracted_data
        
        # Metrics Overview in modern card design
        st.markdown("""
        <div class="custom-card metrics-card">
            <div class="card-header">📈 Key Metrics Overview</div>
        """, unsafe_allow_html=True)
        
        # Group metrics by period
        if 'Period' in df.columns:
            mom_metrics = df[df['Period'] == 'Month on Month'] if 'Month on Month' in df['Period'].values else pd.DataFrame()
            yoy_metrics = df[df['Period'] == 'Year on Year'] if 'Year on Year' in df['Period'].values else pd.DataFrame()
            
            if not mom_metrics.empty:
                st.markdown("#### Month on Month Performance")
                for i in range(0, len(mom_metrics), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if i + j < len(mom_metrics):
                            metric = mom_metrics.iloc[i + j]
                            formatted_value = format_metric_value(metric['Value'])
                            formatted_change = format_change_value(metric.get('Change (%)', ''))
                            change_class = get_change_class(formatted_change)
                            change_icon = get_change_icon(formatted_change)
                            
                            col.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-name">{metric['Metric']}</div>
                                <div class="metric-period">{metric['Period']}</div>
                                <div class="metric-value">
                                    {formatted_value}
                                    {f'<span class="metric-change {change_class}">{change_icon} {formatted_change}</span>' if formatted_change else ''}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            if not yoy_metrics.empty:
                st.markdown("#### Year on Year Performance")
                for i in range(0, len(yoy_metrics), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if i + j < len(yoy_metrics):
                            metric = yoy_metrics.iloc[i + j]
                            formatted_value = format_metric_value(metric['Value'])
                            formatted_change = format_change_value(metric.get('Change (%)', ''))
                            change_class = get_change_class(formatted_change)
                            change_icon = get_change_icon(formatted_change)
                            
                            col.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-name">{metric['Metric']}</div>
                                <div class="metric-period">{metric['Period']}</div>
                                <div class="metric-value">
                                    {formatted_value}
                                    {f'<span class="metric-change {change_class}">{change_icon} {formatted_change}</span>' if formatted_change else ''}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # Fallback if no Period column
            st.dataframe(df, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Extracted Data as CSV", 
            csv, 
            f"ads_analysis_{int(time.time())}.csv", 
            "text/csv"
        )

        # Generate Initial Analysis if none exists
        if not st.session_state.analysis_history:
            st.subheader("🎯 Generating Analysis...")
            
            analysis_prompt = f"""
            You are an online paid advertising expert who manages ad campaigns on behalf of your client. Generate a comprehensive summary report for your client's PPC 
            account with the following metrics provided in the below table:

            {df.to_string(index=False)}

            Analyse both Month on Month and Year on Year performance where available. Include Shopify data if present.
            Identify key trends and provide insights. Expand on any performance trends and insights. 
            
            Structure your analysis as follows:
            1. **Traffic & Cost** - Analyse clicks, impressions, CPC, and total cost trends
            2. **Engagement** - Review CTR, search impression share, and engagement metrics  
            3. **Conversions** - Examine conversion rates, conversion values, ROAS, and revenue metrics
            4. **Year on Year Comparison** - Compare current performance to the same period last year (if data available)
            5. **Key Takeaways & Next Steps** - Provide actionable recommendations

            Write in a personal style. Ensure the tone of voice is friendly but not informal. 
            Write in the present perfect tense, for example rather than "The number of clicks has increased by 6.4%" say "We've seen a significant increase in traffic, with clicks up by 6.4%". 
            Overall we want the analysis to make it seem as though it's 'our' account. This is because when we talk about it, it's our work so the responsibility and performance is on our shoulders.
            Keep the tone professional but approachable, without excessive formality or technical jargon.
            Ensure all content is written in UK English(e.g., humanise instead of humanize, colour instead of color) and does not include greetings or sign-offs.
            Do not use emojis or exclamation marks. 
            
            You MUST NOT include any of the following words in the response:
            {banned_words}
            """
            
            with st.spinner("📝 Generating comprehensive analysis..."):
                first_analysis = call_openai_api(analysis_prompt, model="gpt-4.1")
            
            if first_analysis:
                st.session_state.analysis_history.append(first_analysis)
                st.success("✅ Analysis generated successfully!")
            else:
                st.error("❌ Failed to generate analysis. Please try again.")

        # Display All Versions of Analysis
        for i, analysis in enumerate(st.session_state.analysis_history):
            st.markdown("---")
            st.markdown(f"""
            <div class="custom-card analysis-card">
                <div class="card-header">🤖 Analysis Version {i+1}</div>
                <div class="analysis-content">
            """, unsafe_allow_html=True)
            
            # Process and display analysis
            analysis_html = analysis.replace('\n\n', '</p><p>').replace('**', '<strong>').replace('**', '</strong>')
            analysis_html = f"<p>{analysis_html}</p>"
            
            st.markdown(analysis_html, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

            # Refinement Section for Each Analysis Version
            st.markdown("### 🔧 Refine This Analysis")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                user_prompt = st.text_area(
                    f"Enter refinements for Version {i+1}:", 
                    key=f"user_input_{i}",
                    placeholder="E.g., 'Focus more on conversion data' or 'Add competitor comparison insights'"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                if st.button(f"🚀 Improve Version {i+1}", key=f"refine_button_{i}"):
                    if user_prompt.strip():
                        with st.spinner("🔄 Generating refined analysis..."):
                            refine_prompt = f"""
                            The user provided additional instructions to refine the analysis.
                            Original analysis:
                            {analysis}

                            User request:
                            "{user_prompt}"

                            Provide an improved analysis based on this feedback. Keep the same professional tone and UK English style.
                            
                            You MUST NOT include any of the following words in the response:
                            {banned_words}
                            """
                            
                            new_analysis = call_openai_api(refine_prompt, model="gpt-4.1")
                            
                            if new_analysis:
                                st.session_state.analysis_history.append(new_analysis)
                                st.success("✅ Refined analysis generated!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to generate refined analysis. Please try again.")
                    else:
                        st.warning("⚠️ Please enter some instructions before submitting.")

else:
    # Welcome message when no file is uploaded
    with st.container():
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: white; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## Welcome to The SEO Works Ad Analyser! 👋")
        st.markdown("*This tool helps you quickly analyse Google Ads performance reports using AI.*")
        
        st.markdown("### 🚀 Getting Started:")
        st.markdown("""
        1. Upload your Google Ads PDF report using the sidebar
        2. Our AI will automatically extract key metrics
        3. Get comprehensive analysis and insights
        4. Refine the analysis with custom prompts
        """)
        
        st.markdown("### ✨ Supported Features:")
        st.markdown("""
        - ✅ Multi-page PDF processing
        - ✅ Automatic metric extraction
        - ✅ AI-powered insights
        - ✅ Custom analysis refinements
        - ✅ CSV data export
        - ✅ Analysis history tracking
        """)
        
        st.info("📁 Upload your PDF to get started!")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 12px;">Powered by The SEO Works | AI-Enhanced PPC Analysis</div>', 
    unsafe_allow_html=True
)
