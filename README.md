# Vintage Editorial

Vintage Editorial is a Django-powered news and community publishing platform. It presents articles through a newspaper-inspired interface and gives authenticated users a complete reading and publishing workflow: browse and search articles, filter by category, publish rich-text stories, upload article images, comment, bookmark articles, and manage their own work from an editor desk.

The project is built with Django 5, a custom user model, CKEditor, django-crispy-forms, Bootstrap 5, Pillow, WhiteNoise, and Gunicorn. It uses SQLite by default in the checked-in development database, while the settings also support any database URL understood by `dj-database-url`.

## Features

### Reading and discovery

- Public landing page with a newspaper-style editorial presentation.
- Authenticated article index with a featured story and secondary stories.
- Category navigation and category-filtered article lists.
- Search across article titles, rich-text bodies, and author usernames.
- Article detail pages with reading-time estimates, images, and comments.
- Reading list backed by a many-to-many bookmark relationship.
- Responsive templates with a vintage editorial visual system, Bootstrap utilities, custom CSS, loading states, and reading progress indicators.

### Publishing and editorial tools

- Authenticated users can publish articles with a title, CKEditor rich-text body, optional image, and optional category.
- Authors can edit and delete their own articles.
- Staff users can mark an article as featured.
- Saving a featured article automatically unfeatures any previously featured article, so the application maintains one featured article at a time.
- Uploaded article images are converted to JPEG, optimized, and resized to a maximum width of 800 pixels.
- The editor desk summarizes the signed-in user's article count, comment count, latest article, most-commented article, and article distribution by category.

### Accounts

- Custom `accounts.CustomUser` model based on Django's `AbstractUser`.
- Signup with username, required email address, and password confirmation.
- Login, logout confirmation, password change, and password reset flows.
- Optional account fields for age, biography, and profile picture, primarily exposed through the Django admin in the current implementation.
- Django admin support for users, articles, categories, and comments.

## Technology Stack

- Python 3.10 or newer
- Django 5.0.14
- SQLite for the repository's default local database, or another database supported through `DATABASE_URL`
- `django-ckeditor` 6.7.3 for article authoring
- `django-crispy-forms` with `crispy-bootstrap5` for form rendering
- Pillow for image processing
- WhiteNoise for serving compressed static files
- Gunicorn for WSGI deployment
- Bootstrap 5.3 loaded by the base template

The complete pinned dependency list is in [requirements.txt](requirements.txt).

## Project Layout

```text
news/
+-- accounts/                Custom user model, authentication, and account routes
+-- articles/                Article, category, comment, bookmark, and publishing logic
+-- pages/                   Landing, about, and privacy-policy pages
+-- django_project/          Django settings, root URLs, ASGI, and WSGI configuration
+-- templates/               Shared and page-specific Django templates
+-- static/                  Source CSS, JavaScript, and image assets
+-- staticfiles/             Collected static files, including admin and CKEditor assets
+-- media/                   User-uploaded article and profile images
+-- db.sqlite3               Existing local SQLite database
+-- manage.py                Django command-line entry point
+-- Procfile                 Gunicorn deployment command
+-- requirements.txt         Pinned Python dependencies
```

`staticfiles/` and `media/` may contain generated or user-created files. In a fresh deployment, static files should be collected and media storage should be configured deliberately rather than relying on ephemeral local disk.

## Prerequisites

Install the following before starting:

- Python 3.10 or newer
- `pip`
- A virtual environment tool such as `venv`
- Git, if cloning the repository

For local development, SQLite is sufficient. A PostgreSQL driver is included in `requirements.txt` for deployments that provide a PostgreSQL `DATABASE_URL`.

## Local Setup

From the repository root:

### 1. Create and activate a virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

The settings module loads a `.env` file through `environs`, but no `.env` file is committed. At minimum, define the following values in the environment or in a local, untracked `.env` file:

```dotenv
SECRET_KEY=replace-this-with-a-long-random-development-secret
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

`SECRET_KEY` is required and has no code-level default. `DEBUG` defaults to `False` when omitted. `DATABASE_URL` is also required by `env.dj_db_url("DATABASE_URL")`; the SQLite value above points Django at the repository's `db.sqlite3` file.

For a PostgreSQL database, provide a URL in the format accepted by `dj-database-url`, for example:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/vintage_editorial
```

Do not commit real secrets or production database credentials.

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create an administrator

```bash
python manage.py createsuperuser
```

The admin is available at `/admin/`. Staff users can manage content and are the only users who see the `is_featured` field in article create and edit forms.

### 6. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser. The root page is public. Authenticated users are redirected to the article index.

## Application Workflow

1. Visit `/accounts/signup/` and create an account with a username, email, and password.
2. After signup, Django logs the user in and redirects to the article index.
3. Browse the latest content, choose a category, or search by title, body, or author.
4. Open an article to read it, add a comment of up to 140 characters, or toggle its bookmark.
5. Open the editor desk to review personal publishing and engagement statistics.
6. Publish at `/articles/new/`. The title, body, optional image, and optional category are available to regular users; staff users also receive the featured toggle.
7. Use the edit and delete controls on articles authored by the current user.

All article browsing, detail, search, category, editor desk, bookmark, and reading-list views require authentication. Anonymous users can view the landing, about, privacy-policy, login, signup, and password-management entry points.

## URL Reference

### Public pages

| URL | Name | Purpose |
| --- | --- | --- |
| `/` | `home` | Landing page; authenticated users are redirected to the article index |
| `/landing/` | `landing` | Alternate landing-page URL |
| `/about/` | `about` | About page |
| `/privacy-policy/` | `privacy_policy` | Privacy-policy page |

