# Blood Cell Detection API

A production-style FastAPI service that uses a YOLO model to detect and count blood cells (RBCs, WBCs, platelets) in microscope images.

## Features

- FastAPI REST API with auto-generated OpenAPI docs at `/docs`
- YOLO (Ultralytics) inference with a thread-safe, lazy-loaded model wrapper
- Per-class detection counts and bounding-box coordinates
- Optional endpoint that returns the annotated image
- Configurable via environment variables / `.env`

## Project Structure

```
BRProject/
├── app/                # App-level config and Pydantic schemas
│   ├── config.py
│   └── schemas.py
├── routes/             # HTTP route handlers
│   ├── detection.py
│   └── health.py
├── models/             # Model wrapper + weights
│   ├── yolo_loader.py
│   └── weights/        # Place trained `best.pt` here
├── utils/              # Logging and image helpers
│   ├── image_processing.py
│   └── logger.py
├── data/               # Local samples and inference outputs
│   ├── samples/
│   └── outputs/
├── main.py             # FastAPI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example env file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

3. Place your trained YOLO weights at `models/weights/best.pt`.
   If the file is missing, the service falls back to the pretrained `yolov8n.pt`
   (downloaded automatically by Ultralytics) so the API is still runnable for smoke-testing.

## Running the API

Start the FastAPI server with uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available locally at:

- API base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can also run the app through Python:

```bash
python main.py
```

### Sample Request

Analyze an uploaded blood smear image:

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@data/samples/blood_smear.jpg"
```

Optionally add a short OpenAI-generated explanation:

```bash
export OPENAI_API_KEY="your_api_key_here"

curl -X POST "http://localhost:8000/api/v1/analyze?enhance_with_ai=true" \
  -F "file=@data/samples/blood_smear.jpg"
```

The AI step is disabled by default. If enabled but not configured, the API still
returns the normal rule-based report and includes a non-blocking `ai_error`.

## Endpoints

| Method | Path                         | Description                                        |
| ------ | ---------------------------- | -------------------------------------------------- |
| GET    | `/`                          | Service banner / health                            |
| GET    | `/health`                    | Liveness probe                                     |
| POST   | `/api/v1/analyze`            | Detect cells, count them, and generate a report    |
| POST   | `/api/v1/detect`             | Run detection, returns JSON with boxes and counts  |
| POST   | `/api/v1/detect/annotated`   | Returns the input image with bounding boxes drawn  |

### Example

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@data/samples/blood_smear.jpg"
```

Response:

```json
{
  "filename": "blood_smear.jpg",
  "image_width": 1280,
  "image_height": 960,
  "inference_time_ms": 84.21,
  "detections": [
    {
      "class_id": 0,
      "class_name": "RBC",
      "confidence": 0.91,
      "bbox": { "x_min": 120.4, "y_min": 88.1, "x_max": 178.6, "y_max": 145.0 }
    }
  ],
  "counts": { "RBC": 42, "WBC": 3, "Platelets": 11 }
}
```

## Configuration

All settings can be overridden via environment variables (see `.env.example`):

| Variable               | Default                          | Description                          |
| ---------------------- | -------------------------------- | ------------------------------------ |
| `HOST`                 | `0.0.0.0`                        | Bind address                         |
| `PORT`                 | `8000`                           | Bind port                            |
| `DEBUG`                | `false`                          | Enables uvicorn auto-reload          |
| `MODEL_WEIGHTS_PATH`   | `models/weights/best.pt`         | Path to YOLO weights                 |
| `CONFIDENCE_THRESHOLD` | `0.25`                           | Minimum detection confidence         |
| `IOU_THRESHOLD`        | `0.45`                           | NMS IoU threshold                    |
| `IMAGE_SIZE`           | `640`                            | Inference image size                 |
| `DEVICE`               | `cpu`                            | `cpu`, `cuda`, `cuda:0`, `mps`, etc. |
| `MAX_UPLOAD_SIZE_MB`   | `10`                             | Reject uploads larger than this      |
| `OPENAI_API_KEY`       |                                  | Optional key for AI report rewrite   |
| `OPENAI_MODEL`         | `gpt-4o-mini`                    | Optional OpenAI model name           |
| `OPENAI_TIMEOUT_SECONDS` | `8`                            | OpenAI request timeout               |

## License

MIT
