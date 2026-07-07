import json

from app.probe import parse_ffprobe_json


def test_normal_json_returns_dims_and_duration():
    text = json.dumps({
        "streams": [{"width": 1080, "height": 1920}],
        "format": {"duration": "12.345000"},
    })
    assert parse_ffprobe_json(text) == {"width": 1080, "height": 1920, "duration": 12}


def test_duplicated_stream_section_does_not_corrupt_duration():
    # MPEG-TS / HLS-remuxed files make ffprobe emit the stream twice.
    # With key-based JSON parsing this must not shift duration into a
    # duplicated width/height value.
    text = json.dumps({
        "streams": [
            {"width": 352, "height": 288},
            {"width": 352, "height": 288},
        ],
        "format": {"duration": "1.000000"},
    })
    assert parse_ffprobe_json(text) == {"width": 352, "height": 288, "duration": 1}


def test_missing_streams_omits_dims():
    text = json.dumps({"format": {"duration": "5.0"}})
    assert parse_ffprobe_json(text) == {"duration": 5}


def test_empty_streams_list_omits_dims():
    text = json.dumps({"streams": [], "format": {"duration": "5.0"}})
    assert parse_ffprobe_json(text) == {"duration": 5}


def test_missing_format_omits_duration():
    text = json.dumps({"streams": [{"width": 640, "height": 480}]})
    assert parse_ffprobe_json(text) == {"width": 640, "height": 480}


def test_zero_or_negative_dims_are_excluded():
    text = json.dumps({
        "streams": [{"width": 0, "height": 0}],
        "format": {"duration": "3.0"},
    })
    assert parse_ffprobe_json(text) == {"duration": 3}


def test_non_numeric_duration_is_ignored():
    text = json.dumps({
        "streams": [{"width": 640, "height": 480}],
        "format": {"duration": "N/A"},
    })
    assert parse_ffprobe_json(text) == {"width": 640, "height": 480}


def test_invalid_json_returns_empty_dict():
    assert parse_ffprobe_json("not json at all") == {}


def test_empty_string_returns_empty_dict():
    assert parse_ffprobe_json("") == {}
