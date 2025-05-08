# 🧾 PDF to Obsidian AI Note Generator

This Python automation script monitors a local folder for incoming PDF files, extracts and summarizes their content using an AI model, and creates structured Obsidian-compatible markdown notes. The goal is to streamline your research and note-taking workflow with minimal manual effort.

======================================================================

## 📁 How It Works

1. Place a PDF file into a monitored folder (`C:\Automation\PaperDrop`).
2. The script automatically:
   - Moves the PDF into your Obsidian vault (`Papers/` subfolder)
   - Extracts text using PyMuPDF
   - Summarizes the content using a HuggingFace transformer
   - Generates keywords using TF-IDF
   - Extracts the conclusion section (if found)
   - Creates a markdown note with metadata and links
   - Saves the note into the Obsidian vault (`Notes/` subfolder)

======================================================================

## 🧰 Dependencies

- Python 3.8+
- [transformers (Hugging Face)](https://huggingface.co/docs/transformers/)
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
- [scikit-learn](https://scikit-learn.org/)
- [watchdog](https://pypi.org/project/watchdog/)

Install all dependencies with:

```bash
pip install -r requirements.txt
```

======================================================================

The following paths are hardcoded in the script. 
Please revise to match your loacl machine directory.

INCOMING_FOLDER = "C:\\Automation\\PaperDrop"
VAULT_PATH = "C:\\ResearchPaperVault\\ResearchPaperVault"
PDF_FOLDER = os.path.join(VAULT_PATH, "Papers")
NOTE_FOLDER = os.path.join(VAULT_PATH, "Notes")

======================================================================

[Example]
---
title: "Sample_Research_Paper"
tags: [machine, learning, neural, model, accuracy]
source_pdf: ./Papers/Sample_Research_Paper.pdf
created: 2025-05-08
---

## 🔍 Summary
This paper explores...

## 🧠 Key Points
- The model achieves state-of-the-art...
- Evaluation was done on...

## ✅ Conclusion
The results demonstrate...

## 📎 Link to PDF
[Open PDF](../Papers/Sample_Research_Paper.pdf)

======================================================================
