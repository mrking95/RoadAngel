import requests
import socket
import numpy as np
import cv2
import logging
import json
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

class SwitchMode(str, Enum):
    LIVE = "live"
    TOGGLE = "toggle"

@dataclass
class SessionData:
    acsession_id: str

@dataclass
class MailboxMessage:
    msgid: str
    data: dict

    @staticmethod
    def from_dict(d):
        return MailboxMessage(
            msgid=d.get("msgid"),
            data=json.loads(d.get("data")) if isinstance(d.get("data"), str) else d.get("data")
        )

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
                # Probeer eerst JSON te parsen
                parsed = json.loads(self._data_raw) if isinstance(self._data_raw, str) else self._data_raw
            except Exception:
                parsed = self._data_raw
            
            # Automatische dispatch op basis van keys:
            if isinstance(parsed, dict):
                if "acsession_id" in parsed:
                    self._data = SessionData(**parsed)
                elif "msg" in parsed:
                    self._data = [MailboxMessage.from_dict(m) for m in parsed["msg"]]
                else:
                    self._data = parsed  # fallback
            else:
                self._data = parsed
        return self._data
    

class HaloPro:
    def __init__(self, host, username="admin", password="admin"):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.uid = "8f852e60dccd41299e873c62e3ba1ae38750231a"
        self.stream_url = f'tcp://{self.host}:6200/'

    def test(self, timeout=5):
        """Test remote connection"""
        try:
            with socket.create_connection((self.host, 80), timeout=timeout):
                logging.info(f"[success] Verbinding met {self.host}:80 succesvol.")
                return True
        except Exception as e:
            raise RuntimeError(f"[error] Failed to connect {self.host}, {e}")
        
    def get_session(self):
        """Initialize a connection and get session_id"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_Requestsession_id"
            payload = json.dumps({
                "vyou": "1",
                "id": "2"
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=payload, timeout=5)
            response.raise_for_status()

            # Parse direct naar HaloResponse
            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"[error] API returned error code: {halo_resp.errcode}")

            # Extract acsession_id uit de geneste data
            self.session_id = halo_resp.data.acsession_id
            if not self.session_id:
                raise RuntimeError("[error] acsession_id not found in response data")

            logging.info(f"[success] session_id stored")

        except Exception as e:
            raise RuntimeError(f"[error] Failed to get session ID: {e}")
        
    def get_certificate(self):
        """Request certificate from HaloPro with session_id as cookie"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_RequestCertificate"

            payload = json.dumps({
                "password": self.password,
                "uid": self.session_id,
                "level": 0,
                "user": self.username
            })

            headers = {
                'Content-Type': 'application/json',
                'session_id': self.session_id
            }

            cookies = {
                'Jsession_id': self.session_id
            }

            response = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[success] Certificaat stored")
            return halo_resp.data

        except Exception as e:
            raise RuntimeError(f"[error] Failed to get certificate: {e}")
        
    def get_mailboxdata(self):
        """Check if there is any data ready for us"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_GetMailboxData"

            payload = json.dumps({
                "vyou": "1",
                "id": "2"
            })

            headers = {
                'Content-Type': 'application/json',
                'session_id': self.session_id
            }

            cookies = {
                'Jsession_id': self.session_id
            }

            response = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] Mailboxdata retreived {halo_resp.data}")
            return halo_resp.data

        except Exception as e:
            raise RuntimeError(f"[error] Failed to get mailboxdata: {e}")


    def set_playbackliveswitch(self, switch: SwitchMode = SwitchMode.LIVE):
        """Check if there is any data ready for us"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_GetMailboxData"

            payload = json.dumps({
                "switch": switch.value,
                "playtime": "0"
            })

            headers = {
                'Content-Type': 'application/json',
                'session_id': self.session_id
            }

            cookies = {
                'Jsession_id': self.session_id
            }

            response = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] Livestream switched {switch}. Stream available at: {self.stream_url}")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set livestream: {e}")
        

    def visualize_stream(self):
        """Opens CV2 stream to the dashcam"""
        try:
            cap = cv2.VideoCapture(self.stream_url)
            cap.set(cv2.CAP_PROP_FPS, 30)

            while True:
                ret, frame = cap.read()
                if not ret:
                    logging.info("⚠️ Frame niet ontvangen, probeer opnieuw...")
                    break

                cv2.imshow('Livestream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            raise RuntimeError(f"[error] Failed to open VLC: {e}")