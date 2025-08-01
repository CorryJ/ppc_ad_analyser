import streamlit as st
import pdfplumber
import openai
import pandas as pd
import json
import time
import hashlib
import re
from typing import Optional, Dict, Any
import io

# Page configuration
st.set_page_config(
    page_title="The SEO Works Google Ads Analyser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Secure API Key Retrieval
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

client = openai.Client(api_key=OPENAI_API_KEY)

# Define banned words list
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
        box-shadow: 0 4px 20px -4px rgba(133, 189, 65, 0.2);
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
        box-shadow: 0 4px 6px -1px rgba(67, 61, 63, 0.1), 0 2px 4px -2px rgba(67, 61, 63, 0.1);
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
        box-shadow: 0 4px 12px -2px rgba(133, 189, 65, 0.3);
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
        box-shadow: 0 4px 12px -2px rgba(133, 189, 65, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #aadd6a, #bbd14f) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 16px -4px rgba(133, 189, 65, 0.4) !important;
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
def cached_openai_call(prompt_hash: str, prompt: str, model: str = "gpt-4-turbo") -> Optional[str]:
    """Cached OpenAI API call to avoid repeated requests"""
    return call_openai_api_with_retry(prompt, model)

def call_openai_api_with_retry(prompt: str, model: str = "gpt-4-turbo", max_retries: int = 3) -> Optional[str]:
    """Call OpenAI API with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,  # Changed from "gpt-4.1" to "gpt-4-turbo"
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant specialized in parsing advertising reports."},
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

def call_openai_api(prompt: str, model: str = "gpt-4-turbo") -> Optional[str]:
    """Main OpenAI API call function with caching"""
    # Create hash for caching
    prompt_hash = hashlib.md5(f"{prompt}{model}".encode()).hexdigest()
    return cached_openai_call(prompt_hash, prompt, model)

def clean_json_string(json_str: str) -> str:
    """
    Comprehensive JSON string cleaning to handle unterminated strings and special characters
    """
    # Remove any markdown code blocks first
    if '```json' in json_str:
        json_str = json_str.split('```json')[1].split('```')[0].strip()
    elif '```' in json_str:
        json_str = json_str.split('```')[1].split('```')[0].strip()
    
    # Extract just the JSON array part
    start_idx = json_str.find('[')
    end_idx = json_str.rfind(']') + 1
    
    if start_idx != -1 and end_idx > start_idx:
        json_str = json_str[start_idx:end_idx]
    
    # Fix common JSON issues
    # 1. Replace single quotes with double quotes (but be careful about apostrophes)
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)  # Fix keys
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)  # Fix values
    
    # 2. Handle infinity values
    json_str = json_str.replace('+∞%', 'null')
    json_str = json_str.replace('-∞%', 'null')
    json_str = json_str.replace('∞%', 'null')
    json_str = json_str.replace('+∞', 'null')
    json_str = json_str.replace('-∞', 'null')
    json_str = json_str.replace('∞', 'null')
    
    # 3. Fix boolean values
    json_str = json_str.replace('True', 'true').replace('False', 'false').replace('None', 'null')
    
    # 4. Remove trailing commas
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # 5. Fix unescaped quotes within strings - this is the main fix for the error
    # Find all string values and escape quotes within them
    def fix_quotes_in_strings(match):
        """Fix quotes within JSON string values"""
        full_match = match.group(0)
        key_part = match.group(1)  # The key part like "Metric": 
        string_content = match.group(2)  # The actual string content
        
        # Escape any unescaped quotes within the string content
        fixed_content = string_content.replace('\\', '\\\\')  # Escape backslashes first
        fixed_content = fixed_content.replace('"', '\\"')     # Escape quotes
        fixed_content = fixed_content.replace('\n', '\\n')    # Escape newlines
        fixed_content = fixed_content.replace('\r', '\\r')    # Escape carriage returns
        fixed_content = fixed_content.replace('\t', '\\t')    # Escape tabs
        
        return f'{key_part}"{fixed_content}"'
    
    # Pattern to match JSON key-value pairs with string values
    # This finds patterns like "Metric": "some value with "quotes" in it"
    pattern = r'("(?:Metric|Value|Period|Change \(%\))"\s*:\s*")([^"]*(?:"[^"]*"[^"]*)*)"'
    json_str = re.sub(pattern, fix_quotes_in_strings, json_str)
    
    return json_str

def parse_structured_data(structured_data: str) -> Optional[pd.DataFrame]:
    """
    Enhanced parsing function with multiple fallback strategies
    """
    if not structured_data or not structured_data.strip():
        st.error("No data received from AI analysis.")
        return None
    
    # Strategy 1: Try with comprehensive cleaning
    try:
        cleaned_json = clean_json_string(structured_data)
        data = json.loads(cleaned_json)
        
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            st.success(f"✅ Successfully parsed {len(data)} metrics")
            return df
            
    except json.JSONDecodeError as e:
        st.warning(f"Strategy 1 failed: {str(e)}")
    
    # Strategy 2: Try to extract data line by line using regex
    try:
        st.info("Attempting alternative parsing method...")
        metrics_data = []
        
        # Look for JSON-like objects in the text
        object_pattern = r'\{\s*"Metric"\s*:\s*"([^"]+)"\s*,\s*"Value"\s*:\s*"([^"]+)"\s*,\s*"Change \(%\)"\s*:\s*([^,}]+)\s*,\s*"Period"\s*:\s*"([^"]+)"\s*\}'
        
        matches = re.findall(object_pattern, structured_data, re.DOTALL)
        
        for match in matches:
            metric, value, change, period = match
            
            # Clean up the change value
            change = change.strip().rstrip(',')
            if change in ['null', 'None', '']:
                change = None
            else:
                try:
                    change = float(change)
                except ValueError:
                    change = None
            
            metrics_data.append({
                'Metric': metric.strip(),
                'Value': value.strip(),
                'Change (%)': change,
                'Period': period.strip()
            })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            st.success(f"✅ Successfully extracted {len(metrics_data)} metrics using fallback method")
            return df
    
    except Exception as e:
        st.warning(f"Strategy 2 failed: {str(e)}")
    
    # Strategy 3: Create fallback data
    try:
        st.info("Creating fallback data...")
        fallback_data = [
            {"Metric": "Parsing Error", "Value": "Check Debug Info", "Change (%)": None, "Period": "N/A"},
            {"Metric": "Manual Review Required", "Value": "See Raw Response", "Change (%)": None, "Period": "N/A"}
        ]
        
        df = pd.DataFrame(fallback_data)
        st.warning("⚠️ Created fallback data. Please check the debug section and try again.")
        
        # Show debug information
        with st.expander("🔍 Debug Information - Raw AI Response", expanded=True):
            st.text_area("Full AI Response:", structured_data, height=400)
            st.text_area("Cleaned JSON (if any):", clean_json_string(structured_data), height=200)
        
        return df
        
    except Exception as e:
        st.error(f"All parsing strategies failed: {str(e)}")
        return None

def get_safer_extraction_prompt(raw_text: str) -> str:
    """
    Generate a safer extraction prompt that's less likely to cause JSON issues
    """
    return f"""
Extract key performance metrics from this Google Ads report and return as valid JSON.

CRITICAL JSON RULES:
1. Use ONLY double quotes, never single quotes
2. Escape any quotes in string values with backslash
3. Use null (not "null") for missing values
4. Keep numbers as numbers, not strings for Change (%)
5. Remove % symbol from Change (%) values - just use the number
6. Be extra careful with product names containing quotes or special characters

Return EXACTLY this format:
[
  {{"Metric": "Clicks", "Value": "2025", "Change (%)": 11.3, "Period": "Month on Month"}},
  {{"Metric": "Impressions", "Value": "173.25K", "Change (%)": 33.9, "Period": "Month on Month"}},
  {{"Metric": "Cost", "Value": "£1564.51", "Change (%)": 22.4, "Period": "Month on Month"}},
  {{"Metric": "Conversions", "Value": "8.75", "Change (%)": -66.6, "Period": "Month on Month"}},
  {{"Metric": "CTR", "Value": "1.17%", "Change (%)": -16.9, "Period": "Month on Month"}},
  {{"Metric": "Average CPC", "Value": "£0.77", "Change (%)": 10.0, "Period": "Month on Month"}},
  {{"Metric": "Cost per Conversion", "Value": "£178.73", "Change (%)": 266.8, "Period": "Month on Month"}},
  {{"Metric": "Conversion Rate", "Value": "0.2%", "Change (%)": -81.9, "Period": "Month on Month"}}
]

Text to analyze:
{raw_text[:3000]}...

JSON only:"""

def get_change_class(change_str):
    """Return CSS class based on change direction"""
    if not change_str or str(change_str).lower() in ['null', 'none', '']:
        return 'change-neutral'
    
    # Extract numeric value
    try:
        # Remove % and + signs, keep - sign
        clean_str = str(change_str).replace('%', '').replace('+', '').strip()
        num_value = float(clean_str)
        
        if num_value > 0:
            return 'change-positive'
        elif num_value < 0:
            return 'change-negative'
        else:
            return 'change-neutral'
            
    except ValueError:
        # Fallback to string checking
        change_clean = str(change_str).strip()
        if change_clean.startswith('+'):
            return 'change-positive'
        elif change_clean.startswith('-'):
            return 'change-negative'
        else:
            return 'change-neutral'

def get_change_icon(change_str):
    """Return appropriate icon for change"""
    if not change_str or str(change_str).lower() in ['null', 'none', '']:
        return '●'
    
    # Extract numeric value
    try:
        # Remove % and + signs, keep - sign
        clean_str = str(change_str).replace('%', '').replace('+', '').strip()
        num_value = float(clean_str)
        
        if num_value > 0:
            return '↗'
        elif num_value < 0:
            return '↘'
        else:
            return '●'
            
    except ValueError:
        # Fallback to string checking
        change_clean = str(change_str).strip()
        if change_clean.startswith('+'):
            return '↗'
        elif change_clean.startswith('-'):
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
    """Format change values to ensure % symbol is shown and + sign for positive values"""
    if not change or pd.isna(change) or str(change).lower() in ['null', 'none', '']:
        return ''
    
    change_str = str(change).strip()
    
    # If it's empty after stripping, return empty
    if not change_str:
        return ''
    
    # If it already has %, work with it
    if '%' in change_str:
        # Extract the number part
        number_part = change_str.replace('%', '').strip()
    else:
        number_part = change_str
        
    # Try to convert to float to determine sign
    try:
        num_value = float(number_part)
        
        # Format with proper sign and %
        if num_value > 0:
            return f"+{abs(num_value)}%"
        elif num_value < 0:
            return f"-{abs(num_value)}%"
        else:
            return "0%"
            
    except ValueError:
        # If we can't parse as number, return as-is with % if not present
        if '%' not in change_str:
            return f"{change_str}%"
        return change_str

def get_clipboard_text(df: pd.DataFrame, analysis: str) -> str:
    """Create clipboard-friendly text version of the report"""
    clipboard_text = "📊 THE SEO WORKS - PPC ANALYSIS REPORT\n"
    clipboard_text += "=" * 50 + "\n\n"
    clipboard_text += f"Generated on: {time.strftime('%B %d, %Y')}\n\n"
    
    # Add metrics
    if not df.empty:
        clipboard_text += "KEY PERFORMANCE METRICS\n"
        clipboard_text += "-" * 30 + "\n\n"
        
        for _, row in df.iterrows():
            clipboard_text += f"• {row.get('Metric', '')}: {row.get('Value', '')}"
            if row.get('Change (%)', ''):
                clipboard_text += f" ({row.get('Change (%)', '')})"
            clipboard_text += f" [{row.get('Period', '')}]\n"
        
        clipboard_text += "\n"
    
    # Add analysis
    if analysis:
        clipboard_text += "ANALYSIS REPORT\n"
        clipboard_text += "-" * 20 + "\n\n"
        
        # Clean up analysis for plain text
        clean_analysis = analysis.replace('**', '').replace('##', '').replace('#', '')
        clipboard_text += clean_analysis
    
    return clipboard_text

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

# Add debug option in sidebar
debug_mode = st.sidebar.checkbox("🔍 Debug Mode", value=False)

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

            # AI Data Extraction - Updated Section
            st.subheader("🔍 Extracting Performance Metrics...")
            
            # Use the safer extraction prompt
            extraction_prompt = get_safer_extraction_prompt(raw_text)
            
            with st.spinner("🤖 AI is analyzing your data..."):
                structured_data = call_openai_api(extraction_prompt, model="gpt-4-turbo")

            if structured_data:
                # Show AI response in debug mode
                if debug_mode:
                    st.sidebar.subheader("🔍 AI Response Debug")
                    st.sidebar.text_area("Raw AI Response", structured_data, height=200)
                
                # Use the robust parsing function
                df = parse_structured_data(structured_data)
                
                if df is not None and not df.empty:
                    st.session_state.extracted_data = df
                    st.success("✅ Data extraction completed successfully!")
                else:
                    st.error("❌ Failed to extract valid data from the PDF.")
                    
                    # Offer manual retry with different approach
                    if st.button("🔄 Try Alternative Extraction Method"):
                        st.info("Attempting simpler extraction...")
                        
                        # Simpler prompt for problematic cases
                        simple_prompt = f"""
                        Extract the main metrics from this Google Ads report. Return as simple JSON array.
                        Focus only on the key metrics from the dashboard:
                        
                        From this text: {raw_text[:2000]}
                        
                        Return format:
                        [{{"Metric": "Clicks", "Value": "2025", "Change (%)": 11.3, "Period": "Month on Month"}}]
                        """
                        
                        simple_response = call_openai_api(simple_prompt, model="gpt-4-turbo")
                        if simple_response:
                            df_simple = parse_structured_data(simple_response)
                            if df_simple is not None:
                                st.session_state.extracted_data = df_simple
                                st.success("✅ Alternative extraction successful!")
                            else:
                                st.error("❌ Alternative extraction also failed.")
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

        # Export Options
        st.markdown("### 📤 Export Options")
        
        # Create export buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            # Simple CSV Export (no complex dependencies)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📊 Download CSV", 
                csv, 
                f"ads_analysis_{int(time.time())}.csv", 
                "text/csv",
                key="download_csv"
            )
        
        with col2:
            # Clipboard Copy
            if st.button("📋 Copy Text", key="copy_clipboard"):
                clipboard_text = get_clipboard_text(df, st.session_state.analysis_history[-1] if st.session_state.analysis_history else "")
                
                # Display the text in a text area for easy copying
                st.text_area(
                    "Copy this text to clipboard:",
                    value=clipboard_text,
                    height=200,
                    key="clipboard_text"
                )
                st.success("✅ Text ready to copy! Select all and copy from the text area above.")

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
                first_analysis = call_openai_api(analysis_prompt, model="gpt-4-turbo")
            
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
                            
                            new_analysis = call_openai_api(refine_prompt, model="gpt-4-turbo")
                            
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
