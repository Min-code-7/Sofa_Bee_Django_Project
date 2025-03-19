from django import template
import re

register = template.Library()

@register.filter
def extract_field(value, field_name):
    """
    Extract a field from a formatted address string.
    Usage: {{ value|extract_field:"Full Name:" }}
    """
    pattern = f"{field_name}(.*?)(?:Phone Number:|Delivery Address:|$)"
    match = re.search(pattern, value, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

@register.filter
def strip(value):
    """
    Strip whitespace from the beginning and end of a string.
    Usage: {{ value|strip }}
    """
    return value.strip()
