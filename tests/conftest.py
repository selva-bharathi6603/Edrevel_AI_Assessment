import os
import socket
import threading
import time

import pytest
import requests

# ProdConfig reads DATABASE_URL at import time. Ensure tests always have a valid URL.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from appname import create_app
from appname.models import db
from appname.models.user import User


@pytest.fixture()
def testapp(request):
    app = create_app('appname.settings.TestConfig')
    client = app.test_client()

    db.app = app
    app_ctx = app.app_context()
    app_ctx.push()
    db.create_all()

    if getattr(request.module, "create_user", True):
        admin = User('admin@example.com', 'supersafepassword', admin=True)
        user = User('user@example.com', 'safepassword')
        db.session.add_all([admin, user])
        db.session.commit()

    def teardown():
        db.session.remove()
        db.drop_all()
        app_ctx.pop()

    request.addfinalizer(teardown)

    return client


def _get_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture()
def live_server(request):
    """Boots the real Flask app on a background thread with a real TCP port
    so Playwright can drive it with an actual browser, the same way a user
    would. Used by the UI tests (tests/test_ui_login.py).
    """
    app = create_app("appname.settings.TestConfig")
    port = _get_free_port()
    base_url = f"http://127.0.0.1:{port}"

    db.app = app
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    if getattr(request.module, "create_user", True):
        admin = User("admin@example.com", "supersafepassword", admin=True)
        user = User("user@example.com", "safepassword")
        db.session.add_all([admin, user])
        db.session.commit()

    server_thread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, use_reloader=False),
        daemon=True,
    )
    server_thread.start()

    for _ in range(50):
        try:
            requests.get(base_url, timeout=0.5)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    else:
        raise RuntimeError("Live test server did not start in time")

    yield base_url

    db.session.remove()
    db.drop_all()
    ctx.pop()
