import requests
import socket
import numpy as np
import cv2
import logging
import json
from datetime import datetime, timezone, timedelta

import time
from .models import DeviceInfo, GpsFileReq, HaloResponse, SessionData, SwitchMode

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
        """Change playback live mode"""
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
        """Change the app's state"""
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
        

    def syncdate(self):
        """Sync the date & time"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_SyncDate"

            tz = timezone(timedelta(seconds=7200))  # 7200 sec = +02:00

            payload = json.dumps({
                "imei": "",
                "format": "dd/MM/yyyy HH:mm:ss",
                "lang": "en_US",
                "time_zone": 7200,
                "date": datetime.now(tz).strftime("%Y%m%d%H%M%S")
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] Datetime synced")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set applivestate: {e}")


    def get_baseinfo(self) -> DeviceInfo:
        """Get DeviceInfo"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_GetBaseInfo"

            payload = json.dumps({
                "vyou": "1",
                "id": "2"
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            if isinstance(halo_resp.data, DeviceInfo):
                return halo_resp.data
            
            raise RuntimeError(f"Unable to get device info")

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set livestream: {e}")
        
    
    def superdownload(self, switch: SwitchMode = SwitchMode.OFF):
        """Set SuperDownload"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_SuperDownload"

            payload = json.dumps({
                "switch": switch.value,
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] superdownload switched {switch}")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set superdownload: {e}")
        
    def gpsfilelistreq(self) -> GpsFileReq:
        """http://193.168.0.1/vcam/cmd.cgi?cmd=API_GpsFileListReq"""
        """Get GPS file list"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_GpsFileListReq"

            payload = json.dumps({
                "vyou": "1",
                "id": "2"
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] GPS File req downloaded")
            if isinstance(halo_resp.data, GpsFileReq):
                return halo_resp.data
            
            raise RuntimeError(f'Response not of correct type')

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set superdownload: {e}")
        

    def generalsave(self, 
                    event_before_time=0, 
                    speaker_turn=50, 
                    parking_power_mgr=0, 
                    mic_switch="off",
                    osd_switch="off",
                    osd_speedswitch="off",
                    start_sound_switch="off",
                    scam_vertical_mirror="off",
                    scam_horizontal_mirror="off",
                    parking_status="hibernate",
                    power_guard_value="mid"
                ):
        """Allow changing of the config"""
        try:
            url = f"http://{self.host}/vcam/cmd.cgi?cmd=API_GeneralSave"

            payload = json.dumps({
                "int_params": [
                    {"key": "event_before_time", "value": event_before_time},         # 0-30
                    {"key": "event_after_time", "value": event_before_time},          # 0-30
                    {"key": "speaker_turn", "value": speaker_turn},              # 0-100
                    {"key": "parking_power_mgr", "value": parking_power_mgr},          # 0,1,2,3,4
                ],
                "string_params": [
                    {"key": "mic_switch", "value": mic_switch},
                    {"key": "osd_switch", "value": osd_switch},
                    {"key": "osd_speedswitch", "value": osd_speedswitch},
                    {"key": "start_sound_switch", "value": start_sound_switch},
                    {"key": "scam_vertical_mirror", "value": scam_vertical_mirror},
                    {"key": "scam_horizontal_mirror", "value": scam_horizontal_mirror},
                    {"key": "parking_status", "value": parking_status},   # timelapse | hibernate | normal
                    {"key": "power_guard_value", "value": power_guard_value},      # high | mid | low
                ]
            })

            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=payload, timeout=5)
            response.raise_for_status()

            print(response.json())

            halo_resp = HaloResponse.from_json(response.json())

            if halo_resp.errcode != 0:
                raise RuntimeError(f"API returned error code: {halo_resp.errcode}")

            logging.info(f"[info] Config changed")
            return True

        except Exception as e:
            raise RuntimeError(f"[error] Failed to set config: {e}")

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