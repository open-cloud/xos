""" PlusObjectMixin

    Implements fields that are common to all OpenCloud objects. For example,
    stuff related to backend icons.
"""

class PlusObjectMixin:
    def getBackendIcon(self):
        if (self.enacted is not None) and self.enacted >= self.updated or self.backend_status.startswith("1 -"):
            return "/static/admin/img/icon_success.gif"
        else:
            if ((self.backend_status is not None) and self.backend_status.startswith("0 -")) or self.backend_status == "Provisioning in progress" or self.backend_status=="":
                return "/static/admin/img/icon_clock.gif"
            else:
                return "/static/admin/img/icon_error.gif"

    def getBackendHtml(self):
        if (self.enacted is not None) and self.enacted >= self.updated:
            return '<img src="%s">' % self.getBackendIcon()
        else:
            return '<span title="%s"><img src="%s"></span>' % (self.backend_status, self.getBackendIcon())


