"""Validation group definitions and configuration loading"""
from typing import List, NamedTuple, Dict
import yaml
import os


# Step name mapping for better readability
STEP_NAMES: Dict[int, str] = {
    1: "BOND TRADE",
    2: "BOND QUOTE",
    3: "BOND_FUT SNAPSHOT"
}


class ValidationGroup(NamedTuple):
    """Validation group definition"""
    group_id: int
    product_type: str
    message_type: str
    description: str
    required_columns: List[str]


def load_groups_from_config(config_path: str = None) -> List[ValidationGroup]:
    """
    Load validation groups from YAML configuration file

    Args:
        config_path: Path to groups.yaml config file. If None, uses default path.

    Returns:
        List of ValidationGroup objects loaded from config

    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config file is invalid
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '../../config/groups.yaml')
        config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Groups configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    groups = []
    for group_config in config_data.get('groups', []):
        group = ValidationGroup(
            group_id=group_config['group_id'],
            product_type=group_config['product_type'],
            message_type=group_config['message_type'],
            description=group_config['description'],
            required_columns=group_config['required_columns']
        )
        groups.append(group)

    return groups


# Load validation groups from config
VALIDATION_GROUPS: List[ValidationGroup] = load_groups_from_config()


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
        if step not in STEP_NAMES:
            valid_steps = ", ".join([f"{k} ({v})" for k, v in sorted(STEP_NAMES.items())])
            raise ValueError(f"Invalid step number: {step}. Valid steps: {valid_steps}")
        return [group for group in VALIDATION_GROUPS if group.group_id == step]

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
        if group.group_id == step:
            return group

    valid_steps = ", ".join([f"{k} ({v})" for k, v in sorted(STEP_NAMES.items())])
    raise ValueError(f"Invalid step number: {step}. Valid steps: {valid_steps}")
