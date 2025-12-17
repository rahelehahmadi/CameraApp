from __future__ import annotations

import argparse
import sys

import cv2


def backend_candidates() -> list[tuple[str, int]]:
    def add(name: str, acc: list[tuple[str, int]]) -> None:
        value = getattr(cv2, name, None)
        if value is None:
            return
        if any(v == value for _, v in acc):
            return
        acc.append((name, value))

    candidates: list[tuple[str, int]] = []
    if sys.platform.startswith("win"):
        add("CAP_DSHOW", candidates)
        add("CAP_MSMF", candidates)
    elif sys.platform == "darwin":
        add("CAP_AVFOUNDATION", candidates)
    else:
        add("CAP_V4L2", candidates)
    add("CAP_ANY", candidates)
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="List working OpenCV camera indices/backends.")
    parser.add_argument("--max-index", type=int, default=5, help="Max index to probe (default: 5)")
    args = parser.parse_args()

    backends = backend_candidates()
    print("Backends:", ", ".join(name for name, _ in backends))

    found_any = False
    for index in range(max(0, args.max_index) + 1):
        ok = False
        for name, backend in backends:
            cap = None
            try:
                cap = cv2.VideoCapture(index, backend)
                if cap is None or not cap.isOpened():
                    continue
                ret, frame = cap.read()
                shape = getattr(frame, "shape", None) if ret else None
                print(f"OK: index={index} backend={name} frame_shape={shape}")
                ok = True
                found_any = True
                break
            except Exception as e:
                print(f"ERR: index={index} backend={name} error={e}")
            finally:
                try:
                    if cap is not None:
                        cap.release()
                except Exception:
                    pass
        if not ok:
            print(f"NO: index={index}")

    if not found_any:
        print("\nNo camera could be opened. If you're on Windows, check:")
        print("- Settings > Privacy & security > Camera (desktop apps allowed)")
        print("- Another app isn't using the camera (Teams/Zoom/etc)")
        print("- Device Manager driver status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

