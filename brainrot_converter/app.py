from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import threading
import pdfplumber
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT
import ollama
import time
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERSION_FOLDER'] = 'conversions'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERSION_FOLDER'], exist_ok=True)

# Job tracking
jobs = {}

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF while preserving paragraph structure"""
    paragraphs = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    # Split by double newlines to identify paragraphs
                    page_paragraphs = text.split('\n\n')
                    paragraphs.extend([p.strip() for p in page_paragraphs if p.strip()])
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return paragraphs

def chunk_text(paragraphs, chunk_size=600):
    """Split paragraphs into chunks of approximately chunk_size words"""
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for paragraph in paragraphs:
        word_count = len(paragraph.split())
        
        if current_word_count + word_count > chunk_size and current_chunk:
            # Save current chunk and start new one
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_word_count = word_count
        else:
            current_chunk.append(paragraph)
            current_word_count += word_count
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def convert_chunk_to_brainrot(text, job_id):
    """Send chunk to Ollama Mistral for conversion"""
    # Simpler, shorter prompt for faster responses
    prompt = f"""Make this Gen Z slang: {text}"""
    
    try:
        response = ollama.generate(
            model='neural-chat',  # Faster than mistral (change to 'mistral' if you prefer quality over speed)
            prompt=prompt,
            stream=False
        )
        result = response['response'].strip()
        print(f"Converted chunk {job_id}: {len(result)} chars")
        return result
    except Exception as e:
        print(f"Error converting chunk: {e}")
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        # Return original text as fallback
        return text

def process_pdf_conversion(job_id, pdf_path, output_path):
    """Main conversion pipeline"""
    try:
        jobs[job_id]['status'] = 'extracting'
        
        # Check if Ollama is running
        try:
            requests.get('http://localhost:11434/api/tags', timeout=2)
        except:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = 'Ollama is not running. Please start Ollama with: ollama serve'
            return
        
        # Extract text
        paragraphs = extract_text_from_pdf(pdf_path)
        total_paragraphs = len(paragraphs)
        jobs[job_id]['total_paragraphs'] = total_paragraphs
        
        if not paragraphs:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = 'No text found in PDF'
            return
        
        jobs[job_id]['status'] = 'chunking'
        
        # Chunk text
        chunks = chunk_text(paragraphs, chunk_size=1200)
        total_chunks = len(chunks)
        jobs[job_id]['total_chunks'] = total_chunks
        
        jobs[job_id]['status'] = 'converting'
        
        # Convert chunks
        converted_chunks = []
        start_time = time.time()
        
        for idx, chunk in enumerate(chunks):
            converted_text = convert_chunk_to_brainrot(chunk, job_id)
            converted_chunks.append(converted_text)
            
            # Update progress
            progress = int((idx + 1) / total_chunks * 100)
            jobs[job_id]['progress'] = progress
            jobs[job_id]['current_chunk'] = idx + 1
            
            # Estimate time remaining
            elapsed = time.time() - start_time
            avg_time_per_chunk = elapsed / (idx + 1)
            remaining_chunks = total_chunks - (idx + 1)
            estimated_remaining = avg_time_per_chunk * remaining_chunks
            jobs[job_id]['estimated_remaining'] = int(estimated_remaining)
        
        jobs[job_id]['status'] = 'generating'
        
        # Generate output PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom style for body text
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=12
        )
        
        # Add converted text to PDF
        converted_text = '\n\n'.join(converted_chunks)
        paragraphs_to_add = converted_text.split('\n\n')
        
        for para_text in paragraphs_to_add:
            if para_text.strip():
                story.append(Paragraph(para_text.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Conversion error: {e}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
    finally:
        # Clean up uploaded file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route('/')
def index():
    """Serve upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and start conversion"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = f"{job_id}.pdf"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Initialize job
        jobs[job_id] = {
            'status': 'queued',
            'progress': 0,
            'current_chunk': 0,
            'total_chunks': 0,
            'estimated_remaining': 0,
            'uploaded_at': datetime.now().isoformat(),
            'filename': file.filename
        }
        
        # Start conversion in background thread
        output_filename = f"{job_id}_converted.pdf"
        output_path = os.path.join(app.config['CONVERSION_FOLDER'], output_filename)
        
        thread = threading.Thread(
            target=process_pdf_conversion,
            args=(job_id, upload_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'job_id': job_id}), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<job_id>')
def get_progress(job_id):
    """Get conversion progress"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id]), 200

@app.route('/download/<job_id>')
def download(job_id):
    """Download converted PDF"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': f'Conversion not complete. Status: {job["status"]}'}), 400
    
    output_filename = f"{job_id}_converted.pdf"
    output_path = os.path.join(app.config['CONVERSION_FOLDER'], output_filename)
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(output_path, as_attachment=True, download_name=f"brainrot_{job['filename']}")

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 5MB'}), 413

if __name__ == '__main__':
    app.run(debug=True, port=5000)
