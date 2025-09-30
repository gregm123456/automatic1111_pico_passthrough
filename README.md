# Pico A1111 Proxy

Author: Greg Merritt <greg.merritt@gmail.com>

Repository: gregm123456/automatic1111_pico_passthrough

License: MIT

Minimal FastAPI service that proxies Automatic1111 `/sdapi/v1/txt2img` requests and converts PNG output to Pico-compatible RGB565 big-endian binary.



Notes:
- CI runs pytest on Python 3.11 via GitHub Actions (`.github/workflows/ci.yml`).
- The project includes a systemd service and nginx config for Jetson deployment under `deploy/` and an installer script under `scripts/`.
- For full technical details see `flask_fastAPI_automatic1111_passthrough_for_Pico.md`.

Contact: Greg Merritt <greg.merritt@gmail.com>

Quickstart

1. Create virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `A1111_BASE_URL`.
3. (Optional) Set an API key in `.env` with `SERVICE_API_KEY` to protect the endpoint.

3. Run server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

4. Health check:

```bash
curl http://localhost:8080/health
```

Run tests:

```bash
pytest -q
```

Deployment (Jetson / Ubuntu)

1. Copy the project to the Jetson or run the installer script on the device (run as root):

```bash
sudo ./scripts/install_system_service.sh /path/to/project
```

2. After install, edit `/opt/pico-a1111-proxy/.env` and set `A1111_BASE_URL` and `SERVICE_API_KEY` (optional).

3. Restart and check status:

```bash
sudo systemctl restart pico-a1111-proxy.service
sudo systemctl status pico-a1111-proxy.service
```

Notes:
- Service runs as `www-data` by default (adjust `deploy/pico-a1111-proxy.service` if needed).
- Ensure `nginx` is installed on the target; installer will copy a site file and attempt to reload nginx.

Using MicroPython from a Pico 2W
--------------------------------

This section shows example MicroPython code you can run on a Raspberry Pi Pico 2W (or similar MicroPython-capable board) to call this Automatic1111 passthrough service. The service supports API key authentication using the `X-API-Key` HTTP header when `SERVICE_API_KEY` is set in the server `.env` file.

Server-side notes
- If you protect the service with an API key, set `SERVICE_API_KEY` in the project's `.env` file. The MicroPython client must include the header `X-API-Key: <your-key>` with every request.
- The primary endpoint is `POST /sdapi/v1/txt2img` and accepts the standard A1111 JSON payload. The proxy will return either raw binary RGB565 (big-endian) when requested, or a JSON response containing base64-encoded image data depending on client preference.
- Binary responses use these headers:

```
Content-Type: application/octet-stream
Content-Length: 115200
X-Image-Width: 240
X-Image-Height: 240
X-Image-Format: rgb565-be
```

MicroPython example: save RGB565 binary to file

This example demonstrates connecting the Pico 2W to Wi-Fi, posting a minimal txt2img payload, sending the `X-API-Key` header, and saving the returned 240x240 RGB565 big-endian binary to a file on the board's filesystem.

```python
import network
import urequests as requests
import ujson as json

# Wi-Fi setup
ssid = 'YOUR_SSID'
pw = 'YOUR_WIFI_PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
	wlan.connect(ssid, pw)
	while not wlan.isconnected():
		pass

print('network config:', wlan.ifconfig())

# Replace with your proxy server address (include port if not 80/443)
server = 'http://192.168.1.100:8080'
endpoint = server + '/sdapi/v1/txt2img'

# Replace with your service API key if set on the server
api_key = 'YOUR_SERVICE_API_KEY'

# Minimal A1111 txt2img payload; adjust as needed
payload = {
	'prompt': 'a simple test image',
	'steps': 10,
	'width': 240,
	'height': 240
}

headers = {
	'Content-Type': 'application/json',
	'X-API-Key': api_key,
	# Request binary response mode; the server may use a query param or header to select.
	# This project returns binary when client accepts application/octet-stream.
	'Accept': 'application/octet-stream'
}

resp = requests.post(endpoint, data=json.dumps(payload), headers=headers)
if resp.status_code != 200:
	print('error', resp.status_code, resp.text)
else:
	# Expect exactly 115200 bytes (240*240*2)
	data = resp.content
	print('received', len(data), 'bytes')
	if len(data) == 240 * 240 * 2:
		with open('image_rgb565.bin', 'wb') as f:
			f.write(data)
		print('saved image_rgb565.bin')
	else:
		print('unexpected length; check server mode or error payload')

resp.close()
```

MicroPython example: handle base64 JSON response

Some clients prefer JSON responses where the image is base64-encoded. The following example shows how to request JSON mode, decode a base64 PNG (or base64 RGB565) and save it. Adjust based on the server's JSON response schema.

```python
import network
import urequests as requests
import ujson as json
import ubinascii as binascii

# Assume Wi-Fi already connected as above
server = 'http://192.168.1.100:8080'
endpoint = server + '/sdapi/v1/txt2img'
api_key = 'YOUR_SERVICE_API_KEY'

payload = {
	'prompt': 'another test',
	'steps': 10,
	'width': 240,
	'height': 240,
	# If the proxy supports a flag to return base64 JSON, include it here.
	'return_base64': True
}

headers = {
	'Content-Type': 'application/json',
	'X-API-Key': api_key,
	'Accept': 'application/json'
}

resp = requests.post(endpoint, data=json.dumps(payload), headers=headers)
if resp.status_code != 200:
	print('error', resp.status_code, resp.text)
else:
	j = resp.json()
	# Example response shape: { 'image_base64': '<b64data>' }
	b64 = j.get('image_base64') or j.get('images', [None])[0]
	if not b64:
		print('no image in response')
	else:
		raw = binascii.a2b_base64(b64)
		# If the proxy returned PNG, save as .png; if it returned rgb565 save as .bin
		with open('image_from_json.bin', 'wb') as f:
			f.write(raw)
		print('saved image_from_json.bin', len(raw), 'bytes')

resp.close()
```

Tips and troubleshooting
- If you get an HTTP 401/403, verify that the `X-API-Key` value matches `SERVICE_API_KEY` in the server `.env`.
- The binary mode must return exactly 115200 bytes for a 240x240 RGB565 image. If the length differs, check for upstream A1111 errors returned as JSON instead of binary.
- For space-limited storage on the Pico, consider streaming the response to the filesystem in chunks rather than holding the entire body in memory.


