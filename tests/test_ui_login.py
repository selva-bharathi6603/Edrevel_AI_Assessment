"""UI test using Playwright: a real user opens the login page in a browser,
signs in with valid credentials, and lands on their dashboard. This covers
the same user-facing flow as tests/test_login.py, but end-to-end through
real HTML/CSS/JS rendering rather than Flask's test client.
"""

create_user = True


def test_user_can_log_in_through_the_browser(page, live_server):
    page.goto(f"{live_server}/login")

    # The rename to MyTemplate should be visible on the login page.
    assert "MyTemplate" in page.title()

    page.fill('input[name="email"]', "admin@example.com")
    page.fill('input[name="password"]', "supersafepassword")
    page.click('button[type="submit"]')

    # A successful login redirects to the dashboard and shows a flash message.
    page.wait_for_load_state("networkidle")
    assert "Logged in successfully" in page.content()


def test_user_sees_error_on_bad_password(page, live_server):
    page.goto(f"{live_server}/login")

    page.fill('input[name="email"]', "admin@example.com")
    page.fill('input[name="password"]', "wrong-password")
    page.click('button[type="submit"]')

    page.wait_for_load_state("networkidle")
    assert "Invalid email or password" in page.content()
