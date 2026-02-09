from typing import Any

import nh3
from django.db.models import TextField

# nh3 default allowed tags, extended for tiptap editor support.
# Additions beyond nh3 defaults are marked with comments.
ALLOWED_TAGS: set[str] = {
    "a",
    "abbr",
    "acronym",
    "area",
    "article",
    "aside",
    "b",
    "bdi",
    "bdo",
    "blockquote",
    "br",
    "caption",
    "center",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "dd",
    "del",
    "details",
    "dfn",
    "div",
    "dl",
    "dt",
    "em",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "i",
    "iframe",  # tiptap Video extension
    "img",
    "input",  # tiptap TaskList extension (checkboxes)
    "ins",
    "kbd",
    "label",  # tiptap TaskList extension
    "li",
    "map",
    "mark",
    "nav",
    "ol",
    "p",
    "pre",
    "q",
    "rp",
    "rt",
    "rtc",
    "ruby",
    "s",
    "samp",
    "small",
    "span",
    "strike",
    "strong",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "time",
    "tr",
    "tt",
    "u",
    "ul",
    "var",
    "wbr",
}

# nh3 default allowed attributes, extended for tiptap editor support.
# Attributes listed under "*" apply to all tags.
# tag_attribute_values (below) is used for value-restricted attributes like input[type].
ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    "*": {"lang", "style", "title"},
    "a": {"href", "hreflang", "target"},  # target added for tiptap Link
    "bdo": {"dir"},
    "blockquote": {"cite"},
    "code": {"class"},  # tiptap CodeBlock (language-* classes, filtered below)
    "col": {"align", "char", "charoff", "span"},
    "colgroup": {"align", "char", "charoff", "span"},
    "del": {"cite", "datetime"},
    "hr": {"align", "size", "width"},
    "iframe": {"allowfullscreen", "frameborder", "height", "src", "width"},  # tiptap Video
    "img": {"align", "alt", "height", "src", "width"},
    "input": {"checked", "disabled"},  # tiptap TaskList (type restricted via tag_attribute_values)
    "ins": {"cite", "datetime"},
    "ol": {"start"},
    "q": {"cite"},
    "table": {"align", "char", "charoff", "summary"},
    "tbody": {"align", "char", "charoff"},
    "td": {"align", "char", "charoff", "colspan", "headers", "rowspan"},
    "tfoot": {"align", "char", "charoff"},
    "th": {"align", "char", "charoff", "colspan", "headers", "rowspan", "scope"},
    "thead": {"align", "char", "charoff"},
    "tr": {"align", "char", "charoff"},
}

# Only allow checkbox type for input elements (tiptap TaskList).
TAG_ATTRIBUTE_VALUES: dict[str, dict[str, set[str]]] = {
    "input": {"type": {"checkbox"}},
}

# Allow all data-* attributes. Tiptap uses these extensively:
# data-type (TaskList), data-checked (TaskItem), data-color (Highlight),
# data-youtube-video (Video), etc.
GENERIC_ATTRIBUTE_PREFIXES: set[str] = {"data-"}

# CSS properties used by tiptap extensions. Only these are kept in style
# attributes; all others (position, display, z-index, etc.) are stripped.
ALLOWED_CSS_PROPERTIES: set[str] = {
    "background-color",  # Highlight
    "color",  # Color
    "font-family",  # FontFamily
    "font-size",  # FontSize
    "margin-left",  # Indent
    "min-width",  # Table column sizing
    "text-align",  # TextAlign
    "width",  # Table column sizing
}


_ALLOWED_IFRAME_SRC_PREFIXES: tuple[str, ...] = (
    "https://www.youtube.com/",
    "https://www.youtube-nocookie.com/",
    "https://player.vimeo.com/",
)


def _attribute_filter(tag: str, attribute: str, value: str) -> str | None:
    """Filter attribute values after nh3's allowlist check.

    - Restricts code[class] to only language-* values (for CodeBlock syntax
      highlighting) while rejecting arbitrary class names.
    - Restricts iframe[src] to known video embed domains only.
    """
    if tag == "code" and attribute == "class":
        classes = " ".join(c for c in value.split() if c.startswith("language-"))
        return classes if classes else None
    if tag == "iframe" and attribute == "src":
        if not value.startswith(_ALLOWED_IFRAME_SRC_PREFIXES):
            return None
    return value


_cleaner = nh3.Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRIBUTES,
    attribute_filter=_attribute_filter,
    strip_comments=True,
    link_rel="noopener noreferrer",
    generic_attribute_prefixes=GENERIC_ATTRIBUTE_PREFIXES,
    tag_attribute_values=TAG_ATTRIBUTE_VALUES,
    url_schemes=nh3.ALLOWED_URL_SCHEMES,
    filter_style_properties=ALLOWED_CSS_PROPERTIES,
)


class SanitizedHtmlField(TextField):
    def to_python(self, value: Any) -> str | None:
        if value := super().to_python(value):
            value = _cleaner.clean(value)
        return value
