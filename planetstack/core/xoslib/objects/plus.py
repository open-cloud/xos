""" PlusObjectMixin

    Implements fields that are common to all OpenCloud objects. For example,
    stuff related to backend icons.
"""

ICON_URLS = {"success": "/static/admin/img/icon_success.gif",
            "clock": "/static/admin/img/icon_clock.gif",
            "error": "/static/admin/img/icon_error.gif"}



class PlusObjectMixin:
    def getBackendIcon(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")
        return icon_url

    def getBackendHtml(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")

        if tooltip:
            return '<span title="%s"><img src="%s"></span>' % (tooltip, icon_url)
        else:
            return '<img src="%s">' % icon_url


