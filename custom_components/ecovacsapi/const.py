# default connection timeout
DEFAULT_TIMEOUT = 10

# max api retries
MAX_RETRIES = 3

# defaults
DEFAULT_API_URL = "https://open.ecovacs.cn"
API_KEY = "FLpgn3WUF2jOErI8upubZgzEQfmVjGlC"

# end points
ENDPOINT_DEVICE_LIST = "robot/deviceList"
ENDPOINT_CONTROL = "robot/ctl"

# command
CMD_CLEAN = "Clean"
CMD_CHARGE = "Charge"
CMD_GETCLEANSTATE = "GetCleanState"
CMD_GETCHARGESTATE = "GetChargeState"

# Actions
CLEAN_ACTIONS = {
    "start" : "s",
    "pause" : "p",
    "resume" : "r",
    "stop" : "h"
}
CHARGE_ACTIONS = {
    "return_dock" : "go",
    "cancel_return" : "stopGo",
}

# States
CLEAN_STATES = {
    "s" : "Cleaning",
    "p" : "Paused",
    "h" : "Idle",
}

# buttons supported by this library
BUTTONS = {
    "startClean": "[Clean] Start",
    "stopClean": "[Clean] Stop",
    "pauseClean": "[Clean] Pause",
    "resumeClean": "[Clean] Resume",
    "returnDock": "[Charge] Return to Dock",
    "cancelReturn": "[Charge] Cancel return"
}

# sensors supported by this library
SENSORS = {
    "cleanState": "Clean state",
    "chargeState": "Charge state",
}

CONTROLS = {
    "controlClean" : "Cleaning Control"
}
