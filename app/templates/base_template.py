"""
Base template class for all device types.
All device templates must inherit from this class and implement the abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseTemplate(ABC):
    """Abstract base class for device configuration templates."""

    @property
    @abstractmethod
    def device_type(self) -> str:
        """Return the device type identifier used in YAML (e.g., 'OpcUa', 'SiemensS7')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI display."""
        pass

    @property
    @abstractmethod
    def device_columns(self) -> List[Dict[str, Any]]:
        """
        Return list of device-level Excel columns.
        Each dict: {"name": str, "description": str, "mandatory": bool, "default": Any}
        """
        pass

    @property
    @abstractmethod
    def tag_columns(self) -> List[Dict[str, Any]]:
        """
        Return list of tag-level Excel columns.
        Each dict: {"name": str, "description": str, "mandatory": bool, "default": Any}
        """
        pass

    @property
    def bundling_columns(self) -> List[Dict[str, Any]]:
        """
        Return list of bundling Excel columns. Override in subclass if different.
        """
        return [
            {"name": "Bundle Name", "description": "Identifier for this bundle group", "mandatory": True, "default": None},
            {"name": "Mode", "description": "cyclic or trigger", "mandatory": True, "default": "cyclic"},
            {"name": "Cyclic (ms)", "description": "Interval in ms for cyclic mode", "mandatory": False, "default": 3000},
            {"name": "Trigger Tag", "description": "Tag name that triggers bundle (trigger mode)", "mandatory": False, "default": None},
            {"name": "Trigger Mode", "description": "change, rising, or falling", "mandatory": False, "default": "change"},
            {"name": "Data Tags", "description": "Comma-separated tag names included in bundle", "mandatory": True, "default": None},
        ]

    @property
    def topics_template(self) -> Dict[str, str]:
        """Default MQTT topics template. Override if needed."""
        return {
            "subscriptionStream": "mel/ot/machine-data/{{name}}/s",
            "error": "mel/ot/error/{{name}}/e",
            "writeAcknowledgment": "mel/ot/write-ack/{{name}}/wa",
            "writeRequest": "mel/pcc/data-for-machine/{{name}}/w",
            "readRequest": "mel/read-request/pcc/{{name}}/r",
            "readResponse": "mel/read-request/pcc/{{name}}/ra",
        }

    @abstractmethod
    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build the 'configuration' section from device-level data."""
        pass

    @abstractmethod
    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a single tag entry from tag data row."""
        pass

    def build_bundling(self, bundling_data: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Build the bundling section. Returns None if no bundling data provided."""
        if not bundling_data:
            return None

        # Group rows by bundle name — same name merges data tags into one entry
        grouped = {}
        for row in bundling_data:
            bundle_name = str(row.get("Bundle Name", "bundle")).strip()
            mode = str(row.get("Mode", "cyclic")).strip().lower()
            data_tags = [t.strip() for t in str(row.get("Data Tags", "")).split(",") if t.strip()]

            if not data_tags:
                continue

            if bundle_name in grouped:
                # Same bundle name — merge data tags
                grouped[bundle_name]["data"].extend(data_tags)
            else:
                bundle = {"name": bundle_name, "bundletype": mode}

                if mode == "cyclic":
                    cyclic_val = row.get("Cyclic (ms)", 3000)
                    bundle["cyclic"] = int(cyclic_val) if cyclic_val else 3000
                elif mode == "trigger":
                    trigger_tag = row.get("Trigger Tag", "")
                    if trigger_tag:
                        bundle["trigger"] = str(trigger_tag).strip()
                    trigger_mode = row.get("Trigger Mode", "change")
                    if trigger_mode and str(trigger_mode).strip():
                        bundle["triggerMode"] = str(trigger_mode).strip()

                bundle["data"] = data_tags
                grouped[bundle_name] = bundle

        bundles = list(grouped.values())
        return bundles if bundles else None

    def generate_yaml_dict(self, device_data: Dict[str, Any], tags_data: List[Dict[str, Any]],
                           bundling_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate the complete YAML dictionary for the device configuration.
        """
        device_name = str(device_data.get("Device Name", "device1")).strip()
        disabled = str(device_data.get("Disabled", "false")).strip().lower() == "true"
        ack_level = str(device_data.get("Ack Level", "AL0")).strip()

        yaml_dict = {
            "type": self.device_type,
            "name": device_name,
            "topics": self.topics_template,
            "disabled": disabled,
            "ackLevel": ack_level,
            "configuration": self.build_device_configuration(device_data),
        }

        # Build tags
        tags = []
        for tag_row in tags_data:
            tag = self.build_tag(tag_row)
            if tag:
                tags.append(tag)
        if tags:
            yaml_dict["tags"] = tags

        # Build bundling
        if bundling_data:
            bundling = self.build_bundling(bundling_data)
            if bundling:
                yaml_dict["bundling"] = bundling

        return yaml_dict
