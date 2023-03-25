from django import template
register = template.Library()

@register.filter
def get(indexable, i):

    if i == "test_type":
        return indexable[0]
    elif i == "bar_graph":
        return indexable[1]
    elif i == "line_graph":
        return indexable[2]
    elif i == "prev_val":
        return indexable[3]
    elif i == "latest_val":
        return indexable[4]
    elif i == "change":
        return indexable[5]

    return indexable[i]