import streamlit as st
import pandas as pd
import re
import io
import os
import base64
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from pypdf import PdfReader
from google import genai
import docx
import math


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sensitive Data Detection & Compliance Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR PREMIUM GLASSMORPHIC DESIGN (dashboard only) ---
st.markdown(
    """
    <style>
    /* Global Styles — clean premium white background with dark slate text */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    /* Remove default Streamlit top padding to eliminate gap at the top */
    [data-testid="stMainBlockContainer"], .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2rem !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        font-weight: 700;
        color: #0f172a !important;
    }
    
    /* Hero Title Styling */
    .hero-title {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    .hero-subtitle {
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* KPI Metric Cards styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    
    /* Styled Containers */
    .glass-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
        color: #0f172a !important;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 9999px;
        color: white !important;
    }
    .badge-low  { background-color: #10b981; }
    .badge-medium { background-color: #f59e0b; }
    .badge-high { background-color: #ef4444; }
    
    /* Table modifications */
    .dataframe { border-radius: 8px; overflow: hidden; }
    
    /* AI Response box */
    .qa-box {
        background: rgba(99, 102, 241, 0.05);
        border-left: 4px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin-top: 16px;
        color: #0f172a !important;
    }
    
    /* Hide deploy button and header top-bar completely */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* --- DASHBOARD PRE-UPLOAD STATE UI --- */
    .dash-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .dash-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .dash-logo-icon {
        font-size: 1.4rem;
        vertical-align: middle;
    }
    .dash-logo-text {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.15rem;
        color: #475569;
    }
    .dash-nav-actions {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .dash-play-btn {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 50%;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 0.75rem;
        color: #475569;
        transition: background 0.15s;
    }
    .dash-play-btn:hover {
        background: #e2e8f0;
    }
    .dash-export-btn {
        background: #f1f5f9;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem 1.1rem;
        font-weight: 500;
        font-size: 0.85rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        transition: background 0.15s;
    }
    .dash-export-btn:hover {
        background: #e2e8f0;
    }
    
    .upload-card {
        border: 1px dashed #cbd5e1;
        border-radius: 12px;
        background-color: #f9fafb;
        padding: 3rem 2rem;
        text-align: center;
        max-width: 900px;
        margin: 0 auto 2.5rem auto;
    }
    .upload-card-icons {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        margin-bottom: 1.2rem;
    }
    .file-badge {
        font-size: 0.68rem;
        font-weight: 700;
        border: 1.5px solid #cbd5e1;
        border-radius: 4px;
        padding: 0.25rem 0.5rem;
        color: #64748b;
        background: #ffffff;
        letter-spacing: 0.05em;
    }
    
    /* Streamlit native uploader custom blending */
    [data-testid="stFileUploader"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] label {
        display: none !important;
    }
    [data-testid="stFileUploaderHeader"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] > div {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] small {
        display: none !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2.2rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transition: background 0.15s, transform 0.1s !important;
        cursor: pointer !important;
        margin-top: 0.5rem !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #1e1e1e !important;
        transform: translateY(-1px) !important;
    }
    
    /* Timeline / How It Works layout */
    .timeline-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #0f172a;
        margin-bottom: 1.2rem;
        text-align: left;
    }
    .timeline {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        margin-bottom: 3rem;
        padding-left: 0.5rem;
    }
    .timeline-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    .step-icon-wrap {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .blue-bg { background-color: #e0f2fe; color: #0284c7; }
    .green-bg { background-color: #dcfce7; color: #16a34a; }
    .purple-bg { background-color: #f3e8ff; color: #7c3aed; }
    
    .step-text {
        text-align: left;
    }
    .step-text h4 {
        margin: 0 0 0.2rem 0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }
    .step-text p {
        margin: 0 !important;
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.4;
    }
    
    /* Bottom status cards */
    .status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .status-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2.2rem 1.5rem;
        text-align: center;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.01);
    }
    .status-card-icon {
        font-size: 1.6rem;
        color: #94a3b8;
        margin-bottom: 0.8rem;
    }
    .status-card h4 {
        margin: 0 0 0.3rem 0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    .status-card p {
        margin: 0 !important;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONSTANTS & HELPERS ---
RISK_WEIGHTS = {
    "Aadhaar Number": 20,
    "Credit Card Number": 20,
    "API Key / Secret": 25,
    "Password Field": 20,
    "PAN Number": 15,
    "Bank Account Number": 15,
    "IFSC Code": 10,
    "Email Address": 5,
    "Phone Number": 5,
    "Employee ID": 5,
    "Confidential Keywords": 5,
}

def luhn_checksum(card_number: str) -> bool:
    """Validate credit card number using Luhn Algorithm."""
    cleaned = re.sub(r"\D", "", card_number)
    if not cleaned or len(cleaned) < 13 or len(cleaned) > 16:
        return False
    
    total = 0
    reverse_digits = cleaned[::-1]
    for idx, digit in enumerate(reverse_digits):
        val = int(digit)
        if idx % 2 == 1:
            val *= 2
            if val > 9:
                val -= 9
        total += val
    return total % 10 == 0

def mask_value(val: str) -> str:
    """Mask value to show only first and last characters, with middle as asterisks."""
    val_str = str(val).strip()
    if len(val_str) <= 2:
        return "*" * len(val_str)
    return val_str[0] + "*" * (len(val_str) - 2) + val_str[-1]

def get_context_around(text: str, start: int, end: int, window: int = 30) -> str:
    """Get characters surrounding match for contextual visibility."""
    start_context = max(0, start - window)
    end_context = min(len(text), end + window)
    prefix = "..." if start_context > 0 else ""
    suffix = "..." if end_context < len(text) else ""
    snippet = text[start_context:end_context].replace("\n", " ")
    return f"{prefix}{snippet}{suffix}"

# --- FILE PARSING ENGINE ---
def extract_text_from_txt(uploaded_file) -> str:
    """Extract string from raw text upload."""
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("latin-1")
        except Exception as e:
            raise ValueError(f"Failed to decode text file: {e}")

def extract_text_from_pdf(uploaded_file) -> tuple[str, list[dict]]:
    """Extract string and page mappings from PDF upload."""
    uploaded_file.seek(0)
    pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
    full_text = ""
    page_offsets = []
    
    for idx, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text() or ""
        start_offset = len(full_text)
        full_text += page_text + "\n"
        end_offset = len(full_text)
        page_offsets.append({
            "page": idx + 1,
            "start": start_offset,
            "end": end_offset
        })
        
    return full_text, page_offsets

def extract_text_from_docx(uploaded_file) -> str:
    """Extract string from docx upload."""
    uploaded_file.seek(0)
    doc = docx.Document(io.BytesIO(uploaded_file.read()))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_csv(uploaded_file) -> tuple[str, list[dict], pd.DataFrame]:
    """Extract string and row mappings from CSV upload, returning DataFrame."""
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Could not parse CSV: {e}")
        
    full_text = ""
    row_offsets = []
    
    for idx, row in df.iterrows():
        row_str = f"Row {idx + 1}: " + ", ".join([f"{col}: {val}" for col, val in row.items()]) + "\n"
        start_offset = len(full_text)
        full_text += row_str
        end_offset = len(full_text)
        row_offsets.append({
            "row": idx + 1,
            "start": start_offset,
            "end": end_offset
        })
        
    return full_text, row_offsets, df

def is_part_of_longer_sequence(text: str, start: int, end: int) -> bool:
    """Check if the matched segment is a subset of a longer sequence of digits/separators."""
    before = text[max(0, start - 10):start]
    after = text[end:min(len(text), end + 10)]
    
    if re.search(r'\d[- ]*$', before):
        return True
    if re.search(r'^[- ]*\d', after):
        return True
    return False

# --- CORE SENSITIVE DATA DETECTION ENGINE ---
def detect_sensitive_data(text: str, page_offsets: list = None, row_offsets: list = None, file_type: str = "TXT") -> list:
    """Scan text against named regexes in priority order to prevent double-matching."""
    findings = []
    
    patterns = {
        "Aadhaar Number": r"\b[2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4}\b",
        "PAN Number": r"\b[A-Za-z]{5}\d{4}[A-Za-z]\b",
        "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "Phone Number": r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b",
        "Credit Card Number": r"\b(?:\d[-\s]?){13,16}\b",
        "Bank Account Number": r"\b\d{9,18}\b",
        "IFSC Code": r"\b[A-Za-z]{4}0[A-Za-z0-9]{6}\b",
        "API Key / Secret": r"\b(?:sk|pk|api|token|secret)[-_][a-zA-Z0-9]{16,}\b",
        "Password Field": r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*([^\s,;\"']+)",
        "Employee ID": r"(?i)\bEMP-\d+\b",
        "Confidential Keywords": r"(?i)\b(?:confidential|internal use only|do not distribute|proprietary|trade secret|NDA|restricted)\b"
    }

    matched_indices = set()
    
    category_order = [
        "Password Field",
        "Credit Card Number",
        "Aadhaar Number",
        "API Key / Secret",
        "PAN Number",
        "IFSC Code",
        "Employee ID",
        "Phone Number",
        "Email Address",
        "Bank Account Number",
        "Confidential Keywords"
    ]
    
    for category in category_order:
        pattern = patterns[category]
        for match in re.finditer(pattern, text):
            if category == "Password Field":
                val = match.group(1)
                start, end = match.start(1), match.end(1)
            else:
                val = match.group(0)
                start, end = match.start(), match.end()
                
            if category in ["Aadhaar Number", "Credit Card Number", "Phone Number", "Bank Account Number"]:
                if is_part_of_longer_sequence(text, start, end):
                    continue
                    
            span_indices = set(range(start, end))
            if span_indices.intersection(matched_indices):
                continue
                
            if category == "Credit Card Number":
                if not luhn_checksum(val):
                    continue
                    
            if category == "Bank Account Number":
                cleaned_val = re.sub(r"\D", "", val)
                if len(cleaned_val) < 9 or len(cleaned_val) > 18:
                    continue
                if any(c.isalpha() for c in val):
                    continue

            location = "N/A"
            if file_type == "PDF" and page_offsets:
                for offset in page_offsets:
                    if offset["start"] <= start < offset["end"]:
                        location = f"Page {offset['page']}"
                        break
            elif file_type == "CSV" and row_offsets:
                for offset in row_offsets:
                    if offset["start"] <= start < offset["end"]:
                        location = f"Row {offset['row']}"
                        break

            matched_indices.update(span_indices)
            findings.append({
                "category": category,
                "value": val.strip(),
                "location": location,
                "context": get_context_around(text, start, end),
                "start": start,
                "end": end
            })
            
    findings.sort(key=lambda x: x["start"])
    return findings

# --- RISK CLASSIFICATION LOGIC ---
def calculate_risk(findings: list) -> tuple[int, str, str]:
    """Calculate point-based risk and bucket into levels."""
    detected_cats = set(finding["category"] for finding in findings)
    raw_score = sum(RISK_WEIGHTS.get(cat, 0) for cat in detected_cats)
    score = min(raw_score, 100)
    
    if score == 0:
        level = "No Risk"
        color = "#10b981"
    elif score <= 30:
        level = "Low Risk"
        color = "#10b981"
    elif score <= 70:
        level = "Medium Risk"
        color = "#f59e0b"
    else:
        level = "High Risk"
        color = "#ef4444"
        
    return score, level, color

# --- RULE-BASED FALLBACK SUMMARY GENERATOR ---
def generate_rule_based_summary(findings: list) -> dict:
    """Generate structured fallback compliance summaries based on detected categories."""
    categories = set(f["category"] for f in findings)
    
    observations = []
    if not categories:
        observations.append("No sensitive personal data or confidential keywords were detected in the document.")
    else:
        observations.append(f"The document analysis identified the presence of sensitive personal and/or confidential data across {len(categories)} categories: {', '.join(categories)}.")
        
        acts = []
        if any(c in categories for c in ["Aadhaar Number", "PAN Number", "Bank Account Number", "Credit Card Number"]):
            acts.append("the Digital Personal Data Protection (DPDP) Act 2023 (India)")
        if any(c in categories for c in ["Email Address", "Phone Number", "Credit Card Number"]):
            acts.append("the General Data Protection Regulation (GDPR) (EU)")
        if any(c in categories for c in ["Credit Card Number", "Bank Account Number"]):
            acts.append("the Payment Card Industry Data Security Standard (PCI-DSS)")
        if any(c in categories for c in ["Confidential Keywords", "API Key / Secret", "Password Field"]):
            acts.append("ISO 27001 / SOC 2 security framework controls")
            
        if acts:
            observations.append(f"Processing and storing this content triggers compliance and regulatory requirements under: {', '.join(acts)}.")
        else:
            observations.append("No regulatory violations or compliance conflicts were automatically flagged, but best-practice data-minimization rules apply.")
            
    risks = []
    if not categories:
        risks.append("No immediate security risks were detected from sensitive data leaks in this document.")
    else:
        if "Password Field" in categories or "API Key / Secret" in categories:
            risks.append("🚨 **CRITICAL**: Exposed passwords or API keys can allow malicious access to critical cloud systems, database panels, or active service APIs.")
        if "Credit Card Number" in categories or "Bank Account Number" in categories:
            risks.append("💳 **HIGH**: Exposed financial assets (credit cards, bank numbers) create immediate avenues for financial fraud, card duplication, and steep PCI-DSS fines.")
        if "Aadhaar Number" in categories or "PAN Number" in categories:
            risks.append("🆔 **HIGH**: Exposed national identity credentials can be leveraged by attackers for identity theft, fraudulent applications, or secondary authentication spoofing.")
        if "Phone Number" in categories or "Email Address" in categories:
            risks.append("📧 **MEDIUM**: Exposed phone numbers and emails represent targets for automated phishing campaigns, social engineering, and spam vectors.")
        if "Employee ID" in categories:
            risks.append("👤 **LOW**: Exposed employee IDs offer system boundaries that allow targeted spear-phishing or internal directory reconstruction.")
        if "Confidential Keywords" in categories:
            risks.append("📄 **MEDIUM**: The document contains strict proprietary, NDA, or trade-secret terminology, suggesting unauthorized leakage of internal IP.")

    remediations = []
    if not categories:
        remediations.append("No active remediation steps are required.")
    else:
        if any(c in categories for c in ["Password Field", "API Key / Secret"]):
            remediations.append("Immediately rotate all compromised passwords, credentials, and API secret keys.")
        if "Credit Card Number" in categories:
            remediations.append("Redact credit card characters using PCI-compliant tokenization or strict character mask rules (e.g. show first 6, last 4).")
        if any(c in categories for c in ["Aadhaar Number", "PAN Number", "Bank Account Number"]):
            remediations.append("Mask national ID and bank digits before storing or transmitting documents in multi-tenant systems.")
        if "Confidential Keywords" in categories:
            remediations.append("Apply DRM (Digital Rights Management) protections and restrict document distribution using role-based access control (RBAC).")
        remediations.append("Follow the principle of data minimization: delete this file permanently if it is not required for legal or business operations.")
        remediations.append("Encrypt this document at rest using robust AES-256 standards.")

    return {
        "observations": "\n\n".join(observations),
        "risks": "\n\n".join(risks),
        "remediations": "\n\n".join(remediations)
    }

# --- GEMINI API INTEGRATIONS ---
def generate_gemini_summary(api_key: str, model_name: str, findings: list, document_text: str) -> dict:
    """Generate structured compliance report using Google Gemini API."""
    client = genai.Client(api_key=api_key)
    
    findings_summary = {}
    for f in findings:
        cat = f["category"]
        findings_summary[cat] = findings_summary.get(cat, 0) + 1
        
    findings_str = "\n".join([f"- {cat}: {count} instance(s)" for cat, count in findings_summary.items()])
    if not findings_str:
        findings_str = "No sensitive data detected."
        
    truncated_text = document_text[:6000]
    if len(document_text) > 6000:
        truncated_text += "\n... [TRUNCATED DUE TO BUFFER SIZE CONTROLS] ..."
        
    prompt = f"""You are an expert Data Protection & Security Compliance officer.
Analyze the following sensitive data findings and the document excerpt provided below to draft a compliance report.

SUMMARY OF DETECTED SENSITIVE DATA:
{findings_str}

EXCERPT OF THE DOCUMENT:
---
{truncated_text}
---

Your response MUST be generated in EXACTLY the following three sections. Use clean markdown format. Do not change the section titles.

### Compliance Observations
(Discuss what was found. Discuss obligations and potential violations under specific laws like DPDP Act 2023, GDPR, PCI-DSS, or ISO 27001 standards as applicable to the detected categories.)

### Security Risks
(Detail the specific security hazards: risk of identity theft, financial fraud, phishing, system exploitation, etc., stemming from this data.)

### Suggested Remediation Steps
(Provide actionable, step-by-step guidance to secure this document, redact entries, rotate compromised credentials, or minimize exposures.)
"""
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        text_out = response.text
        
        sections = {
            "observations": "Compliance Observations section could not be structured automatically.",
            "risks": "Security Risks section could not be structured automatically.",
            "remediations": "Suggested Remediation Steps section could not be structured automatically."
        }
        
        pattern = r"(?i)###?\s*(Compliance\s+Observations|Security\s+Risks|Suggested\s+Remediation\s+Steps)"
        matches = list(re.finditer(pattern, text_out))
        
        if len(matches) >= 3:
            for i in range(len(matches)):
                header = matches[i].group(1).lower()
                start = matches[i].end()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text_out)
                content = text_out[start:end].strip()
                
                if "compliance" in header:
                    sections["observations"] = content
                elif "security" in header:
                    sections["risks"] = content
                elif "remediation" in header:
                    sections["remediations"] = content
        else:
            sections["observations"] = text_out
            sections["risks"] = "Refer to the comprehensive report under the Compliance Observations section."
            sections["remediations"] = "Refer to the comprehensive report under the Compliance Observations section."
            
        return sections
    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {e}")

# --- DOCUMENT Q&A HANDLING ---
def handle_qa(api_key: str, model_name: str, findings: list, document_text: str, question: str) -> str:
    """Process user questions on document content, using Gemini or rule-based fallback."""
    if not api_key:
        return rule_based_qa(findings, question)
        
    client = genai.Client(api_key=api_key)
    
    findings_summary = {}
    for f in findings:
        cat = f["category"]
        findings_summary[cat] = findings_summary.get(cat, 0) + 1
    findings_str = "\n".join([f"- {cat}: {count} instance(s)" for cat, count in findings_summary.items()])
    if not findings_str:
        findings_str = "No sensitive data detected."
        
    truncated_text = document_text[:6000]
    if len(document_text) > 6000:
        truncated_text += "\n... [TRUNCATED] ..."
        
    prompt = f"""You are a helpful Security & Compliance Q&A assistant.
The user has uploaded a document and we have processed it for sensitive items.
Here is the context:

SUMMARY OF DETECTED SENSITIVE DATA:
{findings_str}

EXCERPT OF THE DOCUMENT:
---
{truncated_text}
---

USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer the user's question directly and concisely, matching the details in the findings.
2. Ground your answer strictly on the provided excerpt and findings summary. Do not assume or hallucinate external facts.
3. If the answer cannot be determined from the excerpt or findings, state exactly: "I cannot find the answer to this question in the provided document excerpt or findings."
"""
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error during Q&A: {e}"

def rule_based_qa(findings: list, question: str) -> str:
    """Search for keywords in the user question to generate rule-based response offline."""
    question_lower = question.lower()
    
    findings_summary = {}
    for f in findings:
        cat = f["category"]
        findings_summary[cat] = findings_summary.get(cat, 0) + 1
        
    total_detections = len(findings)
    
    if any(k in question_lower for k in ["how many", "count", "number of", "how much"]):
        if total_detections == 0:
            return "No sensitive data instances were detected in the document."
        ans = f"A total of **{total_detections}** sensitive item(s) were detected:\n\n"
        for cat, count in findings_summary.items():
            ans += f"- **{cat}**: {count} detection(s)\n"
        return ans
        
    elif any(k in question_lower for k in ["what data", "sensitive", "detect", "confidential", "found"]):
        if not findings_summary:
            return "No sensitive data or confidential keywords were detected in the document."
        ans = "The following sensitive data categories were detected in the document:\n\n"
        for cat in findings_summary.keys():
            ans += f"- **{cat}**\n"
        ans += "\nYou can review the exact matching items and their locations in the Results Table."
        return ans
        
    elif any(k in question_lower for k in ["summarize", "summary", "overview"]):
        fallback = generate_rule_based_summary(findings)
        ans = "### Document Summary (Offline Fallback Mode)\n\n"
        ans += f"**Compliance Observations:**\n{fallback['observations']}\n\n"
        ans += f"**Security Risks:**\n{fallback['risks']}\n\n"
        ans += f"**Suggested Remediation Steps:**\n{fallback['remediations']}"
        return ans
        
    elif any(k in question_lower for k in ["compliance", "gdpr", "dpdp", "pci", "framework", "law"]):
        fallback = generate_rule_based_summary(findings)
        ans = "### Regulatory & Compliance Impact\n\n"
        ans += f"{fallback['observations']}\n\n"
        ans += "**Suggested Remediation Advice:**\n\n"
        ans += f"{fallback['remediations']}"
        return ans
        
    else:
        if total_detections == 0:
            return "No sensitive data was detected in this document. Please enter a Gemini API Key in the sidebar to enable general natural language questions about the text content."
        
        score, level, _ = calculate_risk(findings)
        ans = (
            "⚠️ **Running in Offline Fallback Mode** (No Gemini API key provided).\n\n"
            "To ask arbitrary questions about the document, please input an API Key in the sidebar settings.\n\n"
            "Here is the rule-based metadata I parsed from the document:\n"
            f"- **Total Sensitive Detections**: {total_detections}\n"
            f"- **Risk Level Classification**: {level} (Risk Score: {score})\n"
            f"- **Detected Categories**: {', '.join(findings_summary.keys())}\n\n"
            "*Try asking: 'How many email addresses?', 'What sensitive data is found?', or 'Summarize the compliance findings.'*"
        )
        return ans


# --- LANDING PAGE ---
def render_landing_page():
    """Render a clean, minimal landing page using st.html() so HTML always renders correctly."""
    # Hide all Streamlit chrome
    st.markdown("""
    <style>
    header[data-testid="stHeader"]       { display: none !important; }
    [data-testid="stSidebar"]            { display: none !important; }
    footer                               { display: none !important; }
    #MainMenu                            { display: none !important; }
    [data-testid="stToolbar"]            { display: none !important; }
    [data-testid="stDecoration"]         { display: none !important; }
    [data-testid="stStatusWidget"]       { display: none !important; }
    section[data-testid="stMain"]        { padding: 0 !important; background: #ffffff !important; }
    section[data-testid="stMain"] > div { padding: 0 !important; }
    .main .block-container               { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
    div.block-container                  { padding: 0 !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    landing_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap"></noscript>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', sans-serif;
    background: #ffffff;
    color: #0f172a;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 2.8rem;
    border-bottom: 1px solid #f1f5f9;
  }
  .nav-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.45rem;
  }
  .nav-pill {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    background: #f1f5f9;
    color: #64748b;
    padding: 0.25rem 0.7rem;
    border-radius: 9999px;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 1.5rem 4rem;
  }

  @keyframes floatBob {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-10px); }
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .illustration-wrap {
    width: 240px;
    margin: 0 auto 2rem auto;
    animation: floatBob 4s ease-in-out infinite;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.07));
  }

  h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2rem, 4.5vw, 3rem);
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 1rem;
    animation: fadeUp 0.5s ease 0.1s both;
  }

  .subtitle {
    font-size: 1.1rem;
    color: #64748b;
    font-weight: 400;
    line-height: 1.75;
    max-width: 560px;
    text-align: center;
    margin: 0 auto 2rem auto;
    letter-spacing: 0.01em;
    animation: fadeUp 0.5s ease 0.2s both;
  }

  .cta-wrapper {
    position: relative;
    display: inline-flex;
    margin-bottom: 1.8rem;
    animation: fadeUp 0.5s ease 0.3s both;
  }
  .cta-glow {
    position: absolute;
    top: 6px;
    left: 8px;
    width: calc(100% - 16px);
    height: calc(100% - 6px);
    background: linear-gradient(90deg, #6366f1, #f43f5e, #fbbf24);
    filter: blur(18px);
    opacity: 0.5;
    z-index: 1;
    border-radius: 12px;
    pointer-events: none;
    transition: opacity 0.3s ease, filter 0.3s ease;
  }
  .cta-btn {
    position: relative;
    z-index: 2;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #111522;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    padding: 0.8rem 2.2rem;
    border-radius: 12px;
    text-decoration: none;
    transition: background 0.2s ease, transform 0.15s ease;
    border: none;
    cursor: pointer;
  }
  .cta-btn:hover {
    background: #171d2e;
    transform: translateY(-1px);
  }
  .cta-wrapper:hover .cta-glow {
    opacity: 0.7;
    filter: blur(20px);
  }

  .no-signup {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-bottom: 2.8rem;
    animation: fadeUp 0.5s ease 0.35s both;
  }
  .no-signup span { margin: 0 0.3rem; }

  .pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    justify-content: center;
    animation: fadeUp 0.5s ease 0.4s both;
  }
  .pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 9999px;
    padding: 0.38rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: #334155;
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
    cursor: default;
  }
  .pill:hover {
    background: #f1f5f9;
    border-color: #c7d2e0;
    transform: translateY(-1px);
  }

  .proof-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    padding: 1.3rem 2rem;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    animation: fadeUp 0.5s ease 0.5s both;
  }
  .proof {
    font-size: 0.8rem;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }
  .proof strong { color: #475569; font-weight: 600; }
</style>
</head>
<body>

<nav>
  <a class="nav-logo" href="#">&#x1F6E1;&#xFE0F;&nbsp; DataGuard</a>
  <span class="nav-pill"></span>
</nav>

<main>
  <div class="illustration-wrap">
    <svg viewBox="0 0 280 240" xmlns="http://www.w3.org/2000/svg" width="240" height="210" fill="none" style="overflow:visible">
      <rect x="40" y="175" width="200" height="8" rx="4" stroke="#1e293b" stroke-width="2.5" fill="#f1f5f9"/>
      <rect x="70" y="183" width="11" height="36" rx="3" stroke="#1e293b" stroke-width="2" fill="#e2e8f0"/>
      <rect x="199" y="183" width="11" height="36" rx="3" stroke="#1e293b" stroke-width="2" fill="#e2e8f0"/>
      <rect x="75" y="143" width="130" height="34" rx="5" stroke="#1e293b" stroke-width="2.5" fill="#e2e8f0"/>
      <rect x="80" y="93" width="120" height="76" rx="6" stroke="#1e293b" stroke-width="2.5" fill="#ffffff"/>
      <rect x="92" y="106" width="48" height="5" rx="2.5" fill="#6366f1" opacity="0.75"/>
      <rect x="92" y="117" width="78" height="3.5" rx="1.5" fill="#cbd5e1"/>
      <rect x="92" y="126" width="62" height="3.5" rx="1.5" fill="#cbd5e1"/>
      <rect x="92" y="135" width="70" height="3.5" rx="1.5" fill="#cbd5e1"/>
      <circle cx="170" cy="107" r="7" fill="#ef4444" opacity="0.88"/>
      <text x="167" y="111" font-size="8" fill="white" font-family="sans-serif" font-weight="bold">!</text>
      <ellipse cx="140" cy="66" rx="17" ry="19" stroke="#1e293b" stroke-width="2.5" fill="#fef9c3"/>
      <path d="M123 63 Q124 47 140 45 Q156 47 157 63" stroke="#1e293b" stroke-width="2.5" fill="#f59e0b"/>
      <circle cx="134" cy="65" r="2" fill="#1e293b"/>
      <circle cx="146" cy="65" r="2" fill="#1e293b"/>
      <path d="M134 74 Q140 79 146 74" stroke="#1e293b" stroke-width="1.8" stroke-linecap="round" fill="none"/>
      <rect x="135" y="84" width="10" height="10" fill="#fef9c3"/>
      <path d="M112 135 Q112 96 140 94 Q168 96 168 135" stroke="#1e293b" stroke-width="2.5" fill="#dbeafe"/>
      <path d="M112 115 Q97 126 93 141" stroke="#1e293b" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <path d="M168 115 Q183 126 187 141" stroke="#1e293b" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <circle cx="238" cy="42" r="13" stroke="#6366f1" stroke-width="2.5" fill="white"/>
      <line x1="247" y1="52" x2="257" y2="63" stroke="#6366f1" stroke-width="3" stroke-linecap="round"/>
      <line x1="231" y1="39" x2="238" y2="39" stroke="#6366f1" stroke-width="1.8" opacity="0.45"/>
      <line x1="238" y1="32" x2="238" y2="39" stroke="#6366f1" stroke-width="1.8" opacity="0.45"/>
      <path d="M28 34 Q28 18 42 14 Q56 18 56 34 Q56 50 42 56 Q28 50 28 34Z" stroke="#10b981" stroke-width="2.5" fill="#d1fae5"/>
      <path d="M36 34 L40 38 L48 30" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <rect x="234" y="148" width="32" height="40" rx="4" stroke="#f59e0b" stroke-width="2" fill="#fef9c3"/>
      <path d="M242 161 h16 M242 169 h16 M242 177 h10" stroke="#f59e0b" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M254 148 v7 h12" stroke="#f59e0b" stroke-width="2" stroke-linejoin="round" fill="none"/>
      <circle cx="28" cy="125" r="4" fill="#6366f1" opacity="0.25"/>
      <circle cx="18" cy="150" r="3" fill="#10b981" opacity="0.25"/>
      <circle cx="258" cy="118" r="5" fill="#f59e0b" opacity="0.25"/>
      <circle cx="268" cy="94" r="3" fill="#ef4444" opacity="0.2"/>
    </svg>
  </div>

  <h1>AI Powered Sensitive Data Detection <br> & Compliance Assistant</h1>

  <p class="subtitle">
    Detect sensitive data, classify risk, and get an AI compliance summary &mdash;
    upload a <strong style="color:#475569;font-weight:600;">PDF</strong>,
    <strong style="color:#475569;font-weight:600;">TXT</strong>, or
    <strong style="color:#475569;font-weight:600;">CSV</strong>.
  </p>

  <div class="cta-wrapper">
    <div class="cta-glow"></div>
    <a class="cta-btn" href="?page=dashboard" id="scan-now-btn">
      Get Started &nbsp;<span style="font-weight: bold; font-family: system-ui, sans-serif; margin-left: 2px;">&gt;</span>
    </a>
  </div>

  <div class="pills">
    <span class="pill">&#x1FAA6; Aadhaar &amp; PAN</span>
    <span class="pill">&#x1F4B3; Credit Cards</span>
    <span class="pill">&#x1F4E7; Emails &amp; Phones</span>
    <span class="pill">&#x1F511; API Keys &amp; Passwords</span>
    <span class="pill">&#x1F3E6; Bank Accounts</span>
    <span class="pill">&#x1F4C4; Confidential Keywords</span>
  </div>
</main>

<script>
    document.getElementById('scan-now-btn').addEventListener('click', function(e) {
        e.preventDefault();
        const targetUrl = this.getAttribute('href');
        document.body.style.transition = 'opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
        document.body.style.opacity = '0';
        setTimeout(function() {
            window.location.href = targetUrl;
        }, 380);
    });
</script>
</body>
</html>"""
    st.html(landing_html)



# --- DASHBOARD ---
def render_dashboard():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    model_choice = "gemini-3.1-flash-lite"
    
    uploaded_file = st.file_uploader(
        "Upload document to analyze", 
        type=["pdf", "txt", "csv", "docx"], 
        label_visibility="collapsed"
    )
    
    if uploaded_file is None:
        upload_emoji_b64 = ""
        upload_emoji_path = Path("upload_emoji.png")
        if upload_emoji_path.exists():
            try:
                with open(upload_emoji_path, "rb") as f:
                    upload_emoji_b64 = base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass

        dashboard_html = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
<style>
    /* Premium Page Transitions & Keyframe Entrance Animations */
    @keyframes dashboardFadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes dashboardFadeInDown {
        from { opacity: 0; transform: translateY(-16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUpNav {
        from { transform: translateY(100%); }
        to   { transform: translateY(0); }
    }
    
    .stitch-header {
        animation: dashboardFadeInDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .stitch-upload-card {
        animation: dashboardFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both 0.1s;
    }
    .stitch-timeline-section {
        animation: dashboardFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both 0.2s;
    }
    .stitch-status-section {
        animation: dashboardFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both 0.3s;
    }
    .stitch-footer-nav {
        animation: slideUpNav 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    /* Style native Streamlit uploader to render as black pill "Select Files" button */
    [data-testid="stFileUploader"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: -1.8rem 0 -0.5rem 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploader"] small {
        display: none !important;
    }
    [data-testid="stFileUploader"] button {
        min-width: 180px !important;
        height: 48px !important;
        border-radius: 9999px !important;
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        cursor: pointer !important;
        transition: transform 0.15s ease, background-color 0.15s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: scale(1.03) !important;
        background-color: #191c1e !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button [data-testid="stMarkdownContainer"] p {
        font-size: 0 !important;
    }
    [data-testid="stFileUploader"] button [data-testid="stMarkdownContainer"] p::after {
        content: "Select Files" !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        display: inline-block;
        line-height: 1;
        text-transform: none;
        letter-spacing: normal;
        word-wrap: normal;
        white-space: nowrap;
        direction: ltr;
    }
    
    /* Hide default Streamlit header & margins to eliminate top gap completely */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }
    .main .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* --- STITCH VANILLA CLASS REPLICA --- */
    .stitch-dashboard {
        font-family: 'Inter', sans-serif;
        background-color: #f7f9fb; /* Grayish background for page body */
        color: #191c1e;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        margin: -1.25rem -2rem; /* Negate Streamlit block container padding */
    }
    
    .stitch-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #ffffff; /* Pure white header */
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e0e3e5;
    }
    .stitch-header-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .stitch-header-logo-icon {
        font-size: 1.5rem;
        color: #191c1e;
    }
    .stitch-header-logo-text {
        font-size: 1.125rem;
        font-weight: 700;
        color: #191c1e;
    }
    .stitch-header-bell {
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: none;
        color: #191c1e;
        cursor: pointer;
    }
    
    .stitch-content {
        flex: 1;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding-bottom: 6rem;
    }
    
    .stitch-upload-card {
        border: 2px dashed #c6c6cd;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 3rem 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: border-color 0.2s, background-color 0.2s;
    }
    .stitch-upload-card:hover {
        border-color: #00687a !important;
        background-color: #f2f4f6 !important;
    }
    
    .stitch-upload-icon-circle {
        width: 64px;
        height: 64px;
        border-radius: 16px; /* Squircle upload icon */
        background-color: #57dffe;
        color: #006172;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-size: 2.2rem; /* Perfect upload emoji size */
    }
    
    .stitch-upload-glow {
        position: absolute;
        inset: -12px;
        background-color: rgba(87, 223, 254, 0.2);
        border-radius: 16px; /* Squircle glow */
        filter: blur(8px);
        z-index: 1;
    }
    .stitch-upload-icon-circle svg, .stitch-upload-icon-circle span {
        position: relative;
        z-index: 2;
    }
    
    .stitch-upload-badges {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.5rem;
    }
    .stitch-badge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
    }
    .stitch-badge-box {
        width: 40px;
        height: 40px;
        border-radius: 10px; /* Squircle badge boxes */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem; /* Perfect badge emoji size */
        line-height: 1;
        padding-bottom: 2px; /* Fix baseline drop */
    }
    .stitch-badge-box.pdf { background-color: #dae2fd; color: #131b2e; }
    .stitch-badge-box.txt { background-color: #acedff; color: #001f26; }
    .stitch-badge-box.csv { background-color: #6ffbbe; color: #002113; }
    
    .stitch-badge-label {
        font-size: 10px;
        font-weight: 700;
        color: #76777d;
        letter-spacing: 0.05em;
    }
    .stitch-select-btn {
        min-width: 180px;
        height: 48px;
        border-radius: 9999px;
        background-color: #000000;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.88rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.15s;
    }
    .stitch-select-btn:hover {
        transform: scale(1.03);
    }
    
    /* Timeline styles */
    .stitch-timeline-section {
        text-align: left;
    }
    .stitch-timeline-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #191c1e;
        margin-bottom: 1.5rem;
    }
    .stitch-timeline {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    .stitch-timeline-step {
        display: flex;
        gap: 1rem;
        align-items: center; /* Vertically align icon and text rows */
    }
    .stitch-step-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px; /* Squircle steps */
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        position: relative;
        font-size: 1.4rem; /* Crisp emoji size */
        line-height: 1;
        padding-bottom: 3px; /* Fix baseline drop, shifting emoji up */
    }
    .stitch-step-icon.blue { background-color: #dae2fd; color: #131b2e; } /* Match Step 1 blue bg */
    .stitch-step-icon.green { background-color: #6ffbbe; color: #002113; }
    .stitch-step-icon.purple { background-color: #dae2fd; color: #131b2e; }
    
    /* Connector line */
    .step-line::after {
        content: '';
        position: absolute;
        left: 50%;
        top: 48px;
        bottom: -24px;
        width: 2px;
        background-color: #e0e3e5;
        transform: translateX(-50%);
        z-index: 1;
    }
    .stitch-timeline-step:last-child .step-line::after {
        display: none;
    }
    
    .stitch-step-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }
    .stitch-step-title {
        font-size: 1rem;
        font-weight: 700;
        color: #191c1e;
        margin-bottom: 0.15rem;
    }
    .stitch-step-desc {
        font-size: 0.88rem;
        color: #45464d;
        line-height: 1.4;
    }
    
    /* Bottom cards grid */
    .stitch-status-section {
        background-color: #f2f4f6;
        border-top: 1px solid #c6c6cd;
        padding: 2rem 1.5rem;
        margin: 1.5rem -1.5rem -1.5rem -1.5rem;
    }
    .stitch-status-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    @media (min-width: 768px) {
        .stitch-status-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    .stitch-status-card {
        background-color: #f7f9fb;
        border: 1px solid #c6c6cd;
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 0.75rem;
        min-height: 180px;
    }
    .stitch-status-card-icon {
        font-size: 2.25rem;
        color: #c6c6cd;
    }
    .stitch-status-card-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #45464d;
    }
    .stitch-status-card-desc {
        font-size: 0.75rem;
        color: #45464d;
        margin-top: 0.15rem;
    }
    
    .stitch-summary-placeholder {
        margin-top: 1rem;
        background-color: rgba(230,232,234,0.5);
        border: 1px solid #c6c6cd;
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .stitch-placeholder-icon {
        width: 40px;
        height: 40px;
        border-radius: 4px;
        background-color: #f7f9fb;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #76777d;
        flex-shrink: 0;
    }
    .stitch-placeholder-line-1 {
        height: 8px;
        width: 120px;
        background-color: #c6c6cd;
        border-radius: 4px;
        margin-bottom: 6px;
    }
    .stitch-placeholder-line-2 {
        height: 8px;
        width: 240px;
        background-color: rgba(198,198,205,0.3);
        border-radius: 4px;
    }
    
    /* Bottom navigation bar */
    .stitch-footer-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 50;
        display: flex;
        background-color: #f7f9fb;
        border-top: 1px solid #c6c6cd;
        padding: 0.5rem 1rem 0.75rem 1rem;
        gap: 0.5rem;
    }
    .stitch-nav-item {
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        gap: 0.25rem;
        color: #45464d;
        text-decoration: none;
    }
    .stitch-nav-item.active {
        color: #191c1e;
    }
</style>
<div class="stitch-dashboard">
    <!-- TopAppBar -->
    <div class="stitch-header">
        <div class="stitch-header-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stitch-header-logo-icon" style="color: #191c1e;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="11" r="3"/><path d="M8 17a4 4 0 0 1 8 0"/></svg>
            <span class="stitch-header-logo-text">Dashboard</span>
        </div>
        <button class="stitch-header-bell">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #191c1e;"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </button>
    </div>
    
    <!-- Main Content Area -->
    <div class="stitch-content">
        <!-- Hero Upload Section -->
        <div class="stitch-upload-card upload-zone">
            <div class="stitch-upload-icon-circle">
                <div class="stitch-upload-glow"></div>
                <span style="position: relative; z-index: 2;">📤</span>
            </div>
            <div>
                <h1 style="font-size: 1.5rem; font-weight: 700; color: #191c1e; margin-bottom: 0.5rem;">Upload Document</h1>
                <p style="font-size: 0.88rem; color: #45464d; max-width: 320px; margin: 0 auto; line-height: 1.4;">
                    Drag and drop your files here or click to browse. We support PDF, TXT, and CSV for deep compliance scanning.
                </p>
            </div>
            
            <div class="stitch-upload-badges">
                <div class="stitch-badge-container">
                    <div class="stitch-badge-box pdf">
                        📄
                    </div>
                    <span class="stitch-badge-label">PDF</span>
                </div>
                <div class="stitch-badge-container">
                    <div class="stitch-badge-box txt">
                        📝
                    </div>
                    <span class="stitch-badge-label">TXT</span>
                </div>
                <div class="stitch-badge-container">
                    <div class="stitch-badge-box txt">
                        📝
                    </div>
                    <span class="stitch-badge-label">DOCX</span>
                </div>
                <div class="stitch-badge-container">
                    <div class="stitch-badge-box csv">
                        📊
                    </div>
                    <span class="stitch-badge-label">CSV</span>
                </div>
            </div>
        </div> <!-- Close stitch-upload-card -->
        
        
        <!-- Empty Data State -->
        <div class="stitch-status-section" style="background-color: transparent; border: none; display: flex; justify-content: center; margin-top: 2rem; padding: 0;">
            <div class="stitch-status-card" style="width: 100%; max-width: 600px; padding: 3rem 2rem; border-style: dashed; background-color: #ffffff;">
                <div style="font-size: 3rem; margin-bottom: 1rem; color: #c6c6cd;">📄</div>
                <h3 style="font-size: 1.125rem; font-weight: 700; color: #191c1e; margin-bottom: 0.5rem;">No document uploaded yet</h3>
                <p style="font-size: 0.88rem; color: #45464d;">Upload a PDF, DOCX, TXT, or CSV file to begin analysis.</p>
            </div>
        </div>
    </div>
</div>
"""

        if upload_emoji_b64:
            img_html = f'<img src="data:image/png;base64,{upload_emoji_b64}" style="width: 42px; height: 42px; object-fit: contain; position: relative; z-index: 2;" alt="Upload Icon" />'
            dashboard_html = dashboard_html.replace('<span style="position: relative; z-index: 2;">📤</span>', img_html)

        # Inject transparent overlay CSS rules to position native file uploader directly over the hero card
        st.markdown("""
        <style>
        .main .block-container {
            position: relative !important;
        }
        [data-testid="stFileUploader"] {
            position: absolute !important;
            top: 80px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 90% !important;
            max-width: 800px !important;
            height: 350px !important;
            opacity: 0 !important;
            z-index: 100 !important;
            cursor: pointer !important;
        }
        [data-testid="stFileUploader"] * {
            cursor: pointer !important;
            height: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.html(dashboard_html)
    else:
        # Style active uploader to look compact
        st.markdown("""
        <style>
        [data-testid="stFileUploader"] {
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 0.8rem 1.5rem !important;
            margin-bottom: 2rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        file_name = uploaded_file.name
        file_extension = file_name.split(".")[-1].upper()
        file_size_kb = uploaded_file.size / 1024
        
        from datetime import datetime
        import time
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        text_content = ""
        page_offsets = None
        row_offsets = None
        df_csv = None
        
        # 1. Multi-step progress indicator
        progress_container = st.container()
        with progress_container:
            st.markdown("### 🔄 Processing Document")
            status_placeholder = st.empty()
            
            status_placeholder.info("✓ Upload Complete")
            time.sleep(0.3)
            
            status_placeholder.info("🔄 Reading Document...")
            try:
                if file_extension == "TXT":
                    text_content = extract_text_from_txt(uploaded_file)
                elif file_extension == "PDF":
                    text_content, page_offsets = extract_text_from_pdf(uploaded_file)
                elif file_extension == "CSV":
                    text_content, row_offsets, df_csv = extract_text_from_csv(uploaded_file)
                elif file_extension == "DOCX":
                    text_content = extract_text_from_docx(uploaded_file)
            except Exception as e:
                st.error(f"Error reading file: {e}")
                return
                
            if not text_content.strip():
                st.warning("⚠️ The uploaded document is empty or text could not be extracted.")
                return
                
            word_count = len(text_content.split())
            if file_extension == "PDF" and page_offsets:
                page_count = len(page_offsets)
            elif file_extension in ["DOCX", "TXT"]:
                page_count = max(1, math.ceil(word_count / 300))
            elif file_extension == "CSV" and df_csv is not None:
                page_count = max(1, math.ceil(len(df_csv) / 50))
            else:
                page_count = "N/A"
            
            status_placeholder.info("🔄 Detecting Sensitive Data...")
            findings = detect_sensitive_data(
                text_content, 
                page_offsets=page_offsets, 
                row_offsets=row_offsets, 
                file_type=file_extension
            )
            
            status_placeholder.info("🔄 Classifying Risk...")
            risk_score, risk_level, risk_color = calculate_risk(findings)
            
            status_placeholder.info("🔄 Generating AI Summary...")
            if gemini_key:
                try:
                    summary = generate_gemini_summary(gemini_key, model_choice, findings, text_content)
                except Exception as e:
                    summary = generate_rule_based_summary(findings)
            else:
                summary = generate_rule_based_summary(findings)
                
            status_placeholder.success("✓ Analysis Complete")
            time.sleep(0.5)
            progress_container.empty()
            
        # 2. Document Information Card
        st.markdown("### 📄 Document Information")
        st.markdown(f"""
        <div class="glass-card" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; padding: 1.5rem;">
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">File Name</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{file_name}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">File Type</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{file_extension}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">File Size</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{file_size_kb:.1f} KB</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">Pages</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{page_count}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">Word Count</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{word_count:,}</span></div>
            <div><strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase;">Upload Time</strong><br><span style="font-size: 1.1rem; font-weight: 500;">{upload_time}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Sensitive Data Summary Grid
        st.markdown("### 🔍 Sensitive Data Summary")
        category_counts = {
            "Aadhaar Number": 0, "PAN Number": 0, "Email Address": 0, 
            "Phone Number": 0, "Credit Card Number": 0, "Bank Account Number": 0, 
            "IFSC Code": 0, "Password Field": 0, "API Key / Secret": 0, 
            "Employee ID": 0, "Confidential Keywords": 0
        }
        for f in findings:
            if f["category"] in category_counts:
                category_counts[f["category"]] += 1
                
        grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem;">'
        for cat, count in category_counts.items():
            color = "#ef4444" if count > 0 else "#10b981"
            grid_html += f"""
            <div class="glass-card" style="padding: 1rem; margin-bottom: 0; display: flex; justify-content: space-between; align-items: center; border-radius: 8px;">
                <span style="font-weight: 500; font-size: 0.9rem;">{cat}</span>
                <span style="background-color: {color}; color: white; padding: 2px 10px; border-radius: 9999px; font-weight: 700;">{count}</span>
            </div>"""
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        
        # 4. Risk Assessment Card
        st.markdown("### 🛡️ Risk Assessment")
        
        # Risk Domains
        personal_cats = {"Aadhaar Number", "PAN Number", "Employee ID", "Email Address", "Phone Number"}
        financial_cats = {"Credit Card Number", "Bank Account Number", "IFSC Code"}
        credential_cats = {"Password Field", "API Key / Secret"}
        confidential_cats = {"Confidential Keywords"}
        
        detected_cats = [cat for cat, count in category_counts.items() if count > 0]
        
        personal_score = sum(RISK_WEIGHTS.get(cat, 0) for cat in personal_cats if category_counts.get(cat, 0) > 0)
        financial_score = sum(RISK_WEIGHTS.get(cat, 0) for cat in financial_cats if category_counts.get(cat, 0) > 0)
        credential_score = sum(RISK_WEIGHTS.get(cat, 0) for cat in credential_cats if category_counts.get(cat, 0) > 0)
        confidential_score = sum(RISK_WEIGHTS.get(cat, 0) for cat in confidential_cats if category_counts.get(cat, 0) > 0)
        
        total_raw = personal_score + financial_score + credential_score + confidential_score
        
        if total_raw > 0:
            personal_share = int(round((personal_score / total_raw) * 100))
            financial_share = int(round((financial_score / total_raw) * 100))
            credential_share = int(round((credential_score / total_raw) * 100))
            confidential_share = int(round((confidential_score / total_raw) * 100))
            
            # Adjust rounding errors
            diff = 100 - (personal_share + financial_share + credential_share + confidential_share)
            if diff != 0:
                shares = [personal_share, financial_share, credential_share, confidential_share]
                idx_max = shares.index(max(shares))
                if idx_max == 0: personal_share += diff
                elif idx_max == 1: financial_share += diff
                elif idx_max == 2: credential_share += diff
                elif idx_max == 3: confidential_share += diff
        else:
            personal_share = 0
            financial_share = 0
            credential_share = 0
            confidential_share = 0
            
        # Conic gradient styling for donut chart
        if total_raw > 0:
            conic_gradient_style = f"""conic-gradient(
                #6366f1 0% {personal_share}%, 
                #3b82f6 {personal_share}% {personal_share + financial_share}%, 
                #f43f5e {personal_share + financial_share}% {personal_share + financial_share + credential_share}%, 
                #10b981 {personal_share + financial_share + credential_share}% 100%
            )"""
        else:
            conic_gradient_style = "#e2e8f0"
            
        display_names = {
            "Aadhaar Number": "Aadhaar Number",
            "PAN Number": "PAN Number",
            "Email Address": "Email Addresses",
            "Phone Number": "Phone Numbers",
            "Credit Card Number": "Credit Card Numbers",
            "Bank Account Number": "Bank Account Numbers",
            "IFSC Code": "IFSC Code",
            "Password Field": "Passwords",
            "API Key / Secret": "API Key / Secrets",
            "Employee ID": "Employee ID",
            "Confidential Keywords": "Confidential Keywords"
        }
        
        bullets_html = ""
        bullets_text = []
        if detected_cats:
            for cat in detected_cats:
                bullets_html += f"<li style='margin-bottom: 0.25rem;'>&bull; {display_names.get(cat, cat)}</li>"
                bullets_text.append(f"- {display_names.get(cat, cat)}")
            bullets_text_str = "\n".join(bullets_text)
            risk_reason_text = f"This document contains:\n{bullets_text_str}\n\nThese findings classify the document as {risk_level}."
        else:
            bullets_html = "<li style='margin-bottom: 0.25rem;'>&bull; No sensitive data categories detected.</li>"
            risk_reason_text = "No sensitive data detected."
            
        # Determine badge settings
        if risk_level == "High Risk":
            badge_bg = "rgba(239, 68, 68, 0.1)"
            badge_text = "#ef4444"
            badge_shadow = "rgba(239, 68, 68, 0.15)"
            badge_dot = "🔴"
        elif risk_level == "Medium Risk":
            badge_bg = "rgba(245, 158, 11, 0.1)"
            badge_text = "#d97706"
            badge_shadow = "rgba(245, 158, 11, 0.15)"
            badge_dot = "🟡"
        else:
            badge_bg = "rgba(16, 185, 129, 0.1)"
            badge_text = "#10b981"
            badge_shadow = "rgba(16, 185, 129, 0.15)"
            badge_dot = "🟢"
            
        # Formulate HTML card string
        raw_card_html = f"""
        <div class="glass-card" style="border-left: 6px solid {risk_color}; padding: 2rem; margin-bottom: 2.5rem;">
            <!-- Top Row: Risk Level & Score -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 1.5rem;">
                <div>
                    <strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.25rem;">Overall Risk Score</strong>
                    <span style="font-size: 2.6rem; font-weight: 800; color: #0f172a; line-height: 1;">{risk_score}%</span>
                </div>
                
                <div>
                    <strong style="color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.25rem;">Risk Classification</strong>
                    <span style="background-color: {badge_bg}; color: {badge_text}; padding: 6px 14px; border-radius: 9999px; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 8px {badge_shadow};">
                        {badge_dot} {risk_level.upper()}
                    </span>
                </div>
            </div>
            
            <!-- Animated Progress Bar -->
            <div style="background-color: #f1f5f9; border-radius: 9999px; height: 12px; width: 100%; overflow: hidden; margin-bottom: 2rem;">
                <div style="background-color: {risk_color}; height: 100%; width: 0%; border-radius: 9999px; animation: fillRiskBar 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;" class="risk-bar-fill"></div>
            </div>
            
            <style>
            @keyframes fillRiskBar {{
                from {{ width: 0%; }}
                to {{ width: {risk_score}%; }}
            }}
            </style>
            
            <!-- Lower Grid: Reason (Left) & Risk Breakdown Donut (Right) -->
            <div class="risk-assessment-grid" style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 2.5rem; align-items: start;">
                <!-- Left Column: Reason -->
                <div>
                    <strong style="color: #475569; font-size: 0.95rem; display: block; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.03em;">Reason</strong>
                    <div style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.6;">
                        This document contains:
                        <ul style="list-style-type: none; padding-left: 0; margin: 0.75rem 0 1rem 0;">
                            {bullets_html}
                        </ul>
                        These findings classify the document as <strong>{risk_level}</strong>.
                    </div>
                </div>
                
                <!-- Right Column: Donut Chart Breakdown -->
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <strong style="color: #475569; font-size: 0.95rem; display: block; margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 0.03em; align-self: flex-start; width: 100%;">Risk Breakdown</strong>
                    
                    <!-- Donut Graphic -->
                    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 1.25rem; position: relative;">
                        <div style="width: 130px; height: 130px; border-radius: 50%; background: {conic_gradient_style}; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.06); animation: spinIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;">
                            <div style="width: 85px; height: 85px; background-color: white; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: inset 0 2px 6px rgba(0,0,0,0.03);">
                                <span style="font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.02em;">Total</span>
                                <span style="font-size: 1.15rem; font-weight: 800; color: #0f172a;">{total_raw} pts</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Donut Legend Grid -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; width: 100%; font-size: 0.8rem; font-weight: 500; color: #475569;">
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background-color: #6366f1; flex-shrink: 0;"></span>
                            <span>Personal ({personal_share}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background-color: #3b82f6; flex-shrink: 0;"></span>
                            <span>Financial ({financial_share}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background-color: #f43f5e; flex-shrink: 0;"></span>
                            <span>Credentials ({credential_share}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background-color: #10b981; flex-shrink: 0;"></span>
                            <span>Confidential ({confidential_share}%)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        @media (max-width: 768px) {{
            .risk-assessment-grid {{
                grid-template-columns: 1fr !important;
                gap: 1.5rem !important;
            }}
        }}
        @keyframes spinIn {{
            from {{ transform: rotate(-90deg) scale(0.9); opacity: 0; }}
            to {{ transform: rotate(0deg) scale(1); opacity: 1; }}
        }}
        </style>
        """
        
        # programmatically strip leading spaces to prevent markdown parser code-block bugs
        clean_card_html = "\n".join([line.strip() for line in raw_card_html.split("\n")])
        st.markdown(clean_card_html, unsafe_allow_html=True)

        # 5. AI Compliance Summary
        st.markdown("### ✨ AI Compliance Summary")
        
        # Helper to convert LLM markdown to clean HTML
        def clean_llm_markdown(text: str) -> str:
            if not text:
                return "N/A"
            # Remove excessive newlines after list items
            text = re.sub(r'(^|\n)(\s*\d+\.)\s*\n+', r'\1\2 ', text)
            text = re.sub(r'(^|\n)(\s*[-*•])\s*\n+', r'\1\2 ', text)
            text = re.sub(r'\n{3,}', r'\n\n', text)
            return text.strip()
            
        def markdown_to_html(text: str) -> str:
            text = clean_llm_markdown(text)
            
            # Bold text **word** -> <strong>word</strong>
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            # Code blocks `code` -> custom styled span
            text = re.sub(r'`(.*?)`', r'<code style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 5px; border-radius: 4px; font-family: monospace; font-size: 0.9em; color: #0f172a;">\1</code>', text)
            
            lines = text.split('\n')
            in_list = False
            list_type = None
            html_lines = []
            
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                    
                ol_match = re.match(r'^(\d+)\.\s*(.*)', line_str)
                ul_match = re.match(r'^[-*•]\s*(.*)', line_str)
                
                if ol_match:
                    if not in_list or list_type != 'ol':
                        if in_list:
                            html_lines.append(f"</{list_type}>")
                        html_lines.append('<ol style="padding-left: 1.2rem; margin-top: 0.5rem; margin-bottom: 0.5rem;">')
                        in_list = True
                        list_type = 'ol'
                    html_lines.append(f'<li style="margin-bottom: 0.5rem; line-height: 1.6; color: #334155;">{ol_match.group(2)}</li>')
                elif ul_match:
                    if not in_list or list_type != 'ul':
                        if in_list:
                            html_lines.append(f"</{list_type}>")
                        html_lines.append('<ul style="list-style-type: disc; padding-left: 1.2rem; margin-top: 0.5rem; margin-bottom: 0.5rem;">')
                        in_list = True
                        list_type = 'ul'
                    html_lines.append(f'<li style="margin-bottom: 0.5rem; line-height: 1.6; color: #334155;">{ul_match.group(1)}</li>')
                else:
                    if in_list:
                        html_lines.append(f"</{list_type}>")
                        in_list = False
                        list_type = None
                    html_lines.append(f'<p style="margin-bottom: 0.75rem; line-height: 1.6; color: #334155;">{line_str}</p>')
                    
            if in_list:
                html_lines.append(f"</{list_type}>")
                
            return '\n'.join(html_lines)
            
        obs_html = markdown_to_html(summary.get('observations', 'N/A'))
        risks_html = markdown_to_html(summary.get('risks', 'N/A'))
        remeds_html = markdown_to_html(summary.get('remediations', 'N/A'))
        
        raw_summary_html = f"""
        <div class="glass-card" style="padding: 2rem; margin-bottom: 2.5rem;">
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-top: 0;">📜 Compliance Observations</h4>
                <div style="font-size: 0.95rem; margin-top: 0.75rem;">
                    {obs_html}
                </div>
            </div>
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: #db2777; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-top: 0;">⚠️ Security Risks</h4>
                <div style="font-size: 0.95rem; margin-top: 0.75rem;">
                    {risks_html}
                </div>
            </div>
            <div>
                <h4 style="color: #059669; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-top: 0;">🛠️ Suggested Remediation</h4>
                <div style="font-size: 0.95rem; margin-top: 0.75rem;">
                    {remeds_html}
                </div>
            </div>
        </div>
        """
        clean_summary_html = "\n".join([line.strip() for line in raw_summary_html.split("\n")])
        st.markdown(clean_summary_html, unsafe_allow_html=True)
        
        # 6. Ask AI About This Document
        st.markdown("### 💬 Ask AI About This Document")
        
        if "qa_input" not in st.session_state:
            st.session_state.qa_input = ""
        if "trigger_ask" not in st.session_state:
            st.session_state.trigger_ask = False
            
        def set_question(q):
            st.session_state.qa_input = q
            st.session_state.trigger_ask = True
            
        st.markdown("<p style='font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;'>Suggested Questions:</p>", unsafe_allow_html=True)
        sug_col1, sug_col2, sug_col3, sug_col4 = st.columns(4)
        
        # We apply type="secondary" and avoid weird custom CSS collisions to prevent white-on-white text issues
        with sug_col1:
            st.button("What sensitive info exists?", on_click=set_question, args=("What sensitive information exists?",), use_container_width=True)
        with sug_col2:
            st.button("Summarize this document.", on_click=set_question, args=("Summarize this document.",), use_container_width=True)
        with sug_col3:
            st.button("What compliance risks?", on_click=set_question, args=("What compliance risks were detected?",), use_container_width=True)
        with sug_col4:
            st.button("Recommended remediation steps?", on_click=set_question, args=("What remediation steps are recommended?",), use_container_width=True)
            
        user_question = st.text_input("Enter your question:", key="qa_input")
        ask_btn = st.button("Ask Assistant", type="primary")
        
        if ask_btn or st.session_state.trigger_ask:
            # We clear the trigger
            st.session_state.trigger_ask = False
            
            # The user might have typed a question OR clicked a button. Both end up in user_question because of key="qa_input"
            current_q = st.session_state.qa_input
            
            if current_q.strip():
                with st.spinner("Processing answer..."):
                    answer = handle_qa(gemini_key, model_choice, findings, text_content, current_q)
                    
                st.markdown(f"""
                <div class="qa-box" style="background-color: #f8fafc; border-left: 4px solid #6366f1; padding: 1.5rem; border-radius: 0 8px 8px 0; margin-top: 1rem; margin-bottom: 2.5rem;">
                    <strong style="color: #4f46e5; font-size: 1.1rem;">Assistant Response:</strong>
                    <div style="margin-top: 0.75rem; line-height: 1.6; color: #1e293b; white-space: pre-line;">{answer}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

        # 7. Download Compliance Report PDF
        st.markdown("---")
        
        try:
            from fpdf import FPDF
            
            class PDF(FPDF):
                def header(self):
                    self.set_font("Helvetica", "B", 15)
                    self.cell(0, 10, "Sensitive Data Compliance Report", 0, 1, "C")
                    self.ln(5)
                    
                def footer(self):
                    self.set_y(-15)
                    self.set_font("Helvetica", "I", 8)
                    self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

            pdf = PDF()
            pdf.add_page()
            
            # Document Info
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "1. Document Information", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"File Name: {file_name}", 0, 1)
            pdf.cell(0, 6, f"File Type: {file_extension}", 0, 1)
            pdf.cell(0, 6, f"File Size: {file_size_kb:.1f} KB", 0, 1)
            pdf.cell(0, 6, f"Word Count: {word_count:,}", 0, 1)
            pdf.cell(0, 6, f"Upload Time: {upload_time}", 0, 1)
            pdf.ln(5)
            
            # Risk Classification
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "2. Risk Classification", 0, 1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, f"Overall Risk Score: {risk_score}%", 0, 1)
            pdf.cell(0, 6, f"Risk Level: {risk_level}", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, f"Reason:\n{risk_reason_text}".encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Risk Breakdown:", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"- Personal Data: {personal_share}%", 0, 1)
            pdf.cell(0, 6, f"- Financial Data: {financial_share}%", 0, 1)
            pdf.cell(0, 6, f"- Credentials: {credential_share}%", 0, 1)
            pdf.cell(0, 6, f"- Confidential Data: {confidential_share}%", 0, 1)
            pdf.ln(5)
            
            # Sensitive Data Detected
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "3. Sensitive Data Summary", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            for cat, count in category_counts.items():
                if count > 0:
                    pdf.cell(0, 6, f"- {cat}: {count}", 0, 1)
            if not findings:
                pdf.cell(0, 6, "No sensitive data detected.", 0, 1)
            pdf.ln(5)
            
            # AI Summary
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "4. AI Compliance Summary", 0, 1)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Observations:", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            obs = str(summary.get('observations', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, obs)
            pdf.ln(3)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Security Risks:", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            risks = str(summary.get('risks', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, risks)
            pdf.ln(3)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Suggested Remediation:", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            rem = str(summary.get('remediations', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, rem)
            
            pdf_bytes = bytes(pdf.output())
            
            st.download_button(
                label="📄 Download Compliance Report",
                data=pdf_bytes,
                file_name=f"{file_name}_compliance_report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not generate PDF report. (Ensure fpdf2 is installed). Error: {e}")



# --- ROUTER ---
def main():
    params = st.query_params
    page = params.get("page", "landing")

    if page == "dashboard":
        with st.sidebar:
            st.markdown("### 🏠 Navigation")
            if st.button("← Back to Home", use_container_width=True):
                st.query_params.clear()
                st.rerun()
            st.markdown("---")
        render_dashboard()
    else:
        render_landing_page()


if __name__ == "__main__":
    main()
