from ipa.datetime import parse_datetime


def test_parse_datetime():
    dt = parse_datetime("2023-01-01 12:00:00")
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 12
    assert dt.minute == 0
    assert dt.second == 0