### Accounts

| URL | Name | Purpose |
| --- | --- | --- |
| `/accounts/signup/` | `signup` | Create an account and sign in automatically |
| `/accounts/login/` | `login` | Sign in |
| `/accounts/logout/` | `logout` | Display logout confirmation, then log out on POST |
| `/accounts/password_change/` | `password_change` | Change the current password |
| `/accounts/password_change/done/` | `password_change_done` | Password-change completion page |
| `/accounts/password_reset/` | `password_reset` | Start a password reset |
| `/accounts/password_reset/done/` | `password_reset_done` | Password-reset request completion page |
| `/accounts/password_reset/<uidb64>/<token>/` | `password_reset_confirm` | Set a new password |
| `/accounts/password_reset/complete/` | `password_reset_complete` | Password-reset completion page |

### Articles

| URL | Name | Purpose |
| --- | --- | --- |
| `/articles/` | `article_list` | Authenticated article index |
| `/articles/new/` | `article_new` | Publish an article |
| `/articles/<pk>/` | `article_detail` | Read an article and post comments |
| `/articles/<pk>/edit/` | `article_edit` | Edit an article owned by the current user |
| `/articles/<pk>/delete/` | `article_delete` | Delete an article owned by the current user |
| `/articles/category/<slug>/` | `article_by_category` | Filter articles by category |
| `/articles/search/` | `article_search` | Search with the `q` query parameter |
| `/articles/desk/` | `editor_desk` | View the current user's publishing dashboard |
| `/articles/<pk>/bookmark/` | `article_bookmark` | POST to toggle a bookmark and receive JSON |
| `/articles/reading-list/` | `reading_list` | View bookmarked articles |

Example search URL:

```text
/articles/search/?q=climate
```

The bookmark endpoint expects an authenticated POST request with Django's CSRF protection and returns JSON such as `{"bookmarked": true, "status": "success"}`.

## Data Model

### `CustomUser`

Extends Django's `AbstractUser` with:

- `age`: optional positive integer
- `bio`: optional text
- `profile_picture`: optional image uploaded under `media/profiles/`

Signup currently exposes only `username`, `email`, `password1`, and `password2`. The additional profile fields are available in the custom admin form.

### `Category`

Stores a category name and unique slug. Categories are ordered alphabetically and can be used to filter article lists.

### `Article`

Stores a title, CKEditor `RichTextField` body, creation date, author, optional image, optional category, bookmarks, and the `is_featured` flag. Articles are ordered newest first. Article reading time is estimated at approximately 200 words per minute, with a minimum of one minute.

When an image is saved, Pillow converts it to RGB JPEG, resizes images wider than 800 pixels, and saves with optimization and quality settings suitable for web delivery. Keep this behavior in mind when testing unusual image formats or storage backends.

### `Comment`

Associates a maximum-140-character comment with an article and its author. Comments are deleted with their article and are displayed through the article detail workflow.

## Static and Media Files

Static configuration is defined in [django_project/settings.py](django_project/settings.py):

- `STATIC_URL = "static/"`
- Source directory: `static/`
- Collection directory: `staticfiles/`
- Storage: WhiteNoise's `CompressedManifestStaticFilesStorage`

Run the following before deployment or when rebuilding collected assets:

```bash
python manage.py collectstatic --noinput
```

Uploaded files use:

- `/media/articles/` for article images
- `/media/profiles/` for profile pictures

During development, Django serves media through the root URL configuration. Production deployments should use persistent or object storage for media because local dyno/container filesystems can be ephemeral.

## Testing

Run the Django test suite with:

```bash
python manage.py test
```

The current tests cover custom-user creation, superuser flags, signup rendering and submission, landing-page rendering, anonymous route protection for the article index, and redirecting authenticated visitors from the landing page. The article test module currently contains no substantive tests, so bookmark behavior, comments, publishing permissions, image processing, search, category filtering, and editor-desk calculations should receive additional coverage before a high-risk production release.

## Deployment

The repository includes a [Procfile](Procfile) for Gunicorn:

```text
web: gunicorn django_project.wsgi --log-file -
```

A deployment should provide at least:

```dotenv
SECRET_KEY=<strong-production-secret>
DEBUG=False
DATABASE_URL=<production-database-url>
```

Typical deployment steps are:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn django_project.wsgi --log-file -
```

Before exposing the application publicly, review Django's deployment checklist and configure the following according to the hosting platform:

- Restrict `ALLOWED_HOSTS`; the current settings include `"*"`.
- Configure HTTPS, secure cookies, and proxy settings.
- Replace the console email backend with a real email provider if password reset must send email to users. In the current configuration, reset messages are printed to the application console.
- Provide persistent media storage and backups.
- Confirm `CSRF_TRUSTED_ORIGINS` includes the actual HTTPS domains.
- Keep `DEBUG=False` and rotate any development secret before production.

## Configuration Notes

- The project uses the custom user model `accounts.CustomUser`; use `settings.AUTH_USER_MODEL` or `get_user_model()` in new code and migrations.
- The configured timezone is `Africa/Douala`, while internationalization is enabled and timestamps are stored with timezone support.
- The base template loads Google Fonts and Bootstrap from external CDNs, so those assets require network access unless replaced with local copies.
- CKEditor content is configured to permit a restricted set of text, list, quote, and link elements. Article bodies should still be treated as user-generated content and reviewed accordingly.
- The checked-in SQLite database may contain local development data. For a clean environment, create a new database and run migrations rather than relying on existing rows.

## Useful Management Commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py collectstatic --noinput
python manage.py runserver
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.
