from dataclasses import dataclass
from typing import List, Optional, Union, Any
from enum import Enum
import json

class SwitchMode(str, Enum):
    LIVE = "live"
    TOGGLE = "toggle"

@dataclass
class SessionData:
    acSessionId: str

@dataclass
class DeviceInfo:
    nickname: str
    password: str
    ordernum: str
    model: str
    version: str
    uuid: str
    macaddr: str
    sn: str
    chipsn: str
    legalret: int
    btnver: int
    totalruntime: int
    sdcapacity: int
    sdspare: int
    sdbrand: str
    hbbitrate: int
    hsbitrate: int
    mbbitrate: int
    msbitrate: int
    lbbitrate: int
    lsbitrate: int
    rbbitrate: int
    rsbitrate: int
    default_user: str
    is_neeed_update: int
    edog_model: str
    edog_version: str
    edog_status: int
    cid: str
    is_support_emmc_and_tf: int

@dataclass
class AccStatus:
    connetc_acc_status: str

@dataclass
class StateInfo:
    state: int

@dataclass
class ErrorData:
    errcode: int
    data: List[str]

@dataclass
class GpsState:
    gpsstate: int

@dataclass
class IntParam:
    key: str
    value: int

@dataclass
class StringParam:
    key: str
    value: str

@dataclass
class SystemParams:
    int_params: List[IntParam]
    string_params: List[StringParam]

@dataclass
class SdCardInfo:
    sdcapacity: int
    sdspare: int
    n_num: int
    g_num: int
    stmsize: int
    playback_size: int
    slCycleSpace: int
    smart_ok: int
    smart_version: int
    increasebadblock: int
    replaceblockleft: int
    runtime: int
    totalruntime: int
    remainlifetimedegree: int
    degreeofwear: int
    totalweartime: int

@dataclass
class LoginInfo:
    imei: str
    logon_time: str
    postion: str
    device_name: str

@dataclass
class LoginHistory:
    info: List[LoginInfo]

@dataclass
class BasicDeviceInfo:
    default_user: str
    model: str
    nickname: str
    macaddr: str
    version: str
    totalruntime: int

@dataclass
class TripStats:
    total_time: int
    total_mileage: int
    avg_speed: float

@dataclass
class HaloResponse:
    def __init__(self, errcode: int, data_raw):
        self.errcode = errcode
        self._data_raw = data_raw
        self._data = None
        
    @staticmethod
    def from_json(resp_json):
        errcode = resp_json.get("errcode")
        data_raw = resp_json.get("data")
        return HaloResponse(errcode, data_raw)
    
    @property
    def data(self):
        if self._data is None:
            try:               
                # Handle empty string responses
                if self._data_raw == "":
                    self._data = None
                    return self._data
                
                # Parse JSON string responses
                parsed = json.loads(self._data_raw) if isinstance(self._data_raw, str) else self._data_raw
                
                # Dispatch based on keys in the parsed data
                if isinstance(parsed, dict):
                    # Session response
                    if "acSessionId" in parsed:
                        self._data = SessionData(acSessionId=parsed["acSessionId"])
                    
                    # Device info (comprehensive)
                    elif "nickname" in parsed and "model" in parsed and "uuid" in parsed:
                        self._data = DeviceInfo(**parsed)
                    
                    # ACC status
                    elif "connetc_acc_status" in parsed:
                        self._data = AccStatus(**parsed)
                    
                    # State info
                    elif "state" in parsed:
                        self._data = StateInfo(**parsed)
                    
                    # GPS state
                    elif "gpsstate" in parsed:
                        self._data = GpsState(**parsed)
                    
                    # System parameters
                    elif "int_params" in parsed and "string_params" in parsed:
                        int_params = [IntParam(**param) for param in parsed["int_params"]]
                        string_params = [StringParam(**param) for param in parsed["string_params"]]
                        self._data = SystemParams(int_params=int_params, string_params=string_params)
                    
                    # SD Card info
                    elif "sdcapacity" in parsed and "playback_size" in parsed:
                        self._data = SdCardInfo(**parsed)
                    
                    # Login history
                    elif "info" in parsed and isinstance(parsed["info"], list):
                        login_infos = [LoginInfo(**info) for info in parsed["info"]]
                        self._data = LoginHistory(info=login_infos)
                    
                    # Basic device info (minimal)
                    elif "model" in parsed and "default_user" in parsed:
                        self._data = BasicDeviceInfo(**parsed)
                    
                    # Trip statistics
                    elif "total_time" in parsed and "total_mileage" in parsed:
                        self._data = TripStats(**parsed)
                    
                    # Fallback for unknown structures
                    else:
                        self._data = parsed
                else:
                    self._data = parsed
                    
            except Exception as e:
                # If parsing fails, store raw data
                self._data = self._data_raw
                
        return self._data