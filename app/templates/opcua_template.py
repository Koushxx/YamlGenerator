"""OPC UA device template."""

from typing import Dict, List, Any
from app.templates.base_template import BaseTemplate


class OpcUaTemplate(BaseTemplate):

    @property
    def device_type(self) -> str:
        return "OpcUa"

    @property
    def display_name(self) -> str:
        return "OPC UA"

    @property
    def device_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Device Name", "description": "Unique device identifier", "mandatory": True, "default": None},
            {"name": "Endpoint URL", "description": "OPC UA server endpoint (e.g., opc.tcp://192.168.1.100:4840)", "mandatory": True, "default": None},
            {"name": "Use Security", "description": "Enable TLS (true/false)", "mandatory": False, "default": "false"},
            {"name": "Session Timeout (ms)", "description": "Session idle timeout in ms", "mandatory": False, "default": 60000},
            {"name": "Connection Timeout (ms)", "description": "Connection timeout in ms", "mandatory": False, "default": 6000},
            {"name": "Credential Key", "description": "Key for stored credentials (optional)", "mandatory": False, "default": None},
            {"name": "Certificate Key", "description": "Key for PEM certificate (optional)", "mandatory": False, "default": None},
            {"name": "Disabled", "description": "Disable device (true/false)", "mandatory": False, "default": "false"},
            {"name": "Ack Level", "description": "AL0, AL1, or AL2", "mandatory": False, "default": "AL0"},
        ]

    @property
    def tag_columns(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Tag Name", "description": "Unique tag identifier", "mandatory": True, "default": None},
            {"name": "Node ID", "description": "OPC UA Node ID (e.g., ns=2;s=Channel1.Device1.Tag1)", "mandatory": True, "default": None},
            {"name": "Sampling Interval (ms)", "description": "Sampling interval in milliseconds", "mandatory": False, "default": 1000},
            {"name": "Write Enabled", "description": "Enable write (true/false)", "mandatory": False, "default": "false"},
            {"name": "Write Min", "description": "Minimum write value (optional)", "mandatory": False, "default": None},
            {"name": "Write Max", "description": "Maximum write value (optional)", "mandatory": False, "default": None},
            {"name": "Write Discrete", "description": "Comma-separated discrete values (optional)", "mandatory": False, "default": None},
        ]

    def build_device_configuration(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        config = {
            "endPointUrl": str(device_data.get("Endpoint URL", "")).strip(),
            "useSecurity": str(device_data.get("Use Security", "false")).strip().lower() == "true",
            "sessionTimeOut": int(device_data.get("Session Timeout (ms)", 60000) or 60000),
            "connectionTimeOut": int(device_data.get("Connection Timeout (ms)", 6000) or 6000),
        }

        cred_key = device_data.get("Credential Key")
        if cred_key and str(cred_key).strip():
            config["credentialKey"] = str(cred_key).strip()

        cert_key = device_data.get("Certificate Key")
        if cert_key and str(cert_key).strip():
            config["certificateKey"] = str(cert_key).strip()

        return config

    def build_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        tag_name = str(tag_data.get("Tag Name", "")).strip()
        if not tag_name:
            return None

        tag = {
            "name": tag_name,
            "configuration": {
                "nodeId": str(tag_data.get("Node ID", "")).strip(),
                "samplingInterval": str(int(tag_data.get("Sampling Interval (ms)", 1000) or 1000)),
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
                    write_config["range"] = {
                        "min": float(write_min),
                        "max": float(write_max),
                    }
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
