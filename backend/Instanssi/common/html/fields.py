from typing import Any

import nh3
from django.db.models import TextField

# Allowed HTML tags — only what CKEditor 5 outputs with our plugin set.
TAGS: set[str] = {
    # Inline formatting
    "a",
    "br",
    "code",
    "em",
    "s",
    "span",
    "strong",
    "sub",
    "sup",
    "u",
    # Block elements
    "blockquote",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "p",
    "pre",
    # Lists
    "li",
    "ol",
    "ul",
    # Tables
    "figure",
    "figcaption",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    # Media
    "img",
    "oembed",
}

# Allowed attributes per tag.  The "rel" attribute on <a> is managed by nh3's
# link_rel parameter (default: "noopener noreferrer") and must not be listed here.
ATTRIBUTES: dict[str, set[str]] = {
    "*": {"class", "style"},
    "a": {"href", "target"},
    "img": {"alt", "height", "src", "width"},
    "oembed": {"url"},
    "ol": {"start"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
}

# Only allow safe CSS properties inside style attributes.
STYLE_PROPERTIES: set[str] = {
    "background-color",
    "color",
    "float",
    "font-family",
    "font-size",
    "height",
    "margin",
    "margin-left",
    "margin-right",
    "padding",
    "text-align",
    "width",
}


class SanitizedHtmlField(TextField):
    def to_python(self, value: Any) -> str | None:
        if value := super().to_python(value):
            value = nh3.clean(
                value,
                tags=TAGS,
                attributes=ATTRIBUTES,
                filter_style_properties=STYLE_PROPERTIES,
            )
        return value
