"""Constants for ecovacs_cn"""

# Internal constants
DOMAIN = "ecovacs_cn"
# PLATFORMS = ["button", "control", "sensor"]
PLATFORMS = ["button", "sensor"]

# Configuration definitions
CONF_API_URL = "api_url"
CONF_DEVICE_NAME = "device_name"
CONF_API_KEY = "api_key"
CONF_DISCOVERED_DEVICE = "discovered_device"

OPTION_API_TIMEOUT = "api_timeout"
OPTION_API_URL = "api_url"
OPTION_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_API_URL = "https://open.ecovacs.cn"
DEFAULT_SCAN_INTERVAL = 15

# icons of the sensors
SENSOR_ICONS = {
    "__default__": "mdi:bookmark",
    "startClean": "mdi:car-turbocharger",
    "stopClean": "mdi:car-turbocharger",
    "pauseClean": "mdi:car-turbocharger",
    "resumeClean": "mdi:car-turbocharger",
    "returnDock": "mdi:lightning-bolt",
    "cancelReturn": "mdi:lightning-bolt",
    "cleanState": "mdi:car-turbocharger",
    "chargeState": "mdi:lightning-bolt",
}

