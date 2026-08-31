import pytest

create_user = True


@pytest.mark.usefixtures("testapp")
class TestBrandingAndSignup:
    """Small but meaningful checks that cover a real user-facing flow:
    a visitor lands on the homepage, sees the MyTemplate branding, and can
    reach the signup form from there.
    """

    def test_homepage_shows_mytemplate_branding(self, testapp):
        """The rename from Ignite to MyTemplate should be visible to visitors."""
        rv = testapp.get('/')

        assert rv.status_code == 200
        assert b'<title>MyTemplate</title>' in rv.data

    def test_homepage_links_to_signup(self, testapp):
        """A new visitor should be able to find their way to the signup page."""
        rv = testapp.get('/')

        assert rv.status_code == 200
        assert b'/signup' in rv.data

    def test_signup_page_loads(self, testapp):
        """The signup form itself should render for anonymous visitors."""
        rv = testapp.get('/signup')

        assert rv.status_code == 200
        assert b'email' in rv.data.lower()
