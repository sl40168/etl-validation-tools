"""Validation group definitions"""
from typing import List, Tuple, NamedTuple


class ValidationGroup(NamedTuple):
    """Validation group definition"""
    step: int
    product_type: str
    tick_type: str
    description: str


# Predefined validation groups
VALIDATION_GROUPS: List[ValidationGroup] = [
    ValidationGroup(
        step=1,
        product_type="BOND",
        tick_type="TRADE",
        description="Bond trade data"
    ),
    ValidationGroup(
        step=2,
        product_type="BOND",
        tick_type="QUOTE",
        description="Bond quote data"
    ),
    ValidationGroup(
        step=3,
        product_type="BOND_FUT",
        tick_type="SNAPSHOT",
        description="Bond futures snapshot data"
    )
]


def get_validation_groups(step: int = None) -> List[ValidationGroup]:
    """
    Get validation groups, optionally filtered by step number

    Args:
        step: Step number to filter (1, 2, or 3). If None, returns all groups.

    Returns:
        List of validation groups matching the filter criteria

    Raises:
        ValueError: If step is not 1, 2, or 3
    """
    if step is not None:
        if step not in [1, 2, 3]:
            raise ValueError(f"Invalid step number: {step}. Must be 1, 2, or 3")
        return [group for group in VALIDATION_GROUPS if group.step == step]

    return VALIDATION_GROUPS


def get_group_by_step(step: int) -> ValidationGroup:
    """
    Get a specific validation group by step number

    Args:
        step: Step number (1, 2, or 3)

    Returns:
        ValidationGroup object

    Raises:
        ValueError: If step is not valid
    """
    for group in VALIDATION_GROUPS:
        if group.step == step:
            return group

    raise ValueError(f"Invalid step number: {step}. Must be 1, 2, or 3")
