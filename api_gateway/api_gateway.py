from flask import Flask, jsonify, request

from data_quality_service.data_quality_service import DataQualityService
from ingestion_service import IngestionService
from migration_service import MigrationService

app = Flask(__name__)


@app.route('/')
def health_check():
    return jsonify({"status": "API is running!"})


# Initialize services
ingestion_service = IngestionService()
migration_service = MigrationService(
    db_config={
        'dbname': 'your_redshift_db',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'your_redshift_endpoint',
        'port': 'your_redshift_port',
        'iam_role': 'your_redshift_iam_role',
        'region': 'your_s3_region',
    }
)


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


@app.route('/migrate', methods=['POST'])
def migrate_data():
    data = request.get_json()
    s3_bucket = data.get("s3_bucket")
    s3_key = data.get("s3_key")
    table_name = data.get("table_name")

    if not s3_bucket or not s3_key or not table_name:
        return jsonify({"error": "S3 bucket, S3 key, and table name are required."}), 400

    try:
        migration_service.migrate_to_redshift(s3_bucket, s3_key, table_name)
        return jsonify({"message": "Data migration triggered", "s3_bucket": s3_bucket, "s3_key": s3_key,
                        "table_name": table_name}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500


quality_service = DataQualityService()


@app.route('/data-quality', methods=['POST'])
def check_data_quality():
    data = request.get_json()
    file_path = data.get("file_path")

    if not file_path:
        return jsonify({"error": "File path is required"}), 400

    try:
        # Load the data
        df = ingestion_service.load_data(file_path)
        # Assess the data quality
        quality_metrics = quality_service.assess_data_quality(df)

        return jsonify({"data_quality_metrics": quality_metrics.__dict__}), 200
    except Exception as e:
        return jsonify({"error": str(e)}),


@app.route('/anomalies', methods=['GET'])
def detect_anomalies():
    # You would call your anomaly detection logic here
    return jsonify({"message": "Anomaly detection started"}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
