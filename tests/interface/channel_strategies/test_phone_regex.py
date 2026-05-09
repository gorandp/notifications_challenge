from app.interface.channel_strategies.sms import PHONE_NUMBER_REGEX


def test_regex():
    valid_phones = [
        "54_9_3400123456",
    ]
    for p in valid_phones:
        assert PHONE_NUMBER_REGEX.match(p) is not None
    invalid_phones = [
        "54_99_3400123456",
        "54_9_34001234567",
    ]
    for p in invalid_phones:
        assert PHONE_NUMBER_REGEX.match(p) is None
