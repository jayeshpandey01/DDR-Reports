# Loom Video Script: AI-Powered DDR Report Pipeline

This script is designed for a **3-5 minute** presentation covering the core requirements.

---

## 🕒 0:00 - 0:45 | 1. What I Built
- **Greeting**: "Hi, my name is [Your Name]. For this challenge, I built an end-to-end **AI-Powered DDR Report Pipeline**."
- **Problem**: "Manual inspection reports are time-consuming and prone to errors. Text and images are often disconnected."
- **The Solution**: "I built a professional web application that takes raw structural and thermal PDF reports and automatically generates a 50+ page, color-coded, diagnostic PDF with images correctly mapped to observations."
- **Show Results**: *[Show the Web UI at localhost:8000/app/index.html]* "This is the interface where users can simply drag and drop their files to trigger the analysis."

---

## 🕒 0:45 - 2:30 | 2. How It Works
- **The Pipeline**: "The system follows a 3-step architecture: Extraction, AI Analysis, and Professional Generation."
- **Extraction (`PyMuPDF`)**: "We first extract text and images. I implemented a noise filter to discard items under 150px, ensuring only relevant inspection photos reach the AI."
- **AI Analysis (`Gemini 2.5 Flash`)**: "The heart of the app is Gemini 2.5 Flash. I use a strict Pydantic schema and detailed prompt engineering to ensure the AI identifies severity, suggests technical remedies (like epoxy grouting), and maps the correct photos to the correct areas."
- **Reliability**: "I integrated the `tenacity` library for exponential backoff retries, ensuring the pipeline recovers automatically from any API timeouts or quota issues."
- **PDF Generation (`fpdf2`)**: "The backend generates a professional document with a dedicated Table of Contents, color-coded checklists (Green/Orange/Red), and a smart image grid to save space."

---

## 🕒 2:30 - 3:30 | 3. Limitations
- **Page Context Mapping**: "Currently, image mapping relies on the page context where the image was found. While highly accurate, it doesn't use pixel-perfect coordinates yet."
- **Processing Time**: "Because each report can be 50+ pages, the AI analysis takes about 45-60 seconds. Currently, this is a sequential process."
- **Layout Constraints**: "The PDF output is currently optimized for A4 portrait layout and doesn't support dynamic orientations or custom branding themes yet."

---

## 🕒 3:30 - 4:30 | 4. How I Would Improve It
- **OCR-Based Mapping**: "I would implement OCR coordinate mapping to link images to specific text blocks with 100% precision, regardless of page flow."
- **Batch Processing**: "I'd add a Celery/Redis queue to handle multiple report generations in parallel, allowing users to upload dozens of files at once."
- **Interactive dashboard**: "Instead of a static PDF, I'd build an interactive dashboard where users can click on an issue to see the thermal overlay and edit the AI-suggested remedies before exporting."

---

## 🕒 4:30 - 5:00 | Conclusion
- **Conclusion**: "Thank you for watching! This project proves that AI can transform raw inspection data into professional, actionable intelligence in seconds. The full source code and ARCHITECTURE.md are available in the repository."

---
*Pro Tip: Have the final PDF open and the Web UI ready to show the 'Generate' button in action while you speak!*
