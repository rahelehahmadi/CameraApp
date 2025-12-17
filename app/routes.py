from __future__ import annotations

import datetime as _dt
import time
from pathlib import Path

import cv2
from flask import Blueprint, Response, current_app, redirect, render_template, request, url_for

from .processing import (
    mirror,
    negative,
    placeholder_frame,
    resize_with_padding,
    to_grey_bgr,
)

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    state = current_app.extensions["state"]
    recorder = current_app.extensions["recorder"]
    view_state = state.snapshot() | {"recording_on": recorder.is_recording}
    return render_template("index.html", state=view_state)


@bp.post("/actions")
def actions():
    state = current_app.extensions["state"]
    camera = current_app.extensions["camera"]
    recorder = current_app.extensions["recorder"]

    if "stop" in request.form:
        stream_on = state.toggle_stream()
        if stream_on:
            camera.open()
        else:
            recorder.stop()
            camera.release()

    if "click" in request.form:
        state.request_capture()

    if "grey" in request.form:
        state.toggle_grey()

    if "neg" in request.form:
        state.toggle_negative()

    if "face" in request.form:
        state.toggle_face_only()

    if "rec" in request.form:
        if not state.snapshot()["stream_on"]:
            state.toggle_stream()
            camera.open()
        if recorder.is_recording:
            recorder.stop()
        else:
            camera.open()
            cfg = camera.config
            try:
                recorder.start((cfg.width, cfg.height))
            except Exception:
                pass

    return redirect(url_for("main.index"))


@bp.get("/video_feed")
def video_feed():
    camera = current_app.extensions["camera"]
    state = current_app.extensions["state"]
    face_detector = current_app.extensions["face_detector"]
    recorder = current_app.extensions["recorder"]

    cfg = camera.config
    target_size = (cfg.width, cfg.height)

    return Response(
        _generate_mjpeg(camera, state, face_detector, recorder, target_size),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def _generate_mjpeg(camera, state, face_detector, recorder, target_size: tuple[int, int]):
    target_w, target_h = target_size
    shots_dir = Path("shots")
    shots_dir.mkdir(parents=True, exist_ok=True)

    while True:
        s = state.snapshot()
        if not s["stream_on"]:
            frame = placeholder_frame(target_size, "Stream paused")
            yield _encode_mjpeg_frame(frame)
            time.sleep(0.1)
            continue

        ok, frame = camera.read()
        if not ok or frame is None:
            frame = placeholder_frame(target_size, "Camera not available")
            yield _encode_mjpeg_frame(frame)
            time.sleep(0.1)
            continue

        try:
            frame = cv2.resize(frame, (target_w, target_h))
        except Exception:
            frame = placeholder_frame(target_size, "Resize failed")

        if s["face_only_on"]:
            try:
                face = face_detector.crop_face(frame)
                frame = resize_with_padding(face, target_size)
            except Exception:
                frame = resize_with_padding(frame, target_size)

        if s["grey_on"]:
            frame = to_grey_bgr(frame)

        if s["negative_on"]:
            frame = negative(frame)

        if state.consume_capture_request():
            now = _dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            path = shots_dir / f"shot_{now}.png"
            try:
                cv2.imwrite(str(path), frame)
            except Exception:
                pass

        if recorder.is_recording:
            recorder.update_frame(frame)

        display = frame.copy()
        if recorder.is_recording:
            cv2.putText(
                display,
                "Recording...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
            )

        display = mirror(display)
        yield _encode_mjpeg_frame(display)
        time.sleep(0.01)


def _encode_mjpeg_frame(frame):
    ret, buffer = cv2.imencode(".jpg", frame)
    if not ret:
        return b""
    jpg = buffer.tobytes()
    return (
        b"--frame\r\n"
        b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
    )
