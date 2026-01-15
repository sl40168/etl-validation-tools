"""Unit tests for report generator"""
import pytest
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


def test_format_number():
    """Test number formatting with commas"""
    assert format_number(1234) == "1,234"
    assert format_number(12345678) == "12,345,678"
    assert format_number(0) == "0"
    assert format_number(1) == "1"


def test_format_column_differences():
    """Test formatting column differences as Markdown table"""
    differences = {
        'last_trade_price': 12,
        'bid_0_price': 8,
        'offer_0_price': 5
    }

    result = format_column_differences(differences)

    assert 'last_trade_price' in result
    assert '12' in result
    assert 'bid_0_price' in result
    assert '8' in result
    assert 'offer_0_price' in result
    assert '5' in result
    assert '|' in result  # Markdown table format


def test_format_column_differences_empty():
    """Test formatting empty column differences"""
    result = format_column_differences({})
    assert 'No differences' in result or 'None' in result or result == ''


def test_format_side_counts():
    """Test formatting side counts"""
    result = format_side_counts(98, 88)

    assert '98' in result
    assert '88' in result
    assert 'Left Only' in result
    assert 'Right Only' in result
    assert '|' in result  # Markdown table format


def test_generate_report_structure(sample_validation_stats, sample_group_info):
    """Test report generation with correct structure"""
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=temp_dir
        )

        # Verify file was created
        assert os.path.exists(report_path)

        # Read and verify content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify header
        assert 'BOND/TRADE' in content
        assert '20260115' in content

        # Verify summary table
        assert 'Records Retrieved' in content
        assert '45,234' in content or '45234' in content
        assert '45,198' in content or '45198' in content

        # Verify match results
        assert '45,123' in content or '45123' in content
        assert '186' in content

        # Verify column differences table
        assert 'last_trade_price' in content
        assert '12' in content
        assert 'bid_0_price' in content
        assert '8' in content

        # Verify side counts table
        assert '98' in content
        assert '88' in content


def test_generate_report_filename(sample_validation_stats, sample_group_info):
    """Test report filename follows correct format"""
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=temp_dir
        )

        filename = os.path.basename(report_path)
        expected_filename = "validation_BOND_TRADE_20260115.md"

        assert filename == expected_filename


def test_generate_report_creates_directory(sample_validation_stats, sample_group_info):
    """Test that generate_report creates output directory if it doesn't exist"""
    validation_date = "20260115"
    new_dir = tempfile.mkdtemp()
    output_dir = os.path.join(new_dir, 'reports', 'nested')

    try:
        assert not os.path.exists(output_dir)

        report_path = generate_report(
            sample_validation_stats,
            sample_group_info,
            validation_date,
            output_dir=output_dir
        )

        assert os.path.exists(output_dir)
        assert os.path.exists(report_path)
    finally:
        import shutil
        shutil.rmtree(new_dir)


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
        assert '|-' in content or '|---' in content  # Table separator

        # Verify Markdown bold
        assert '**' in content


def test_generate_report_with_all_zeros(sample_validation_stats, sample_group_info):
    """Test report generation with zero statistics"""
    zero_stats = {
        'step': 2,
        'product_type': 'BOND',
        'tick_type': 'QUOTE',
        'left_retrieved_count': 0,
        'right_retrieved_count': 0,
        'matched_count': 0,
        'unmatched_count': 0,
        'column_differences': {},
        'left_unmatched_count': 0,
        'right_unmatched_count': 0
    }

    group = ValidationGroup(step=2, product_type='BOND', tick_type='QUOTE', description='Bond quote data')
    validation_date = "20260115"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = generate_report(
            zero_stats,
            group,
            validation_date,
            output_dir=temp_dir
        )

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '0' in content


def test_generate_report_timestamp(sample_validation_stats, sample_group_info):
    """Test that report includes generation timestamp"""
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

        # Verify timestamp format (YYYY-MM-DD HH:MM:SS)
        assert 'Generated At:' in content
        assert '-' in content and ':' in content
