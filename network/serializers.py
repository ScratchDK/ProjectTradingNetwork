from rest_framework import serializers

from .models import Factory, IndividualEntrepreneur, Product, RetailNetwork


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class FactorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = Factory
        fields = "__all__"


class RetailNetworkSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = RetailNetwork
        fields = "__all__"
        read_only_fields = ("debt_to_supplier",)

    def validate(self, data):
        # Для существующего объекта (обновление) пропускаем проверку поставщика
        if self.instance:
            return data

        # Для нового объекта проверяем оба поля поставщика
        supplier_content_type = data.get("supplier_content_type")
        supplier_object_id = data.get("supplier_object_id")

        if not supplier_content_type or not supplier_object_id:
            raise serializers.ValidationError(
                {
                    "supplier": "Необходимо указать supplier_content_type и supplier_object_id"
                }
            )

        # Проверка, что поставщик существует
        try:
            supplier_class = supplier_content_type.model_class()
            supplier = supplier_class.objects.get(pk=supplier_object_id)
        except (AttributeError, ValueError, supplier_class.DoesNotExist):
            raise serializers.ValidationError(
                {"supplier": "Указанный поставщик не существует"}
            )

        return data


class IndividualEntrepreneurSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = IndividualEntrepreneur
        fields = "__all__"
        read_only_fields = ("debt_to_supplier",)

    def validate(self, data):
        # Для существующего объекта (обновление) пропускаем проверку поставщика
        if self.instance:
            return data

        # Для нового объекта проверяем оба поля поставщика
        supplier_content_type = data.get("supplier_content_type")
        supplier_object_id = data.get("supplier_object_id")

        if not supplier_content_type or not supplier_object_id:
            raise serializers.ValidationError(
                {
                    "supplier": "Необходимо указать supplier_content_type и supplier_object_id"
                }
            )

        # Проверка, что поставщик существует
        try:
            supplier_class = supplier_content_type.model_class()
            supplier = supplier_class.objects.get(pk=supplier_object_id)
        except (AttributeError, ValueError, supplier_class.DoesNotExist):
            raise serializers.ValidationError(
                {"supplier": "Указанный поставщик не существует"}
            )

        return data
