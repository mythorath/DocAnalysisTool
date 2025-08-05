# Installation Guide

## Quick Start

### 1. Clone or Download Project
```bash
git clone <repository-url>
cd public-comment-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install System Dependencies

#### Windows (via Conda - Recommended)
```bash
conda install poppler tesseract -c conda-forge
```

#### Windows (Manual Installation)
1. **Tesseract OCR**: Download from https://github.com/UB-Mannheim/tesseract/wiki
2. **Poppler**: Download from https://blog.alivate.com.au/poppler-windows/

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

#### macOS
```bash
brew install tesseract poppler
```

### 4. Verify Installation
```bash
python main.py --help
```

## Detailed Setup

### Python Environment
- **Python 3.8+** required
- **Virtual environment** recommended

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependency Details

#### Core Processing
- `pandas`: Data manipulation and CSV handling
- `requests`: HTTP downloads with retry logic
- `tqdm`: Progress bars for long operations
- `numpy`: Numerical operations for ML

#### PDF and Document Processing
- `PyMuPDF`: Fast PDF text extraction
- `pdf2image`: PDF to image conversion for OCR
- `pytesseract`: Python wrapper for Tesseract OCR
- `Pillow`: Image processing
- `python-docx`: Microsoft Word document processing

#### Machine Learning and Text Analysis
- `scikit-learn`: Classical ML algorithms (TF-IDF, KMeans, LDA)
- `sentence-transformers`: BERT embeddings for semantic analysis
- `bertopic`: Advanced topic modeling with BERT
- `umap-learn`: Dimensionality reduction for clustering
- `hdbscan`: Density-based clustering
- `nltk`: Natural language processing toolkit

#### Visualization and Output
- `wordcloud`: Generate word clouds from text
- `matplotlib`: Basic plotting and visualization
- `plotly`: Interactive visualizations
- `openpyxl`: Excel file generation

### System Requirements

#### Minimum
- **RAM**: 4GB (8GB recommended for large document sets)
- **Storage**: 2GB free space (more for large document collections)
- **CPU**: Any modern processor (multi-core recommended)

#### Recommended for Large Datasets
- **RAM**: 16GB+ for processing 1000+ documents
- **Storage**: SSD for faster processing
- **CPU**: Multi-core processor for parallel processing

### Troubleshooting

#### Common Issues

**1. Tesseract not found**
```
TesseractNotFoundError: tesseract is not installed
```
- **Solution**: Install Tesseract and ensure it's in PATH
- **Windows**: Add Tesseract installation directory to PATH
- **Linux/macOS**: Install via package manager

**2. Poppler not found**
```
Unable to get page count. Is poppler installed and in PATH?
```
- **Solution**: Install Poppler utilities
- **Windows**: Use conda or download binaries
- **Linux**: `sudo apt-get install poppler-utils`

**3. Memory errors with large PDFs**
```
MemoryError during OCR processing
```
- **Solution**: Process files in smaller batches
- **Alternative**: Use `--single-file` option for individual processing

**4. NLTK data not found**
```
LookupError: Resource punkt not found
```
- **Solution**: NLTK data downloads automatically, but if it fails:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

**5. BERTopic model download issues**
```
ConnectionError: Failed to download model
```
- **Solution**: Ensure internet connection for first run
- **Alternative**: Use offline models or TF-IDF method

### Performance Optimization

#### For Large Document Collections
1. **Use SSD storage** for faster file I/O
2. **Increase RAM** for better caching
3. **Process in batches** using directory splitting
4. **Use TF-IDF + KMeans** for faster clustering

#### Configuration Options
```bash
# Fast processing (TF-IDF)
python main.py group --method tfidf_kmeans --clusters 5

# Best quality (BERTopic - slower)
python main.py group --method bertopic

# Memory efficient (LDA)
python main.py group --method lda --clusters 3
```

### Verification Tests

After installation, run these tests:

```bash
# Test download functionality
python downloader.py --help

# Test text extraction
python extractor.py --help

# Test search indexing
python indexer.py --help

# Test document grouping
python grouper.py --help

# Test complete workflow
python main.py --help
```

### Docker Installation (Alternative)

If you prefer Docker:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

CMD ["python", "main.py", "--help"]
```

### Next Steps

After successful installation:

1. **Prepare your data**: Create CSV file with document URLs
2. **Run the workflow**: Follow the usage examples in README.md
3. **Explore results**: Check output files in the `output/` directory
4. **Customize settings**: Modify clustering parameters as needed

For detailed usage instructions, see [README.md](README.md).