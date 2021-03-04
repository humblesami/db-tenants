from django.contrib import admin
from django.forms import ModelForm
from dj_utils.admin import ParentModelAdmin

from .models import Package, Subscription, Payment, Product


class ProductAdmin(ParentModelAdmin):
    search_fields = ['name']


class PackageAdmin(ParentModelAdmin):
    list_display= ['name']
    search_fields = ['name']
    autocomplete_fields = ['products']


class SubscriptionAdmin(ParentModelAdmin):
    list_display = ['__str__', 'price', 'connection_charges']
    search_fields = ['__str__']
    autocomplete_fields = ['client', 'package']
    readonly_fields = ['expiry_date', 'created_at', 'updated_at', 'created_by', 'updated_by']

    class Media:
        js = (
            '/static/change_form_subscription.js',
        )


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        exclude = []

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super().save(commit=False)
        if commit:
            obj.save()
        return obj

    def clean(self):
        super().clean()
        due_amount = self.cleaned_data.get('due_amount')
        being_paid = self.cleaned_data.get('amount')

        if not being_paid:
            being_paid = 0
        if not due_amount:
            due_amount = 0
        amount_error = 'Give amount must be non zero'# and at least half of due amount='+str(due_amount)
        valid_amount = being_paid and being_paid > 0
        #valid_amount = being_paid and being_paid < due_amount / 2
        if not valid_amount:
            self._errors['amount'] = self.error_class([amount_error])
        return self.cleaned_data


class PaymentAdmin(ParentModelAdmin):
    form = PaymentForm
    add_form = PaymentForm

    list_display = ['__str__', 'due_amount']
    search_fields = ['subscription']
    readonly_fields = ['renewal_start_date', 'renewal_end_date', 'created_at', 'updated_at', 'created_by', 'updated_by']
    autocomplete_fields = ['subscription']

    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '/static/change_form_payment.js',
        )
        css = {
            'all': ('/static/payment.css ',)
        }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Payment, PaymentAdmin)
