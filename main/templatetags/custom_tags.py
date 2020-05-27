from django import template

register = template.Library()

def add_5_mult_with(value, arg):
    return int(value)+(int(arg)*5)

register.filter('add_5_mult_with', add_5_mult_with)