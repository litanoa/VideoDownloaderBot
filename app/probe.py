import json
import subprocess
from typing import Any, Dict


def parse_ffprobe_json(text: str) -> Dict[str, Any]:
    """Parse `ffprobe -of json` output into {"width", "height", "duration"}.

    Reads values by key (streams[0].width/height, format.duration) instead of
    positional token parsing, so duplicated stream sections (e.g. MPEG-TS /
    HLS-remuxed files emit the stream info twice) can't shift a later field
    into the wrong slot. Any missing/invalid field is simply omitted.
    """
    result: Dict[str, Any] = {}

    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return result

    streams = data.get("streams") or []
    if streams:
        stream = streams[0]
        try:
            width, height = int(stream["width"]), int(stream["height"])
            if width > 0 and height > 0:
                result["width"] = width
                result["height"] = height
        except (KeyError, TypeError, ValueError):
            pass

    fmt = data.get("format") or {}
    try:
        result["duration"] = int(float(fmt["duration"]))
    except (KeyError, TypeError, ValueError):
        pass

    return result


def probe_video_dimensions(file_path: str) -> Dict[str, Any]:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "json", file_path],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception:
        return {}

    return parse_ffprobe_json(out)
