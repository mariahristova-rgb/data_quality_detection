# data-quality-service/src/rules.py
import pandas as pd

class QualityRules:
    def check_completeness(self, data_frame: pd.DataFrame) -> float:
        """Calculate completeness of the dataset."""
        total_cells = data_frame.size
        total_missing = data_frame.isnull().sum().sum()
        completeness = (total_cells - total_missing) / total_cells
        return completeness

    def check_accuracy(self, data_frame: pd.DataFrame) -> float:
        """Example accuracy check: Percentage of unique values."""
        if 'id' in data_frame.columns:
            unique_count = data_frame['id'].nunique()
            total_count = data_frame['id'].count()
            accuracy = unique_count / total_count
            return accuracy
        return 0.0

    def check_consistency(self, data_frame: pd.DataFrame) -> bool:
        """Check if the data formats are consistent."""
        if 'date' in data_frame.columns:
            format_check = pd.to_datetime(data_frame['date'], errors='coerce').notnull().all()
            return format_check
        return True

    def check_validity(self, data_frame: pd.DataFrame) -> bool:
        """Check if data entries are valid according to predefined rules."""
        if 'email' in data_frame.columns:
            valid_emails = data_frame['email'].str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            return valid_emails.all()
        return True

    def check_duplicates(self, data_frame: pd.DataFrame) -> bool:
        """Check for duplicate rows in the dataset."""
        duplicates = data_frame.duplicated().sum()
        return duplicates == 0

    def check_categorical_consistency(self, data_frame: pd.DataFrame, column: str, valid_values: list) -> bool:
        """Check if categorical column values are consistent with a predefined list."""
        if column in data_frame.columns:
            inconsistent_values = set(data_frame[column]) - set(valid_values)
            return len(inconsistent_values) == 0
        return True

    def check_numeric_ranges(self, data_frame: pd.DataFrame, column: str, min_value: float, max_value: float) -> bool:
        """Check if numeric values in the column are within the specified range."""
        if column in data_frame.columns:
            out_of_range = data_frame[(data_frame[column] < min_value) | (data_frame[column] > max_value)]
            return out_of_range.empty
        return True

    def check_column_presence(self, data_frame: pd.DataFrame, expected_columns: list) -> bool:
        """Check for the presence of expected columns in the DataFrame."""
        missing_columns = set(expected_columns) - set(data_frame.columns)
        return len(missing_columns) == 0

    def check_data_types(self, data_frame: pd.DataFrame, expected_types: dict) -> bool:
        """Check if columns have the expected data types."""
        for column, expected_type in expected_types.items():
            if column in data_frame.columns:
                if not pd.api.types.is_dtype_equal(data_frame[column].dtype, expected_type):
                    return False
        return True
