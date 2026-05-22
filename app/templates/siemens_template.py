"""Siemens S7 device template."""

from typing import Dict, List, Any
from app.templates.base_template import BaseTemplate


class SiemensTemplate(BaseTemplate):

    @property
    def device_type(self) -> str:
        return "SiemensS7"

    @property
    def display_name(self) -> str:
        return "Siemens S7"

    @property
    def device_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Device Name", "description": "Unique device identifier", "mandatory": True, "default": None},
            {"name": "IP Address", "description": "IPv4 address of the Siemens device", "mandatory": True, "default": None},
            {"name": "Port", "description": "Communication port (default: 102)", "mandatory": False, "default": 102},
            {"name": "CPU", "description": "CPU model: S71200, S71500, S7200, S7300, S7400", "mandatory": True, "default": "S71200"},
            {"name": "Rack", "description": "Rack number (0-7)", "mandatory": False, "default": 0},
            {"name": "Slot", "description": "Slot number (0-31)", "mandatory": False, "default": 0},
            {"name": "Timeout (ms)", "description": "Connection timeout in milliseconds", "mandatory": False, "default": 1000},
            {"name": "Force Reconnect", "description": "Reconnect after failure (true/false)", "mandatory": False, "default": "true"},
            {"name": "Disabled", "description": "Disable device (true/false)", "mandatory": False, "default": "false"},
            {"name": "Ack Level", "description": "AL0, AL1, or AL2", "mandatory": False, "default": "AL0"},
        ]

    @property
    def tag_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Tag Name", "description": "Unique tag identifier", "mandatory": True, "default": None},
            {"name": "Address", "description": "Tag address (e.g., DB45.DBW2, M9.3)", "mandatory": True, "default": None},
            {"name": "Data Type", "description": "Bit, Byte, Word, DWord, Int, DInt, Real, String, Timer, Counter, DateTime, Bool, DataBlock", "mandatory": True, "default": None},
            {"name": "Count", "description": "Number of bytes to read", "mandatory": True, "default": 1},
        ]

    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        config = {
            "ipAddress": str(device_data.get("IP Address", "")).strip(),
            "port": int(device_data.get("Port", 102) or 102),
            "cpu": str(device_data.get("CPU", "S71200")).strip(),
            "rack": int(device_data.get("Rack", 0) or 0),
            "slot": int(device_data.get("Slot", 0) or 0),
            "timeOut": int(device_data.get("Timeout (ms)", 1000) or 1000),
            "forceReconnectOnFailure": str(device_data.get("Force Reconnect", "true")).strip().lower() == "true",
        }
        return config

    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        tag_name = str(tag_data.get("Tag Name", "")).strip()
        if not tag_name:
            return None

        tag = {
            "name": tag_name,
            "type": "S7Variable",
            "configuration": {
                "address": str(tag_data.get("Address", "")).strip(),
                "type": str(tag_data.get("Data Type", "")).strip(),
                "count": int(tag_data.get("Count", 1) or 1),
            }
        }
        return tag
