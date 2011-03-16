from django import template

register = template.Library()

def commis_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': False,
        'show_save_and_add_another': False,
        'show_save_and_continue': not is_popup and context['has_change_permission'] and change,
        'is_popup': is_popup,
        'show_save': True
    }
commis_submit_row = register.inclusion_tag('admin/submit_line.html', takes_context=True)(commis_submit_row)
