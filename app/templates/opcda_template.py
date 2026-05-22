"""OPC DA device template."""

from typing import Dict, List, Any
from app.templates.base_template import BaseTemplate


class OpcDaTemplate(BaseTemplate):

    @property
    def device_type(self) -> str:
        return "OpcDa"

    @property
    def display_name(self) -> str:
        return "OPC DA"

    @property
    def device_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Device Name", "description": "Unique device identifier", "mandatory": True, "default": None},
            {"name": "IP Address", "description": "IP address or URL of the OPC DA server", "mandatory": True, "default": None},
            {"name": "Port", "description": "OPC DA server port", "mandatory": True, "default": 4840},
            {"name": "Prog ID", "description": "Program ID of OPC DA server (e.g., Kepware.KEPServerEX.V6)", "mandatory": True, "default": None},
            {"name": "Update Rate (ms)", "description": "Server update rate in milliseconds", "mandatory": False, "default": 100},
            {"name": "Timeout (ms)", "description": "Server response timeout in milliseconds", "mandatory": False, "default": 60000},
            {"name": "Disabled", "description": "Disable device (true/false)", "mandatory": False, "default": "false"},
            {"name": "Ack Level", "description": "AL0, AL1, or AL2", "mandatory": False, "default": "AL0"},
        ]

    @property
    def tag_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Tag Name", "description": "Unique tag identifier", "mandatory": True, "default": None},
            {"name": "Item ID", "description": "OPC DA item ID (e.g., Channel1.Device1.Tag1)", "mandatory": True, "default": None},
        ]

    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        config = {
            "ip": str(device_data.get("IP Address", "")).strip(),
            "port": str(int(device_data.get("Port", 4840) or 4840)),
            "progID": str(device_data.get("Prog ID", "")).strip(),
            "updateRate": int(device_data.get("Update Rate (ms)", 100) or 100),
            "timeOut": int(device_data.get("Timeout (ms)", 60000) or 60000),
        }
        return config

    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        tag_name = str(tag_data.get("Tag Name", "")).strip()
        if not tag_name:
            return None

        tag = {
            "type": "da",
            "name": tag_name,
            "configuration": {
                "itemId": str(tag_data.get("Item ID", "")).strip(),
            }
        }
        return tag
