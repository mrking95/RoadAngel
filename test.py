from roadangel import wifi, dashcam

def auto_connect():
    matches = wifi.list_networks()
    if not matches:
        print("❌ Geen geschikte netwerken gevonden.")
        return

    ssid = matches[0]
    print(f"[info] Verbinden met: {ssid}")

    passwords = ["1234567890"]

    for pw in passwords:
        try:
            wifi.connect_to_wifi(ssid, pw)
            print(f"[success] Verbonden met {ssid}")
            return  # Stop als verbinden lukt
        except Exception as e:
            print(f"[error] Verbinden met {ssid} mislukt: {e}")

    print(f"[error] Alle wachtwoorden geprobeerd, verbinding met {ssid} is niet gelukt.")


auto_connect()

dashcam = dashcam.HaloPro("193.168.0.1")
dashcam.test()
dashcam.get_session()
dashcam.get_certificate()
dashcam.get_mailboxdata()
dashcam.set_playbackliveswitch()
dashcam.visualize_stream()