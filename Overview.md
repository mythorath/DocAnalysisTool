

## 🧠 Project Overview

**Goal:**
Create a Python-based desktop or CLI app that:

1. Downloads all linked documents from a provided spreadsheet.
2. Converts all non-searchable files (e.g. scanned PDFs) into machine-searchable format via OCR.
3. Indexes all text for keyword and phrase search.
4. Clusters or groups documents based on similar keywords or themes.

---

## 📁 Input

* CSV file with comment letter URLs (like the one you received).
* Each row contains:

  * Link (mostly PDFs)
  * Document metadata (optional: docket ID, commenter name, etc.)

---

## 🧰 Output

* Folder with all downloaded and OCR-processed PDFs.
* A searchable index of documents.
* A grouped/exported dataset, possibly in Excel/CSV, showing:

  * Detected keywords/topics per document.
  * Group assignment (cluster label or theme).
  * Search result hits per document (if applicable).

---

## 🔧 App Design Plan

### 1. **Downloader Module**

* Parse the CSV.
* Validate links (retry broken links).
* Download all files (PDF and otherwise).
* Save with unique, sanitized filenames.

### 2. **PDF OCR + Preprocessing Module**

* Detect if PDF is text-based or image-based.

  * Use `PyMuPDF`, `pdfminer.six`, or `pypdf` to check for text.
* If not text-based:

  * Convert pages to images.
  * Use Tesseract OCR to extract text.
* Store extracted text alongside PDF (as `.txt` or `.json`).

### 3. **Searchable Index Creation**

* Use `Whoosh`, `ElasticSearch`, or `sqlite + full-text index` to build a local keyword search engine.
* Enable basic phrase search, keyword highlight, boolean support.

### 4. **Keyword Detection + Grouping**

* Extract:

  * Top N keywords per document (via `TF-IDF`, `RAKE`, or `KeyBERT`)
  * Topics (via `BERTopic`, `LDA`, or sentence embeddings + KMeans)
* Output:

  * Grouped documents by dominant keyword/theme
  * CSV with group labels, keyword hits, document summaries

### 5. **Frontend (Optional)**

CLI is fine for now:

* `download_and_process.py <csv_path>`
* `search.py "<keyword>"`
* `group_by_topic.py --method bertopic`

Later, a minimal Streamlit or Tkinter UI can be added.

---

## 🔐 Dependencies & Stack

* `requests`, `pandas`, `tqdm`
* `PyMuPDF` / `pdfminer.six`
* `pytesseract`, `pdf2image`, `Pillow`
* `scikit-learn`, `KeyBERT`, `BERTopic`, `nltk`
* Optional: `streamlit`, `openpyxl`, `sqlite3`

---

## 🗺️ Development Roadmap

### Phase 1 – Setup and Downloader

* [x] Load and parse CSV
* [x] Download and save PDFs
* [ ] Retry failed downloads and log them

### Phase 2 – Text Extraction

* [ ] Detect text-based vs scanned PDFs
* [ ] Extract text via PDF parser or Tesseract OCR
* [ ] Save `.txt` for each PDF

### Phase 3 – Keyword Search + Topic Grouping

* [ ] Create full-text index for searching
* [ ] Extract keywords for each document
* [ ] Cluster or group documents by topic

### Phase 4 – Export & Reporting

* [ ] Export full summary CSV (filename, key topics, hit count, etc.)
* [ ] Export grouped folder view or Excel sheet

---

## ✅ Deliverables

* Python script(s) for:

  * Document download
  * OCR + text extraction
  * Search + keyword clustering
* Output folder with:

  * All downloaded PDFs
  * Text files and metadata
* Summary CSV file with:

  * Keyword hits
  * Cluster labels
  * Link back to source


