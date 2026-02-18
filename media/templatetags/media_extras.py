from django import template

register = template.Library()


@register.filter
def rating_stars(value):
    if value is None:
        return ""
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return ""

    stars = round((max(0, min(10, numeric)) / 10) * 5)
    return "★" * stars + "☆" * (5 - stars)
