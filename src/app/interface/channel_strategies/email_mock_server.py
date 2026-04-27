from app.core.logger import LoggerConfig


SMTP_DEBUG_SERVER = "debug"


class EmailMockServer:
    def __init__(self, smtp_server: str, smtp_port: int):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = None
        self.password = None
        self.n_try = 0
        self.logger = LoggerConfig.get_logger(self.__module__)

    def simulate_error_until_n_try(self, n_try: int):
        self.n_try = n_try

    def check_try(self):
        if self.n_try > 0:
            self.n_try -= 1
            raise RuntimeError("Error on login")

    def ehlo(self):
        pass

    def starttls(self, context=None):
        pass

    def login(self, username: str, pwd: str):
        self.check_try()
        self.username = username
        self.password = pwd

    def quit(self):
        self.check_try()

    def sendmail(
        self,
        from_addr: str | None = None,
        to_addrs: list[str] | None = None,
        msg: str | None = None,
    ):
        self.check_try()
        self.logger.debug("Mock sent")
