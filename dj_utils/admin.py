from datetime import datetime
from django.contrib import admin
from django.http import HttpResponseRedirect


class ParentModelAdmin(admin.ModelAdmin):

    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',  # jquery
        )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            res = super().changeform_view(request, object_id, form_url, extra_context)
            return res
        except Exception as e:
            return HttpResponseRedirect(request.path)

    def changelist_view(self, request, extra_context=""):
        response = super().changelist_view(request, extra_context)
        group_id = request.GET.get('group_id', None)
        if group_id:
            extra_context = {
                'group_id': group_id,
            }
            response.context_data.update(extra_context)
        return response

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if obj.pk:
            obj.updated_by_id = obj.user.id
            obj.updated_at = datetime.now()
        else:
            obj.created_by_id = obj.user.id
            obj.created_at = datetime.now()
        super().save_model(request, obj, form, change)
