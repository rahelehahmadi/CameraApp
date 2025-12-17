from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Optional

import sys
import time

import cv2


@dataclass(frozen=True)
class CameraConfig:
    device_index: int = 0
    width: int = 640
    height: int = 480


class Camera:
    def __init__(
        self,
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
        *,
        auto_detect: bool = True,
        max_index: int = 5,
        open_retry_seconds: float = 1.0,
    ) -> None:
        self._config = CameraConfig(device_index=device_index, width=width, height=height)
        self._auto_detect = auto_detect
        self._max_index = max(0, int(max_index))
        self._open_retry_seconds = max(0.1, float(open_retry_seconds))
        self._lock = Lock()
        self._cap: Optional[cv2.VideoCapture] = None
        self._active_index: Optional[int] = None
        self._active_backend: Optional[int] = None
        self._last_open_failure_at: Optional[float] = None

    @property
    def config(self) -> CameraConfig:
        return self._config

    @property
    def active_index(self) -> Optional[int]:
        with self._lock:
            return self._active_index

    @property
    def active_backend(self) -> Optional[int]:
        with self._lock:
            return self._active_backend

    def open(self) -> None:
        with self._lock:
            if self._cap is not None and self._cap.isOpened():
                return
            if self._last_open_failure_at is not None:
                if (time.monotonic() - self._last_open_failure_at) < self._open_retry_seconds:
                    return

        preferred_index = self._config.device_index
        indices = [preferred_index]
        if self._auto_detect:
            indices.extend(i for i in range(self._max_index + 1) if i != preferred_index)

        for index in indices:
            cap = self._try_open_index(index)
            if cap is None:
                continue
            with self._lock:
                self._cap = cap
                self._active_index = index
                self._last_open_failure_at = None
            return

        with self._lock:
            self._cap = None
            self._active_index = None
            self._active_backend = None
            self._last_open_failure_at = time.monotonic()

    def _try_open_index(self, index: int) -> Optional[cv2.VideoCapture]:
        for backend in self._backend_candidates():
            cap: Optional[cv2.VideoCapture] = None
            try:
                cap = cv2.VideoCapture(index, backend)
                if cap is None or not cap.isOpened():
                    if cap is not None:
                        cap.release()
                    continue
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.height)
                with self._lock:
                    self._active_backend = backend
                return cap
            except Exception:
                try:
                    if cap is not None:
                        cap.release()
                except Exception:
                    pass
        return None

    def _backend_candidates(self) -> list[int]:
        def add(name: str, acc: list[int]) -> None:
            value = getattr(cv2, name, None)
            if value is None:
                return
            if value not in acc:
                acc.append(value)

        candidates: list[int] = []
        if sys.platform.startswith("win"):
            add("CAP_DSHOW", candidates)
            add("CAP_MSMF", candidates)
        elif sys.platform == "darwin":
            add("CAP_AVFOUNDATION", candidates)
        else:
            add("CAP_V4L2", candidates)
        add("CAP_ANY", candidates)
        return candidates

    def release(self) -> None:
        with self._lock:
            if self._cap is None:
                return
            try:
                self._cap.release()
            finally:
                self._cap = None
                self._active_index = None
                self._active_backend = None

    def read(self) -> tuple[bool, Optional["cv2.Mat"]]:
        with self._lock:
            cap = self._cap
        if cap is None or not cap.isOpened():
            self.open()
            with self._lock:
                cap = self._cap
        if cap is None:
            return False, None
        success, frame = cap.read()
        if not success:
            self.release()
            with self._lock:
                self._last_open_failure_at = time.monotonic()
            return False, None
        return True, frame
