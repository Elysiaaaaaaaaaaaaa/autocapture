"""Camera streaming engine — manages continuous frame capture from
1 Intel RealSense + 2 Orbbec 3D cameras in background threads.

Thread safety
-------------
Each camera has its own ``threading.Lock`` guarding ``_latest_frame``.
Readers (preview / capture) acquire the lock, ``.copy()`` the frame,
then release before doing I/O.  Writers (camera threads) hold the lock
only long enough to replace the reference — never across a
``wait_for_frames()`` call.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

# Allow importing modules from the project root (capture_base, path_config_standard)
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import cv2
import numpy as np

from capture_base import frame_to_bgr_image
from path_config_standard import ORBBEC_C1_SERIAL, WARMUP_FRAMES


# ── camera identifiers ────────────────────────────────────────────────────

REALSENSE = "realsense"
ORBBEC_C1 = "orbbec_c1"
ORBBEC_C2 = "orbbec_c2"
CAMERA_IDS = [REALSENSE, ORBBEC_C1, ORBBEC_C2]

# Number of consecutive ``None`` frames before marking a camera unhealthy
_CONSECUTIVE_NONE_LIMIT = 30


def list_connected_cameras() -> str:
    """Return a human-readable string describing connected cameras.

    Safe to call before starting any streams — this performs a one-shot
    device query and does **not** keep pipelines open.
    """
    lines: list[str] = []

    # ── RealSense ──────────────────────────────────────────────────────
    try:
        import pyrealsense2 as rs
    except ImportError:
        lines.append("RealSense: pyrealsense2 SDK not installed")
    else:
        rs_ctx = rs.context()
        rs_devices = rs_ctx.query_devices()
        lines.append(f"RealSense: {len(rs_devices)} connected")
        for dev in rs_devices:
            name = dev.get_info(rs.camera_info.name)
            sn = dev.get_info(rs.camera_info.serial_number)
            lines.append(f"  - {name}  SN={sn}")

    # ── Orbbec ─────────────────────────────────────────────────────────
    try:
        from pyorbbecsdk import Context  # type: ignore[import-untyped]
    except ImportError:
        lines.append("Orbbec: pyorbbecsdk SDK not installed")
        return "\n".join(lines)

    ob_ctx = Context()
    ob_list = ob_ctx.query_devices()
    lines.append(f"Orbbec: {ob_list.get_count()} connected")
    for i in range(ob_list.get_count()):
        serial = ob_list.get_device_serial_number_by_index(i)
        name = ob_list.get_device_name_by_index(i)
        role = "c1" if serial == ORBBEC_C1_SERIAL else "c2"
        lines.append(f"  - {name}  SN={serial}  -> {role}")

    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────────
# CameraManager
# ────────────────────────────────────────────────────────────────────────────


class CameraManager:
    """Start / stop continuous streams for all three cameras and expose
    the latest frame from each via thread-safe accessors.

    Usage::

        mgr = CameraManager()
        mgr.start_all()
        frame = mgr.get_latest_frame("realsense")  # np.ndarray or None
        mgr.capture_frame("realsense", Path("output.png"))
        mgr.stop_all()
    """

    def __init__(self) -> None:
        self._running = threading.Event()

        # per-camera state
        self._frames: dict[str, np.ndarray | None] = {
            cid: None for cid in CAMERA_IDS
        }
        self._locks: dict[str, threading.Lock] = {
            cid: threading.Lock() for cid in CAMERA_IDS
        }
        self._threads: dict[str, threading.Thread] = {}
        self._pipelines: dict[str, object] = {}  # kept for stop()
        self._healthy: dict[str, bool] = {cid: False for cid in CAMERA_IDS}

    # ── public API ────────────────────────────────────────────────────

    def start_all(self, orbbec_c1_serial: str = ORBBEC_C1_SERIAL) -> dict[str, bool]:
        """Discover cameras and start streaming threads for all three.

        Returns a dict mapping camera id to start-success boolean.
        Cameras that fail to start are left in unhealthy state.
        If the RealSense camera is not found the slot is simply marked
        unhealthy (the lab machine may have it disconnected at times).
        For Orbbec the two expected serial numbers **must** be present;
        otherwise ``RuntimeError`` is raised.
        """
        if self._running.is_set():
            return {cid: self._healthy[cid] for cid in CAMERA_IDS}

        # ── discover Orbbec devices ────────────────────────────────
        from pyorbbecsdk import Context  # type: ignore[import-untyped]

        ob_ctx = Context()
        device_list = ob_ctx.query_devices()
        serials = [
            device_list.get_device_serial_number_by_index(i)
            for i in range(device_list.get_count())
        ]

        if len(serials) != 2:
            raise RuntimeError(
                f"Need exactly 2 Orbbec cameras, found {len(serials)}. "
                f"Serials: {serials}"
            )
        if orbbec_c1_serial not in serials:
            raise RuntimeError(
                f"Orbbec c1 (SN={orbbec_c1_serial}) not found. "
                f"Connected: {serials}"
            )

        c1_serial = orbbec_c1_serial
        c2_serial = [s for s in serials if s != c1_serial][0]

        self._running.set()

        # ── RealSense thread ───────────────────────────────────────
        t_rs = threading.Thread(
            target=self._stream_realsense,
            name="cam-rs",
            daemon=True,
        )
        self._threads[REALSENSE] = t_rs
        t_rs.start()

        # ── Orbbec threads ─────────────────────────────────────────
        t_c1 = threading.Thread(
            target=self._stream_orbbec,
            args=(ORBBEC_C1, c1_serial),
            name="cam-c1",
            daemon=True,
        )
        self._threads[ORBBEC_C1] = t_c1
        t_c1.start()

        t_c2 = threading.Thread(
            target=self._stream_orbbec,
            args=(ORBBEC_C2, c2_serial),
            name="cam-c2",
            daemon=True,
        )
        self._threads[ORBBEC_C2] = t_c2
        t_c2.start()

        # Brief pause so threads have time to reach their warmup loop
        return {cid: True for cid in CAMERA_IDS}

    def stop_all(self) -> None:
        """Signal all camera threads to stop, tear down pipelines, and
        wait for threads to join.

        Safe to call multiple times.
        """
        self._running.clear()

        # Stop RealSense pipeline (unblocks wait_for_frames)
        rs_pipeline = self._pipelines.pop(REALSENSE, None)
        if rs_pipeline is not None:
            try:
                rs_pipeline.stop()  # type: ignore[union-attr]
            except Exception:
                pass

        # Stop Orbbec pipelines (unblocks wait_for_frames)
        for cid in (ORBBEC_C1, ORBBEC_C2):
            pipeline = self._pipelines.pop(cid, None)
            if pipeline is not None:
                try:
                    pipeline.stop()  # type: ignore[union-attr]
                except Exception:
                    pass

        # Join threads
        for cid in CAMERA_IDS:
            t = self._threads.pop(cid, None)
            if t is not None and t.is_alive():
                t.join(timeout=3.0)

        # Reset state
        for cid in CAMERA_IDS:
            with self._locks[cid]:
                self._frames[cid] = None
            self._healthy[cid] = False

    def get_latest_frame(self, camera_id: str) -> np.ndarray | None:
        """Return a **copy** of the most recent frame from *camera_id*.

        Returns ``None`` when no frame has been received yet or the
        camera is unhealthy.
        """
        lock = self._locks.get(camera_id)
        if lock is None:
            return None
        with lock:
            f = self._frames.get(camera_id)
            if f is None:
                return None
            return f.copy()

    def capture_frame(self, camera_id: str, output_path: Path) -> bool:
        """Grab the latest frame from *camera_id* and write it to
        *output_path* as a PNG / BMP / JPG (whatever the extension).

        Returns ``True`` on success, ``False`` if no frame is available.
        Parent directories are created automatically.
        """
        frame = self.get_latest_frame(camera_id)
        if frame is None:
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return bool(cv2.imwrite(str(output_path), frame))

    def capture_all(self, output_paths: dict[str, Path]) -> dict[str, bool]:
        """Convenience wrapper: call :meth:`capture_frame` for every
        entry in *output_paths*.

        Returns a dict mapping camera id to success boolean.
        """
        results: dict[str, bool] = {}
        for cam_id, path in output_paths.items():
            results[cam_id] = self.capture_frame(cam_id, path)
        return results

    def is_healthy(self, camera_id: str) -> bool:
        """Return whether *camera_id* is currently streaming frames."""
        return self._healthy.get(camera_id, False)

    def is_running(self) -> bool:
        """Return whether the camera streams are active."""
        return self._running.is_set()

    @staticmethod
    def get_camera_ids() -> list[str]:
        """Return the list of managed camera identifiers."""
        return list(CAMERA_IDS)

    # ── camera thread functions ─────────────────────────────────────

    def _stream_realsense(self) -> None:
        import pyrealsense2 as rs

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color)

        self._pipelines[REALSENSE] = pipeline

        try:
            try:
                pipeline.start(config)
            except RuntimeError as exc:
                print(f"[camera_manager] RealSense start failed: {exc}")
                return

            # Warmup — let auto-exposure settle
            for _ in range(WARMUP_FRAMES):
                pipeline.wait_for_frames()

            self._healthy[REALSENSE] = True
            consecutive_none = 0

            while self._running.is_set():
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                if color_frame is None:
                    consecutive_none += 1
                    if consecutive_none >= _CONSECUTIVE_NONE_LIMIT:
                        print("[camera_manager] RealSense: too many None frames")
                        self._healthy[REALSENSE] = False
                        break
                    continue
                consecutive_none = 0

                image = np.asanyarray(color_frame.get_data())
                fmt = color_frame.get_profile().format()

                if fmt == rs.format.rgb8:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                elif fmt == rs.format.bgr8:
                    pass
                else:
                    # Try to handle RGBA or unknown formats
                    if len(image.shape) == 3 and image.shape[2] == 4:
                        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

                with self._locks[REALSENSE]:
                    self._frames[REALSENSE] = image

        except RuntimeError:
            # pipeline.stop() called from main thread — expected on shutdown
            pass
        except Exception as exc:
            print(f"[camera_manager] RealSense thread error: {exc}")
        finally:
            self._healthy[REALSENSE] = False
            self._pipelines.pop(REALSENSE, None)
            try:
                pipeline.stop()
            except Exception:
                pass

    def _stream_orbbec(self, camera_id: str, serial: str) -> None:
        from pyorbbecsdk import (  # type: ignore[import-untyped]
            Config,
            Context,
            OBError,
            OBFrameAggregateOutputMode,
            OBSensorType,
            Pipeline,
            VideoStreamProfile,
        )

        # Each Orbbec thread MUST create its own Context
        ctx = Context()
        device_list = ctx.query_devices()

        device = None
        for i in range(device_list.get_count()):
            if device_list.get_device_serial_number_by_index(i) == serial:
                device = device_list.get_device_by_index(i)
                break

        if device is None:
            print(f"[camera_manager] Orbbec {camera_id} (SN={serial}) not found")
            return

        pipeline = Pipeline(device)
        config = Config()
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if profile_list is None:
            print(f"[camera_manager] Orbbec {camera_id}: no color stream profile")
            return

        color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
        config.enable_stream(color_profile)
        config.set_frame_aggregate_output_mode(
            OBFrameAggregateOutputMode.FULL_FRAME_REQUIRE
        )

        self._pipelines[camera_id] = pipeline

        try:
            try:
                pipeline.start(config)
            except OBError as exc:
                print(f"[camera_manager] Orbbec {camera_id} start failed: {exc}")
                return

            # Warmup
            for _ in range(WARMUP_FRAMES):
                pipeline.wait_for_frames(1000)

            self._healthy[camera_id] = True
            consecutive_none = 0

            while self._running.is_set():
                frames = pipeline.wait_for_frames(1000)
                if frames is None:
                    consecutive_none += 1
                    if consecutive_none >= _CONSECUTIVE_NONE_LIMIT:
                        print(
                            f"[camera_manager] Orbbec {camera_id}: "
                            f"too many None frame-sets"
                        )
                        self._healthy[camera_id] = False
                        break
                    continue
                consecutive_none = 0

                color_frame = frames.get_color_frame()
                if color_frame is None:
                    continue

                image = frame_to_bgr_image(color_frame)
                if image is None:
                    continue

                with self._locks[camera_id]:
                    self._frames[camera_id] = image

        except Exception as exc:
            print(f"[camera_manager] Orbbec {camera_id} thread error: {exc}")
        finally:
            self._healthy[camera_id] = False
            self._pipelines.pop(camera_id, None)
            try:
                pipeline.stop()
            except Exception:
                pass


# ── quick smoke-test (run this file directly) ──────────────────────────────
if __name__ == "__main__":
    import time

    print(list_connected_cameras())
    print()

    mgr = CameraManager()
    try:
        results = mgr.start_all()
        print(f"start_all: {results}")

        # Let streams stabilise
        time.sleep(2.0)

        for cid in CAMERA_IDS:
            frame = mgr.get_latest_frame(cid)
            if frame is not None:
                print(f"{cid}: frame {frame.shape}, healthy={mgr.is_healthy(cid)}")
            else:
                print(f"{cid}: no frame yet, healthy={mgr.is_healthy(cid)}")

        # Capture one frame from each
        out_dir = Path(__file__).resolve().parent / "_test_capture"
        paths = {
            REALSENSE: out_dir / "test_realsense.png",
            ORBBEC_C1: out_dir / "test_orbbec_c1.png",
            ORBBEC_C2: out_dir / "test_orbbec_c2.png",
        }
        results = mgr.capture_all(paths)
        print(f"\ncapture_all: {results}")
    finally:
        mgr.stop_all()
        print("stopped.")
