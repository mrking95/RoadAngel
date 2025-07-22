# RoadAngel Halo SDK

This Python SDK makes it easy to connect to and communicate with the HaloPro dashcam via the API.

## Features

- Automatically connect to WiFi networks with specific SSID criteria
- Session management with automatic parsing of API responses
- Basic API functions such as starting sessions, retrieving certificates, and starting livestreams
- Streaming of the live video feed with OpenCV

## Usage

```python
from roadangel import wifi, dashcam

# Automatically connect to WiFi networks
wifi.auto_connect()

# Connect to the HaloPro dashcam
halo = dashcam.HaloPro("193.168.0.1", username="admin", password="admin")

# Start session
halo.get_session()

# Retrieve certificate
halo.get_certificate()

# Enable live playback
halo.set_playbackliveswitch("live")

# Play livestream UI 
halo.visualize_stream()

# Or use the stream to process yourself
url = f'tcp://{halo.host}:6200/'

```

## Response Model

The SDK automatically parses API responses into a `HaloResponse` object with `errcode` and `data`. Data is converted to an appropriate data model such as `SessionData` or `MailboxMessage`.

## Error Handling

If an API call fails, a `RuntimeError` is raised with a clear error message.

---

### Contact

For questions or feedback, open an issue on GitHub