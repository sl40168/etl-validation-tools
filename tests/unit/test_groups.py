"""Unit tests for validation groups"""
import pytest
from src.validation.groups import get_validation_groups, get_group_by_step, VALIDATION_GROUPS, ValidationGroup


def test_get_all_groups():
    """Test retrieving all validation groups"""
    groups = get_validation_groups()

    assert len(groups) == 3
    assert all(isinstance(g, ValidationGroup) for g in groups)


def test_get_group_by_step_1():
    """Test retrieving group 1"""
    group = get_group_by_step(1)

    assert group.group_id == 1
    assert group.product_type == "BOND"
    assert group.message_type == "TRADE"
    assert "Bond trade data" in group.description.lower()
    assert len(group.required_columns) == 18


def test_get_group_by_step_2():
    """Test retrieving group 2"""
    group = get_group_by_step(2)

    assert group.group_id == 2
    assert group.product_type == "BOND"
    assert group.message_type == "QUOTE"
    assert "Bond quote data" in group.description.lower()
    assert len(group.required_columns) == 60


def test_get_group_by_step_3():
    """Test retrieving group 3"""
    group = get_group_by_step(3)

    assert group.group_id == 3
    assert group.product_type == "BOND_FUT"
    assert group.message_type == "SNAPSHOT"
    assert "Bond futures snapshot data" in group.description.lower()
    assert len(group.required_columns) == 39


def test_get_groups_filtered_by_step_1():
    """Test filtering groups by step 1"""
    groups = get_validation_groups(step=1)

    assert len(groups) == 1
    assert groups[0].group_id == 1
    assert groups[0].product_type == "BOND"
    assert groups[0].message_type == "TRADE"


def test_get_groups_filtered_by_step_2():
    """Test filtering groups by step 2"""
    groups = get_validation_groups(step=2)

    assert len(groups) == 1
    assert groups[0].group_id == 2
    assert groups[0].product_type == "BOND"
    assert groups[0].message_type == "QUOTE"


def test_get_groups_filtered_by_step_3():
    """Test filtering groups by step 3"""
    groups = get_validation_groups(step=3)

    assert len(groups) == 1
    assert groups[0].group_id == 3
    assert groups[0].product_type == "BOND_FUT"
    assert groups[0].message_type == "SNAPSHOT"


def test_get_groups_invalid_step():
    """Test error when filtering by invalid step"""
    with pytest.raises(ValueError, match="Invalid step number: 4"):
        get_validation_groups(step=4)

    with pytest.raises(ValueError, match="Invalid step number: 0"):
        get_validation_groups(step=0)


def test_get_group_by_step_invalid():
    """Test error when retrieving invalid group by step"""
    with pytest.raises(ValueError, match="Invalid step number: 4"):
        get_group_by_step(4)


def test_validation_groups_constant():
    """Test that VALIDATION_GROUPS constant is correctly defined"""
    assert len(VALIDATION_GROUPS) == 3

    # Check group 1
    assert VALIDATION_GROUPS[0].group_id == 1
    assert VALIDATION_GROUPS[0].product_type == "BOND"
    assert VALIDATION_GROUPS[0].message_type == "TRADE"

    # Check group 2
    assert VALIDATION_GROUPS[1].group_id == 2
    assert VALIDATION_GROUPS[1].product_type == "BOND"
    assert VALIDATION_GROUPS[1].message_type == "QUOTE"

    # Check group 3
    assert VALIDATION_GROUPS[2].group_id == 3
    assert VALIDATION_GROUPS[2].product_type == "BOND_FUT"
    assert VALIDATION_GROUPS[2].message_type == "SNAPSHOT"


def test_validation_groups_ordering():
    """Test that groups are in correct order (1, 2, 3)"""
    groups = get_validation_groups()

    assert groups[0].group_id == 1
    assert groups[1].group_id == 2
    assert groups[2].group_id == 3
