class JWTConfig:
    SECRET = ""
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @classmethod
    def set_secret(cls, secret: str):
        cls.SECRET = secret

    @classmethod
    def set_expire_minutes(cls, expire_minutes: int):
        cls.ACCESS_TOKEN_EXPIRE_MINUTES = expire_minutes
