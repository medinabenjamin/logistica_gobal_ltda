from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from .forms import (
    AeronaveForm,
    CargaForm,
    ClienteForm,
    ConductorForm,
    DespachoForm,
    PilotoForm,
    RutaForm,
    VehiculoForm,
)
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


@login_required(login_url="login")
def home(request):
    """Render the public homepage for the transporte module."""

    module_config = {
        "vehiculos": {
            "label": "Vehículos",
            "model": Vehiculo,
            "form_class": VehiculoForm,
            "fields": [
                ("patente", "Patente"),
                ("marca", "Marca"),
                ("modelo", "Modelo"),
                ("capacidad_kg", "Capacidad (kg)"),
                ("anio", "Año"),
                ("estado", "Estado"),
            ],
        },
        "aeronaves": {
            "label": "Aeronaves",
            "model": Aeronave,
            "form_class": AeronaveForm,
            "fields": [
                ("matricula", "Matrícula"),
                ("fabricante", "Fabricante"),
                ("modelo", "Modelo"),
                ("capacidad_kg", "Capacidad (kg)"),
                ("estado", "Estado"),
            ],
        },
        "conductores": {
            "label": "Conductores",
            "model": Conductor,
            "form_class": ConductorForm,
            "fields": [
                ("run", "RUN"),
                ("nombre", "Nombre"),
                ("licencia", "Licencia"),
                ("telefono", "Teléfono"),
                ("activo", "Activo"),
            ],
        },
        "pilotos": {
            "label": "Pilotos",
            "model": Piloto,
            "form_class": PilotoForm,
            "fields": [
                ("run", "RUN"),
                ("nombre", "Nombre"),
                ("licencia", "Licencia"),
                ("horas_vuelo", "Horas vuelo"),
                ("activo", "Activo"),
            ],
        },
        "clientes": {
            "label": "Clientes",
            "model": Cliente,
            "form_class": ClienteForm,
            "fields": [
                ("nombre", "Nombre"),
                ("rut", "RUT"),
                ("telefono", "Teléfono"),
                ("email", "Email"),
            ],
        },
        "cargas": {
            "label": "Cargas",
            "model": Carga,
            "form_class": CargaForm,
            "fields": [
                ("descripcion", "Descripción"),
                ("cliente", "Cliente"),
                ("peso_kg", "Peso (kg)"),
                ("tipo", "Tipo"),
                ("valor_estimado", "Valor estimado"),
            ],
        },
        "rutas": {
            "label": "Rutas",
            "model": Ruta,
            "form_class": RutaForm,
            "fields": [
                ("codigo", "Código"),
                ("origen", "Origen"),
                ("destino", "Destino"),
                ("tipo_transporte", "Tipo"),
                ("duracion_estimada_min", "Duración (min)"),
            ],
        },
        "despachos": {
            "label": "Despachos",
            "model": Despacho,
            "form_class": DespachoForm,
            "fields": [
                ("codigo", "Código"),
                ("fecha", "Fecha"),
                ("ruta", "Ruta"),
                ("vehiculo", "Vehículo"),
                ("aeronave", "Aeronave"),
                ("conductor", "Conductor"),
                ("piloto", "Piloto"),
                ("carga", "Carga"),
                ("estado", "Estado"),
            ],
        },
    }

    def _format_value(instance, field_name):
        display_method = getattr(instance, f"get_{field_name}_display", None)
        if callable(display_method):
            value = display_method()
        else:
            value = getattr(instance, field_name)
        if value is None or value == "":
            return "—"
        if isinstance(value, bool):
            return "Sí" if value else "No"
        return str(value)

    module_contexts = {}
    for key, config in module_config.items():
        instances = config["model"].objects.all()
        module_contexts[key] = {
            "key": key,
            "label": config["label"],
            "create_form": config["form_class"](),
            "headers": [label for _, label in config["fields"]],
            "rows": [
                {
                    "pk": instance.pk,
                    "values": [
                        _format_value(instance, field_name)
                        for field_name, _ in config["fields"]
                    ],
                }
                for instance in instances
            ],
            "total": instances.count(),
        }

    if request.method == "POST":
        module_key = request.POST.get("module")
        action = request.POST.get("action", "create")
        config = module_config.get(module_key)
        if not config:
            messages.error(request, "El módulo seleccionado no es válido.")
            return HttpResponseRedirect(reverse("home"))

        redirect_url = f"{reverse('home')}#module-{module_key}"

        if action == "delete":
            pk = request.POST.get("pk")
            instance = get_object_or_404(config["model"], pk=pk)
            instance.delete()
            messages.success(
                request,
                f"{config['label']} — registro eliminado correctamente.",
            )
            return HttpResponseRedirect(redirect_url)

        instance = None
        if action == "update":
            pk = request.POST.get("pk")
            instance = get_object_or_404(config["model"], pk=pk)

        form = config["form_class"](request.POST, instance=instance)

        if form.is_valid():
            form.save()
            verb = "actualizado" if action == "update" else "creado"
            messages.success(
                request,
                f"{config['label']} — registro {verb} correctamente.",
            )
            return HttpResponseRedirect(redirect_url)

        context_form = module_contexts[module_key]
        if action == "update":
            context_form["edit_form"] = form
            context_form["edit_instance"] = instance
        else:
            context_form["create_form"] = form

    edit_module_key = request.GET.get("module")
    edit_pk = request.GET.get("pk")
    if edit_module_key in module_config and edit_pk:
        config = module_config[edit_module_key]
        instance = get_object_or_404(config["model"], pk=edit_pk)
        module_contexts[edit_module_key]["edit_form"] = config["form_class"](
            instance=instance
        )
        module_contexts[edit_module_key]["edit_instance"] = instance

    return render(
        request,
        "transporte/home.html",
        {
            "modules": list(module_contexts.values()),
        },
    )


def login_view(request):
    """Handle user authentication for the management panel."""

    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request=request, data=request.POST or None)
    for field in form.fields.values():
        existing_classes = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = " ".join(
            value for value in [existing_classes, "form-control"] if value
        )

    if request.method == "POST":
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("home")

    return render(
        request,
        "transporte/login.html",
        {
            "form": form,
        },
    )


@login_required(login_url="login")
def logout_view(request):
    """Log out the current user and redirect to the login page."""

    if request.method == "POST":
        auth_logout(request)
        return redirect("login")

    return redirect("home")


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
