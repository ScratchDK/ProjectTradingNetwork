from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class NetworkNode(models.Model):
    """Базовый абстрактный класс для всех элементов сети"""

    name = models.CharField(max_length=255, verbose_name="Название")
    email = models.EmailField(verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house_number = models.CharField(max_length=20, verbose_name="Номер дома")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        abstract = True  # Не создает таблицу в БД
        ordering = ["-created_at"]

    def has_children(self):
        """Проверяет, есть ли зависимые объекты"""
        content_type = ContentType.objects.get_for_model(self)
        # Проверяем RetailNetwork и IndividualEntrepreneur как потенциальных потомков
        has_retail_children = RetailNetwork.objects.filter(
            supplier_content_type=content_type, supplier_object_id=self.id
        ).exists()

        has_entrepreneur_children = IndividualEntrepreneur.objects.filter(
            supplier_content_type=content_type, supplier_object_id=self.id
        ).exists()

        return has_retail_children or has_entrepreneur_children


class Product(models.Model):
    """Модель продукта"""

    name = models.CharField(max_length=255, verbose_name="Название")
    model = models.CharField(max_length=255, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class SupplierMixin(models.Model):
    """Миксин для элементов с поставщиками"""

    debt_to_supplier = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Задолженность перед поставщиком",
    )

    # Поле с поставщиком обязательное, поэтому иерархической цепочки без завода в начале быть не может
    supplier_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": ("factory", "retailnetwork", "individualentrepreneur")
        },
        verbose_name="Тип поставщика",
    )
    supplier_object_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="ID поставщика"
    )
    supplier = GenericForeignKey("supplier_content_type", "supplier_object_id")

    class Meta:
        abstract = True

    def get_supplier_name(self):
        return str(self.supplier) if self.supplier else "Нет поставщика"

    get_supplier_name.short_description = "Поставщик"

    def clean(self):
        if not self.supplier:
            raise ValidationError("Поставщик не найден или не был указан!")

        if self.supplier and self.supplier == self:
            raise ValidationError(
                "Элемент не может быть своим собственным поставщиком!"
            )

        # hasattr - Проверяем существует ли атрибут у объекта
        if (
            hasattr(self, "hierarchy_level")
            and self.supplier
            and self.supplier.hierarchy_level >= self.hierarchy_level
        ):
            raise ValidationError("Некорректная иерархия поставщиков!")


class Factory(NetworkNode):
    """Завод (уровень 0)"""

    products = models.ManyToManyField(
        Product, related_name="factories", verbose_name="Продукты"
    )

    def __str__(self):
        return f"Завод: {self.name}"

    @property
    def hierarchy_level(self):
        return 0

    class Meta:
        verbose_name = "Завод"
        verbose_name_plural = "Заводы"

    def delete(self, *args, **kwargs):
        if self.has_children():
            raise models.ProtectedError(
                "Невозможно удалить завод, пока существуют зависимые розничные сети или ИП",
                self,
            )
        super().delete(*args, **kwargs)


class RetailNetwork(NetworkNode, SupplierMixin):
    """Розничная сеть (уровень 1 или выше)"""

    products = models.ManyToManyField(
        Product, related_name="retail_networks", verbose_name="Продукты"
    )

    def __str__(self):
        return f"Розничная сеть: {self.name}"

    @property
    def hierarchy_level(self):
        if not self.supplier:
            return 0
        return self.supplier.hierarchy_level + 1

    class Meta:
        verbose_name = "Розничная сеть"
        verbose_name_plural = "Розничные сети"

    def delete(self, *args, **kwargs):
        if self.has_children():
            raise models.ProtectedError(
                "Невозможно удалить розничную сеть, пока существуют зависимости", self
            )
        super().delete(*args, **kwargs)


class IndividualEntrepreneur(NetworkNode, SupplierMixin):
    """Индивидуальный предприниматель (уровень 1 или выше)"""

    products = models.ManyToManyField(
        Product, related_name="entrepreneurs", verbose_name="Продукты"
    )

    def __str__(self):
        return f"ИП: {self.name}"

    @property
    def hierarchy_level(self):
        if not self.supplier:
            return 0
        return self.supplier.hierarchy_level + 1

    class Meta:
        verbose_name = "Индивидуальный предприниматель"
        verbose_name_plural = "Индивидуальные предприниматели"

    def delete(self, *args, **kwargs):
        if self.has_children():
            raise models.ProtectedError(
                "Невозможно удалить ИП, пока существуют зависимости", self
            )
        super().delete(*args, **kwargs)
