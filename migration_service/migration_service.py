# ingestion_service/migration_service.py
import psycopg2


class MigrationService:
    def __init__(self, db_config):
        self.db_config = db_config

    def migrate_to_redshift(self, s3_bucket: str, s3_key: str, table_name: str):
        """Migrate data from S3 to Redshift."""
        # Establish connection to Redshift
        conn = psycopg2.connect(
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            host=self.db_config['host'],
            port=self.db_config['port']
        )
        cursor = conn.cursor()

        copy_command = f"""
            COPY {table_name}
            FROM 's3://{s3_bucket}/{s3_key}'
            IAM_ROLE '{self.db_config['iam_role']}'
            CSV
            DELIMITER ','
            IGNOREHEADER 1
            REGION 'us-east-1';  -- Update region as necessary
        """
        try:
            cursor.execute(copy_command)
            conn.commit()
            print(f"Data migrated to {table_name} in Redshift successfully.")
        except Exception as e:
            print(f"Migration to Redshift failed: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
