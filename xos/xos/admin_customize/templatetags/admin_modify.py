from django.contrib.admin.templatetags.admin_modify import *
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row
from django.conf import settings
import random
@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    ctx = original_submit_row(context)
    ctx.update({
        'show_save': context.get('show_save', ctx['show_save']),
        'show_save_and_add_another': context.get('show_save_and_add_another', ctx['show_save_and_add_another']),
        'show_save_and_continue': context.get('show_save_and_continue', ctx['show_save_and_continue']),
        'custom_delete_url': context.get("custom_delete_url",None),
        })                                                                  
    return ctx 



@register.simple_tag
def random_str(a):
    a = ["You are now signed out. Thank you and have a great day",
         "Thanks for spending some quality time with the Web site today.",
         "Thanks for using " +settings.XOS_BRANDING_NAME + " to manage your network today.",
         "You have successfully logged out, Thanks for spending some quality time",
         "The "+settings.XOS_BRANDING_NAME +" team is glad that you used our product to get your work done."]
    return a[random.randint(0,4)]