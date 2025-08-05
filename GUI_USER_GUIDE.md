# GUI User Guide - Public Comment Analysis Tool

## 🚀 Quick Start

### Windows
1. **Double-click** `launch_gui.bat` to start the application
2. **Alternative**: Open command prompt and run `python gui_app.py`

### Linux/macOS
1. **Run** `./launch_gui.sh` in terminal
2. **Alternative**: Run `python3 gui_app.py`

## 📋 Step-by-Step Workflow

### 1. Welcome Tab 🏠
- **Read instructions** and overview
- **Quick start buttons** for common tasks
- **Sample CSV format** reference

### 2. Download Tab ⬇️
1. **Load CSV File**: Click "Browse..." to select your CSV file
2. **Check Preview**: Verify document count and URLs found
3. **Set Download Directory**: Choose where to save files (default: `downloads/`)
4. **Start Download**: Click "🚀 Start Download"
5. **Monitor Progress**: Watch progress bar and log messages
6. **Review Results**: Check successful/failed download counts

### 3. Extract Tab 📝
1. **Set Input Directory**: Choose folder with downloaded documents (default: `downloads/`)
2. **Set Output Directory**: Choose where to save text files (default: `text/`)
3. **Start Extraction**: Click "🔤 Start Extraction"
4. **Monitor Progress**: Text extraction with OCR progress
5. **Review Results**: Check extraction statistics

### 4. Search Tab 🔍
1. **Build Index**: Click "🏗️ Build Index" to create searchable database
2. **Enter Search Query**: Type keywords, phrases, or boolean queries
3. **Set Limit**: Choose number of results (1-100)
4. **Search**: Click "🔍 Search" or press Enter
5. **Review Results**: Browse highlighted search results

### 5. Cluster Tab 🎯
1. **Choose Method**:
   - **🧠 BERTopic**: Best quality, advanced AI (recommended)
   - **⚡ TF-IDF + KMeans**: Fast, reliable
   - **📊 LDA**: Memory efficient
2. **Set Clusters**: Choose number or use "auto" detection
3. **Start Clustering**: Click "🚀 Start Clustering"
4. **Monitor Progress**: AI processing progress
5. **Review Results**: Check cluster statistics

### 6. Results Tab 📊
1. **View Summary**: Processing statistics and completion status
2. **Browse Results**: Table view of clustered documents
3. **Export Options**:
   - **📂 Open Output Folder**: View all generated files
   - **📊 View Clustering CSV**: Open results in Excel/CSV viewer
   - **🔍 Open Search Database**: Information about search index

## 🔍 Search Features

### Basic Search
- **Keywords**: `medicare`, `hospital`, `quality`
- **Multiple words**: `quality measures` (searches for both terms)

### Advanced Search
- **Exact phrases**: `"payment rate"` (must appear exactly)
- **Boolean operators**: `medicare AND quality`, `vanderbilt OR upmc`
- **Wildcards**: `hospital*` (finds hospital, hospitals, hospitalization)
- **Exclusion**: `medicare NOT advantage`

### Search Tips
- Use quotes for exact phrases
- Use AND/OR for complex queries
- Use * for word variations
- Check spelling and try synonyms
- Start broad, then narrow down

## 🎯 Clustering Methods Comparison

| Method | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **BERTopic** | Slow | Excellent | Topic discovery, semantic clustering |
| **TF-IDF + KMeans** | Fast | Good | Large datasets, known cluster count |
| **LDA** | Medium | Good | Statistical topics, interpretable results |

### When to Use Each Method

**BERTopic** (Recommended):
- ✅ Best semantic understanding
- ✅ Automatic topic discovery
- ✅ Works well with any document count
- ❌ Slower processing (30+ seconds)
- ❌ Requires internet for first model download

**TF-IDF + KMeans**:
- ✅ Very fast processing (5-10 seconds)
- ✅ Consistent results
- ✅ Works offline
- ❌ Requires specifying cluster count
- ❌ Less semantic understanding

