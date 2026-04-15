from flask import Flask, request, send_file, jsonify
from PyPDF2 import PdfMerger
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def hello():
    return "PDF API Working!"

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    bio = BytesIO()
    merger.write(bio)
    bio.seek(0)
    return send_file(bio, mimetype='application/pdf', 
                    as_attachment=True, download_name='merged.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
