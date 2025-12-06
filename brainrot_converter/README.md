# 🧠 Brainrot Textbook Converter

Convert your textbooks to Gen Z brainrot speak using AI! Upload a PDF, and watch as academic language transforms into peak Gen Z slang while maintaining the original meaning and formatting.

## Features

- 📄 **PDF Upload** - Drag and drop or select PDF files (max 5MB)
- 🤖 **AI-Powered Conversion** - Uses Ollama + Mistral 7B for intelligent brainrot translation
- ⚡ **Fast Processing** - Converts 10,000 word documents in 5-20 seconds
- 🎯 **Smart Chunking** - Processes text in 1,200-word chunks to maintain context
- 📊 **Real-time Progress** - Live progress tracking with estimated time remaining
- 💾 **PDF Generation** - Outputs a new PDF with converted text
- 🎨 **Beautiful UI** - Modern, responsive web interface with drag-and-drop

## Tech Stack

- **Backend:** Flask (Python 3.12)
- **PDF Processing:** pdfplumber (extract), reportlab (generate)
- **AI/LLM:** Ollama + Mistral 7B (local)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Concurrency:** Python threading for parallel processing

## Prerequisites
### ⚠️ CRITICAL: Install and Run Ollama FIRST

The app will NOT work without Ollama running. Ollama is the local AI engine that powers the brainrot conversion.

### 1. Install Ollama

