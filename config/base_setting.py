

SERVER_PORT = 5000
DEBUG = False
SQLALCHEMY_ECHO = False
AUTH_COOKIE_NAME = "food"

IGNORE_URLS = {
    "^/user/login",
    "^/face/face_login",
    "^/face/face_register"
}

IGNORE_CHECK_LOGIN_URLS = {
    "^/static",
    "^/favicon.ico"
}

PAGE_SIZE = 50
PAGE_DISPLAY = 10