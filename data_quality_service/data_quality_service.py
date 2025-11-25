# data-quality-service/src/data_quality_service.py
import pandas as pd
from rules import QualityRules
from models import DataQualityMetrics
import boto3
from azure.storage.filedatalake import DataLakeServiceClient
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import os


class DataQualityService:
    def __init__(self):
        self.rules = QualityRules()

    def assess_data_quality(self, file_path: str) -> DataQualityMetrics:

        data_frame = self.load_data(file_path)

        quality_metrics = DataQualityMetrics()
        quality_metrics.completeness = self.rules.check_completeness(data_frame)
        quality_metrics.accuracy = self.rules.check_accuracy(data_frame)
        quality_metrics.consistency = self.rules.check_consistency(data_frame)
        quality_metrics.validity = self.rules.check_validity(data_frame)
        quality_metrics.duplicates = self.rules.check_duplicates(data_frame)

        return quality_metrics

    def load_data(self, file_path: str) -> pd.DataFrame:

        if file_path.startswith('s3://'):
            return self.load_from_s3(file_path)

        elif file_path.startswith('https://') and 'blob.core.windows.net' in file_path:
            return self.load_from_azure(file_path)

        elif file_path.startswith('https://') and 'sharepoint.com' in file_path:
            return self.load_from_sharepoint(file_path)

        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV, Excel, or Parquet file.")

    def load_from_s3(self, s3_path: str) -> pd.DataFrame:

        bucket_name = s3_path.split('/')[2]
        key = '/'.join(s3_path.split('/')[3:])

        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        data_frame = pd.read_csv(response['Body'])  # Assuming CSV file
        return data_frame

    def load_from_azure(self, azure_url: str) -> pd.DataFrame:

        container_name = azure_url.split('/')[3]
        blob_path = '/'.join(azure_url.split('/')[4:])

        service_client = DataLakeServiceClient.from_connection_string('YOUR_AZURE_CONNECTION_STRING')
        file_system_client = service_client.get_file_system_client(container_name)
        file_client = file_system_client.get_file_client(blob_path)

        download = file_client.download_file()
        downloaded_bytes = download.readall()
        return pd.read_csv(pd.compat.BytesIO(downloaded_bytes))  # Assuming CSV file

    def load_from_sharepoint(self, sharepoint_url: str) -> pd.DataFrame:


        site_url = sharepoint_url.split('/')[0:5]  # Extract the site URL
        file_relative_url = '/'.join(sharepoint_url.split('/')[5:])  # Get the relative URL of the file

        user_credentials = UserCredential('YOUR_USERNAME', 'YOUR_PASSWORD')
        ctx = ClientContext('/'.join(site_url)).with_credentials(user_credentials)

        response = ctx.web.get_file_by_server_relative_url(file_relative_url).download()
        response.execute_query()

        # Load the content into
