"""Integration tests for report generation"""
import pytest
import pandas as pd
import tempfile
import os
from datetime import datetime
from src.reporting.generator import generate_report
from src.reporting.formatter import format_number, format_column_differences, format_side_counts
from src.validation.groups import ValidationGroup


@pytest.fixture
def sample_validation_stats():
    """Create sample validation statistics"""
    return {
        'step': 1,
        'product_type': 'BOND',
        'tick_type': 'TRADE',
        'left_retrieved_count': 45234,
        'right_retrieved_count': 45198,
        'matched_count': 45123,
        'unmatched_count': 186,
        'column_differences': {
            'last_trade_price': 12,
            'bid_0_price': 8,
            'offer_0_price': 5
        },
        'left_unmatched_count': 98,
        'right_unmatched_count': 88
    }


@pytest.fixture
def sample_group_info():
    """Create sample validation group info"""
    return ValidationGroup(
        step=1,
        product_type='BOND',
        tick_type='TRADE',
        description='Bond trade data'
    )


def test_generate_report_creates_file(sample_validation_stats, sample_group_info):
    """Test that report file is created"""
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=temp_dir
        )

        assert os.path.exists(report_path)
        assert report_path.endswith('.md')


def test_generate_report_content_accuracy(sample_validation_stats, sample_group_info):
    """Test that report content is accurate"""
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=temp_dir
        )

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify key statistics are in the report
        assert '45,234' in content or '45234' in content
        assert '45,198' in content or '45198' in content
        assert '45,123' in content or '45123' in content
        assert '186' in content
        assert '12' in content  # last_trade_price differences


def test_generate_report_markdown_format(sample_validation_stats, sample_group_info):
    """Test that report is valid Markdown"""
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=temp_dir
        )

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify Markdown headings
        assert '# ' in content  # H1
        assert '## ' in content  # H2
        assert '### ' in content  # H3

        # Verify Markdown tables
        assert '|' in content  # Table separator

        # Verify Markdown bold
        assert '**' in content


def test_generate_report_all_groups():
    """Test generating reports for all 3 validation groups"""
    validation_date = "20260115"
    stats = {
        'step': 1,
        'product_type': 'BOND',
        'tick_type': 'TRADE',
        'left_retrieved_count': 1000,
        'right_retrieved_count': 1000,
        'matched_count': 1000,
        'unmatched_count': 0,
        'column_differences': {},
        'left_unmatched_count': 0,
        'right_unmatched_count': 0
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate reports for all 3 groups
        groups = [
            ValidationGroup(1, 'BOND', 'TRADE', 'Bond trade data'),
            ValidationGroup(2, 'BOND', 'QUOTE', 'Bond quote data'),
            ValidationGroup(3, 'BOND_FUT', 'SNAPSHOT', 'Bond futures snapshot data')
        ]

        report_paths = []
        for group in groups:
            stats_copy = stats.copy()
            stats_copy['step'] = group.step
            stats_copy['product_type'] = group.product_type
            stats_copy['tick_type'] = group.tick_type

            report_path = generate_report(
                stats_copy,
                group,
                validation_date,
                output_dir=temp_dir
            )
            report_paths.append(report_path)

        # Verify all 3 reports were created
        assert len(report_paths) == 3
        assert all(os.path.exists(p) for p in report_paths)

        # Verify filenames
        filenames = [os.path.basename(p) for p in report_paths]
        assert 'validation_BOND_TRADE_20260115.md' in filenames
        assert 'validation_BOND_QUOTE_20260115.md' in filenames
        assert 'validation_BOND_FUT_SNAPSHOT_20260115.md' in filenames


def test_format_number_integration():
    """Test number formatting with realistic values"""
    assert format_number(0) == "0"
    assert format_number(1) == "1"
    assert format_number(999) == "999"
    assert format_number(1000) == "1,000"
    assert format_number(1000000) == "1,000,000"
    assert format_number(1234567890) == "1,234,567,890"


def test_format_column_differences_integration():
    """Test formatting column differences with realistic data"""
    differences = {
        'last_trade_price': 150,
        'bid_0_price': 98,
        'offer_0_price': 76,
        'total_volume': 45,
        'last_trade_yield': 23
    }

    result = format_column_differences(differences)

    assert 'last_trade_price' in result
    assert '150' in result
    assert 'bid_0_price' in result
    assert '98' in result


def test_format_side_counts_integration():
    """Test formatting side counts with realistic values"""
    result = format_side_counts(12345, 67890)

    assert '12,345' in result
    assert '67,890' in result
    assert 'Left Only' in result
    assert 'Right Only' in result
