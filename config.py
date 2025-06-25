#!/usr/bin/env python3
"""
Configuration settings for the Docling PDF Processor.
"""

# Processing Options
PROCESSING_CONFIG = {
    # OCR Settings
    "enable_ocr": True,                    # Enable OCR for scanned documents
    "ocr_languages": ["en"],               # OCR languages (e.g., ["en", "es", "fr"])
    
    # Table Extraction
    "enable_tables": True,                 # Extract table structures
    "table_cell_matching": True,           # Match table cells for better structure
    
    # Image Processing
    "generate_page_images": True,          # Generate page images
    "generate_picture_images": True,       # Generate individual picture images
    "enable_picture_classification": True, # Classify pictures (chart, photo, etc.)
    "image_resolution_scale": 2,          # Image resolution scale factor
    
    # Advanced Features
    "enable_code_enrichment": False,       # Detect and extract code blocks
    "enable_formula_enrichment": False,    # Detect and extract mathematical formulas
    
    # Performance Settings
    "num_threads": 4,                     # Number of processing threads
    "device": "auto",                     # Processing device: "auto", "cpu", "cuda"
}

# Output Settings
OUTPUT_CONFIG = {
    "output_directory": "output",          # Directory to save processed files
    "save_json": True,                    # Save as structured JSON
    "save_markdown": True,                # Save as Markdown
    "save_html": True,                    # Save as HTML
    "save_text": True,                    # Save as plain text
    "save_summary": True,                 # Save processing summary
    
    # Image handling in exports
    "image_mode": "placeholder",          # "placeholder", "embedded", "referenced"
    
    # JSON formatting
    "json_indent": 2,                     # JSON indentation
    "json_ensure_ascii": False,           # Allow unicode characters in JSON
}

# File Handling
FILE_CONFIG = {
    "supported_extensions": [".pdf"],      # Supported file extensions
    "max_file_size_mb": 100,              # Maximum file size in MB
    "create_backup": False,               # Create backup of original file
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",                      # Logging level: DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "save_logs": True,                    # Save logs to file
    "log_file": "processing.log",         # Log file name
}
