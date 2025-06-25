#!/usr/bin/env python3
"""
Docling PDF Processor

A simple script that uses Docling to extract and process PDF documents,
converting them to structured JSON format along with other export formats.

Usage:
    python pdf_processor.py <pdf_file_path>

Example:
    python pdf_processor.py sample_document.pdf
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DoclingPDFProcessor:
    """
    A processor class that handles PDF document extraction using Docling.
    """
    
    def __init__(self, enable_ocr: bool = True, enable_tables: bool = True):
        """
        Initialize the PDF processor with configuration options.
        
        Args:
            enable_ocr: Whether to enable OCR for scanned documents
            enable_tables: Whether to enable table structure extraction
        """
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure pipeline options
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = enable_ocr
        self.pipeline_options.do_table_structure = enable_tables
        
        if enable_tables:
            self.pipeline_options.table_structure_options.do_cell_matching = True
        
        # Enable additional features for comprehensive extraction
        self.pipeline_options.generate_page_images = True
        self.pipeline_options.generate_picture_images = True
        self.pipeline_options.do_picture_classification = True
        
        # Initialize the document converter
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=self.pipeline_options
                )
            }
        )
        
        logger.info("DoclingPDFProcessor initialized with OCR=%s, Tables=%s", 
                   enable_ocr, enable_tables)
    
    def process_pdf(self, pdf_path: str) -> Optional[dict]:
        """
        Process a PDF file and extract its content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing the extracted document data, or None if processing failed
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        if not pdf_file.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {pdf_path}")
            return None
        
        logger.info(f"Processing PDF: {pdf_file.name}")
        start_time = time.time()
        
        try:
            # Convert the document
            result = self.converter.convert(pdf_file)
            
            if result.status.name != 'SUCCESS':
                logger.error(f"Conversion failed with status: {result.status.name}")
                return None
            
            processing_time = time.time() - start_time
            logger.info(f"PDF processed successfully in {processing_time:.2f} seconds")
            
            # Extract document data
            document = result.document
            document_data = document.export_to_dict()
            
            # Add processing metadata
            document_data['processing_metadata'] = {
                'source_file': str(pdf_file),
                'processing_time_seconds': round(processing_time, 2),
                'num_pages': document.num_pages(),
                'docling_version': 'Latest',
                'processing_options': {
                    'ocr_enabled': self.pipeline_options.do_ocr,
                    'table_extraction_enabled': self.pipeline_options.do_table_structure,
                    'picture_classification_enabled': self.pipeline_options.do_picture_classification
                }
            }
            
            # Save outputs
            self._save_outputs(document, pdf_file, document_data)
            
            return document_data
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return None
    
    def _save_outputs(self, document, pdf_file: Path, document_data: dict):
        """
        Save the extracted document in various formats.
        
        Args:
            document: The Docling document object
            pdf_file: Original PDF file path
            document_data: Extracted document data as dictionary
        """
        base_filename = pdf_file.stem
        
        # Save as JSON
        json_path = self.output_dir / f"{base_filename}.json"
        with json_path.open('w', encoding='utf-8') as f:
            json.dump(document_data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON output saved: {json_path}")
        
        # Save as Markdown
        md_path = self.output_dir / f"{base_filename}.md"
        document.save_as_markdown(
            filename=md_path,
            image_mode=ImageRefMode.PLACEHOLDER
        )
        logger.info(f"Markdown output saved: {md_path}")
        
        # Save as HTML
        html_path = self.output_dir / f"{base_filename}.html"
        document.save_as_html(
            filename=html_path,
            image_mode=ImageRefMode.PLACEHOLDER
        )
        logger.info(f"HTML output saved: {html_path}")
        
        # Save summary information
        summary_path = self.output_dir / f"{base_filename}_summary.txt"
        with summary_path.open('w', encoding='utf-8') as f:
            f.write(f"Document Processing Summary\n")
            f.write(f"==========================\n\n")
            f.write(f"Source File: {pdf_file.name}\n")
            f.write(f"Number of Pages: {document.num_pages()}\n")
            f.write(f"Number of Tables: {len(document.tables)}\n")
            f.write(f"Number of Pictures: {len(document.pictures)}\n")
            f.write(f"Processing Time: {document_data['processing_metadata']['processing_time_seconds']} seconds\n\n")
            
            # Add table information if any
            if document.tables:
                f.write("Tables Found:\n")
                for i, table in enumerate(document.tables, 1):
                    try:
                        df = table.export_to_dataframe()
                        f.write(f"  Table {i}: {df.shape[0]} rows × {df.shape[1]} columns\n")
                    except:
                        f.write(f"  Table {i}: Structure available\n")
                f.write("\n")
            
            # Add a preview of the extracted text
            text_preview = document.export_to_markdown(strict_text=True)[:500]
            f.write("Text Preview (first 500 characters):\n")
            f.write(f"{text_preview}...\n")
        
        logger.info(f"Summary saved: {summary_path}")


def main():
    """
    Main function to run the PDF processor from command line.
    """
    if len(sys.argv) != 2:
        print("Usage: python pdf_processor.py <pdf_file_path>")
        print("Example: python pdf_processor.py sample_document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if it's a placeholder file
    if pdf_path == "sample_document.pdf" and not Path(pdf_path).exists():
        print("\n" + "="*60)
        print("PLACEHOLDER FILE DETECTED")
        print("="*60)
        print("The file 'sample_document.pdf' is a placeholder.")
        print("Please place your actual PDF file in the project directory and run:")
        print(f"python pdf_processor.py your_actual_file.pdf")
        print("="*60)
        sys.exit(1)
    
    # Initialize processor
    processor = DoclingPDFProcessor(
        enable_ocr=True,      # Enable OCR for scanned documents
        enable_tables=True    # Enable table extraction
    )
    
    # Process the PDF
    result = processor.process_pdf(pdf_path)
    
    if result:
        print("\n" + "="*60)
        print("PROCESSING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"✓ Processed: {pdf_path}")
        print(f"✓ Pages: {result['processing_metadata']['num_pages']}")
        print(f"✓ Time: {result['processing_metadata']['processing_time_seconds']} seconds")
        print(f"✓ Output directory: ./output/")
        print("\nGenerated files:")
        base_name = Path(pdf_path).stem
        print(f"  • {base_name}.json (structured data)")
        print(f"  • {base_name}.md (markdown format)")
        print(f"  • {base_name}.html (web format)")
        print(f"  • {base_name}_summary.txt (processing summary)")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("PROCESSING FAILED")
        print("="*60)
        print("Please check the error messages above.")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
