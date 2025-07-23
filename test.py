from roadangel import wifi, dashcam
from roadangel.models import SwitchMode




#wifi.auto_connect()

dashcam = dashcam.HaloPro("193.168.0.1")
dashcam.test()
dashcam.get_session()
dashcam.get_certificate()
dashcam.get_mailboxdata()
dashcam.set_playbackliveswitch()
dashcam.set_applivestate(switch=SwitchMode.OFF)