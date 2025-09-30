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

