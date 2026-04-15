from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfMerger
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'port': 10000})

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
