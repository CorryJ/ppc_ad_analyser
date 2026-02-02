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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Ad Analyser | The SEO Works",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect fill='%234f46e5' width='24' height='24' rx='4'/><path fill='white' d='M7 8h10v2H7zm0 4h10v2H7zm0 4h6v2H7z'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

client = openai.Client(api_key=OPENAI_API_KEY)
OPENAI_MODEL = "gpt-4o"

# Define banned words list
banned_words = "Everest, Matterhorn, levate, juncture, moreover, landscape, utilise, maze, labyrinth, cusp, hurdles, bustling, harnessing, unveiling the power,\
       realm, depicted, demystify, insurmountable, new era, poised, unravel, entanglement, unprecedented, eerie connection, unliving, \
       beacon, unleash, delve, enrich, multifaceted, elevate, discover, supercharge, unlock, unleash, tailored, elegant, delve, dive, \
       ever-evolving, pride, realm, meticulously, grappling, superior, weighing, merely, picture, architect, adventure, journey, embark, \
       navigate, navigation, navigating, enchanting, world, dazzle, tapestry, in this blog, in this article, dive-in, in today's, right place, \
       let's get started, imagine this, picture this, consider this, just explore"

# ═══════════════════════════════════════════════════════════════════════════════
# MODERN SAAS CSS DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════════════════════
       FONT IMPORTS - Inter & System UI Stack
       ═══════════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ═══════════════════════════════════════════════════════════════════════════
       CSS DESIGN TOKENS - Modern SaaS Palette
       ═══════════════════════════════════════════════════════════════════════════ */
    :root {
        /* Primary - Indigo */
        --primary-50: #eef2ff;
        --primary-100: #e0e7ff;
        --primary-200: #c7d2fe;
        --primary-500: #6366f1;
        --primary-600: #4f46e5;
        --primary-700: #4338ca;
        --primary-800: #3730a3;

        /* Slate Neutrals */
        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-300: #cbd5e1;
        --slate-400: #94a3b8;
        --slate-500: #64748b;
        --slate-600: #475569;
        --slate-700: #334155;
        --slate-800: #1e293b;
        --slate-900: #0f172a;

        /* Semantic Colors */
        --success-50: #f0fdf4;
        --success-500: #22c55e;
        --success-600: #16a34a;
        --warning-50: #fffbeb;
        --warning-500: #f59e0b;
        --danger-50: #fef2f2;
        --danger-500: #ef4444;
        --info-50: #eff6ff;
        --info-500: #3b82f6;

        /* Typography */
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-10: 2.5rem;
        --space-12: 3rem;
        --space-16: 4rem;

        /* Border Radius - 12px as specified */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-full: 9999px;

        /* Shadows - Soft & Subtle */
        --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

        /* Ring for focus states */
        --ring-primary: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       GLOBAL RESETS & BASE
       ═══════════════════════════════════════════════════════════════════════════ */
    #MainMenu, footer, header {
        visibility: hidden;
    }

    .stApp {
        background: var(--slate-50);
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--slate-900);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       SIDEBAR - Clean Navigation Panel
       ═══════════════════════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--slate-200);
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: var(--space-8);
    }

    section[data-testid="stSidebar"] * {
        color: var(--slate-700) !important;
    }

    /* Sidebar Section Headers */
    .sidebar-section {
        padding: var(--space-4) var(--space-6);
        margin-bottom: var(--space-2);
    }

    .sidebar-section-title {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--slate-400) !important;
        margin-bottom: var(--space-3);
    }

    .sidebar-section-title svg {
        width: 14px;
        height: 14px;
        stroke: currentColor;
        stroke-width: 2;
        fill: none;
    }

    /* File Uploader Styling */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: var(--slate-50);
        border: 2px dashed var(--slate-200);
        border-radius: var(--radius-md);
        padding: var(--space-6);
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-500);
        background: var(--primary-50);
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: var(--primary-600) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: var(--space-2) var(--space-4) !important;
        transition: all 0.15s ease !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
        background: var(--primary-700) !important;
        transform: translateY(-1px);
    }

    /* Sidebar Checkbox */
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        background: var(--slate-50);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-sm);
        border: 1px solid var(--slate-200);
        transition: all 0.15s ease;
    }

    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover {
        background: var(--slate-100);
        border-color: var(--slate-300);
    }

    /* Sidebar Help Text */
    .sidebar-help {
        padding: var(--space-4);
        background: var(--slate-50);
        border-radius: var(--radius-md);
        border: 1px solid var(--slate-100);
        margin: var(--space-4) 0;
    }

    .sidebar-help-title {
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--slate-800) !important;
        margin-bottom: var(--space-2);
    }

    .sidebar-help-text {
        font-size: 0.8125rem;
        color: var(--slate-500) !important;
        line-height: 1.5;
    }

    .sidebar-help-item {
        display: flex;
        align-items: flex-start;
        gap: var(--space-2);
        margin-bottom: var(--space-2);
    }

    .sidebar-help-item-number {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        background: var(--primary-100);
        color: var(--primary-700) !important;
        border-radius: var(--radius-full);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.6875rem;
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       HERO HEADER - Clean & Professional
       ═══════════════════════════════════════════════════════════════════════════ */
    .hero-header {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-lg);
        padding: var(--space-10) var(--space-8);
        margin-bottom: var(--space-8);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }

    .hero-header::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 40%;
        height: 100%;
        background: linear-gradient(135deg, transparent 50%, var(--primary-50) 100%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-1) var(--space-3);
        background: var(--primary-50);
        color: var(--primary-700);
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: var(--space-4);
    }

    .hero-title {
        font-family: var(--font-sans);
        font-size: clamp(1.75rem, 3vw, 2.5rem);
        font-weight: 700;
        color: var(--slate-900);
        letter-spacing: -0.025em;
        line-height: 1.2;
        margin: 0 0 var(--space-3) 0;
    }

    .hero-title-accent {
        background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 1.0625rem;
        color: var(--slate-500);
        font-weight: 400;
        line-height: 1.6;
        margin: 0;
        max-width: 560px;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       WELCOME STATE - Onboarding Card
       ═══════════════════════════════════════════════════════════════════════════ */
    .welcome-card {
        max-width: 720px;
        margin: var(--space-8) auto;
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-lg);
        padding: var(--space-12);
        box-shadow: var(--shadow-md);
        text-align: center;
    }

    .welcome-icon {
        width: 72px;
        height: 72px;
        background: linear-gradient(135deg, var(--primary-100), var(--primary-50));
        border: 1px solid var(--primary-200);
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto var(--space-6);
    }

    .welcome-icon svg {
        width: 36px;
        height: 36px;
        stroke: var(--primary-600);
        stroke-width: 1.5;
        fill: none;
    }

    .welcome-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--slate-900);
        margin: 0 0 var(--space-3) 0;
    }

    .welcome-description {
        font-size: 1rem;
        color: var(--slate-500);
        line-height: 1.7;
        margin: 0 0 var(--space-8) 0;
    }

    .steps-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-4);
        margin-bottom: var(--space-8);
    }

    @media (max-width: 640px) {
        .steps-container {
            grid-template-columns: 1fr;
        }
    }

    .step-card {
        background: var(--slate-50);
        border: 1px solid var(--slate-100);
        border-radius: var(--radius-md);
        padding: var(--space-5);
        text-align: center;
        transition: all 0.2s ease;
    }

    .step-card:hover {
        background: white;
        border-color: var(--slate-200);
        box-shadow: var(--shadow-sm);
        transform: translateY(-2px);
    }

    .step-number {
        width: 32px;
        height: 32px;
        background: var(--primary-600);
        color: white;
        border-radius: var(--radius-full);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8125rem;
        font-weight: 600;
        margin: 0 auto var(--space-3);
    }

    .step-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--slate-900);
        margin: 0 0 var(--space-1) 0;
    }

    .step-description {
        font-size: 0.8125rem;
        color: var(--slate-500);
        margin: 0;
        line-height: 1.5;
    }

    .features-row {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        justify-content: center;
    }

    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-2) var(--space-3);
        background: var(--success-50);
        color: var(--success-600);
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 500;
    }

    .feature-pill::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--success-500);
        border-radius: var(--radius-full);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       SECTION HEADERS - Organized Content
       ═══════════════════════════════════════════════════════════════════════════ */
    .section-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin-bottom: var(--space-6);
        padding-bottom: var(--space-4);
        border-bottom: 1px solid var(--slate-100);
    }

    .section-icon {
        width: 40px;
        height: 40px;
        background: var(--primary-600);
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
    }

    .section-icon svg {
        width: 20px;
        height: 20px;
        stroke: white;
        stroke-width: 2;
        fill: none;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--slate-900);
        margin: 0;
        letter-spacing: -0.01em;
    }

    .section-subtitle {
        font-size: 0.875rem;
        color: var(--slate-400);
        margin: 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       METRIC CARDS - Data Display
       ═══════════════════════════════════════════════════════════════════════════ */
    .metric-card {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-md);
        padding: var(--space-5);
        box-shadow: var(--shadow-xs);
        transition: all 0.2s ease;
        position: relative;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: var(--primary-600);
        border-radius: var(--radius-md) 0 0 var(--radius-md);
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    .metric-card:hover {
        border-color: var(--primary-200);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--slate-500);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: var(--space-1);
    }

    .metric-period {
        font-size: 0.6875rem;
        color: var(--slate-400);
        margin-bottom: var(--space-3);
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--slate-900);
        letter-spacing: -0.02em;
        line-height: 1;
        margin-bottom: var(--space-2);
    }

    .metric-change {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        font-size: 0.8125rem;
        font-weight: 600;
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
    }

    .change-positive {
        background: var(--success-50);
        color: var(--success-600);
    }

    .change-negative {
        background: var(--danger-50);
        color: var(--danger-500);
    }

    .change-neutral {
        background: var(--slate-100);
        color: var(--slate-500);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       ANALYSIS CARDS - AI Content Display
       ═══════════════════════════════════════════════════════════════════════════ */
    .analysis-card {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        margin-bottom: var(--space-6);
        overflow: hidden;
    }

    .analysis-header {
        background: var(--slate-50);
        border-bottom: 1px solid var(--slate-200);
        padding: var(--space-4) var(--space-6);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .analysis-header-left {
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }

    .analysis-badge {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .analysis-badge svg {
        width: 18px;
        height: 18px;
        stroke: white;
        stroke-width: 2;
        fill: none;
    }

    .analysis-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--slate-900);
        margin: 0;
    }

    .analysis-version {
        font-size: 0.75rem;
        color: var(--slate-400);
        font-weight: 400;
    }

    .analysis-content {
        padding: var(--space-6);
        line-height: 1.75;
        color: var(--slate-700);
        font-size: 0.9375rem;
    }

    .analysis-content h2,
    .analysis-content h3,
    .analysis-content strong {
        color: var(--slate-900);
    }

    .analysis-content h2 {
        font-size: 1.125rem;
        font-weight: 600;
        margin: var(--space-6) 0 var(--space-3) 0;
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--slate-100);
    }

    .analysis-content h2:first-child {
        margin-top: 0;
    }

    .analysis-content p {
        margin-bottom: var(--space-4);
    }

    .analysis-content ul,
    .analysis-content ol {
        margin: var(--space-4) 0;
        padding-left: var(--space-6);
    }

    .analysis-content li {
        margin-bottom: var(--space-2);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       REFINEMENT INPUT
       ═══════════════════════════════════════════════════════════════════════════ */
    .refinement-card {
        background: var(--slate-50);
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-md);
        padding: var(--space-5);
        margin-top: var(--space-4);
    }

    .refinement-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--slate-700);
        margin: 0 0 var(--space-3) 0;
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       BUTTONS - High Contrast Primary Actions
       ═══════════════════════════════════════════════════════════════════════════ */
    .stButton > button {
        background: var(--primary-600) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: var(--space-3) var(--space-5) !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        box-shadow: var(--shadow-sm), 0 1px 2px rgba(79, 70, 229, 0.1) !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background: var(--primary-700) !important;
        box-shadow: var(--shadow-md), 0 4px 12px rgba(79, 70, 229, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Download Button - Secondary Style */
    .stDownloadButton > button {
        background: white !important;
        color: var(--slate-700) !important;
        border: 1px solid var(--slate-200) !important;
        border-radius: var(--radius-sm) !important;
        padding: var(--space-2) var(--space-4) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        box-shadow: var(--shadow-xs) !important;
        transition: all 0.15s ease !important;
    }

    .stDownloadButton > button:hover {
        background: var(--slate-50) !important;
        border-color: var(--primary-300) !important;
        color: var(--primary-700) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       FORM INPUTS
       ═══════════════════════════════════════════════════════════════════════════ */
    .stTextArea textarea {
        border: 1px solid var(--slate-200) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.9375rem !important;
        padding: var(--space-4) !important;
        transition: all 0.15s ease !important;
        background: white !important;
        line-height: 1.6 !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--primary-500) !important;
        box-shadow: var(--ring-primary) !important;
        outline: none !important;
    }

    .stTextArea textarea::placeholder {
        color: var(--slate-400) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       STATUS MESSAGES - Toast-style Feedback
       ═══════════════════════════════════════════════════════════════════════════ */
    .stSuccess {
        background: var(--success-50) !important;
        border: 1px solid rgba(34, 197, 94, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--slate-700) !important;
        padding: var(--space-3) var(--space-4) !important;
    }

    .stInfo {
        background: var(--info-50) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--slate-700) !important;
        padding: var(--space-3) var(--space-4) !important;
    }

    .stWarning {
        background: var(--warning-50) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--slate-700) !important;
        padding: var(--space-3) var(--space-4) !important;
    }

    .stError {
        background: var(--danger-50) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--slate-700) !important;
        padding: var(--space-3) var(--space-4) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       EXPANDERS
       ═══════════════════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: var(--slate-50) !important;
        border: 1px solid var(--slate-200) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        color: var(--slate-700) !important;
        font-size: 0.875rem !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--slate-100) !important;
    }

    .streamlit-expanderContent {
        border: 1px solid var(--slate-200) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       EXPORT SECTION
       ═══════════════════════════════════════════════════════════════════════════ */
    .export-card {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-md);
        padding: var(--space-5);
        margin: var(--space-6) 0;
    }

    .export-title {
        font-size: 0.9375rem;
        font-weight: 600;
        color: var(--slate-900);
        margin: 0 0 var(--space-4) 0;
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       FOOTER
       ═══════════════════════════════════════════════════════════════════════════ */
    .footer {
        text-align: center;
        padding: var(--space-8) 0;
        margin-top: var(--space-12);
        border-top: 1px solid var(--slate-100);
    }

    .footer-text {
        font-size: 0.8125rem;
        color: var(--slate-400);
    }

    .footer-brand {
        color: var(--primary-600);
        font-weight: 500;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       SPINNER OVERRIDE
       ═══════════════════════════════════════════════════════════════════════════ */
    .stSpinner > div {
        border-top-color: var(--primary-600) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       PERIOD SECTION TITLES
       ═══════════════════════════════════════════════════════════════════════════ */
    .period-title {
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--slate-600);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: var(--space-6) 0 var(--space-4) 0;
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--slate-100);
    }

    /* ═══════════════════════════════════════════════════════════════════════════
       RESPONSIVE DESIGN
       ═══════════════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .hero-header {
            padding: var(--space-6);
        }

        .hero-title {
            font-size: 1.5rem;
        }

        .welcome-card {
            padding: var(--space-6);
        }

        .metric-value {
            font-size: 1.5rem;
        }

        .analysis-content {
            padding: var(--space-4);
        }

        .steps-container {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_uploaded_file(uploaded_file) -> bool:
    """Validate uploaded file"""
    if not uploaded_file:
        return False

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File size exceeds 10MB limit. Please upload a smaller file.")
        return False

    if not uploaded_file.name.lower().endswith('.pdf'):
        st.error("Invalid file type. Please upload a PDF file.")
        return False

    return True

def extract_pdf_text(uploaded_file) -> Optional[str]:
    """Extract text from all pages of PDF"""
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
                    st.warning(f"Could not extract text from page {i+1}")
                    continue

            if pages_processed == 0:
                st.error("No readable text found in the PDF.")
                return None

            st.toast(f"Extracted text from {pages_processed} page(s)", icon="✅")
            return all_text.strip()

    except Exception as e:
        st.error(f"Failed to process PDF: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def cached_openai_call(prompt_hash: str, prompt: str, model: str = OPENAI_MODEL) -> Optional[str]:
    """Cached OpenAI API call"""
    return call_openai_api_with_retry(prompt, model)

def call_openai_api_with_retry(prompt: str, model: str = OPENAI_MODEL, max_retries: int = 3) -> Optional[str]:
    """Call OpenAI API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant specialized in parsing advertising reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            return response.choices[0].message.content

        except openai.RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1
                st.warning(f"Rate limit reached. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            st.error("Rate limit exceeded. Please try again later.")
            return None

        except openai.APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            st.error(f"API error: {str(e)}")
            return None

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            st.error(f"Unexpected error: {str(e)}")
            return None

    return None

def call_openai_api(prompt: str, model: str = OPENAI_MODEL) -> Optional[str]:
    """Main OpenAI API call function with caching"""
    prompt_hash = hashlib.md5(f"{prompt}{model}".encode()).hexdigest()
    return cached_openai_call(prompt_hash, prompt, model)

def clean_json_string(json_str: str) -> str:
    """Comprehensive JSON string cleaning"""
    if '```json' in json_str:
        json_str = json_str.split('```json')[1].split('```')[0].strip()
    elif '```' in json_str:
        json_str = json_str.split('```')[1].split('```')[0].strip()

    start_idx = json_str.find('[')
    end_idx = json_str.rfind(']') + 1

    if start_idx != -1 and end_idx > start_idx:
        json_str = json_str[start_idx:end_idx]

    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)

    json_str = json_str.replace('+∞%', 'null')
    json_str = json_str.replace('-∞%', 'null')
    json_str = json_str.replace('∞%', 'null')
    json_str = json_str.replace('+∞', 'null')
    json_str = json_str.replace('-∞', 'null')
    json_str = json_str.replace('∞', 'null')

    json_str = json_str.replace('True', 'true').replace('False', 'false').replace('None', 'null')
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

    return json_str

def parse_structured_data(structured_data: str) -> Optional[pd.DataFrame]:
    """Enhanced parsing function with multiple fallback strategies"""
    if not structured_data or not structured_data.strip():
        st.error("No data received from AI analysis.")
        return None

    try:
        cleaned_json = clean_json_string(structured_data)
        data = json.loads(cleaned_json)

        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            st.toast(f"Parsed {len(data)} metrics successfully", icon="✅")
            return df

    except json.JSONDecodeError:
        pass

    try:
        metrics_data = []
        object_pattern = r'\{\s*"Metric"\s*:\s*"([^"]+)"\s*,\s*"Value"\s*:\s*"([^"]+)"\s*,\s*"Change \(%\)"\s*:\s*([^,}]+)\s*,\s*"Period"\s*:\s*"([^"]+)"\s*\}'
        matches = re.findall(object_pattern, structured_data, re.DOTALL)

        for match in matches:
            metric, value, change, period = match
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
            st.toast(f"Extracted {len(metrics_data)} metrics", icon="✅")
            return df

    except Exception:
        pass

    st.error("Failed to parse metrics data.")
    with st.expander("Debug: Raw AI Response"):
        st.code(structured_data, language="json")
    return None

def get_safer_extraction_prompt(raw_text: str) -> str:
    """Generate extraction prompt"""
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

    try:
        clean_str = str(change_str).replace('%', '').replace('+', '').strip()
        num_value = float(clean_str)

        if num_value > 0:
            return 'change-positive'
        elif num_value < 0:
            return 'change-negative'
        else:
            return 'change-neutral'

    except ValueError:
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
        return '—'

    try:
        clean_str = str(change_str).replace('%', '').replace('+', '').strip()
        num_value = float(clean_str)

        if num_value > 0:
            return '↑'
        elif num_value < 0:
            return '↓'
        else:
            return '—'

    except ValueError:
        return '—'

def format_metric_value(value):
    """Format metric values"""
    if not value or pd.isna(value):
        return str(value)

    value_str = str(value).strip()

    if '£' in value_str or '%' in value_str:
        return value_str

    clean_value = value_str.replace(',', '')

    try:
        num_value = float(clean_value)

        if ',' in value_str and num_value > 100:
            return f"£{value_str}"

        if 0 < num_value < 5 and '.' in clean_value:
            return f"{value_str}%"

    except ValueError:
        pass

    return value_str

def format_change_value(change):
    """Format change values"""
    if not change or pd.isna(change) or str(change).lower() in ['null', 'none', '']:
        return ''

    change_str = str(change).strip()

    if not change_str:
        return ''

    if '%' in change_str:
        number_part = change_str.replace('%', '').strip()
    else:
        number_part = change_str

    try:
        num_value = float(number_part)

        if num_value > 0:
            return f"+{abs(num_value):.1f}%"
        elif num_value < 0:
            return f"-{abs(num_value):.1f}%"
        else:
            return "0%"

    except ValueError:
        if '%' not in change_str:
            return f"{change_str}%"
        return change_str

def get_clipboard_text(df: pd.DataFrame, analysis: str) -> str:
    """Create clipboard-friendly text version of the report"""
    clipboard_text = "THE SEO WORKS - PPC ANALYSIS REPORT\n"
    clipboard_text += "=" * 50 + "\n\n"
    clipboard_text += f"Generated: {time.strftime('%B %d, %Y')}\n\n"

    if not df.empty:
        clipboard_text += "KEY PERFORMANCE METRICS\n"
        clipboard_text += "-" * 30 + "\n\n"

        for _, row in df.iterrows():
            clipboard_text += f"• {row.get('Metric', '')}: {row.get('Value', '')}"
            if row.get('Change (%)', ''):
                clipboard_text += f" ({row.get('Change (%)', '')})"
            clipboard_text += f" [{row.get('Period', '')}]\n"

        clipboard_text += "\n"

    if analysis:
        clipboard_text += "ANALYSIS\n"
        clipboard_text += "-" * 20 + "\n\n"
        clean_analysis = analysis.replace('**', '').replace('##', '').replace('#', '')
        clipboard_text += clean_analysis

    return clipboard_text

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
        </svg>
        AI-Powered Analysis
    </div>
    <h1 class="hero-title">The SEO Works <span class="hero-title-accent">Ad Analyser</span></h1>
    <p class="hero-subtitle">Transform your Google Ads reports into actionable insights with intelligent analysis and clear recommendations.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def reset_analysis_state():
    """Reset analysis state when file changes"""
    st.session_state.extracted_data = None
    st.session_state.analysis_history = []

with st.sidebar:
    st.markdown("""<div class="sidebar-section">
<div class="sidebar-section-title">
<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
Upload Report
</div>
</div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose PDF file", 
        type=["pdf"], 
        label_visibility="collapsed",
        on_change=reset_analysis_state
    )

    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.success(f"{uploaded_file.name} ({file_size_mb:.1f} MB)")

    st.markdown("---")

    st.markdown("""<div class="sidebar-section">
<div class="sidebar-section-title">
<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
Settings
</div>
</div>""", unsafe_allow_html=True)

    debug_mode = st.checkbox("Debug mode", value=False, help="Show detailed processing information")

    st.markdown("---")

    st.markdown("""<div class="sidebar-help">
<div class="sidebar-help-title">How it works</div>
<div class="sidebar-help-item">
<span class="sidebar-help-item-number">1</span>
<span class="sidebar-help-text">Upload your Google Ads PDF report</span>
</div>
<div class="sidebar-help-item">
<span class="sidebar-help-item-number">2</span>
<span class="sidebar-help-text">AI extracts key metrics automatically</span>
</div>
<div class="sidebar-help-item">
<span class="sidebar-help-item-number">3</span>
<span class="sidebar-help-text">Review insights and refine with prompts</span>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="sidebar-help" style="margin-top: var(--space-4);">
<div class="sidebar-help-title">Requirements</div>
<div class="sidebar-help-text">
• PDF with readable text<br>
• Maximum file size: 10MB<br>
• Multi-page reports supported
</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
if uploaded_file:
    if st.session_state.extracted_data is None:
        with st.status("Processing your report...", expanded=True) as status:
            st.write("Extracting text from PDF...")
            raw_text = extract_pdf_text(uploaded_file)

            if raw_text:
                if st.checkbox("Show extracted text"):
                    st.text_area("Raw text", raw_text, height=200, label_visibility="collapsed")

                st.write("Analysing with AI...")
                extraction_prompt = get_safer_extraction_prompt(raw_text)
                structured_data = call_openai_api(extraction_prompt)

                if structured_data:
                    if debug_mode:
                        if st.checkbox("Show AI Response Debug"):
                            st.code(structured_data, language="json")

                    st.write("Parsing metrics...")
                    df = parse_structured_data(structured_data)

                    if df is not None and not df.empty:
                        st.session_state.extracted_data = df
                        status.update(label="Analysis complete", state="complete", expanded=False)
                    else:
                        status.update(label="Extraction failed", state="error")

                        if st.button("Try alternative extraction"):
                            simple_prompt = f"""
                            Extract metrics from this Google Ads report as simple JSON:
                            {raw_text[:2000]}
                            Format: [{{"Metric": "Clicks", "Value": "2025", "Change (%)": 11.3, "Period": "Month on Month"}}]
                            """
                            simple_response = call_openai_api(simple_prompt)
                            if simple_response:
                                df_simple = parse_structured_data(simple_response)
                                if df_simple is not None:
                                    st.session_state.extracted_data = df_simple
                                    st.rerun()
                else:
                    status.update(label="AI analysis failed", state="error")
            else:
                status.update(label="Could not extract PDF text", state="error")

    # Display data if available
    if st.session_state.extracted_data is not None:
        df = st.session_state.extracted_data

        # Metrics Section
        st.markdown("""<div class="section-header">
<div class="section-icon">
<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
</div>
<div>
<h2 class="section-title">Key Metrics</h2>
<p class="section-subtitle">Performance data from your report</p>
</div>
</div>""", unsafe_allow_html=True)

        if 'Period' in df.columns:
            mom_metrics = df[df['Period'] == 'Month on Month'] if 'Month on Month' in df['Period'].values else pd.DataFrame()
            yoy_metrics = df[df['Period'] == 'Year on Year'] if 'Year on Year' in df['Period'].values else pd.DataFrame()

            if not mom_metrics.empty:
                st.markdown('<p class="period-title">Month on Month</p>', unsafe_allow_html=True)

                cols = st.columns(3)
                for idx, (_, metric) in enumerate(mom_metrics.iterrows()):
                    col_idx = idx % 3
                    formatted_value = format_metric_value(metric['Value'])
                    formatted_change = format_change_value(metric.get('Change (%)', ''))
                    change_class = get_change_class(formatted_change)
                    change_icon = get_change_icon(formatted_change)

                    with cols[col_idx]:
                        st.markdown(f"""<div class="metric-card">
<div class="metric-label">{metric['Metric']}</div>
<div class="metric-period">{metric['Period']}</div>
<div class="metric-value">{formatted_value}</div>
{f'<span class="metric-change {change_class}">{change_icon} {formatted_change}</span>' if formatted_change else ''}
</div>""", unsafe_allow_html=True)

                    if col_idx == 2 and idx < len(mom_metrics) - 1:
                        cols = st.columns(3)

            if not yoy_metrics.empty:
                st.markdown('<p class="period-title">Year on Year</p>', unsafe_allow_html=True)

                cols = st.columns(3)
                for idx, (_, metric) in enumerate(yoy_metrics.iterrows()):
                    col_idx = idx % 3
                    formatted_value = format_metric_value(metric['Value'])
                    formatted_change = format_change_value(metric.get('Change (%)', ''))
                    change_class = get_change_class(formatted_change)
                    change_icon = get_change_icon(formatted_change)

                    with cols[col_idx]:
                        st.markdown(f"""<div class="metric-card">
<div class="metric-label">{metric['Metric']}</div>
<div class="metric-period">{metric['Period']}</div>
<div class="metric-value">{formatted_value}</div>
{f'<span class="metric-change {change_class}">{change_icon} {formatted_change}</span>' if formatted_change else ''}
</div>""", unsafe_allow_html=True)

                    if col_idx == 2 and idx < len(yoy_metrics) - 1:
                        cols = st.columns(3)
        else:
            st.dataframe(df, use_container_width=True)

        # Export Section
        st.markdown("""<div class="export-card">
<h3 class="export-title">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
<polyline points="7 10 12 15 17 10"/>
<line x1="12" y1="15" x2="12" y2="3"/>
</svg>
Export Data
</h3>
</div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                csv,
                f"ppc_analysis_{int(time.time())}.csv",
                "text/csv",
                key="download_csv"
            )

        with col2:
            if st.button("Copy as text", key="copy_clipboard"):
                clipboard_text = get_clipboard_text(df, st.session_state.analysis_history[-1] if st.session_state.analysis_history else "")
                st.text_area("Select and copy:", value=clipboard_text, height=150, key="clipboard_text", label_visibility="collapsed")

        # Generate Analysis
        if not st.session_state.analysis_history:
            st.markdown("""<div class="section-header">
<div class="section-icon">
<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
</div>
<div>
<h2 class="section-title">AI Analysis</h2>
<p class="section-subtitle">Generating comprehensive insights</p>
</div>
</div>""", unsafe_allow_html=True)

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
            with st.spinner("Generating analysis..."):
                first_analysis = call_openai_api(analysis_prompt)

            if first_analysis:
                st.session_state.analysis_history.append(first_analysis)
                st.toast("Analysis complete", icon="✅")
            else:
                st.error("Failed to generate analysis.")

        # Display Analysis
        for i, analysis in enumerate(st.session_state.analysis_history):
            st.markdown(f"""<div class="analysis-card">
<div class="analysis-header">
<div class="analysis-header-left">
<div class="analysis-badge">
<svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
</div>
<div>
<h3 class="analysis-title">Analysis</h3>
<span class="analysis-version">Version {i+1}</span>
</div>
</div>
</div>
<div class="analysis-content">""", unsafe_allow_html=True)

            st.markdown(analysis)

            st.markdown("</div></div>", unsafe_allow_html=True)

            # Refinement
            st.markdown(f"""<div class="refinement-card">
<h4 class="refinement-title">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
</svg>
Refine this analysis
</h4>
</div>""", unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1])

            with col1:
                user_prompt = st.text_area(
                    f"Instructions for version {i+1}:",
                    key=f"user_input_{i}",
                    placeholder="e.g., Focus more on conversion trends, or add recommendations for budget allocation...",
                    label_visibility="collapsed"
                )

            with col2:
                if st.button("Improve", key=f"refine_button_{i}"):
                    if user_prompt.strip():
                        with st.spinner("Refining..."):
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

                            new_analysis = call_openai_api(refine_prompt)

                            if new_analysis:
                                st.session_state.analysis_history.append(new_analysis)
                                st.toast("Refinement complete", icon="✅")
                                st.rerun()
                            else:
                                st.error("Failed to generate refined analysis.")
                    else:
                        st.warning("Please enter instructions first.")

else:
    # Welcome State
    st.markdown("""<div class="welcome-card">
<div class="welcome-icon">
<svg viewBox="0 0 24 24">
<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
<polyline points="14 2 14 8 20 8"/>
<line x1="16" y1="13" x2="8" y2="13"/>
<line x1="16" y1="17" x2="8" y2="17"/>
<polyline points="10 9 9 9 8 9"/>
</svg>
</div>
<h2 class="welcome-title">Upload your Google Ads report</h2>
<p class="welcome-description">
Get instant AI-powered analysis of your PPC performance. Upload a PDF report
and receive clear metrics, trends, and actionable recommendations.
</p>
<div class="steps-container">
<div class="step-card">
<div class="step-number">1</div>
<h4 class="step-title">Upload</h4>
<p class="step-description">Drop your PDF report in the sidebar</p>
</div>
<div class="step-card">
<div class="step-number">2</div>
<h4 class="step-title">Analyse</h4>
<p class="step-description">AI extracts metrics and insights</p>
</div>
<div class="step-card">
<div class="step-number">3</div>
<h4 class="step-title">Refine</h4>
<p class="step-description">Customise with follow-up prompts</p>
</div>
</div>
<div class="features-row">
<span class="feature-pill">Multi-page PDFs</span>
<span class="feature-pill">Auto metric extraction</span>
<span class="feature-pill">AI insights</span>
<span class="feature-pill">CSV export</span>
<span class="feature-pill">Analysis history</span>
</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <p class="footer-text">Powered by <span class="footer-brand">The SEO Works</span></p>
</div>
""", unsafe_allow_html=True)