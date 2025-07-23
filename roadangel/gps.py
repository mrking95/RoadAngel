import requests
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from dashcam import HaloPro

class GPSFetcher:
    def __init__(self, host: str):
        self.host = host
        self.dashcam = HaloPro(host)
        self._last_known_location = None  # opslaan laatste locatie dict

    def _parse_timestamp(self, ts_str: str) -> Optional[str]:
        # Implementatie naar wens, hier simpelweg return str of None
        return ts_str

    def _parse_coordinate(self, coord_str: str) -> Optional[float]:
        if coord_str is None:
            return None
        try:
            return float(coord_str)
        except ValueError:
            return None

    def _extract_gps_from_line(self, line: str) -> Optional[Dict]:
        # $GPRMC,125207.000,A,5215.61754,N,00648.54750,E,...
        if not line.startswith("$GPRMC"):
            return None

        parts = line.split(",")
        if len(parts) < 7 or parts[2] != "A":  # check valid fix
            return None

        timestamp = parts[1]
        lat_raw = parts[3]
        lat_dir = parts[4]
        lon_raw = parts[5]
        lon_dir = parts[6]

        def convert(coord, direction):
            if not coord:
                return None
            deg = float(coord[:2 if direction in ['N','S'] else 3])
            minutes = float(coord[2 if direction in ['N','S'] else 3:])
            dec = deg + minutes / 60
            if direction in ['S', 'W']:
                dec = -dec
            return dec

        latitude = convert(lat_raw, lat_dir)
        longitude = convert(lon_raw, lon_dir)

        return {
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,

        }
    def fetch_latest_gps(self) -> Optional[Dict]:
        """
        host: "193.168.0.1"
        timestamps: at time of asking (or before that?)
        """
        # We kunnen niet zomaar GPS ophalen, we moeten eerst een request doen naar API_GpsFileListReq, en daar de laatste uithalen, die mogen we downloaden.
        # 20250723145230_0060.gpx
        
        filereq = self.dashcam.gpsfilelistreq()

        if not filereq:
            logging.debug(f'No gps data available')
            return
        
        item = next((f for f in reversed(filereq.file) if f.type == "49"), None)
        
        if not item:
            logging.debug(f'No gps data available')
            return

        url = f"http://{self.host}/{item.name}"
        lines = []
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            lines = r.text.splitlines()
        except Exception:
            logging.warning(f'Failed getting .gpx for {url}')

        gps_data = None
        # reverse zoeken, laatste gps regel
        for line in reversed(lines):
            gps_data = self._extract_gps_from_line(line)
            if gps_data:
                self._last_known_location = gps_data
                break

        if gps_data:
            return {
                "timestamp": self._parse_timestamp(gps_data.get("timestamp")),
                "latitude": self._parse_coordinate(str(gps_data.get("latitude"))),
                "longitude": self._parse_coordinate(str(gps_data.get("longitude"))),
            }

        # geen GPS gevonden, return laatste bekende locatie (kan None zijn)
        if self._last_known_location:
            return {
                "timestamp": self._parse_timestamp(self._last_known_location.get("timestamp")),
                "latitude": self._parse_coordinate(str(self._last_known_location.get("latitude"))),
                "longitude": self._parse_coordinate(str(self._last_known_location.get("longitude"))),
            }

        return None
