from django import template

import datetime

register = template.Library()

def delta(value):
    td = datetime.timedelta(seconds=value)

    return str(td)

register.filter('delta', delta)
