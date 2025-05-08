import os
import time
import shutil
import fitz  # PyMuPDF
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Using our own simple tokenizer instead of nltk
def sent_tokenize(text):
    import re
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def summarize_to_bullets(summary):
    sentences = sent_tokenize(summary)
    bullets = [f"- {s.strip()}" for s in sentences]
    return "\n".join(bullets)

def extract_conclusion(text):
    lowered = text.lower()

    patterns = [
        r'\n\s*conclusion[s]?\s*\n',
        r'\n\s*summary\s*\n',              # Sometimes used instead
        r'\n\s*discussion\s*\n',           # Occasionally overlaps
    ]

    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            start_idx = match.end()
            # Try to capture around 1000 characters after the heading
            conclusion_text = text[start_idx:start_idx + 1000]

            # Try to cut at the next big heading if it exists
            end_heading = re.search(r'\n\s*[A-Z][A-Za-z\s]{3,30}\s*\n', conclusion_text)
            if end_heading:
                conclusion_text = conclusion_text[:end_heading.start()]

            return conclusion_text.strip()

    return "Conclusion not found."


# ==== CONFIG ====
INCOMING_FOLDER = "C:\\Automation\\PaperDrop"
VAULT_PATH = "C:\\ResearchPaperVault\\ResearchPaperVault"
PDF_FOLDER = os.path.join(VAULT_PATH, "Papers")
NOTE_FOLDER = os.path.join(VAULT_PATH, "Notes")

# Summarizer from HuggingFace
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def generate_summary(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = []
    for chunk in chunks[:3]:  # Limit to avoid long processing
        out = summarizer(chunk, max_length=150, min_length=60, do_sample=False)
        summary.append(out[0]['summary_text'])
    return "\n".join(summary)

def generate_tags(text, top_n=5):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X = vectorizer.fit_transform([text])
    indices = X.toarray()[0].argsort()[-top_n:][::-1]
    tags = [vectorizer.get_feature_names_out()[i] for i in indices]
    return tags

def create_markdown_note(title, summary, tags, pdf_filename, conclusion):
    tag_string = " ".join([f"#{tag}" for tag in tags])
    bullet_points = summarize_to_bullets(summary)
    
    md_content = f"""---
title: "{title}"
tags: [{', '.join(tags)}]
source_pdf: ./Papers/{pdf_filename}
created: {time.strftime('%Y-%m-%d')}
---

## 🔍 Summary
{summary}

## 🧠 Key Points
{bullet_points}

## ✅ Conclusion
{conclusion}

## 📎 Link to PDF
[Open PDF](../Papers/{pdf_filename})
"""
    return md_content

class PaperHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".pdf"):
            print(f"[INFO] New PDF: {event.src_path}")
            time.sleep(1)  # Give OS a second to finish copying

            filename = os.path.basename(event.src_path)
            pdf_dest = os.path.join(PDF_FOLDER, filename)
            shutil.move(event.src_path, pdf_dest)

            # === Extract text from PDF ===
            text = extract_text_from_pdf(pdf_dest)

            # === Generate summary and tags ===
            summary = generate_summary(text)
            tags = generate_tags(text)

            # === Extract conclusion ===
            conclusion = extract_conclusion(text)

            # === Create Markdown note ===
            note_filename = filename.replace(".pdf", ".md")
            note_path = os.path.join(NOTE_FOLDER, note_filename)

            md_content = create_markdown_note(
                title=filename.replace(".pdf", ""),
                summary=summary,
                tags=tags,
                pdf_filename=filename,
                conclusion=conclusion  # 🧠 new arg here
            )

            with open(note_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            print(f"[✅ SUCCESS] Note created: {note_path}")


def start_obsidian_watcher():
    print(f"📚 Watching folder: {INCOMING_FOLDER}")
    observer = Observer()
    handler = PaperHandler()
    observer.schedule(handler, path=INCOMING_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
	start_obsidian_watcher()
