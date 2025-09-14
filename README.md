# Deepsint - OSINT Visualizer

A Streamlit-based OSINT (Open Source Intelligence) tool that integrates with Blackbird for username and email investigations.

## Features

- **Web Interface**: Clean Streamlit interface for entering usernames or emails
- **Blackbird Integration**: Automatically finds and executes Blackbird from your system PATH
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Real-time Results**: Displays Blackbird analysis results directly in the web interface

## Prerequisites

1. **Python 3.7+** with the following packages:
   ```bash
   pip install streamlit
   ```

2. **Blackbird**: Install Blackbird OSINT tool
   ```bash
   # Option 1: Install via pip
   pip install blackbird-osint
   
   # Option 2: Install from source
   git clone https://github.com/p1ngul1n0/blackbird
   cd blackbird
   pip install -r requirements.txt
   ```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install streamlit
   ```
3. Ensure Blackbird is installed and available in your PATH

## Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Open your browser** and navigate to the displayed URL (typically `http://localhost:8501`)

3. **Enter a username or email** in the form and click "Search"

4. **View results** in the expandable results section

## Files

- `main.py` - Main Streamlit application
- `run_blackbird.sh` - Shell script for Linux/macOS to execute Blackbird
- `run_blackbird.bat` - Batch script for Windows to execute Blackbird
- `test_blackbird.py` - Test script to verify Blackbird integration

## How It Works

1. The Streamlit form collects username/email input
2. When submitted, the application determines your operating system
3. It executes the appropriate script (`run_blackbird.sh` or `run_blackbird.bat`)
4. The script finds Blackbird in your PATH and executes it with the provided username
5. Results are captured and displayed in the web interface

## Troubleshooting

- **"Blackbird not found in PATH"**: Ensure Blackbird is properly installed and available in your system PATH
- **Script execution fails**: Check that the scripts have execute permissions (`chmod +x run_blackbird.sh` on Linux/macOS)
- **Timeout errors**: Large investigations may take time; the timeout is set to 5 minutes

## Testing

Run the test script to verify your setup:
```bash
python test_blackbird.py