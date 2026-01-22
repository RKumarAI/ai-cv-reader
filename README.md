# AI-Powered CV Reader 📄

A Python-based command-line tool that uses OpenAI's GPT models to extract and summarize key information from PDF resumes. It handles long documents by chunking text and provides a concise summary of skills, experience, and education.

##  Features
* **PDF Text Extraction:** Uses `PyPDF2` to parse local PDF files.
* **Smart Summarization:** Uses OpenAI's `gpt-4o-mini` to identify professional highlights.
* **Large Document Support:** Automatically splits long resumes into chunks to stay within AI context limits.
* **CLI Arguments:** Customize summary length and output paths directly from the terminal.

---

##  Getting Started

### 1. Prerequisites
* Python 3.8 or higher
* An OpenAI API Key

### 2. Installation
Clone this repository or download the source code, then:

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
