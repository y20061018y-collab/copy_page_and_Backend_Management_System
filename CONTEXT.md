# 11号电竞 Domain Context

## Core Terms

- **Game**: a supported esports game shown on the public website.
- **GameService**: a service and price entry belonging to one Game.
- **AdminUser**: the administrator allowed to manage games, services, images, and site settings.
- **SiteSetting**: the single site-wide configuration record, including contact details and the studio image.
- **Studio image**: the brand image shown in the public header/footer and replaceable from the admin settings page.
- **Enabled**: visible on the public website and available through public APIs.
- **Disabled**: retained in the database but hidden from the public website.

## Boundaries

The public website reads enabled data through FastAPI. The admin UI writes data through authenticated FastAPI endpoints. PostgreSQL is the source of truth; browser local storage is not used for business data.
