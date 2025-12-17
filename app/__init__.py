from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from .camera import Camera
from .processing import FaceDetector
from .recording import VideoRecorder
from .state import AppState


def create_app() -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    templates_dir = project_root / "templates"
    static_dir = project_root / "static"
    models_dir = project_root / "models"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
    )

    app.extensions["state"] = AppState()

    camera_index = int(os.environ.get("CAMERA_INDEX", "0"))
    camera_width = int(os.environ.get("CAMERA_WIDTH", "640"))
    camera_height = int(os.environ.get("CAMERA_HEIGHT", "480"))
    camera_auto_detect = os.environ.get("CAMERA_AUTO_DETECT", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    camera_max_index = int(os.environ.get("CAMERA_MAX_INDEX", "5"))

    app.extensions["camera"] = Camera(
        device_index=camera_index,
        width=camera_width,
        height=camera_height,
        auto_detect=camera_auto_detect,
        max_index=camera_max_index,
    )
    app.extensions["face_detector"] = FaceDetector(
        prototxt_path=models_dir / "deploy.prototxt.txt",
        model_path=models_dir / "res10_300x300_ssd_iter_140000.caffemodel",
        min_confidence=0.5,
    )
    app.extensions["recorder"] = VideoRecorder(output_dir=project_root, fps=20.0)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
    return app
