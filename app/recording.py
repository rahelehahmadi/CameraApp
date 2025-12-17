from __future__ import annotations

import datetime as _dt
import time
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Optional

import cv2


class VideoRecorder:
    def __init__(self, output_dir: Path, fps: float = 20.0, fourcc: str = "XVID") -> None:
        self._output_dir = output_dir
        self._fps = fps
        self._fourcc = fourcc
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._writer: Optional[cv2.VideoWriter] = None
        self._latest_frame = None
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._is_recording

    def update_frame(self, frame) -> None:
        with self._lock:
            self._latest_frame = frame

    def start(self, frame_size: tuple[int, int]) -> Path:
        with self._lock:
            if self._is_recording:
                raise RuntimeError("Recorder already started")

            now = _dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            path = self._output_dir / f"vid_{now}.avi"

            fourcc = cv2.VideoWriter_fourcc(*self._fourcc)
            writer = cv2.VideoWriter(str(path), fourcc, self._fps, frame_size)
            if not writer.isOpened():
                raise RuntimeError("Failed to open VideoWriter")

            self._writer = writer
            self._stop_event.clear()
            self._is_recording = True
            self._thread = Thread(target=self._run, name="video-recorder", daemon=True)
            self._thread.start()
            return path

    def stop(self) -> None:
        thread = None
        with self._lock:
            if not self._is_recording:
                return
            self._is_recording = False
            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join(timeout=2.0)

        with self._lock:
            try:
                if self._writer is not None:
                    self._writer.release()
            finally:
                self._writer = None
                self._thread = None
                self._latest_frame = None

    def _run(self) -> None:
        interval = 1.0 / self._fps if self._fps > 0 else 0.05
        while not self._stop_event.is_set():
            writer = None
            frame = None
            with self._lock:
                writer = self._writer
                frame = self._latest_frame
            if writer is not None and frame is not None:
                try:
                    writer.write(frame)
                except Exception:
                    pass
            time.sleep(interval)

