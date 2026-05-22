# Device YAML Generator

A professional desktop application for generating device YAML configuration files from Excel templates. Supports multiple industrial device protocols including OPC UA, Siemens S7, CodeSys, Modbus TCP, and OPC DA.

## Features

- **Multi-Device Support**: OPC UA, Siemens S7, CodeSys (Rexroth), Modbus TCP, OPC DA
- **Excel Template Generation**: Device-specific templates with proper column structures
- **YAML Generation**: Automatically generates valid YAML configuration from filled Excel data
- **Dark Mode UI**: Professional dark theme with modern design
- **Drag & Drop**: Upload Excel files via drag-and-drop
- **YAML Preview**: Syntax-highlighted YAML preview
- **Validation**: Mandatory field validation with error reporting
- **Full Config Export**: Generate complete `values.yaml` format with collector wrapper
- **Clipboard Support**: Copy generated YAML directly to clipboard
- **Auto-save**: Remembers last used device type

## Project Structure

```
DeviceYAMLGenerator/
├── main.py                              # Application entry point
├── requirements.txt                     # Python dependencies
├── build.spec                           # PyInstaller build configuration
├── README.md                            # This file
└── app/
    ├── __init__.py                      # App metadata
    ├── main_window.py                   # Main window UI
    ├── templates/
    │   ├── __init__.py                  # Template registry
    │   ├── base_template.py             # Abstract base template
    │   ├── siemens_template.py          # Siemens S7 template
    │   ├── opcua_template.py            # OPC UA template
    │   ├── codesys_template.py          # CodeSys template
    │   ├── modbus_template.py           # Modbus TCP template
    │   └── opcda_template.py            # OPC DA template
    ├── generators/
    │   ├── __init__.py
    │   ├── excel_generator.py           # Excel template creation & parsing
    │   └── yaml_generator.py            # YAML generation engine
    ├── widgets/
    │   ├── __init__.py
    │   ├── drag_drop.py                 # Drag-and-drop file upload widget
    │   └── yaml_preview.py             # YAML preview with syntax highlighting
    └── utils/
        ├── __init__.py
        ├── validators.py                # Data validation utilities
        └── logger.py                    # Logging configuration
```

## Quick Start

### 1. Install Dependencies

```bash
cd DeviceYAMLGenerator
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Usage Workflow

1. **Select Device Type** from the dropdown (e.g., "OPC UA")
2. **Download Excel Template** - saves a pre-formatted `.xlsx` file
3. **Fill the Excel Template** with your device configuration:
   - Sheet 1: Device Configuration (IP, port, etc.)
   - Sheet 2: Tags (node IDs, addresses, etc.)
   - Sheet 3: Bundling (optional grouping rules)
4. **Upload the filled Excel** file (drag-drop or file dialog)
5. **Click "Generate YAML"** to produce the configuration
6. **Download or Copy** the generated YAML

## Build Executable (.exe)

### Option 1: Using the spec file

```bash
pip install pyinstaller
pyinstaller build.spec
```

### Option 2: Single command

```bash
pyinstaller --onefile --noconsole --name DeviceYAMLGenerator main.py
```

The executable will be created in the `dist/` folder.

## Supported Device Types

| Device Type | Protocol | Default Port |
|-------------|----------|-------------|
| Siemens S7 | S7 Communication | 102 |
| OPC UA | OPC Unified Architecture | 4840 |
| CodeSys (Rexroth) | Arti/Arti3/Gateway3 | 1200 |
| Modbus TCP | Modbus over TCP/IP | 502 |
| OPC DA | OPC Data Access | 4840 |

## Adding New Device Types

To add support for a new device type:

1. Create a new file in `app/templates/` (e.g., `mqtt_template.py`)
2. Inherit from `BaseTemplate` and implement all abstract methods
3. Register it in `app/templates/__init__.py` by adding to `DEVICE_TEMPLATES` dict

Example:
```python
from app.templates.base_template import BaseTemplate

class MqttTemplate(BaseTemplate):
    @property
    def device_type(self) -> str:
        return "MQTT"
    
    @property
    def display_name(self) -> str:
        return "MQTT"
    
    # ... implement remaining methods
```

## Generated YAML Format

The application generates YAML matching the DeviceBridge `configdevices` format:

```yaml
type: OpcUa
name: myDevice
topics:
  subscriptionStream: mel/ot/machine-data/{{name}}/s
  error: mel/ot/error/{{name}}/e
  writeAcknowledgment: mel/ot/write-ack/{{name}}/wa
  writeRequest: mel/pcc/data-for-machine/{{name}}/w
  readRequest: mel/read-request/pcc/{{name}}/r
  readResponse: mel/read-request/pcc/{{name}}/ra
disabled: false
ackLevel: AL0
configuration:
  endPointUrl: opc.tcp://192.168.1.100:4840
  useSecurity: false
  sessionTimeOut: 60000
  connectionTimeOut: 6000
tags:
  - name: Temperature
    configuration:
      nodeId: ns=2;s=Channel1.Device1.Temperature
      samplingInterval: '1000'
bundling:
  - cyclic: 3000
    data:
      - Temperature
```

## Logs

Application logs are stored at:
```
%USERPROFILE%\.device_yaml_generator\logs\app_YYYYMMDD.log
```

## Requirements

- Python 3.8+
- Windows 10/11
- PyQt5 5.15+
- openpyxl 3.1+
- PyYAML 6.0+
