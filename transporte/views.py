from django.shortcuts import render
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

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
from .serializers import (
    AeronaveSerializer,
    CargaSerializer,
    ClienteSerializer,
    ConductorSerializer,
    DespachoSerializer,
    PilotoSerializer,
    RutaSerializer,
    VehiculoSerializer,
)


@api_view(["GET"])
def ping(_request):
    """Simple endpoint for health checks."""

    return Response({"message": "pong"})


def home(request):
    """Render the public homepage for the transporte module."""

    return render(request, "transporte/home.html")


class IsAuthenticatedForWrite(BasePermission):
    """Allow read-only access to anonymous users and write access to authenticated users."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["patente", "marca", "modelo"]
    ordering_fields = ["patente", "marca", "modelo", "capacidad_kg", "anio"]


class AeronaveViewSet(viewsets.ModelViewSet):
    queryset = Aeronave.objects.all()
    serializer_class = AeronaveSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["matricula", "fabricante", "modelo"]
    ordering_fields = ["matricula", "fabricante", "modelo", "capacidad_kg"]


class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["run", "nombre", "licencia"]
    ordering_fields = ["run", "nombre", "licencia", "activo"]


class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["run", "nombre", "licencia"]
    ordering_fields = ["run", "nombre", "licencia", "horas_vuelo", "activo"]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "rut"]
    ordering_fields = ["nombre", "rut", "telefono"]


class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.select_related("cliente")
    serializer_class = CargaSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["descripcion", "tipo", "cliente__nombre", "cliente__rut"]
    ordering_fields = ["descripcion", "peso_kg", "tipo", "valor_estimado"]


class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticatedForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "origen", "destino"]
    ordering_fields = ["codigo", "origen", "destino", "duracion_estimada_min"]


class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.select_related(
        "ruta",
        "vehiculo",
        "aeronave",
        "conductor",
        "piloto",
        "carga",
    )
    serializer_class = DespachoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "estado", "ruta__codigo"]
    ordering_fields = ["codigo", "fecha", "estado", "ruta__codigo"]
