# Camera App (Flask + OpenCV)

I built this project to practice **Flask + OpenCV**: the server reads frames from the webcam and streams them to the browser as a live feed. On top of the stream, there are a few basic controls for taking a photo, recording a video, and toggling simple filters.

Main inspiration: `https://towardsdatascience.com/camera-app-with-flask-and-opencv-bd147f6c0eec/`

## Features
- Live webcam feed in the browser (MJPEG stream)
- `Stop/Start` to toggle the stream
- `Capture` to save a photo into `shots/` using a timestamped filename (e.g. `shot_20260120_153012_123456.png`)
- `Start/Stop Recording` to record and save a video into `shots/` (e.g. `vid_*.avi`)
- Filters (toggle on/off):
  - `Grey`
  - `Negative`
  - `Face Only`

## Project Structure
I kept things modular so it’s easy to extend later (for example, adding a new filter mostly stays inside `processing.py`).

```
CameraApp/
  app/
    __init__.py        # create_app + config
    routes.py          # routes (/, /video_feed, /actions)
    camera.py          # VideoCapture + frame reads
    processing.py      # filters + image processing
    state.py           # toggle state + capture request
    recording.py       # video recording (VideoWriter + thread)
  templates/
    index.html
  static/
    css/
    icons/
  models/
    deploy.prototxt.txt
    res10_300x300_ssd_iter_140000.caffemodel
  pyproject.toml       # dependencies (uv)
  uv.lock              # lockfile (uv)
  requirements.txt     # fallback for pip
  run.py               # entrypoint
  README.md
```

## Run (recommended: uv)
### 1) Install uv (one-time)

```powershell
pip install uv
```

### 2) Install dependencies and run
From inside `CameraApp/`:

```powershell
uv venv
uv sync
uv run python run.py
```

Then open: `http://127.0.0.1:5000/`

## Run with pip (fallback)
If you don’t want to use `uv`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

## Notes
- The timestamp is **not** drawn on the image; it’s only used in the filename.
- If `shots/` doesn’t exist, the app creates it automatically.

## Troubleshooting (Camera not detected / no permission prompt)
- The camera is opened on the server side via OpenCV, so the browser won’t show a permission prompt.
- If the camera doesn’t open, close other apps using the camera (Teams/Zoom/OBS/Camera), and on Windows enable camera access for Desktop apps in `Settings > Privacy & security > Camera`.
