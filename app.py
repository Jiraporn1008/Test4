from flask import Flask, request, jsonify
import pandas as pd
import requests
import re
from io import BytesIO

app = Flask(__name__)

def extract_drive_file_id(url):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    match_alt = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    return match_alt.group(1) if match_alt else None

@app.route('/upload_link', methods=['POST'])
def upload_link():
    data = request.get_json()
    link = data.get("url")
    if not link:
        return jsonify({"error": "No URL provided"}), 400

    file_id = extract_drive_file_id(link)
    if not file_id:
        return jsonify({"error": "Invalid Google Drive link"}), 400

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        resp = requests.get(download_url)
        resp.raise_for_status()
        excel_data = pd.read_excel(BytesIO(resp.content))
        records = excel_data.fillna('').to_dict(orient='records')
        return jsonify({"status": "success", "data": records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
