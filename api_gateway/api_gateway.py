from flask import Flask, jsonify, request
from ingestion_service import IngestionService

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({"status": "API is running!"})


ingestion_service = IngestionService()

@app.route('/ingest', methods=['POST'])
def ingest_data():

    data = request.get_json()
    file_path = data.get("file_path")

    if not file_path:
        return jsonify({"error": "File path is required"}), 400

    try:

        df = ingestion_service.load_data(file_path)
        return jsonify({"message": "Data ingestion triggered", "file_path": file_path}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/data-quality', methods=['GET'])
def check_data_quality():
    return jsonify({"message": "Data quality check initiated"}), 202

@app.route('/anomalies', methods=['GET'])
def detect_anomalies():

    return jsonify({"message": "Anomaly detection started"}), 202


if __name__ == '__main__':
    # Run the app on localhost at port 5000
    app.run(host='0.0.0.0', port=5000)
