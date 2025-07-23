import time
from roadangel import wifi, dashcam
from roadangel.models import SwitchMode




#wifi.auto_connect()

dashcam = dashcam.HaloPro("193.168.0.1")
dashcam.test()
dashcam.get_session()
dashcam.get_certificate()
dashcam.get_mailboxdata()
dashcam.snycdate()
#dashcam.generalsave(mic_switch="off", speaker_turn=100)
dashcam.superdownload()
dashcam.set_applivestate(switch=SwitchMode.ON)
dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)
#dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)
#dashcam.set_playbackliveswitch(switch=SwitchMode.LIVE)

dashcam.visualize_stream()

dashcam.set_playbackliveswitch(switch=SwitchMode.TOGGLE)
dashcam.set_applivestate(switch=SwitchMode.OFF)