from django.contrib import admin
from django.contrib import messages

from .models import (
    Product,
    Order,
    OrderProduct,
    Address,
    Payment,
    Invoice,
    Refund,
    ContactInfo,
)


def make_refund_accepted(modeladmin, request, queryset):
    for obj in queryset.all():
        if obj.refund_requested:
            obj.refund_granted = True
            messages.info(
                request, f"Le status de la commande {obj.ref_code} a été mis à jour"
            )
            obj.save()
        else:
            messages.warning(
                request,
                f"La commande {obj.ref_code} n'a pas sollicité de remboursement",
            )


make_refund_accepted.short_description = "Confirmer le remboursement des commandes sélectionnées"


def confirm_expedition(modeladmin, request, queryset):
    for obj in queryset.all():
        obj.being_delivered = True
        obj.save()
        messages.info(
            request, f"Le status de la commande {obj.ref_code} a été mis à jour"
        )


confirm_expedition.short_description = "Confirmer l'expédition des commandes sélectionnées"


def confirm_delivery(modeladmin, request, queryset):
    for obj in queryset.all():
        if obj.being_delivered:
            obj.recieved = True
            messages.info(
                request, f"Le status de la commande {obj.ref_code} a été mis à jour"
            )
            obj.save()
        else:
            messages.warning(
                request,
                f"La commande {obj.ref_code} n'a pas encore été expédiée",
            )


confirm_delivery.short_description = "Confirmer la réception des commandes sélectionnées"


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "ref_code",
        "ordered",
        "being_delivered",
        "recieved",
        "refund_requested",
        "refund_granted",
        "billing_address",
        "shipping_address",
        "payment",
        "invoice",
    ]
    list_display_links = [
        "ref_code",
        "shipping_address",
        "billing_address",
        "payment",
        "invoice",
    ]
    list_filter = [
        "ref_code",
        "ordered",
        "being_delivered",
        "recieved",
        "refund_requested",
        "refund_granted",
    ]
    search_fields = [
        "ref_code",
    ]
    actions = [confirm_expedition, confirm_delivery, make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'street_address',
        'street_address_line_2',
        'city',
        'country',
        'zip_code',
        'address_type',
    ]
    list_filter = ['address_type', 'country']
    search_fields = [
        'street_address',
        'city',
        'zip_code',
    ]


admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(Refund)
admin.site.register(ContactInfo)
