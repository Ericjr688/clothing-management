# clothing-management

**Repository Description:**
A Django-based web application for managing a clothing library, allowing patrons to browse, request, and borrow items, while librarians can curate collections, approve requests, and manage inventory. Deployed on Heroku with CI/CD workflows on GitHub.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Setup & Installation](#setup--installation)
* [Deployment](#deployment)
* [Usage](#usage)
* [Role & Contributions](#role--contributions)
* [Team & Credits](#team--credits)
* [License](#license)

---

## Project Overview

This project implements a digital clothing library for UVA students and staff. Patrons can browse items, manage favorites, join public or private collections (with approval workflow), and request to borrow items. Librarians oversee inventory, curate collections, review borrow requests, and maintain the system.

---

## Features

* **Collections Management**: Create, edit, and delete public or private collections; users can request access.
* **Borrow Requests**: Patrons submit borrow requests; librarians approve/deny; once approved, other requests are auto‑denied.
* **Search & Filtering**: Full‑text and tag‑based search across items.
* **Favorites & Reviews**: Users can like and review items with star ratings.
* **Item Gallery**: Multiple images per item; librarians upload/delete, all users can view.
* **User Roles**: Patron and librarian roles with distinct permissions.
* **Responsive UI**: Bootstrap‑based layout with cards, modals, and accessible forms.

---

## Tech Stack

* **Framework**: Django 5.1
* **Frontend**: Bootstrap 5, django‑bootstrap5
* **Database**: PostgreSQL (via `psycopg2-binary`), SQLite for local development
* **Storage**: AWS S3 (via `django-storages`)
* **CI/CD**: GitHub Actions, Heroku Deployments
* **Others**: `requests`, `boto3`, `gunicorn`, `whitenoise`

---

## Setup & Installation

1. **Clone the repo:**

   ```bash
   git clone https://github.com/your-org/uvalib-clothing.git
   cd uvalib-clothing
   ```

2. **Create a virtual environment & install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in secrets (DATABASE\_URL, AWS credentials, SECRET\_KEY, etc.)

4. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (librarian):**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run locally:**

   ```bash
   python manage.py runserver
   ```

---

## Deployment

This app is deployed to Heroku using a GitHub Actions workflow:

* On each push to `main`, CI runs tests and static checks.
* On successful CI, the build is released to Heroku automatically.
* Database migrations run during deployment.

* Remember to run `heroku run python manage.py migrate` if manual migrations are needed.

---

## Usage

* **Librarian Dashboard:** Manage items, collections, borrow requests, and users.
* **Patron Dashboard:** Browse items/collections, request access, submit borrow requests, and leave reviews.
* **Search:** Use the search bar on the navbar to filter items by keywords or tags.

---

## Role & Contributions

**My Role:** Full‑stack developer focusing on:

* **Heroku Deployment & CI/CD**: Configured GitHub Actions for automated testing and Heroku releases.
* **Collections & Permissions**: Built public/private collection features, access request flows, and UI cards.
* **Borrow Requests**: Designed and implemented borrow request models, views, and approval workflows.
* **GitHub Workflow**: Established branching strategy, pull request reviews, and issue templates.
* **Front‑end Enhancements**: Improved item and collection cards with Bootstrap styling, tooltips, and responsive layouts.

---

## Team & Credits

* **Scrum Master**: Caroline Xu
* **Devops Manager**: Eric Owuraku Asare, *Me*
* **Testing Manager**: Brian Sounevongsa
* **QA & Testing**: Sarah Warren

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
