
class JWTConfig:
    SECRET = ""
    ALGORITHM = "HS256"

    @classmethod
    def set_secret(cls, secret: str):
        cls.SECRET = secret
