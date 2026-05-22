"""Modbus TCP device template."""

from typing import Dict, List, Any
from app.templates.base_template import BaseTemplate


class ModbusTcpTemplate(BaseTemplate):

    @property
    def device_type(self) -> str:
        return "ModbusTcp"

    @property
    def display_name(self) -> str:
        return "Modbus TCP"

    @property
    def device_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Device Name", "description": "Unique device identifier", "mandatory": True, "default": None},
            {"name": "Server", "description": "IP address or hostname of the Modbus TCP server", "mandatory": True, "default": None},
            {"name": "Port", "description": "TCP port (default: 502)", "mandatory": False, "default": 502},
            {"name": "Slave ID", "description": "Modbus slave/unit identifier", "mandatory": False, "default": 1},
            {"name": "Timeout (ms)", "description": "Communication timeout in milliseconds", "mandatory": False, "default": 3000},
            {"name": "Mode", "description": "Communication mode (TCP, RTU over TCP)", "mandatory": False, "default": "TCP"},
            {"name": "Byte Order", "description": "Byte order (ABCD, DCBA, BADC, CDAB)", "mandatory": False, "default": "ABCD"},
            {"name": "Polling Interval (ms)", "description": "Polling interval in milliseconds", "mandatory": False, "default": 1000},
            {"name": "Disabled", "description": "Disable device (true/false)", "mandatory": False, "default": "false"},
            {"name": "Ack Level", "description": "AL0, AL1, or AL2", "mandatory": False, "default": "AL0"},
        ]

    @property
    def tag_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Tag Name", "description": "Unique tag identifier", "mandatory": True, "default": None},
            {"name": "Type", "description": "Coil, HoldingRegister, InputRegister", "mandatory": True, "default": None},
            {"name": "Address", "description": "Register/coil start address", "mandatory": True, "default": None},
            {"name": "Count", "description": "Number of registers/coils to read", "mandatory": True, "default": 1},
            {"name": "Trigger", "description": "Use as trigger tag (true/false)", "mandatory": False, "default": "false"},
        ]

    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        config = {
            "server": str(device_data.get("Server", "")).strip(),
            "port": int(device_data.get("Port", 502) or 502),
        }

        slave_id = device_data.get("Slave ID")
        if slave_id:
            config["slaveId"] = int(slave_id)

        timeout = device_data.get("Timeout (ms)")
        if timeout:
            config["timeOut"] = int(timeout)

        mode = device_data.get("Mode")
        if mode and str(mode).strip():
            config["mode"] = str(mode).strip()

        byte_order = device_data.get("Byte Order")
        if byte_order and str(byte_order).strip():
            config["byteOrder"] = str(byte_order).strip()

        polling = device_data.get("Polling Interval (ms)")
        if polling:
            config["pollingInterval"] = int(polling)

        return config

    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        tag_name = str(tag_data.get("Tag Name", "")).strip()
        if not tag_name:
            return None

        tag = {
            "name": tag_name,
            "type": str(tag_data.get("Type", "")).strip(),
            "configuration": {
                "address": str(tag_data.get("Address", "")).strip(),
                "count": int(tag_data.get("Count", 1) or 1),
            }
        }

        trigger = str(tag_data.get("Trigger", "false")).strip().lower() == "true"
        if trigger:
            tag["trigger"] = True

        return tag
