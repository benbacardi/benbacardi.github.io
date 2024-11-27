AUTHOR = "Ben Cardy"
SITENAME = "Ben Cardy"
SITEURL = ""

PATH = "content"

TIMEZONE = "Europe/London"

DEFAULT_LANG = "en"

FEED_ATOM = "feed.xml"

DEFAULT_PAGINATION = 10

STATIC_PATHS = ["assets"]

THEME = "theme"
THEME_STATIC_DIR = ""

ARTICLE_URL = "/{date:%Y}/{date:%m}/{date:%d}/{slug}/"
ARTICLE_SAVE_AS = "{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html"

PAGE_URL = "/{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"
CATEGORY_URL = "/category/{slug}/"
CATEGORY_SAVE_AS = "/category/{slug}/index.html"
TAG_URL = "/tag/{slug}/"
TAG_SAVE_AS = "/tag/{slug}/index.html"

ARCHIVES_URL = "/archive/"
ARCHIVES_SAVE_AS = "archive/index.html"
CATEGORIES_URL = "/categories/"
CATEGORIES_SAVE_AS = "categories/index.html"
TAGS_URL = "/tags/"
TAGS_SAVE_AS = "tags/index.html"

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.extra": {},
        "markdown.extensions.admonition": {},
        "markdown.extensions.codehilite": {
            "css_class": "highlight",
        },
        "markdown.extensions.meta": {},
        "smarty": {"smart_angled_quotes": "true"},
        "markdown.extensions.toc": {
            "permalink": "true",
        },
    }
}

import yaml
ALMANAC = yaml.safe_load(open("almanac.yml").read())
