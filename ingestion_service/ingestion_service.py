# ingestion-service/src/ingestion_service.py
import os
import pandas as pd
from pyspark.sql import SparkSession
from data_quality_service import DataQualityService


class IngestionService:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("Data Ingestion Service") \
            .getOrCreate()
        self.quality_service = DataQualityService()

    def load_data(self, file_path: str):
        """
        Load data from various sources based on the given file path.
        It checks for file extensions and reads accordingly.
        """
        if file_path.startswith('s3://'):
            df = self.load_from_s3(file_path)
        elif file_path.startswith('https://') and 'sharepoint.com' in file_path:
            df = self.load_from_sharepoint(file_path)
        elif file_path.startswith('https://') and 'blob.core.windows.net' in file_path:
            df = self.load_from_azure(file_path)
        elif file_path.endswith('.csv'):
            df = self.spark.read.csv(file_path, header=True, inferSchema=True)
        elif file_path.endswith('.xlsx'):
            df = self.load_from_excel(file_path)
        elif file_path.endswith('.parquet'):
            df = self.spark.read.parquet(file_path)
        else:
            raise ValueError(
                "Unsupported file format. Please provide a CSV, Excel, Parquet, S3, Azure, or SharePoint file.")

        self.trigger_data_quality_checks(df)
        return df

    def load_from_s3(self, s3_path: str):
        """Load a file from AWS S3."""
        return self.spark.read.csv(s3_path, header=True)  # Assuming CSV for simplicity

    def load_from_azure(self, azure_url: str):
        """Load a file from Azure Blob Storage."""
        return self.spark.read.option("header", "true").csv(azure_url)  # Assuming CSV for simplicity

    def load_from_sharepoint(self, sharepoint_url: str):
        """Load a file from SharePoint."""
        # Placeholder: Implement SharePoint file download logic here
        # You may need to use Office365-REST-Python-Client similar to previous examples
        raise NotImplementedError("SharePoint loading not implemented yet.")

    def load_from_excel(self, file_path: str):
        """Load data from Excel files using pandas and convert to Spark DataFrame."""
        pdf = pd.read_excel(file_path)  # Using pandas to read Excel
        return self.spark.createDataFrame(pdf)

    def trigger_data_quality_checks(self, df):
        """
        Invoke data quality checks immediately after ingestion.
        """
        quality_metrics = self.quality_service.assess_data_quality(df)
        # Handle the quality metrics (e.g., logging, alerting, etc.)
        print("Data Quality Metrics:", quality_metrics)
