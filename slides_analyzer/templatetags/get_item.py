from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), '')

@register.filter
def letter_to_option(letter, options):
    """Convert a letter (A, B, C, D) to its corresponding option text"""
    if not letter or not options:
        return ''
    try:
        # Convert letter to index (A=0, B=1, C=2, D=3)
        index = ord(letter.upper()) - ord('A')
        if 0 <= index < len(options):
            return options[index]
        return ''
    except (TypeError, IndexError):
        return '' 