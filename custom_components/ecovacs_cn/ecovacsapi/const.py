# default connection timeout
DEFAULT_TIMEOUT = 10

# max api retries
MAX_RETRIES = 3

# defaults
DEFAULT_API_URL = "https://open.ecovacs.cn"

# end points
ENDPOINT_DEVICE_LIST = "robot/deviceList"
ENDPOINT_CONTROL = "robot/ctl"

# command
CMD_CLEAN = "Clean"
CMD_CHARGE = "Charge"
# 查询工作状态：科沃斯官方 ecovacs-mcp 使用 GetWorkState，
# 一次调用同时返回 cleanSt / chargeSt / stationSt。
# 旧的 GetCleanState / GetChargeState 作为回退保留（部分老机型仍可能只认旧命令）。
CMD_GETWORKSTATE = "GetWorkState"
CMD_GETCLEANSTATE_LEGACY = "GetCleanState"
CMD_GETCHARGESTATE_LEGACY = "GetChargeState"

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

# States —— 与官方 ecovacs-mcp 的 GetWorkState 状态码保持一致
CLEAN_STATES = {
    "s": "Cleaning",
    "p": "Paused",
    "h": "Idle",
    "goposition": "Going to position",
    "gopositionpause": "Going to position paused",
    "findpet": "Finding pet",
    "findpetpause": "Finding pet paused",
    "cruise": "Cruising",
    "cruisepause": "Cruising paused",
    "buildmap": "Mapping",
    "buildmappause": "Mapping paused",
}

CHARGE_STATES = {
    "g": "Returning to dock",
    "gp": "Returning paused",
    "i": "Idle",
    "sc": "Dock charging",
    "wc": "Wired charging",
    "charging": "Charging",
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
