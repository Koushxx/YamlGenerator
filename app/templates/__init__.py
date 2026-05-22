from app.templates.base_template import BaseTemplate
from app.templates.siemens_template import SiemensTemplate
from app.templates.opcua_template import OpcUaTemplate
from app.templates.codesys_template import CodesysTemplate
from app.templates.modbus_template import ModbusTcpTemplate
from app.templates.opcda_template import OpcDaTemplate

# Registry of all available device templates
DEVICE_TEMPLATES = {
    "Siemens S7": SiemensTemplate,
    "OPC UA": OpcUaTemplate,
    "CodeSys (Rexroth)": CodesysTemplate,
    "Modbus TCP": ModbusTcpTemplate,
    "OPC DA": OpcDaTemplate,
}


def get_template(device_type: str) -> BaseTemplate:
    """Get template instance for the given device type."""
    template_class = DEVICE_TEMPLATES.get(device_type)
    if template_class is None:
        raise ValueError(f"Unknown device type: {device_type}")
    return template_class()
