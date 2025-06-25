# Docling PDF Reader

A simple Python tool that uses [Docling](https://github.com/docling-project/docling) to extract text, tables, and images from PDF documents.

## Quick Start

1. **Install dependencies:**
   ```bash
   ./install.sh
   ```

2. **Process a PDF:**
   ```bash
   python pdf_processor.py your_document.pdf
   # or for advanced features
   python advanced_processor.py your_document.pdf
   ```

3. **Check results** in the `output/` folder

## Features

- ✅ Extract text with structure preservation
- ✅ Table extraction and conversion
- ✅ Image and figure processing  
- ✅ OCR support for scanned documents
- ✅ Multiple output formats (JSON, Markdown, HTML, Text)
- ✅ Configurable processing options

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt)

## Configuration

Modify settings in [config.py](config.py):

```python
PROCESSING_CONFIG = {
    "enable_ocr": True,        # For scanned documents
    "enable_tables": True,     # Extract tables
    # ... more options
}
```

## Command Line Options

```bash
# Basic processing
python pdf_processor.py document.pdf

# Advanced with options
python advanced_processor.py document.pdf --no-ocr --simple
```

## Output Files

- `document.json` - Structured data
- `document.md` - Markdown format
- `document.html` - Web format
- `document_report.txt` - Processing summary

## License

MIT License - feel free to use and modify!
