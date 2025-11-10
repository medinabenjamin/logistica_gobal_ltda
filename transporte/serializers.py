from rest_framework import serializers

from .models import (
    Aeronave,
    Carga,
    Cliente,
    Conductor,
    Despacho,
    Piloto,
    Ruta,
    Vehiculo,
)


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = "__all__"


class AeronaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aeronave
        fields = "__all__"


class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = "__all__"


class PilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piloto
        fields = "__all__"


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"


class CargaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source="cliente", write_only=True
    )

    class Meta:
        model = Carga
        fields = "__all__"


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = "__all__"


class DespachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despacho
        fields = "__all__"
