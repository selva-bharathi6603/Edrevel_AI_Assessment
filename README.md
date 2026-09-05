[![MyTemplate](https://user-images.githubusercontent.com/882381/45938197-49cfb880-bf7c-11e8-91ea-94fffd9d054a.png)](https://github.com/sumukh/ignite)

# MyTemplate for Flask [![MyTemplate CI](https://github.com/selva-bharathi6603/Edrevel_AI_Assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/selva-bharathi6603/Edrevel_AI_Assessment/actions/workflows/ci.yml)

## Live Demo

🔗 **http://mytemplate-env.eba-bmduu7pa.ap-south-1.elasticbeanstalk.com**

See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment details, architecture, and known limitations.

MyTemplate is a scaffold for starting new SaaS applications built using Python and Flask. It is renamed and
customized from the open-source [Ignite](https://github.com/sumukh/ignite) starter template as part of a
DevOps/QA candidate assessment, and takes care of the boilerplate code (User Registration, OAuth, Teams,
Billing) so you can focus on building the application itself.

## What changed from the Ignite starter

This repo was rebranded from **Ignite** to **MyTemplate** and had a repeatable quality pipeline added
on top:

- All user-facing branding (page titles, logos, footer, emails, static asset paths) renamed to MyTemplate.
- Fixed a real Flask-Caching 2.x compatibility bug that stopped the app from booting (`settings.py` used
  deprecated cache-type strings).
- Added new backend tests (`tests/test_branding_and_signup.py`) and a Playwright UI test
  (`tests/test_ui_login.py`) covering a real login flow end-to-end in a browser.
- Added Ruff (linting), Bandit (security scanning), and pytest coverage/JUnit reporting, all wired into
  the `Makefile` and a GitHub Actions workflow.

## Setup

Usage of Python 3.12 is required. It can be installed [on Python.org](https://www.python.org/downloads/)

```
git clone https://github.com/selva-bharathi6603/Edrevel_AI_Assessment.git
cd Edrevel_AI_Assessment
make env          # creates ./env virtualenv and installs runtime deps
```

## Running the app locally

```
. env/bin/activate
./manage.py resetdb          # creates and seeds the SQLite dev database
FLASK_APP=manage flask --debug run
```

Then open http://localhost:5000 in a browser. A seeded login is available at
`admin@example.com` / `supersafepassword` once you've run `resetdb`.

## Running the quality pipeline

Install the extra dev/CI tooling once (Ruff, Bandit, Playwright + its browser):

```
. env/bin/activate
make deps-dev
```

Then, after making a commit, simulate the CI pipeline locally with a single command:

```
make ci
```

This runs, in order: **Ruff lint → Bandit security scan → pytest backend tests with coverage**, and
writes every report to `./reports/`. Individual pieces can also be run on their own:

| Command            | What it does                                                      |
| ------------------- | ------------------------------------------------------------------ |
| `make lint`         | Ruff static analysis → `reports/lint/ruff-report.{txt,json}`       |
| `make security`     | Bandit security scan → `reports/security/bandit-report.{txt,json}` |
| `make test-unit`    | pytest backend tests, coverage + JUnit XML → `reports/junit/`, `reports/coverage/` |
| `make test-ui`      | Playwright UI tests against a real running instance of the app     |
| `make test`         | `test-unit` + `test-ui`                                            |
| `make ci`           | `lint` + `security` + `test-unit` (the full local pipeline)        |

### Where to find the reports

After running `make ci` or `make test`, look under `./reports/`:

```
reports/
├── junit/pytest-results.xml          # unit test report (JUnit XML)
├── junit/playwright-results.xml      # UI test report (only after make test-ui)
├── coverage/coverage.xml             # coverage report (XML)
├── coverage/html/index.html          # coverage report (HTML, open in a browser)
├── lint/ruff-report.txt              # static analysis report (human-readable)
├── lint/ruff-report.json             # static analysis report (machine-readable)
├── security/bandit-report.txt        # security report (human-readable)
└── security/bandit-report.json       # security report (machine-readable)
```

These are also uploaded automatically as a downloadable artifact on every GitHub Actions run — see the
**Actions** tab on this repo, open a run, and check "Artifacts" at the bottom of the summary page.

## Running tests only

```
APPNAME_ENV=test python -m pytest                 # everything (backend + coverage)
APPNAME_ENV=test python -m pytest tests/test_ui_login.py   # just the Playwright UI test
```



## Features

| Features                              | Status | Details                                                                |
| -------------------------------------- | ------ | ------------------------------------------------------------------------ |
| User Authentication                    | ✅     | User Login, Registration, Forgot Password, Email Confirmation            |
| OAuth Login                            | ✅     | Login or Register with Google, Twitter, Facebook, etc.                   |
| Teams/Groups                           | ✅     | Multi user teams & groups (with Invite Emails)                           |
| User Export & Deletion Request         | ✅     | Allows users to export their data (for GDPR compliance)                  |
| API                                    | ✅     | API (with user tokens) users to access data                              |
| Stripe Product Checkout                | ✅     | One time item purchases with credit cards and receipts (using Stripe)    |
| Heroku/Docker Deployment               | ✅     | Deployment instructions for some platforms. Works on AWS & Google Cloud  |
| Send Emails                            | ✅     | Send email notifications from the application                           |
| Admin Dashboard                        | ✅     | Admin dashboard to edit data                                             |
| File Uploads                           | ✅     | File uploads to cloud storage providers                                  |
| Automated Test Suite (pytest + Playwright) | ✅ | Backend + UI tests, coverage, linting, and security scanning wired into CI |

## AI Agent Guide

If you are using an AI coding agent, start with:

- `AGENTS.md` for repo-specific workflow and architecture guidance
- `documentation/AGENT_QUICKSTART.md` for copy-paste setup/test commands
- `make agent-setup`, `make agent-smoke`, and `make agent-test` for standard agent checks

### Local Secrets

To configure OAuth login and Stripe billing in development, you will need to set some environment variables. See `.env.local.sample` for an example.

```bash
cp .env.local.sample .env.local
# Edit .env.local with your Stripe & Google test keys
source .env.local
FLASK_APP=manage flask --debug run
```

## Deployment

MyTemplate is not tied to a specific platform for deployment; it works well on [Heroku](http://heroku.com) and [Dokku](http://dokku.viewdocs.io/dokku/) with minimal configuration, and is also designed to work on other cloud providers such as AWS, Google Cloud, and DigitalOcean.

Documentation is currently provided for installations on Dokku.

## Stripe Webhooks Locally

- Install the [Stripe CLI](https://stripe.com/docs/stripe-cli)
- Login to the Stripe CLI (`stripe login`)
- Run `stripe listen --forward-to localhost:5000/webhooks/stripe`
- Use the webhook secret and configure your app to use it (`export STRIPE_WEBHOOK_SECRET=whsec_...`)
- To replay an event in a separate console: `stripe events resend evt_XYZ`

## License

MyTemplate is built on the [Ignite](https://github.com/sumukh/ignite) starter template, which is a
commercial product. For details on the underlying license terms, see LICENSE.md and
[the Ignite website](https://ignite.sumukh.me).

## Credits

Design elements from [tabler](https://github.com/tabler/tabler) & Bootstrap 4.

Built off of [Flask Foundation](https://jackstouffer.github.io/Flask-Foundation/) and the [bootstrapy project](https://github.com/kirang89/bootstrapy), rebranded from [Ignite](https://github.com/sumukh/ignite) by Sumukh.

