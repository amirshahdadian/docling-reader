# Docling PDF Reader Installation Script

echo "================================================"
echo "Installing Docling PDF Reader Dependencies"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $python_version"

# Create virtual environment (optional but recommended)
read -p "Do you want to create a virtual environment? (y/n): " create_venv

if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv docling_env
    
    echo "Activating virtual environment..."
    source docling_env/bin/activate
    
    echo "Virtual environment created and activated."
    echo "To activate it later, run: source docling_env/bin/activate"
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip

echo "Installing Docling..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "================================================"
    echo "Installation completed successfully!"
    echo "================================================"
    echo ""
    echo "Usage:"
    echo "  1. Place your PDF file in this directory"
    echo "  2. Run: python pdf_processor.py your_file.pdf"
    echo "  3. Or run: python advanced_processor.py your_file.pdf"
    echo ""
    echo "Examples:"
    echo "  python pdf_processor.py document.pdf"
    echo "  python advanced_processor.py document.pdf --no-ocr"
    echo ""
    echo "Output will be saved in the 'output/' directory"
    echo "================================================"
else
    echo "================================================"
    echo "Installation failed!"
    echo "================================================"
    echo "Please check the error messages above."
    echo "You may need to install additional system dependencies."
    exit 1
fi
