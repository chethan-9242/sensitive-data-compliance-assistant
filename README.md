# Sensitive Data Detection & Compliance Assistant 🛡️

A Streamlit-based web application that detects sensitive, confidential, and personally identifiable information (PII) in uploaded files (PDF, DOCX, TXT, CSV), classifies the document's risk level, generates automated compliance summaries, and enables interactive question-answering.

The app supports rule-based analysis and AI-powered analysis (via the Google Gemini API).

---

## Tech Stack
- **Frontend & Core Layout**: Python, Streamlit
- **Document Extractors**: `pypdf`, `python-docx`, `pandas`
- **AI & LLM Integration**: Google GenAI SDK (`google-genai`), `python-dotenv`
- **PDF Report Generation**: `fpdf2`

---

## Live Demo & Deployment
- **Streamlit Prototype**: [Live Application Link](https://sensitive-data-compliance-assistant-g4zljrqdwytjgkwslzcwx4.streamlit.app/)

---


## Architecture Overview

Below is an ASCII representation of the application's processing pipeline:

```text
               +-------------------------------------------------+
               |             User Uploads Document               |
               |               (PDF, TXT, CSV)                   |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-----------------------+-------------------------+
               |            Text & Metadata Extraction           |
               |     (Extract text, map pages/rows dynamically)  |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-----------------------+-------------------------+
               |        Prioritized Regex Scan Engine            |
               | (Overlaps filtered; Luhn validation on cards)   |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-----------------------+-------------------------+
               |            Risk & Compliance Calculator         |
               |  (Compute risk score, bucket Low/Med/High risk)  |
               +------------+-----------------------+------------+
                            |                       |
                            |                       |
                            v                       v
               [API Key Configured?]         [API Key Missing?]
                            |                       |
                            | (Yes)                 | (No)
                            v                       v
               +------------+----------+ +----------+------------+
               |     Gemini Flash      | |  Localized Rule-Based  |
               |   Audit / Q&A Model   | |    Fallback Engine     |
               +------------+----------+ +----------+------------+
                            |                       |
                            +-----------+-----------+
                                        |
                                        v
               +------------------------+------------------------+
               |                    Streamlit UI                 |
               |   (Metric Cards, Detections Table, Masking,     |
               |         Summaries, Interactive Chat Box)        |
               +-------------------------------------------------+
```

---

## Core Features

1. **Multi-Format Ingestion**: Extracts text page-by-page for PDF files (with raw stream cursor fixes), estimates page counts for Word documents (`.docx`), text files (`.txt`), and CSV spreadsheets, and decodes CSV row-by-row maintaining structure.
2. **Prioritized Regex Engine**: Matches complex identifier structures such as Indian Aadhaar, PAN, Emails, Mobile Numbers, IFSC, Credit Cards, Secrets/API Keys, Passwords, and corporate Confidentiality Terms.
3. **Double-Match Filtering**: Scans in a prioritized order of specificity so that simple digits (e.g. Bank Accounts) do not override complex structures (e.g. Credit Cards or Aadhaar).
4. **Luhn Check Verification**: Minimizes false card matches by verifying all credit card sequences mathematically.
5. **Interactive Masking**: Instantly redacts sensitive outputs visually on the frontend to protect screens from visual leaks.
6. **Dual Mode Architecture**:
   - **Offline Fallback**: Uses pre-defined mapping templates for compliance summaries and simple keyword search matching for Q&A.
   - **AI-Powered**: Uses Google Gemini models (`gemini-3.1-flash-lite`) to generate structured compliance audit insights and answer complex natural language questions grounded strictly in the document context.
7. **Enterprise Risk Assessment**: Displays overall risk score (`0-100%`) with smooth animated CSS bars, color-coded risk badges (🔴/🟡/🟢), bulleted reasons list, and a conic-gradient Donut Chart mapping the risk composition across Personal, Financial, Credentials, and Confidential domains.

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher installed.

### Step 1: Clone or Copy Project Files
Ensure the following files are in your directory:
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`

### Step 2: Install Dependencies
Open your command terminal, navigate to the folder, and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Start the Streamlit development server:
```bash
streamlit run app.py
```
A browser tab should open automatically. If not, click on the local link provided in the command line (usually `http://localhost:8501`).

---

## AI/ML and Engineering Approach

- **Deterministic Scanning**: PII auditing demands auditability. We utilize deterministic regular expressions to extract targets rather than statistical LLM extraction, ensuring 100% reproducibility and complete security boundaries.
- **Strict Context Grounding**: The LLM prompt binds Gemini strictly to the parsed PII findings and document context. It instructs the assistant to report missing information instead of hallucinating answers.
- **Dynamic Risk Score Matrix**: Risk is evaluated using a weighted point system normalized to `100%` (capped at maximum score).
  - **Risk Score Formula**: 
    $$\text{Raw Score} = \sum \text{Weights of Detected Categories}$$
    $$\text{Overall Risk Score} = \min(\text{Raw Score}, 100\%)$$
  - **Data Category Weight Matrix**:
    | Data Category | Weight (Points) | Classification Domain |
    | :--- | :---: | :--- |
    | **API Key / Secret** | 25 | Credentials |
    | **Password Field** | 20 | Credentials |
    | **Credit Card Number** | 20 | Financial Data |
    | **Aadhaar Number** | 20 | Personal Data |
    | **PAN Number** | 15 | Personal Data |
    | **Bank Account Number** | 15 | Financial Data |
    | **IFSC Code** | 10 | Financial Data |
    | **Employee ID** | 5 | Personal Data |
    | **Email Address** | 5 | Personal Data |
    | **Phone Number** | 5 | Personal Data |
    | **Confidential Keywords** | 5 | Confidential Data |
  - **Risk Classification Thresholds**:
    * **Low Risk**: 0% - 30% (Green bar & badge)
    * **Medium Risk**: 31% - 70% (Yellow bar & badge)
    * **High Risk**: 71% - 100% (Red bar & badge)

---

## Challenges Faced & Mitigation

1. **Regex Overlap Conflict**: 
   - *Problem*: Generic bank account expressions (`\b\d{9,18}\b`) overlapped with card sequences, phone numbers, and Aadhaar numbers.
   - *Solution*: Implemented character index tracking (`matched_indices`). By matching card numbers, Aadhaar, and phone numbers *first*, their character positions are registered and skipped for subsequent regex checks.
2. **Card False Positives**:
   - *Problem*: Long digits in code files or spreadsheets triggered fake credit card detections.
   - *Solution*: Added a post-regex Luhn checksum check. Matches are only validated if they pass the Luhn mod 10 arithmetic verify step.
3. **Structured Fallback Formatting**:
   - *Problem*: Maintaining a unified, beautiful UI when alternating between Gemini summaries and local fallbacks.
   - *Solution*: Designed rule-based templates that return the exact same dictionary structure and heading keys. This allows the Streamlit card components to render uniformly regardless of API availability.

---

## Future Improvements

1. **Optical Character Recognition (OCR)**: Integrate Tesseract or EasyOCR to extract selectable text from scanned PDF forms and static images.
2. **Context-Sensitive PII Checking**: Integrate lightweight named entity recognition (NER) models (like spaCy) to match named PII (e.g. Person Names, Addresses) that are too unstructured for regex.
3. **Automated Redacted Downloads**: Add a button allowing the user to export a new, fully redacted version of the uploaded document (PDF or CSV) directly from the dashboard.
