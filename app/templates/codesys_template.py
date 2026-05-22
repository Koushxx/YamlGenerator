"""CodeSys (Rexroth PLC) device template."""

from typing import Dict, List, Any
from app.templates.base_template import BaseTemplate


class CodesysTemplate(BaseTemplate):

    @property
    def device_type(self) -> str:
        return "CodeSys"

    @property
    def display_name(self) -> str:
        return "CodeSys (Rexroth)"

    @property
    def device_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Device Name", "description": "Unique device identifier", "mandatory": True, "default": None},
            {"name": "IP Address", "description": "IPv4 address of the Codesys device", "mandatory": True, "default": None},
            {"name": "Port", "description": "TCP port (default: 1200 for arti)", "mandatory": True, "default": 1200},
            {"name": "Protocol", "description": "Interface: arti, arti3, gateway3", "mandatory": True, "default": "arti"},
            {"name": "Update Rate (ms)", "description": "Data update rate in milliseconds", "mandatory": False, "default": 100},
            {"name": "Gateway IP", "description": "Gateway IP address (for gateway3 protocol)", "mandatory": False, "default": None},
            {"name": "Gateway Port", "description": "Gateway port number (for gateway3 protocol)", "mandatory": False, "default": None},
            {"name": "Disabled", "description": "Disable device (true/false)", "mandatory": False, "default": "false"},
            {"name": "Ack Level", "description": "AL0, AL1, or AL2", "mandatory": False, "default": "AL0"},
        ]

    @property
    def tag_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Tag Name", "description": "Unique tag identifier", "mandatory": True, "default": None},
            {"name": "Symbol", "description": "Codesys symbol path (e.g., Application.MachineStateDefines.Temperature)", "mandatory": True, "default": None},
            {"name": "Write Enabled", "description": "Enable write (true/false)", "mandatory": False, "default": "false"},
            {"name": "Write Discrete", "description": "Comma-separated allowed values (optional)", "mandatory": False, "default": None},
            {"name": "Write Min", "description": "Minimum write value (optional)", "mandatory": False, "default": None},
            {"name": "Write Max", "description": "Maximum write value (optional)", "mandatory": False, "default": None},
        ]

    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        config = {
            "ip": str(device_data.get("IP Address", "")).strip(),
            "port": int(device_data.get("Port", 1200) or 1200),
            "protocol": str(device_data.get("Protocol", "arti")).strip().lower(),
            "updateRate": int(device_data.get("Update Rate (ms)", 100) or 100),
        }

        gateway_ip = device_data.get("Gateway IP")
        if gateway_ip and str(gateway_ip).strip():
            config["gatewayIp"] = str(gateway_ip).strip()

        gateway_port = device_data.get("Gateway Port")
        if gateway_port:
            try:
                config["gatewayport"] = int(gateway_port)
            except (ValueError, TypeError):
                pass

        return config

    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        tag_name = str(tag_data.get("Tag Name", "")).strip()
        if not tag_name:
            return None

        tag = {
            "name": tag_name,
            "configuration": {
                "symbol": str(tag_data.get("Symbol", "")).strip(),
            }
        }

        # Write configuration
        write_enabled = str(tag_data.get("Write Enabled", "false")).strip().lower() == "true"
        if write_enabled:
            write_config = {"enabled": True}

            write_min = tag_data.get("Write Min")
            write_max = tag_data.get("Write Max")
            if write_min is not None and write_max is not None:
                try:
                    write_config["range"] = {"min": float(write_min), "max": float(write_max)}
                except (ValueError, TypeError):
                    pass

            write_discrete = tag_data.get("Write Discrete")
            if write_discrete and str(write_discrete).strip():
                try:
                    discrete_vals = [float(v.strip()) for v in str(write_discrete).split(",") if v.strip()]
                    if discrete_vals:
                        write_config["discrete"] = discrete_vals
                except (ValueError, TypeError):
                    pass

            tag["write"] = write_config

        return tag
