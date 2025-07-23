from roadangel import wifi, dashcam




#wifi.auto_connect()

dashcam = dashcam.HaloPro("193.168.0.1")
dashcam.test()
dashcam.get_session()
dashcam.get_certificate()
dashcam.get_mailboxdata()
dashcam.set_playbackliveswitch()
dashcam.visualize_stream()