import subprocess
import re

WIFI_REGEX = re.compile(r"^WiFi_\d{4}HaloPro$")

def list_networks():
    """List alle zichtbare wifi SSID's die matchen op WiFi_####HaloPro."""
    result = subprocess.run(
        ["nmcli", "-t", "-f", "SSID", "dev", "wifi"],
        capture_output=True, text=True, check=True
    )
    networks = result.stdout.strip().split('\n')
    filtered = [ssid for ssid in networks if WIFI_REGEX.match(ssid)]
    return filtered

def connect_to_wifi(ssid, password, timeout=10):
    """Verbind headless met een WiFi-netwerk en fail hard als het niet binnen <timeout> seconden lukt."""
    try:
        # Oude verbinding verwijderen om credential popups te vermijden
        subprocess.run(
            ["nmcli", "connection", "delete", ssid],
            capture_output=True, text=True
        )
    except Exception:
        pass  # niet erg als hij nog niet bestaat

    try:
        result = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid, "password", password],
            capture_output=True, text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Timeout: Verbinden niet gelukt binnen {timeout} seconden.")

    if result.returncode != 0:
        raise RuntimeError(f"Verbinden met {ssid} mislukt:\n{result.stderr.strip()}")
    return True