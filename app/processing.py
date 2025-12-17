from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np


def ensure_bgr(frame):
    if frame is None:
        return frame
    if len(frame.shape) == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    return frame


def mirror(frame):
    return cv2.flip(frame, 1)


def to_grey_bgr(frame):
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)


def negative(frame):
    return cv2.bitwise_not(frame)


def resize_with_padding(frame, target_size: tuple[int, int], pad_color: tuple[int, int, int] = (0, 0, 0)):
    target_w, target_h = target_size
    frame = ensure_bgr(frame)
    h, w = frame.shape[:2]
    if h == 0 or w == 0:
        return np.full((target_h, target_w, 3), pad_color, dtype=np.uint8)

    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = cv2.resize(frame, (new_w, new_h))

    canvas = np.full((target_h, target_w, 3), pad_color, dtype=np.uint8)
    x0 = (target_w - new_w) // 2
    y0 = (target_h - new_h) // 2
    canvas[y0 : y0 + new_h, x0 : x0 + new_w] = resized
    return canvas


def placeholder_frame(size: tuple[int, int], text: str):
    w, h = size
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    return frame


class FaceDetector:
    def __init__(self, prototxt_path: Path, model_path: Path, min_confidence: float = 0.5) -> None:
        self._prototxt_path = prototxt_path
        self._model_path = model_path
        self._min_confidence = min_confidence
        self._net: Optional[cv2.dnn_Net] = None

    def _load(self) -> cv2.dnn_Net:
        if self._net is None:
            self._net = cv2.dnn.readNetFromCaffe(str(self._prototxt_path), str(self._model_path))
        return self._net

    def crop_face(self, frame):
        net = self._load()
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0),
        )
        net.setInput(blob)
        detections = net.forward()

        if detections.shape[2] == 0:
            return frame

        i = int(np.argmax(detections[0, 0, :, 2]))
        confidence = float(detections[0, 0, i, 2])
        if confidence < self._min_confidence:
            return frame

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        start_x, start_y, end_x, end_y = box.astype("int")
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(w, end_x)
        end_y = min(h, end_y)
        roi = frame[start_y:end_y, start_x:end_x]
        if roi.size == 0:
            return frame
        return roi

