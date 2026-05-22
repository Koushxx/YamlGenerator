"""
Validation utilities for Excel data.
"""

from typing import Dict, List, Any, Tuple
from app.templates.base_template import BaseTemplate


def validate_device_data(template: BaseTemplate, device_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate device configuration data against template requirements.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    for col in template.device_columns:
        if col["mandatory"]:
            value = device_data.get(col["name"])
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"Device Config: Missing mandatory field '{col['name']}'")

    # Specific validations
    ip = device_data.get("IP Address") or device_data.get("Endpoint URL") or device_data.get("Server")
    if ip and isinstance(ip, str):
        ip = ip.strip()
        if not ip:
            errors.append("Device Config: IP/Endpoint cannot be empty")

    return len(errors) == 0, errors


def validate_tags_data(template: BaseTemplate, tags_data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate tag rows against template requirements.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    if not tags_data:
        errors.append("Tags: No tag data found. At least one tag is required.")
        return False, errors

    tag_names = set()
    for row_idx, tag_row in enumerate(tags_data, start=1):
        for col in template.tag_columns:
            if col["mandatory"]:
                value = tag_row.get(col["name"])
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Tags Row {row_idx}: Missing mandatory field '{col['name']}'")

        # Check duplicate tag names
        tag_name = tag_row.get("Tag Name", "")
        if isinstance(tag_name, str):
            tag_name = tag_name.strip()
        if tag_name:
            if tag_name in tag_names:
                errors.append(f"Tags Row {row_idx}: Duplicate tag name '{tag_name}'")
            tag_names.add(tag_name)

    return len(errors) == 0, errors


def validate_bundling_data(bundling_data: List[Dict[str, Any]], 
                           available_tags: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate bundling configuration.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    if not bundling_data:
        return True, []

    for row_idx, row in enumerate(bundling_data, start=1):
        mode = str(row.get("Mode", "")).strip().lower()
        if mode not in ("cyclic", "trigger"):
            errors.append(f"Bundling Row {row_idx}: Mode must be 'cyclic' or 'trigger', got '{mode}'")

        if mode == "cyclic":
            cyclic_val = row.get("Cyclic (ms)")
            if cyclic_val is not None:
                try:
                    val = int(cyclic_val)
                    if val <= 0:
                        errors.append(f"Bundling Row {row_idx}: Cyclic interval must be > 0")
                except (ValueError, TypeError):
                    errors.append(f"Bundling Row {row_idx}: Cyclic interval must be a number")

        if mode == "trigger":
            trigger_tag = row.get("Trigger Tag")
            if not trigger_tag or not str(trigger_tag).strip():
                errors.append(f"Bundling Row {row_idx}: Trigger Tag is required for trigger mode")
            elif str(trigger_tag).strip() not in available_tags:
                errors.append(f"Bundling Row {row_idx}: Trigger Tag '{trigger_tag}' not found in defined tags")

            trigger_mode = row.get("Trigger Mode", "")
            if trigger_mode and str(trigger_mode).strip().lower() not in ("change", "rising", "falling", ""):
                errors.append(f"Bundling Row {row_idx}: Trigger Mode must be 'change', 'rising', or 'falling'")

        # Validate data tags reference
        data_tags_str = row.get("Data Tags", "")
        if not data_tags_str or not str(data_tags_str).strip():
            errors.append(f"Bundling Row {row_idx}: Data Tags cannot be empty")
        else:
            data_tags = [t.strip() for t in str(data_tags_str).split(",") if t.strip()]
            for tag in data_tags:
                if tag not in available_tags:
                    errors.append(f"Bundling Row {row_idx}: Data tag '{tag}' not found in defined tags")

    return len(errors) == 0, errors
