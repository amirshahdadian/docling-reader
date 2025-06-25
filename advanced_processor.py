#!/usr/bin/env python3
"""
Advanced PDF Processor using Docling with configuration support.

This version includes configuration file support and additional features.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import ImageRefMode
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("Warning: Docling not installed. Install with: pip install -r requirements.txt")

from config import PROCESSING_CONFIG, OUTPUT_CONFIG, FILE_CONFIG, LOGGING_CONFIG


class AdvancedDoclingProcessor:
    """
    Advanced PDF processor with configuration support and extended features.
    """
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize the processor with configuration.
        
        Args:
            config_override: Optional configuration overrides
        """
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is not installed. Please run: pip install -r requirements.txt")
        
        # Merge configuration
        self.processing_config = {**PROCESSING_CONFIG}
        self.output_config = {**OUTPUT_CONFIG}
        self.file_config = {**FILE_CONFIG}
        
        if config_override:
            self.processing_config.update(config_override.get('processing', {}))
            self.output_config.update(config_override.get('output', {}))
            self.file_config.update(config_override.get('file', {}))
        
        # Setup logging
        self._setup_logging()
        
        # Setup output directory
        self.output_dir = Path(self.output_config['output_directory'])
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Docling converter
        self._setup_converter()
        
        self.logger.info("AdvancedDoclingProcessor initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, LOGGING_CONFIG['level'].upper())
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=LOGGING_CONFIG['format'],
            handlers=[]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if enabled
        if LOGGING_CONFIG['save_logs']:
            file_handler = logging.FileHandler(LOGGING_CONFIG['log_file'])
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _setup_converter(self):
        """Setup the Docling document converter with configuration."""
        # Configure pipeline options
        pipeline_options = PdfPipelineOptions()
        
        # OCR settings
        pipeline_options.do_ocr = self.processing_config['enable_ocr']
        if self.processing_config['enable_ocr']:
            # Note: OCR language configuration would go here
            pass
        
        # Table extraction
        pipeline_options.do_table_structure = self.processing_config['enable_tables']
        if self.processing_config['enable_tables']:
            pipeline_options.table_structure_options.do_cell_matching = self.processing_config['table_cell_matching']
        
        # Image processing
        pipeline_options.generate_page_images = self.processing_config['generate_page_images']
        pipeline_options.generate_picture_images = self.processing_config['generate_picture_images']
        pipeline_options.do_picture_classification = self.processing_config['enable_picture_classification']
        
        if self.processing_config['generate_page_images']:
            pipeline_options.images_scale = self.processing_config['image_resolution_scale']
        
        # Advanced features
        pipeline_options.do_code_enrichment = self.processing_config['enable_code_enrichment']
        pipeline_options.do_formula_enrichment = self.processing_config['enable_formula_enrichment']
        
        # Performance settings
        try:
            from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
            
            device_map = {
                'auto': AcceleratorDevice.AUTO,
                'cpu': AcceleratorDevice.CPU,
                'cuda': AcceleratorDevice.CUDA
            }
            
            device = device_map.get(self.processing_config['device'], AcceleratorDevice.AUTO)
            pipeline_options.accelerator_options = AcceleratorOptions(
                num_threads=self.processing_config['num_threads'],
                device=device
            )
        except ImportError:
            self.logger.warning("Accelerator options not available")
        
        # Initialize converter
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
    
    def process_pdf(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a PDF file with comprehensive extraction.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted data and metadata
        """
        pdf_file = Path(pdf_path)
        
        # Validate input
        if not self._validate_input_file(pdf_file):
            return None
        
        self.logger.info(f"Starting processing: {pdf_file.name}")
        start_time = time.time()
        
        try:
            # Convert document
            result = self.converter.convert(pdf_file)
            
            if result.status.name != 'SUCCESS':
                self.logger.error(f"Conversion failed with status: {result.status.name}")
                return None
            
            processing_time = time.time() - start_time
            document = result.document
            
            # Extract comprehensive data
            extracted_data = self._extract_comprehensive_data(document, pdf_file, processing_time)
            
            # Save outputs
            if any([self.output_config['save_json'], self.output_config['save_markdown'], 
                   self.output_config['save_html'], self.output_config['save_text']]):
                self._save_all_outputs(document, pdf_file, extracted_data)
            
            self.logger.info(f"Processing completed in {processing_time:.2f} seconds")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}", exc_info=True)
            return None
    
    def _validate_input_file(self, pdf_file: Path) -> bool:
        """Validate the input PDF file."""
        if not pdf_file.exists():
            self.logger.error(f"File not found: {pdf_file}")
            return False
        
        if pdf_file.suffix.lower() not in self.file_config['supported_extensions']:
            self.logger.error(f"Unsupported file type: {pdf_file.suffix}")
            return False
        
        # Check file size
        file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
        if file_size_mb > self.file_config['max_file_size_mb']:
            self.logger.error(f"File too large: {file_size_mb:.1f}MB > {self.file_config['max_file_size_mb']}MB")
            return False
        
        return True
    
    def _extract_comprehensive_data(self, document, pdf_file: Path, processing_time: float) -> Dict[str, Any]:
        """Extract comprehensive data from the processed document."""
        # Basic document data
        document_data = document.export_to_dict()
        
        # Enhanced metadata
        metadata = {
            'source_file': str(pdf_file),
            'file_size_mb': round(pdf_file.stat().st_size / (1024 * 1024), 2),
            'processing_time_seconds': round(processing_time, 2),
            'num_pages': document.num_pages(),
            'processor_version': 'Advanced Docling Processor v1.0',
            'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'configuration': {
                'ocr_enabled': self.processing_config['enable_ocr'],
                'table_extraction': self.processing_config['enable_tables'],
                'image_processing': self.processing_config['generate_picture_images'],
                'picture_classification': self.processing_config['enable_picture_classification']
            }
        }
        
        # Content statistics
        stats = {
            'num_tables': len(document.tables),
            'num_pictures': len(document.pictures),
            'num_figures': len([item for item in document.texts if 'Figure' in str(item)]),
            'estimated_word_count': len(document.export_to_markdown(strict_text=True).split())
        }
        
        # Combine all data
        comprehensive_data = {
            'metadata': metadata,
            'statistics': stats,
            'document_content': document_data,
            'extraction_summary': self._generate_extraction_summary(document)
        }
        
        return comprehensive_data
    
    def _generate_extraction_summary(self, document) -> Dict[str, Any]:
        """Generate a summary of extracted content."""
        summary = {
            'pages': document.num_pages(),
            'tables': [],
            'images': [],
            'text_preview': document.export_to_markdown(strict_text=True)[:500] + "..."
        }
        
        # Table summaries
        for i, table in enumerate(document.tables):
            try:
                df = table.export_to_dataframe()
                summary['tables'].append({
                    'table_id': i + 1,
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'has_headers': True  # This could be determined more accurately
                })
            except Exception:
                summary['tables'].append({
                    'table_id': i + 1,
                    'rows': 'unknown',
                    'columns': 'unknown',
                    'has_headers': 'unknown'
                })
        
        # Image summaries
        for i, picture in enumerate(document.pictures):
            summary['images'].append({
                'image_id': i + 1,
                'type': 'picture',
                'has_classification': hasattr(picture, 'classification')
            })
        
        return summary
    
    def _save_all_outputs(self, document, pdf_file: Path, extracted_data: Dict[str, Any]):
        """Save all configured output formats."""
        base_filename = pdf_file.stem
        
        # JSON output
        if self.output_config['save_json']:
            json_path = self.output_dir / f"{base_filename}.json"
            with json_path.open('w', encoding='utf-8') as f:
                json.dump(
                    extracted_data, 
                    f, 
                    indent=self.output_config['json_indent'],
                    ensure_ascii=self.output_config['json_ensure_ascii']
                )
            self.logger.info(f"Saved JSON: {json_path}")
        
        # Image mode mapping
        image_mode_map = {
            'placeholder': ImageRefMode.PLACEHOLDER,
            'embedded': ImageRefMode.EMBEDDED,
            'referenced': ImageRefMode.REFERENCED
        }
        image_mode = image_mode_map.get(self.output_config['image_mode'], ImageRefMode.PLACEHOLDER)
        
        # Markdown output
        if self.output_config['save_markdown']:
            md_path = self.output_dir / f"{base_filename}.md"
            document.save_as_markdown(filename=md_path, image_mode=image_mode)
            self.logger.info(f"Saved Markdown: {md_path}")
        
        # HTML output
        if self.output_config['save_html']:
            html_path = self.output_dir / f"{base_filename}.html"
            document.save_as_html(filename=html_path, image_mode=image_mode)
            self.logger.info(f"Saved HTML: {html_path}")
        
        # Plain text output
        if self.output_config['save_text']:
            txt_path = self.output_dir / f"{base_filename}.txt"
            with txt_path.open('w', encoding='utf-8') as f:
                f.write(document.export_to_markdown(strict_text=True))
            self.logger.info(f"Saved Text: {txt_path}")
        
        # Summary report
        if self.output_config['save_summary']:
            summary_path = self.output_dir / f"{base_filename}_report.txt"
            self._save_summary_report(summary_path, extracted_data)
            self.logger.info(f"Saved Summary: {summary_path}")
    
    def _save_summary_report(self, summary_path: Path, extracted_data: Dict[str, Any]):
        """Save a detailed summary report."""
        with summary_path.open('w', encoding='utf-8') as f:
            f.write("DOCLING PDF PROCESSING REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Metadata section
            metadata = extracted_data['metadata']
            f.write("DOCUMENT INFORMATION\n")
            f.write("-" * 20 + "\n")
            f.write(f"Source File: {metadata['source_file']}\n")
            f.write(f"File Size: {metadata['file_size_mb']} MB\n")
            f.write(f"Processing Time: {metadata['processing_time_seconds']} seconds\n")
            f.write(f"Processed On: {metadata['processing_timestamp']}\n")
            f.write(f"Total Pages: {metadata['num_pages']}\n\n")
            
            # Statistics section
            stats = extracted_data['statistics']
            f.write("CONTENT STATISTICS\n")
            f.write("-" * 18 + "\n")
            f.write(f"Tables Found: {stats['num_tables']}\n")
            f.write(f"Images Found: {stats['num_pictures']}\n")
            f.write(f"Figures Found: {stats['num_figures']}\n")
            f.write(f"Estimated Word Count: {stats['estimated_word_count']}\n\n")
            
            # Configuration section
            config = metadata['configuration']
            f.write("PROCESSING CONFIGURATION\n")
            f.write("-" * 24 + "\n")
            f.write(f"OCR Enabled: {config['ocr_enabled']}\n")
            f.write(f"Table Extraction: {config['table_extraction']}\n")
            f.write(f"Image Processing: {config['image_processing']}\n")
            f.write(f"Picture Classification: {config['picture_classification']}\n\n")
            
            # Content summary
            summary = extracted_data['extraction_summary']
            if summary['tables']:
                f.write("TABLES SUMMARY\n")
                f.write("-" * 14 + "\n")
                for table in summary['tables']:
                    f.write(f"Table {table['table_id']}: {table['rows']} rows × {table['columns']} columns\n")
                f.write("\n")
            
            # Text preview
            f.write("TEXT PREVIEW\n")
            f.write("-" * 12 + "\n")
            f.write(summary['text_preview'])
            f.write("\n\n")
            
            f.write("=" * 50 + "\n")
            f.write("Report generated by Advanced Docling Processor\n")


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python advanced_processor.py <pdf_file_path> [options]")
        print("\nOptions:")
        print("  --no-ocr          Disable OCR processing")
        print("  --no-tables       Disable table extraction")
        print("  --simple          Use simple processing (faster)")
        print("\nExample:")
        print("  python advanced_processor.py document.pdf")
        print("  python advanced_processor.py document.pdf --no-ocr --simple")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Parse command line options
    config_override = {'processing': {}, 'output': {}}
    
    if '--no-ocr' in sys.argv:
        config_override['processing']['enable_ocr'] = False
    
    if '--no-tables' in sys.argv:
        config_override['processing']['enable_tables'] = False
    
    if '--simple' in sys.argv:
        config_override['processing'].update({
            'enable_picture_classification': False,
            'enable_code_enrichment': False,
            'enable_formula_enrichment': False,
            'generate_picture_images': False
        })
    
    # Check for placeholder
    if pdf_path == "sample_document.pdf" and not Path(pdf_path).exists():
        print("\n" + "="*60)
        print("PLACEHOLDER DETECTED")
        print("="*60)
        print("Please place your actual PDF file and run:")
        print("python advanced_processor.py your_file.pdf")
        print("="*60)
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = AdvancedDoclingProcessor(config_override)
        
        # Process PDF
        result = processor.process_pdf(pdf_path)
        
        if result:
            print("\n" + "="*60)
            print("PROCESSING COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"✓ File: {pdf_path}")
            print(f"✓ Pages: {result['metadata']['num_pages']}")
            print(f"✓ Time: {result['metadata']['processing_time_seconds']}s")
            print(f"✓ Tables: {result['statistics']['num_tables']}")
            print(f"✓ Images: {result['statistics']['num_pictures']}")
            print(f"✓ Output: ./output/")
            print("="*60)
        else:
            print("Processing failed. Check logs for details.")
            sys.exit(1)
            
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
