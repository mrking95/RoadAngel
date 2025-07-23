import requests
import socket
import numpy as np
import cv2
import logging
import json
import time
from .models import HaloResponse, SessionData, SwitchMode

class HaloPro:
    def __init__(self, host, username="admin", password="admin"):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.uid = "8f852e60dccd41299e873c62e3ba1ae38750231a"
        self.stream_url = f'tcp://{self.host}:6200/'
        self.headers = None
        self.coockie = None

    def test(self, timeout=5):
        """Test remote connection"""
        try:
            with socket.create_connection((self.host, 80), timeout=timeout):
                logging.info(f"[success] Verbinding met {self.host}:80 succesvol.")
                return True
        except Exception as e:
            raise RuntimeError(f"[error] Failed to connect {self.host}, {e}")
        

    def get_session(self):
        """Initialize a connection and get session_id with retry logic"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_RequestSessionID"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, data={
                "vyou": "1",
                "id": "2"
            }, timeout=5)
            response.raise_for_status()
            
            # Parse direct naar HaloResponse
            halo_resp = HaloResponse.from_json(response.json())
            if halo_resp.errcode != 0:
                raise RuntimeError(f"[error] API returned error code: {response.json()}")
            
            # Extract acsession_id uit de geneste data
            if isinstance(halo_resp.data, SessionData):
                self.session_id = halo_resp.data.acSessionId

                self.headers = {
                    'Content-Type': 'application/json',
                    'SessionID': self.session_id
                }

                self.cookies = {
                    'Cookie': f'JSESSIONID={self.session_id}'
                }

                if not self.session_id:
                    raise RuntimeError("[error] acsession_id not found in response data")
                
            else:
                raise RuntimeError(f"[error] API returned invalid object: {response.json()}")
            
            return  # Success, exit the function
            
        except Exception as e:
            raise RuntimeError(f"[error] Failed to get session ID: {e}")
        
    def get_certificate(self):
        """Request certificate from HaloPro with session_id as cookie"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_RequestCertificate"

            payload = json.dumps({
                "password": self.password,
                "uid": "8f852e60dccd41299e873c62e3ba1ae38750231a",
                "level": 0,
                "user": self.username
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
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

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
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
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=APP_PlaybackLiveSwitch"

            payload = json.dumps({
                "switch": switch.value,
                "playtime": "0"
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] Livestream switched {switch}. Stream available at: {self.stream_url}")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set livestream: {e}")
        
    def set_applivestate(self, switch: SwitchMode = SwitchMode.ON):
        """Check if there is any data ready for us"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_SetAppLiveState"

            payload = json.dumps({
                "switch": switch.value,
                "playtime": "0"
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] livestate switched {switch}. Stream available at: {self.stream_url}")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set applivestate: {e}")
        

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