from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from .models import Factory, IndividualEntrepreneur, Product, RetailNetwork


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date")
    search_fields = ("name", "model")
    list_filter = ("release_date",)


class FactoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "country", "city", "created_at")
    search_fields = ("name", "email", "city")
    list_filter = ("city", "country")
    filter_horizontal = ("products",)

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except models.ProtectedError as e:
            self.message_user(request, str(e), level=messages.ERROR)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                obj.delete()
            except models.ProtectedError as e:
                self.message_user(request, str(e), level=messages.ERROR)


class BaseNetworkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "supplier_link",
        "get_hierarchy_level",
        "city",
        "debt_to_supplier",
        "created_at",
    )
    search_fields = ("name", "email", "city")
    list_filter = ("city", "country", "debt_to_supplier")
    filter_horizontal = ("products",)
    actions = ["clear_debt"]
    readonly_fields = ("get_hierarchy_level", "created_at", "supplier_link")

    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse(
                f"admin:{obj.supplier_content_type.app_label}_{obj.supplier_content_type.model}_change",
                args=[obj.supplier_object_id],
            )
            return format_html(
                '<a href="{}">{} (ID: {})</a>',
                url,
                str(obj.supplier),
                obj.supplier_object_id,
            )
        return "Нет поставщика"

    supplier_link.short_description = "Текущий поставщик"

    fieldsets = (
        (None, {"fields": ("name", "email", "products")}),
        ("Адрес", {"fields": ("country", "city", "street", "house_number")}),
        (
            "Поставщик",
            {
                "fields": (
                    "supplier_content_type",
                    "supplier_object_id",
                    "supplier_link",
                    "debt_to_supplier",
                ),
                "description": "Выберите тип поставщика и введите его ID. Можно найти ID в списке соответствующих объектов.",
            },
        ),
        (
            "Дополнительно",
            {"fields": ("get_hierarchy_level", "created_at"), "classes": ("collapse",)},
        ),
    )

    def get_supplier_display(self, obj):
        return obj.get_supplier_name()

    get_supplier_display.short_description = "Поставщик"

    def get_hierarchy_level(self, obj):
        return obj.hierarchy_level

    get_hierarchy_level.short_description = "Уровень иерархии"

    def clear_debt(self, request, queryset):
        updated = queryset.update(debt_to_supplier=0)
        self.message_user(request, f"Задолженность очищена для {updated} объектов")

    clear_debt.short_description = "Очистить задолженность"

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except models.ProtectedError as e:
            self.message_user(request, str(e), level=messages.ERROR)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                obj.delete()
            except models.ProtectedError as e:
                self.message_user(request, str(e), level=messages.ERROR)


@admin.register(RetailNetwork)
class RetailNetworkAdmin(BaseNetworkAdmin):
    pass


@admin.register(IndividualEntrepreneur)
class IndividualEntrepreneurAdmin(BaseNetworkAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Factory, FactoryAdmin)
