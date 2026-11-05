"""Serves one version of the site, or the resource, on Cloudflare Python Workers."""

import os

from version import APP, RESOURCE_URL

os.environ["LEGIBLE_RESOURCE_BASE_URL"] = RESOURCE_URL
os.environ["LEGIBLE_LOG_DIR"] = "/tmp/legible-logs"
os.environ["LEGIBLE_LOG_STDOUT"] = "1"

if APP == "resource":
    from demo_resource.app import app
else:
    from demo_site.app import create_app

    app = create_app(APP)


@app.middleware("http")
async def keep_out_of_search(request, call_next):
    """These are mock businesses, so real people shouldn't find them through search."""
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex"
    return response


from workers import asgi  # noqa: E402

Default = asgi.entrypoint(app)
