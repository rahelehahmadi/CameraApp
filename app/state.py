from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class AppState:
    stream_on: bool = True
    grey_on: bool = False
    negative_on: bool = False
    face_only_on: bool = False
    _capture_requested: bool = False
    _lock: Lock = field(default_factory=Lock, repr=False)

    def snapshot(self) -> dict[str, bool]:
        with self._lock:
            return {
                "stream_on": self.stream_on,
                "grey_on": self.grey_on,
                "negative_on": self.negative_on,
                "face_only_on": self.face_only_on,
            }

    def toggle_stream(self) -> bool:
        with self._lock:
            self.stream_on = not self.stream_on
            return self.stream_on

    def toggle_grey(self) -> bool:
        with self._lock:
            self.grey_on = not self.grey_on
            return self.grey_on

    def toggle_negative(self) -> bool:
        with self._lock:
            self.negative_on = not self.negative_on
            return self.negative_on

    def toggle_face_only(self) -> bool:
        with self._lock:
            self.face_only_on = not self.face_only_on
            return self.face_only_on

    def request_capture(self) -> None:
        with self._lock:
            self._capture_requested = True

    def consume_capture_request(self) -> bool:
        with self._lock:
            requested = self._capture_requested
            self._capture_requested = False
            return requested