**LDA Topic Modeling**:
- ✅ Memory efficient
- ✅ Interpretable statistical topics
- ✅ Good for academic analysis
- ❌ May need parameter tuning
- ❌ Less robust with small datasets

## 📁 File Structure

After processing, your project will contain:

```
project_folder/
├── input/
│   └── comment_links.csv          # Your input CSV
├── downloads/
│   ├── document1.pdf              # Downloaded PDFs
│   └── document2.docx             # Downloaded Word docs
├── text/
│   ├── document1.txt              # Extracted text
│   └── document2.txt              # Extracted text
├── output/
│   ├── bertopic_results.csv       # Clustering results
│   ├── bertopic_results_detailed.json  # Detailed metadata
│   └── document_index.db          # Search database
└── logs/
    ├── downloader.log             # Download activity
    ├── extractor.log              # Extraction activity
    └── indexer.log                # Search indexing activity
```

## 🛠️ Troubleshooting

### Common Issues

**"Module import error"**
- **Solution**: Install dependencies using `Tools > Install Dependencies`
- **Alternative**: Run `python install_windows_dependencies.py`

**"Tesseract not found"**
- **Windows**: Use dependency installer or install manually
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

**"Search index not found"**
- **Solution**: Go to Search tab and click "🏗️ Build Index"
- **Ensure**: Text extraction completed first

**"No documents found"**
- **Check**: CSV file has "Attachment Files" column
- **Verify**: URLs are accessible and valid
- **Review**: Download log for specific errors

**Slow processing**
- **OCR**: Normal for scanned PDFs (2-4 seconds per page)
- **BERTopic**: First run downloads models (one-time)
- **Large files**: Break into smaller batches

### Performance Tips

**For Large Document Collections (100+ files)**:
1. **Use TF-IDF + KMeans** for faster clustering
2. **Process in batches** of 50-100 documents
3. **Close other applications** to free memory
4. **Use SSD storage** for faster file operations

**Memory Optimization**:
- **Download**: Process in chunks if memory limited
- **Extraction**: Use single-file mode for large PDFs
- **Clustering**: Reduce cluster count if memory errors occur

### Getting Help

**Built-in Help**:
- **Menu**: Help > User Guide
- **Tooltips**: Hover over buttons for hints
- **Status Bar**: Shows current operation status

**Log Files**:
- **Download issues**: Check `logs/downloader.log`
- **Text extraction**: Check `logs/extractor.log`
- **Search problems**: Check `logs/indexer.log`

**Reset Application**:
1. **Close GUI**
2. **Delete**: `output/` folder contents
3. **Restart**: Application for fresh start

## 📊 Output Files Explained

### CSV Results File
- **filename**: Original document name
- **document_id**: Extracted document identifier
- **organization**: Source organization (from CSV)
- **category**: Document category (from CSV)
- **cluster_id**: Assigned cluster number
- **cluster_keywords**: Top keywords for the cluster
- **document_keywords**: Keywords specific to document
- **summary**: First 500 characters of document

### JSON Detailed Results
- **Complete clustering metadata**
- **Algorithm parameters used**
- **Cluster quality metrics**
- **Processing timestamps**
- **Error logs and warnings**

### Search Database
- **SQLite FTS5 database**
- **Full-text searchable**
- **Metadata linked to original CSV**
- **Can be queried with SQL tools**

## 🎉 Success Checklist

After completing the workflow, you should have:

- ✅ **Downloaded documents** in `downloads/` folder
- ✅ **Extracted text** in `text/` folder  
- ✅ **Search database** in `output/document_index.db`
- ✅ **Clustering results** in `output/*_results.csv`
- ✅ **Processing logs** in `logs/` folder
- ✅ **Working search** functionality
- ✅ **Organized document clusters** with keywords

You can now:
- 🔍 **Search** your document collection instantly
- 📊 **Analyze** document themes and topics
- 📋 **Export** results for further analysis
- 🎯 **Identify** key organizations and categories
- 📈 **Report** on document patterns and trends