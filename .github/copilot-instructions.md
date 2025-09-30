# AI Coding Instructions: Automatic1111 Pico Passthrough Service

## Project Overview
This is a Flask/FastAPI service that proxies Automatic1111 webui requests and converts PNG responses to Pico LCD-compatible RGB565 raw binary format. The service runs on NVIDIA Jetson Orin Nano and eliminates on-device image processing complexity.

## Core Architecture Requirements

### Service Structure
Follow the documented FastAPI structure from the specification:
```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Pydantic settings with .env support
├── models.py            # Request/response models
├── services/
│   ├── a1111_client.py  # Async HTTP client for upstream A1111
│   ├── image_processor.py # PNG→RGB565 conversion pipeline
│   └── cache.py         # Optional LRU image caching
└── routers/
    └── txt2img.py       # Main API endpoints
```

### Critical Image Processing Function
The core conversion function MUST produce exactly **115,200 bytes** (240×240×2) of RGB565 data:

```python
def png_to_pico_rgb565(png_bytes: bytes, width: int = 240, height: int = 240, luminance_invert: bool = True) -> bytes:
    # Big-endian RGB565 format: ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
    # Pack as: data.append((rgb565 >> 8) & 0xFF); data.append(rgb565 & 0xFF)
```

Use Pillow's `Image.LANCZOS` for resizing and validate output size.

## Configuration Patterns

### Environment Variables
Use Pydantic BaseSettings with these required fields:
- `A1111_BASE_URL`: Upstream Automatic1111 service
- `A1111_USERNAME`/`A1111_PASSWORD`: Optional authentication
- `TARGET_WIDTH`/`TARGET_HEIGHT`: Default 240×240
- `LUMINANCE_INVERT`: Boolean for display compatibility
- `SERVICE_HOST`/`SERVICE_PORT`: Default 0.0.0.0:8080

### Error Handling Standards
Return structured JSON errors:
```python
{"error": "Upstream A1111 service unavailable", "code": 502}
{"error": "Failed to process image: unsupported format", "code": 422}
```

## API Implementation

### Primary Endpoint
`POST /sdapi/v1/txt2img` must:
1. Accept standard A1111 txt2img JSON payload
2. Proxy to configured upstream A1111 instance using `httpx` async client
3. Extract PNG from response and convert to RGB565
4. Return either binary (application/octet-stream) or base64 JSON format

### Response Headers for Binary Mode
```
Content-Type: application/octet-stream
Content-Length: 115200
X-Image-Width: 240
X-Image-Height: 240
X-Image-Format: rgb565-be
```

## Development Standards

### Dependencies
- **Web Framework**: FastAPI with uvicorn
- **HTTP Client**: httpx for async upstream requests
- **Image Processing**: Pillow (PIL) 9.0+
- **Config**: python-dotenv, pydantic
- **Testing**: pytest with httpx TestClient

### Performance Requirements
- Total latency < 2 seconds (A1111 + conversion)
- Handle 10 concurrent requests
- Memory < 500MB peak per request
- Validate RGB565 output is exactly 115,200 bytes

### Deployment Considerations
Target environment is Ubuntu 22.04 on Jetson Orin Nano. Include:
- Systemd service file for production deployment
- Nginx reverse proxy config for SSL termination
- Docker support as alternative deployment method
- Health endpoint at `/health` for monitoring

## Testing Requirements
- Unit tests for RGB565 conversion accuracy
- Integration tests against real A1111 instance
- Validate exact byte output (240×240×2 = 115,200)
- Performance benchmarks for conversion pipeline
- Error handling for invalid PNG responses

## Key Constraints
- ARM64 architecture optimization for Jetson platform
- Memory-efficient image processing (avoid fragmentation)
- Graceful upstream service failures
- Strict RGB565 format compliance for Pico LCD compatibility

Refer to `flask_fastAPI_automatic1111_passthrough_for_Pico.md` for complete technical specifications and architecture details.