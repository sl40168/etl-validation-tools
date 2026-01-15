"""Column validation logic"""
from typing import List, NamedTuple, Dict, Any
import pandas as pd
from datetime import datetime


class ColumnValidationResult(NamedTuple):
    """Result of column validation"""
    status: str
    missing_columns: List[str]
    extra_columns: List[str]
    type_mismatches: Dict[str, str]
    validated_at: datetime


class ColumnValidator:
    """Validates DataFrame columns against required columns and type rules"""

    def __init__(self, required_columns: List[str], type_rules: Dict[str, Dict[str, Any]] = None):
        """
        Initialize column validator

        Args:
            required_columns: List of column names that must be present
            type_rules: Optional dictionary mapping column names to their type rules
                       Format: {"column_name": {"type": "int|float|str|datetime", "nullable": bool, "precision": int}}
        """
        self.required_columns = required_columns
        self.type_rules = type_rules or {}

    def validate_columns(self, df: pd.DataFrame) -> ColumnValidationResult:
        """
        Check DataFrame against required columns

        Args:
            df: DataFrame to validate

        Returns:
            ColumnValidationResult with missing and extra columns
        """
        df_columns = set(df.columns)
        required_set = set(self.required_columns)

        missing_columns = list(required_set - df_columns)
        extra_columns = list(df_columns - required_set)

        status = "PASS" if not missing_columns else "FAIL"

        return ColumnValidationResult(
            status=status,
            missing_columns=missing_columns,
            extra_columns=extra_columns,
            type_mismatches={},
            validated_at=datetime.now()
        )

    def validate_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Validate data types for all required columns according to type_rules

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary mapping column names to error messages (empty if all valid)
        """
        type_mismatches = {}

        for column in self.required_columns:
            if column not in df.columns:
                continue

            if column not in self.type_rules:
                continue

            rule = self.type_rules[column]
            expected_type = rule.get('type')
            nullable = rule.get('nullable', True)
            precision = rule.get('precision')

            # Skip NULL validation if nullable
            if nullable and df[column].isna().all():
                continue

            # Validate non-NULL if not nullable
            if not nullable and df[column].isna().any():
                type_mismatches[column] = f"Contains NULL values but nullable=False"
                continue

            # Type validation based on expected type
            if expected_type == 'int':
                self._validate_int_type(df[column], column, precision, type_mismatches)
            elif expected_type == 'float':
                self._validate_float_type(df[column], column, precision, type_mismatches)
            elif expected_type == 'str':
                self._validate_str_type(df[column], column, type_mismatches)
            elif expected_type == 'datetime':
                self._validate_datetime_type(df[column], column, type_mismatches)

        return type_mismatches

    def _validate_int_type(self, series: pd.Series, column: str, precision: int,
                         errors: Dict[str, str]):
        """Validate integer type with precision"""
        if precision == 0:
            # Check if any values have non-zero decimal places
            for val in series.dropna():
                if isinstance(val, float) and not val.is_integer():
                    errors[column] = f"Expected integer (precision=0), got value with decimals: {val}"
                    break

    def _validate_float_type(self, series: pd.Series, column: str, precision: int,
                          errors: Dict[str, str]):
        """Validate float type with precision"""
        if precision is not None:
            for val in series.dropna():
                if isinstance(val, float):
                    # Count decimal places
                    decimal_str = str(val).split('.')[-1] if '.' in str(val) else ''
                    if len(decimal_str) > precision:
                        errors[column] = f"Expected {precision} decimal places, got {len(decimal_str)}: {val}"
                        break

    def _validate_str_type(self, series: pd.Series, column: str, errors: Dict[str, str]):
        """Validate string type"""
        # Check for empty strings in non-nullable columns
        for val in series.dropna():
            if isinstance(val, str) and not val.strip():
                errors[column] = "Contains empty string values"
                break

    def _validate_datetime_type(self, series: pd.Series, column: str, errors: Dict[str, str]):
        """Validate datetime type (YYYYMMDD format or datetime objects)"""
        for val in series.dropna():
            # Check if it's a string in YYYYMMDD format
            if isinstance(val, str):
                try:
                    datetime.strptime(val, '%Y%m%d')
                except ValueError:
                    errors[column] = f"Invalid datetime format (expected YYYYMMDD): {val}"
                    break
            elif not isinstance(val, datetime):
                errors[column] = f"Invalid datetime type: {type(val)}"
                break
