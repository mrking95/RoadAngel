import time
from datetime import datetime
from roadangel import wifi, dashcam
from roadangel.gps import GPSFetcher
from roadangel.models import SwitchMode




#wifi.auto_connect()

dashcam = dashcam.HaloPro("193.168.0.1")
dashcam.get_session()
dashcam.get_certificate()
dashcam.get_mailboxdata()
dashcam.syncdate()

gps = GPSFetcher(dashcam.host)

print(gps.fetch_latest_gps())

# #dashcam.generalsave(mic_switch="off", speaker_turn=100)
# dashcam.superdownload()
# dashcam.set_applivestate(switch=SwitchMode.ON)
# dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)
# #dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)
# #dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)

# dashcam.visualize_stream()

# dashcam.set_playbackliveswitch(switch=SwitchMode.TOGGLE)
# dashcam.set_applivestate(switch=SwitchMode.OFF)