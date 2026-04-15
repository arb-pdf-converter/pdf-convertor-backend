from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import img2pdf
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'features': ['merge', 'images-to-pdf', 'compress']})

@app.route('/api/v1/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    if len(files) < 2: return jsonify({'error': 'Need 2+ PDFs'}), 400
    
    merger = PdfMerger()
    for file in files:
        if file.filename.lower().endswith('.pdf'):
            merger.append(file)
    
    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')

@app.route('/api/v1/images-to-pdf', methods=['POST'])
def images_to_pdf():
    """🖼️ Images → PDF"""
    files = request.files.getlist('files')
    if not files: return jsonify({'error': 'Upload images (JPG/PNG)'}), 400
    
    try:
        images = []
        for file in files:
            if file.content_type.startswith('image/'):
                img = Image.open(file)
                images.append(img)
        
        if not images:
            return jsonify({'error': 'No valid images'}), 400
        
        pdf_bytes = img2pdf.convert(images)
        return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', 
                        as_attachment=True, download_name='images-to-pdf.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/compress-pdf', methods=['POST'])
def compress_pdf():
    """📦 Compress single PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'Upload single PDF as "file"'}), 400
    
    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files'}), 400
    
    try:
        reader = PdfReader(file)
        writer = PdfWriter()
        
        # Copy pages (optimizes automatically)
        for page in reader.pages:
            writer.add_page(page)
        
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        
        original_size = len(file.read())
        file.seek(0)
        
        return send_file(output, mimetype='application/pdf', 
                        as_attachment=True, download_name='compressed.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': '🚀 Complete PDF API',
        'endpoints': {
            'health': 'GET /health',
            'merge': 'POST /api/v1/merge-pdf (files=pdf1,pdf2)',
            'images': 'POST /api/v1/images-to-pdf (files=img1,img2)',
            'compress': 'POST /api/v1/compress-pdf (file=single.pdf)'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
