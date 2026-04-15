from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import img2pdf
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'features': ['merge', 'images-pdf', 'compress']})

@app.route('/api/v1/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': 'Need 2+ PDFs'}), 400
    merger = PdfMerger()
    for file in files:
        if file.filename.endswith('.pdf'):
            merger.append(file)
    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', download_name='merged.pdf')

@app.route('/api/v1/images-to-pdf', methods=['POST'])
def images_to_pdf():
    files = request.files.getlist('files')
    images = [Image.open(file) for file in files if file.content_type.startswith('image/')]
    if not images:
        return jsonify({'error': 'No images'}), 400
    pdf_bytes = img2pdf.convert(images)
    return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', download_name='images.pdf')

@app.route('/api/v1/compress-pdf', methods=['POST'])
def compress_pdf():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Upload PDF as "file"'}), 400
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return send_file(output, mimetype='application/pdf', download_name='compressed.pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
