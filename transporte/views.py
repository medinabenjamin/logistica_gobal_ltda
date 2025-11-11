from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Count, Sum
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView



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

from .filters import (
    VehiculoFilter, AeronaveFilter, ConductorFilter, PilotoFilter,
    ClienteFilter, CargaFilter, RutaFilter, DespachoFilter
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
            "singular_label": "Vehículo",
            "model": Vehiculo,
            "form_class": VehiculoForm,
            "fields": [
                ("patente", "Patente"), ("marca", "Marca"), ("modelo", "Modelo"),
                ("capacidad_kg", "Capacidad (kg)"), ("anio", "Año"), ("estado", "Estado"),
            ],
            "filterset_class": VehiculoFilter,
        },
        "aeronaves": {
            "label": "Aeronaves",
            "singular_label": "Aeronave",
            "model": Aeronave,
            "form_class": AeronaveForm,
            "fields": [
                ("matricula", "Matrícula"), ("fabricante", "Fabricante"), ("modelo", "Modelo"),
                ("capacidad_kg", "Capacidad (kg)"), ("estado", "Estado"),
            ],
            "filterset_class": AeronaveFilter,
        },
        "conductores": {
            "label": "Conductores",
            "singular_label": "Conductor",
            "model": Conductor,
            "form_class": ConductorForm,
            "fields": [
                ("run", "RUN"), ("nombre", "Nombre"), ("licencia", "Licencia"),
                ("telefono", "Teléfono"), ("activo", "Activo"),
            ],
            "filterset_class": ConductorFilter,
        },
        "pilotos": {
            "label": "Pilotos",
            "singular_label": "Piloto",
            "model": Piloto,
            "form_class": PilotoForm,
            "fields": [
                ("run", "RUN"), ("nombre", "Nombre"), ("licencia", "Licencia"),
                ("horas_vuelo", "Horas vuelo"), ("activo", "Activo"),
            ],
            "filterset_class": PilotoFilter,
        },
        "clientes": {
            "label": "Clientes",
            "singular_label": "Cliente",
            "model": Cliente,
            "form_class": ClienteForm,
            "fields": [
                ("nombre", "Nombre"), ("rut", "RUT"),
                ("telefono", "Teléfono"), ("email", "Email"),
            ],
            "filterset_class": ClienteFilter,
        },
        "cargas": {
            "label": "Cargas",
            "singular_label": "Carga",
            "model": Carga,
            "form_class": CargaForm,
            "fields": [
                ("descripcion", "Descripción"), ("cliente", "Cliente"), ("peso_kg", "Peso (kg)"),
                ("tipo", "Tipo"), ("valor_estimado", "Valor estimado"),
            ],
            "filterset_class": CargaFilter,
        },
        "rutas": {
            "label": "Rutas",
            "singular_label": "Ruta",
            "model": Ruta,
            "form_class": RutaForm,
            "fields": [
                ("codigo", "Código"), ("origen", "Origen"), ("destino", "Destino"),
                ("tipo_transporte", "Tipo"), ("duracion_estimada_min", "Duración (min)"),
            ],
            "filterset_class": RutaFilter,
        },
        "despachos": {
            "label": "Despachos",
            "singular_label": "Despacho",
            "model": Despacho,
            "form_class": DespachoForm,
            "fields": [
                ("codigo", "Código"), ("fecha", "Fecha"), ("ruta", "Ruta"),
                ("vehiculo", "Vehículo"), ("aeronave", "Aeronave"), ("conductor", "Conductor"),
                ("piloto", "Piloto"), ("carga", "Carga"), ("estado", "Estado"),
            ],
            "filterset_class": DespachoFilter,
        },
    }

    # --- INICIO LÓGICA DE VISTA REFACTORIZADA ---
    
    # 1. Determinar el módulo, vista y pk de la URL (GET)
    requested_module_key = request.GET.get("module")
    if requested_module_key not in module_config:
        requested_module_key = next(iter(module_config))
        
    current_view_mode = request.GET.get("view", "list") # 'list' por defecto
    current_edit_pk = request.GET.get("pk")

    search_query = request.GET.get('q', '')

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
    
    # 2. Procesar la lógica POST (Crear, Actualizar, Borrar)
    if request.method == "POST":
        module_key = request.POST.get("module")
        action = request.POST.get("action", "create")
        config = module_config.get(module_key)
        
        # Sobrescribir el módulo activo con el del POST
        requested_module_key = module_key 

        if not config:
            messages.error(request, "El módulo seleccionado no es válido.")
            return HttpResponseRedirect(reverse("home"))

        # Mantener los filtros (GET params) en la URL después de la acción
        current_get_params = request.GET.copy()
        current_get_params['module'] = module_key # Asegurar el módulo
        if 'view' in current_get_params: del current_get_params['view'] # Volver a lista
        if 'pk' in current_get_params: del current_get_params['pk'] # Quitar pk
        
        redirect_url = f"{reverse('home')}?{current_get_params.urlencode()}"

        if action == "delete":
            pk = request.POST.get("pk")
            instance = get_object_or_404(config["model"], pk=pk)
            instance.delete()
            messages.success(request, f"{config['label']} — registro eliminado correctamente.")
            return HttpResponseRedirect(redirect_url)

        instance = None
        if action == "update":
            pk = request.POST.get("pk")
            instance = get_object_or_404(config["model"], pk=pk)

        form = config["form_class"](request.POST, instance=instance)

        if form.is_valid():
            form.save()
            verb = "actualizado" if action == "update" else "creado"
            messages.success(request, f"{config['label']} — registro {verb} correctamente.")
            return HttpResponseRedirect(redirect_url)
        else:
            # Si el formulario NO es válido, el POST falla.
            # Guardamos el formulario con errores para mostrarlo.
            if action == "update":
                # Guardamos el form de 'edit' y forzamos el modo 'edit'
                module_contexts['failed_edit_form'] = form
                module_contexts['failed_edit_instance'] = instance
                current_view_mode = 'edit' # Forzar modo
                current_edit_pk = instance.pk # Forzar pk
            else:
                # Guardamos el form de 'create' y forzamos el modo 'create'
                module_contexts['failed_create_form'] = form
                current_view_mode = 'create' # Forzar modo
            
            messages.error(request, "Error al guardar, por favor revisa los campos.")

    # 3. Construir el contexto para TODOS los módulos (para GET y POST fallidos)
    for key, config in module_config.items():
        
        # Filtrar el queryset
        instances_qs = config["model"].objects.all()
        filter_form = None
        if config.get("filterset_class"):
            filter_form = config["filterset_class"](request.GET, queryset=instances_qs)
            instances_qs = filter_form.qs

        instances = instances_qs
        
        # Determinar el modo de visualización final
        display_mode = 'list' # Por defecto
        create_form_instance = config["form_class"]() # Formulario 'create' limpio
        edit_form_instance = None # Formulario 'edit'
        edit_instance_obj = None # Instancia para editar

        if key == requested_module_key:
            if current_view_mode == 'create':
                display_mode = 'create'
                # Si un POST falló, usamos el formulario con errores
                if 'failed_create_form' in module_contexts:
                    create_form_instance = module_contexts['failed_create_form']
            
            elif current_view_mode == 'edit' or (current_edit_pk and not action == "update"):
                display_mode = 'edit'
                # Si un POST falló, usamos el formulario con errores
                if 'failed_edit_form' in module_contexts and 'failed_edit_instance' in module_contexts:
                    edit_form_instance = module_contexts['failed_edit_form']
                    edit_instance_obj = module_contexts['failed_edit_instance']
                # Si es un GET, creamos el formulario de edición
                elif current_edit_pk:
                    try:
                        edit_instance_obj = get_object_or_404(config["model"], pk=current_edit_pk)
                        edit_form_instance = config["form_class"](instance=edit_instance_obj)
                    except:
                        messages.error(request, "El registro a editar no fue encontrado.")
                        display_mode = 'list' # Volver a la lista si hay error

        module_contexts[key] = {
            "key": key,
            "label": config["label"],
            "singular_label": config["singular_label"],
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
            "filter_form": filter_form,
            
            "display_mode": display_mode, # 'list', 'create', o 'edit'
            "create_form": create_form_instance, # Siempre hay un form 'create'
            "edit_form": edit_form_instance, # Solo si display_mode es 'edit'
            "edit_instance": edit_instance_obj, # Solo si display_mode es 'edit'
        }

    # --- FIN LÓGICA DE VISTA REFACTORIZADA ---

    active_module_key = requested_module_key
    return render(
        request,
        "transporte/home.html",
        {
            "modules": [
                {"key": key, "label": config["label"]}
                for key, config in module_config.items()
            ],
            "active_module": module_contexts[active_module_key],
            "active_module_key": active_module_key,     
            "search_query": search_query,
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
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["run", "nombre", "licencia"]
    ordering_fields = ["run", "nombre", "licencia", "activo"]


class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer
    permission_classes = [permissions.IsAdminUser]
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


class ReporteCargasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Carga.objects
            .values("cliente__nombre")
            .annotate(total_peso=Sum("peso_kg"))
            .order_by("-total_peso")
        )
        return Response(data)


class ReporteRutasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Despacho.objects
            .values("ruta__codigo", "ruta__origen", "ruta__destino")
            .annotate(total_despachos=Count("id"))
            .order_by("-total_despachos")
        )
        return Response(data)