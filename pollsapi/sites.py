from django.contrib.admin.sites import AdminSite as BaseAdminSite
# from django.contrib.admin import AdminSite as BaseAdminSite


class AdminSite(BaseAdminSite):

    def _build_app_dict(self, request, label=None):
        res = super(AdminSite, self)._build_app_dict(request, label)
        res.update({'new_attr': 1})
        return res

    def get_app_list(self, request):
        res = super(AdminSite, self).get_app_list(request)
        res.update({'new_attr': 1})
        return res