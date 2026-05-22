"""
YAML configuration file generator.
Takes parsed Excel data and produces YAML output using device templates.
"""

import yaml
from typing import Dict, List, Any

from app.templates.base_template import BaseTemplate


class YamlDumper(yaml.Dumper):
    """Custom YAML dumper for cleaner output."""
    pass


def _str_representer(dumper, data):
    """Handle multiline strings and proper quoting."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if data.startswith("{{") or "{{" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _bool_representer(dumper, data):
    """Represent booleans as lowercase."""
    return dumper.represent_scalar("tag:yaml.org,2002:bool", "true" if data else "false")


YamlDumper.add_representer(str, _str_representer)
YamlDumper.add_representer(bool, _bool_representer)


def generate_yaml(template: BaseTemplate, device_data: Dict[str, Any],
                  tags_data: List[Dict[str, Any]],
                  bundling_data: List[Dict[str, Any]] = None) -> str:
    """
    Generate a YAML configuration string from the parsed Excel data.
    
    Args:
        template: The device template instance.
        device_data: Device configuration data from Excel.
        tags_data: List of tag configuration dicts from Excel.
        bundling_data: Optional list of bundling configuration dicts.
    
    Returns:
        YAML string ready for file output.
    """
    yaml_dict = template.generate_yaml_dict(device_data, tags_data, bundling_data)
    yaml_output = yaml.dump(
        yaml_dict,
        Dumper=YamlDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    return yaml_output


def generate_full_config_yaml(template: BaseTemplate, device_data: Dict[str, Any],
                              tags_data: List[Dict[str, Any]],
                              bundling_data: List[Dict[str, Any]] = None) -> str:
    """
    Generate the full configdevices YAML structure including collector.json wrapper.
    This matches the deployment values.yaml format.
    """
    device_name = str(device_data.get("Device Name", "device1")).strip()
    device_filename = f"{device_name}.json"

    yaml_dict = template.generate_yaml_dict(device_data, tags_data, bundling_data)

    full_config = {
        "configdevices": {
            "collector.json": {
                "collector": {
                    "disabled": False,
                    "ackLevel": str(device_data.get("Ack Level", "AL0")).strip(),
                    "devicefiles": [device_filename],
                }
            },
            device_filename: yaml_dict,
        }
    }

    yaml_output = yaml.dump(
        full_config,
        Dumper=YamlDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    return yaml_output
