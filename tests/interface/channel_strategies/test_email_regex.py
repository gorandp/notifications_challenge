from app.interface.channel_strategies.email import EMAIL_REGEX


def test_regex():
    valid_emails = [
        "john_smith@test.com",
        "john.smith@test.com",
        "john@test.com",
        "john@test.com.ar",
        "john123@test.com",
        "john123.asd@test.com",
        "john-123.asd@test.com",
    ]
    for e in valid_emails:
        assert EMAIL_REGEX.match(e) is not None
    not_valid_emails = [
        "johnsmith",
        "john\\smith@test.com",
        "john#~smith@test.com",
    ]
    for e in not_valid_emails:
        assert EMAIL_REGEX.match(e) is None
