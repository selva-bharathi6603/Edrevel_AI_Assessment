# Deployment Guide — MyTemplate

This document describes how **MyTemplate** (a Flask application forked from the open-source "Ignite" starter template) is deployed to AWS Elastic Beanstalk, along with the issues encountered during deployment and how they were resolved.

## Live Demo

- **URL:** http://mytemplate-env.eba-bmduu7pa.ap-south-1.elasticbeanstalk.com
- **Region:** ap-south-1 (Mumbai)
- **Environment:** MyTemplate-env

## Stack

- **Platform:** Python 3.12 running on Amazon Linux 2023
- **Web server:** gunicorn (sync worker) behind nginx
- **Instance type:** t3.micro (single instance, non-load-balanced)
- **Database:** SQLite (file-based, suitable for demo/assessment purposes)

## Deployment Steps

1. **Initialize the EB CLI** in the project root:
```bash
   eb init -p python-3.12 MyTemplate --region ap-south-1
```

2. **Create the environment** (single instance, no load balancer, to keep within free-tier limits):
```bash
   eb create mytemplate-env --single
```

3. **Deploy updates** after code changes:
```bash
   eb deploy
```

4. **Check status / open the app:**
```bash
   eb status
   eb open
```

## Configuration

Deployment behavior is controlled by `.ebextensions/01-setup.config`, which runs four container commands on every deploy, in order:

| Order | Command             | Purpose                                                        |
|-------|----------------------|------------------------------------------------------------------|
| 00    | `db_cleanup`          | Removes stale/locked SQLite journal files before migration       |
| 01    | `migrate`             | Runs database migrations / demo data reset (`manage.py demo-reset`) |
| 02    | `assets`              | Builds and compiles static assets (webassets)                    |
| 03    | `permissions`         | Fixes file ownership/permissions post-build                      |

## Issues Encountered & Resolutions

During deployment, the following issues were identified and resolved (in chronological order):

1. **Missing/duplicate `DemoConfig`** — Consolidated into a single config class.
2. **`tmp/` directory exclusion** — Added explicit inclusion so the app's temp directory persists across deploys.
3. **Gunicorn port mismatch** — App was configured for port 5000; EB's nginx proxy expects port 8000. Aligned gunicorn's bind port to 8000.
4. **Webassets cache ownership conflict** — Static asset cache directory had incorrect ownership after deploy; fixed via the `03_permissions` container command.
5. **Click command naming** — CLI subcommands used underscores; Click expects hyphens (`demo_reset` → `demo-reset`).
6. **CDN blocking auth pages (403)** — Adjusted CDN/CSP configuration so login/auth pages load required assets.
7. **Duplicate seed data on repeated deploys** — Added `00_db_cleanup` step to clear stale data before migration.
8. **SQLite readonly/journal conflicts** — Caused by leftover `-journal` files from interrupted writes; resolved by the cleanup step and permission fixes.
9. **GitHub Actions mock breakage** — Updated test mocks after dependency bumps (`cryptography`, `requests`, `pytest`, `pytest-cov`) to satisfy Dependabot security alerts.

## Known Limitations

- The sidebar "Dropdown" menu items (Menu Item 1/2/3 in `appname/templates/tabler/_navbar.html`) are placeholder links (`href="#"`) inherited from the Tabler UI template used by Ignite. They are not wired to functional routes, as this was outside the scope of the assessment requirements.
- The app uses SQLite and a single `t3.micro` instance, which is suitable for demo/assessment purposes but not representative of a production-scale deployment (no load balancing, no managed database).

## Monitoring & Troubleshooting

- **Application logs:** `/var/log/web.stdout.log` (gunicorn + app stdout)
- **Deployment engine logs:** `/var/log/eb-engine.log`
- **cfn-init build logs:** `/var/log/cfn-init.log` (shows success/failure of each `.ebextensions` container command)
- **SSH access:** `eb ssh` (requires `eb init` to have been run locally with a configured keypair)

If the EB console's "Request Logs" feature fails to retrieve logs, connect directly via `eb ssh` or EC2 Instance Connect and read the log files above directly from the instance.
