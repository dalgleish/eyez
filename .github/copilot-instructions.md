<!-- Copilot instructions for the Eyez repository. Keep this file short and focused on project-specific patterns. -->
# Eyez — Agent guidance

This repo controls a small Raspberry Pi-based thermal "eye" using a Seeed MLX90640 thermal camera and two hobby servos via pigpio. The goal of an agent working on this repo is to be immediately productive with features, bugfixes, and hardware-facing experiments.

Key facts (big picture)
- Thermal sensor: `seeed_mlx9064x.grove_mxl90640()` provides 32x24 frames (768 values). See `scanner4.py`, `scanner45.py`, `scanner5.py` for examples.
- Actuation: Two servos use GPIO PWM via the `pigpio` library (pins 18 and 12 in scripts). Servos are controlled by mapping a detected column (0..31) to a precomputed pulse-width table (`quadrants`).
- Main flow: read frame -> preprocess (trim/normalize/threshold or diff) -> detect target column -> map to pulse width -> set servo pulse width -> optionally clear PWM.

Entrypoints and workflows
- Primary runtime used in README: `scanner4.py`. On a Pi the canonical run steps are:
  - start pigpio daemon: `sudo killall pigpiod; sudo pigpiod`
  - activate virtualenv and install deps from `requirements.txt`
  - run in background: `nohup python3 -u scanner4.py >> scanner4.log 2>&1 &`
- There are variants: `scanner45.py` (difference-based detection), `scanner5.py` (class-based refactor with smoothing and threshold compare). Use the file that matches the change you intend to make.

Project-specific conventions and patterns
- Frames are 32x24 and often normalized with OpenCV to 0..255 for debugging/video (`cv2.normalize` + `np.uint8`).
- Many scripts write debug frames to `frames/` and then stitch with `create_video()`; removing or reusing this folder is expected before runs (`clear_frames_directory()` is called in main).
- Servo mapping: instead of computing pulse widths at runtime, scripts use precomputed lists: `[60 * i + 600 for i in range(32)]`. Keep this mapping when changing the servo logic unless you update all scripts.
- Error resilience: hardware reads often wrap `mlx.getFrame(frame)` in try/except and continue on error. Follow this pattern to avoid blocking the main loop.

Debugging and testing notes
- To reproduce runtime behavior, run on a Raspberry Pi or mock `seeed_mlx9064x` and `pigpio` (unit tests should mock these imports). The `requirements.txt` lists hardware-only packages.
- Logs: `scanner4.log` is used in README/run scripts. `frames/` images show intermediate masks and are used to generate `output_video.avi`.
- Quick checks: look for `print()` usage in scripts for runtime telemetry (detected_column, target_column, FPS output).

Files to inspect for examples
- `scanner4.py` — main script referenced in README; uses background model + diff -> contour -> center column
- `scanner45.py` — simpler diff-based column detection (argmax over column sums)
- `scanner5.py` — more structured, class-based implementation with smoothing and threshold mask
- `run_eyez.sh` and `README.md` — canonical run steps for the Pi
- `requirements.txt` — hardware dependencies; tests must mock these

Actionable examples for edits
- Add a new detection method: copy `scanner5.py` structure (class Eyez) and replace `detect_person()` while preserving `read_frame()`/`move_servos()` and safety try/except around `mlx.getFrame()`.
- Add unit tests: create tests that import `Eyez` from `scanner5.py` and monkeypatch `seeed_mlx9064x.grove_mxl90640` and `pigpio.pi` objects.

Edge cases to watch
- Scripts assume `frames/` exists; ensure code creates it or checks before writing.
- `pigpio` must be running (`pigpiod`) or `pigpio.pi()` will fail — tests should provide a fake object.
- Thermal values may be None or malformed on read errors — scripts swallow exceptions; preserve that defensive behavior.

If anything here is unclear or you'd like more detail (tests, mocks, CI guidance, or a runnable emulator), tell me what area to expand and I will update this file.
