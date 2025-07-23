# __init__.py
"""
HaloPro Camera API Package
Provides dataclasses and utilities for interfacing with HaloPro dashcam devices.
"""

# Import all dataclasses from the models module
from .models import (
    # Main response class
    HaloResponse,
    
    # Data classes for different response types
    SessionData,
    DeviceInfo,
    AccStatus,
    StateInfo,
    ErrorData,
    GpsState,
    IntParam,
    StringParam,
    SystemParams,
    SdCardInfo,
    LoginInfo,
    LoginHistory,
    BasicDeviceInfo,
    TripStats,
)

# Define what gets imported with "from halopro import *"
__all__ = [
    'HaloResponse',
    'SessionData',
    'DeviceInfo',
    'AccStatus',
    'StateInfo',
    'ErrorData',
    'GpsState',
    'IntParam',
    'StringParam',
    'SystemParams',
    'SdCardInfo',
    'LoginInfo',
    'LoginHistory',
    'BasicDeviceInfo',
    'TripStats',
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Thomas Engberink'
__description__ = 'HaloPro Camera API Data Classes'