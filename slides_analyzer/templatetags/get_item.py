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

@register.filter
def times(number):
    """Returns a range of numbers from 1 to the given number"""
    try:
        return range(1, int(number) + 1)
    except (ValueError, TypeError):
        return range(0) 