1. Download Ollama from **[ollama.ai](https://ollama.ai)**
2. Install it on your system
3. Verify installation by opening a terminal and running: `ollama --version`

### 2. Pull Mistral Model

Open a terminal and run:

```bash
ollama pull mistral
```

This downloads the Mistral 7B model (~4GB). You only need to do this ONCE.

### 3. Start Ollama Service

Before using the converter, you MUST keep Ollama running in the background:

**Option A: Automatic (Windows)**
- Double-click `START.bat` in the project folder (does everything automatically)

**Option B: Manual**
- Open a terminal and run: `ollama serve`
- Keep this terminal open while using the converter
- Ollama will run on `http://localhost:11434`

**Troubleshooting Ollama:**
- If you see "Connection refused" error → Ollama is not running
- Start Ollama first, THEN access the web interface
- Ollama takes ~2-3 seconds to initialize on first start

## Setup Instructions

### Quick Start (Windows)

1. **Install Ollama** (see Prerequisites above)
2. **Double-click `START.bat`** in the project folder
   - This automatically starts Ollama and the Flask app
   - Browser will open at `http://localhost:5000`

### Manual Setup

#### 1. Navigate to Project Directory

```bash
cd Hello-World/brainrot_converter
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Start Ollama (Required!)

Open a NEW terminal and run:

```bash
ollama serve
```

Keep this terminal open.

#### 5. Run the Flask App

In your FIRST terminal (with venv activated), run:

```bash
python app.py
```

#### 6. Open in Browser

Visit `http://localhost:5000` in your web browser.

**IMPORTANT:** Always start Ollama BEFORE uploading files!

## Usage

1. **Open the web interface** at `http://localhost:5000`
2. **Drag and drop** a PDF file into the upload box (or click to select)
3. **Wait for conversion** - Progress bar shows real-time status
4. **Download** the brainrot PDF when complete
5. **Convert another** or repeat with different files

## How It Works

### Conversion Pipeline

1. **Text Extraction** → pdfplumber reads the PDF and extracts all text while preserving paragraph structure
2. **Smart Chunking** → Text is split into ~1,200 word chunks while respecting paragraph boundaries
3. **AI Conversion** → Each chunk is sent to Mistral 7B with the prompt: `"Convert to Gen Z/brainrot slang: '{text}' while keeping meaning similar. Keep technical terms. Preserve punctuation."`
4. **PDF Generation** → reportlab reconstructs a new PDF with the converted text, maintaining basic formatting
5. **Download** → User downloads the "brainrot" version of their textbook

### Example Conversions

| Original | Brainrot |
|----------|----------|
| "The mitochondria is the powerhouse of the cell" | "Bro the mitochondria literally IS the main character of the cell" |
| "Photosynthesis is a biochemical process" | "Photosynthesis is lowkey just plants eating sunlight as food fr fr" |
| "Newton's first law of motion" | "Newton said objects go brr unless something makes them stop" |

## Project Structure

```
brainrot_converter/
├── app.py                    # Flask backend + conversion logic
├── requirements.txt          # Python dependencies
├── static/
│   ├── style.css            # Frontend styling
│   └── script.js            # Frontend logic
├── templates/
│   └── index.html           # Upload interface
├── uploads/                 # Temporary PDF storage
└── conversions/             # Generated brainrot PDFs
```

## Configuration

### File Size Limit

Default: 5MB (set in `app.py` line 12)

```python
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
```

### Chunk Size

Default: 1,200 words (set in `app.py` `chunk_text()` function)

Adjust for better context or faster processing:
- Smaller chunks = faster but less context-aware
- Larger chunks = slower but better understanding

### LLM Model

Currently uses Mistral 7B. To use a different model:

```python
# In app.py, change:
response = ollama.generate(model='mistral', ...)
# To:
response = ollama.generate(model='neural-chat', ...)  # or another model
```

First pull the model: `ollama pull neural-chat`

## Performance

- **Small document (1,000 words):** 1-2 seconds
- **Medium document (5,000 words):** 3-5 seconds  
- **Large document (10,000 words):** 5-20 seconds (depending on CPU/GPU)

**Performance Tips:**
- **With GPU:** Fastest conversion (5-20s for 10K words)
- **With CPU:** Slower (20-45s for 10K words) - still acceptable
- Run Ollama on a machine with sufficient RAM (8GB+ recommended)

## Troubleshooting

### "Ollama is not running" Error

**Problem:** You see an error message saying "Ollama is not running"

**Solution:**
1. Open a NEW terminal window
2. Run: `ollama serve`
3. Keep this terminal open
4. Refresh the converter webpage
5. Try converting again

### "Connection refused" Error

**Problem:** "Error: Could not connect to Ollama"

**Solution:**
- Make sure Ollama is running (`ollama serve` in separate terminal)
- Wait 2-3 seconds after starting Ollama before uploading
- Check that nothing is using port 11434

### PDF Shows Same Text (Not Converted)

**Problem:** Downloaded PDF has original text, no brainrot conversion

**Causes & Solutions:**
1. **Ollama not running:**
   - Open new terminal: `ollama serve`
   - Try conversion again
   
2. **Mistral model not downloaded:**
   - Terminal: `ollama pull mistral`
   - Wait for download to complete
   - Try again

3. **Check browser console for errors:**
   - Press F12 to open Developer Tools
   - Check Console tab for error messages
   - Check Network tab to see if conversion requests failed

4. **Check Flask terminal for errors:**
   - Look at the terminal running Flask (`python app.py`)
   - You should see log messages like "ERROR: ..." if something failed
   - Share the error message for debugging

### Conversion is Very Slow

**Problem:** Takes more than 1 minute for a small document

**Causes & Solutions:**
1. **CPU-only system:** Mistral needs good hardware
   - Intel i7/AMD Ryzen 5+ recommended
   - 8GB+ RAM
   - If you have these specs but it's still slow, Ollama might be using CPU instead of GPU

2. **First conversion takes longer:** Ollama loads model into memory on first use

3. **System under load:** Close other programs using CPU/GPU

### "No module named 'requests'" Error

**Solution:** Reinstall requirements:
```bash
pip install -r requirements.txt
```

### Port 5000 Already In Use

**Problem:** Error "Port 5000 is already in use"

**Solution:**
- Find the process: `netstat -ano | findstr :5000` (Windows) or `lsof -i :5000` (Mac/Linux)
- Kill it or use different port
- Edit `app.py` line 250: change `port=5000` to `port=5001`

## Limitations

- ❌ **Image-based PDFs:** Won't work with scanned textbooks (need OCR first)
- ❌ **Complex layouts:** Multi-column text, sidebars may be reformatted
- ❌ **Embedded images:** Removed from output (noted as "[Image preserved]")
- ❌ **Tables:** Text extracted but structure simplified
- ⚠️ **Formatting:** Basic formatting preserved but won't be pixel-perfect

## Future Enhancements

- [ ] Brainrot intensity levels (light/medium/heavy slang)
- [ ] Preview converted text before PDF generation
- [ ] Batch processing multiple PDFs
- [ ] Custom brainrot dictionary upload
- [ ] Different LLM model selection via UI
- [ ] OCR support for scanned PDFs
- [ ] Image preservation in output

## Elevator Pitch

**Brainrot Textbook Converter** is an AI-powered tool that transforms academic textbooks into entertaining Gen Z versions while preserving meaning and formatting. Perfect for making studying more fun, creating memes, or just having a laugh with your textbooks!

## License

Free to use and modify. Have fun spreading the brainrot! 🧠

## Credits

- **Ollama** - Local LLM framework
- **Mistral 7B** - Foundational language model
- **Flask** - Web framework
- **pdfplumber** - PDF text extraction
- **reportlab** - PDF generation

---

Made with 💜 for the brainrot generation
