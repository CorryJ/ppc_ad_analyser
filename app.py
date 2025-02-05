import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import os
from openai import OpenAI

# Initialise OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 

# Function to extract data from an image
def extract_data_from_image(image):
    # Perform OCR
    text = pytesseract.image_to_string(image)
    
    # Process the OCR text to create a structured DataFrame (modify as needed)
    data = {
        "Metric": [
            "Cost", "Conv.", "Cost / conv.", "Conversion Rate", "CTR",
            "Search Impression Share", "Search Lost IS (budget)", 
            "Search Lost IS (rank)", "Avg. CPC"
        ],
        "Value": [
            "£4,035.32", "39.97", "£100.97", "5.9%", "2.33%", "9.99%", 
            "58.41%", "33.11%", "£5.96"
        ],
        "Change": [
            "-5.0%", "+14.9%", "-17.3%", "+17.8%", "+5.6%", "-2.0%", 
            "+23.9%", "-22.4%", "-2.7%"
        ]
    }
    df = pd.DataFrame(data)
    return df

# Streamlit app
st.title("Google Ads Data Analysis App")

# Upload image
uploaded_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Load image
    image = Image.open(uploaded_file)
    
    # Display uploaded image
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Extract data
    st.write("Extracting data...")
    df = extract_data_from_image(image)
    
    # Display extracted data
    st.write("Extracted Data:")
    st.dataframe(df)

    # Prepare the extracted data for AI analysis
    table_text = df.to_string(index=False)


    # Banned words
    bannedWord1 = "Everest, Matterhorn, levate, juncture, moreover, landscape, utilise, maze, labyrinth, cusp, hurdles, bustling, harnessing, unveiling the power,\
       realm, depicted, demystify, insurmountable, new era, poised, unravel, entanglement, unprecedented, eerie connection, unliving, \
       beacon, unleash, delve, enrich, multifaceted, elevate, discover, supercharge, unlock, unleash, tailored, elegant, delve, dive, \
       ever-evolving, pride, realm,  meticulously, grappling, superior, weighing,  merely, picture, architect, adventure, journey, embark , \
       navigate, navigation, navigating, enchanting, world, dazzle, tapestry, in this blog, in this article, dive-in, in today's, right place, \
        let's get started, imagine this, picture this, consider this, just explore"
    
    # Define AI prompt
    analysis_prompt = f"""
    You are a Google Ads expert. Here is a table containing key Google Ads performance metrics:

    {table_text}

    Please provide a summary of the table and recommendations to improve performance. Write in UK English at all times e.g. (e.g., humanise instead of humanize, colour instead of color).  \
2. Avoid jargon and unnecessarily complex word choices. 4. Clarity is crucial. Do not use emojis or exclamation marks. 3. You MUST not include any of the following words in the response:\
        {0}".format(bannedWor
    """

    # Send request to ChatGPT-4o
    with st.spinner("Analysing table with AI..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": analysis_prompt}]
            )

            # Extract AI response
            ai_analysis = response.choices[0].message.content

            # Display AI-generated analysis
            st.subheader("AI Analysis & Recommendations")
            st.write(ai_analysis)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
