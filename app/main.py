from flask import Flask, request, send_file, jsonify
from PyPDF2 import PdfMerger
from io import BytesIO

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})

@app.route('/api/v1/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', 
                    as_attachment=True, download_name='merged.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
