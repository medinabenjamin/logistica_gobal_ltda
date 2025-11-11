# transporte/filters.py
import django_filters
from django import forms
from django.db.models import Q
from .models import (
    Vehiculo, Aeronave, Conductor, Piloto,
    Cliente, Carga, Ruta, Despacho
)

class BaseFilterSet(django_filters.FilterSet):
    """
    Filtro base para aplicar clases de Bootstrap a todos los campos.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.form.fields.items():
            if isinstance(field, django_filters.ChoiceFilter):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field, django_filters.ModelChoiceFilter):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field, django_filters.BooleanFilter):
                 field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

# --- Definición de Filtros por Modelo ---

class VehiculoFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar patente, marca, modelo...'})
    )
    estado = django_filters.ChoiceFilter(choices=Vehiculo.Estado.choices)

    class Meta:
        model = Vehiculo
        fields = ['q', 'estado']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(patente__icontains=value) |
            Q(marca__icontains=value) |
            Q(modelo__icontains=value)
        ).distinct()

class AeronaveFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar matrícula, fabricante...'})
    )
    estado = django_filters.ChoiceFilter(choices=Aeronave.Estado.choices)

    class Meta:
        model = Aeronave
        fields = ['q', 'estado']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(matricula__icontains=value) |
            Q(fabricante__icontains=value) |
            Q(modelo__icontains=value)
        ).distinct()

class ConductorFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar RUN, nombre, licencia...'})
    )
    
    class Meta:
        model = Conductor
        fields = ['q', 'activo']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(run__icontains=value) |
            Q(nombre__icontains=value) |
            Q(licencia__icontains=value)
        ).distinct()

class PilotoFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar RUN, nombre, licencia...'})
    )

    class Meta:
        model = Piloto
        fields = ['q', 'activo']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(run__icontains=value) |
            Q(nombre__icontains=value) |
            Q(licencia__icontains=value)
        ).distinct()

class ClienteFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar nombre, RUT...'})
    )

    class Meta:
        model = Cliente
        fields = ['q']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(rut__icontains=value)
        ).distinct()

class CargaFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar descripción, tipo, cliente...'})
    )
    cliente = django_filters.ModelChoiceFilter(queryset=Cliente.objects.all())

    class Meta:
        model = Carga
        fields = ['q', 'cliente', 'tipo']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(descripcion__icontains=value) |
            Q(tipo__icontains=value) |
            Q(cliente__nombre__icontains=value) |
            Q(cliente__rut__icontains=value)
        ).distinct()

class RutaFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar código, origen, destino...'})
    )
    tipo_transporte = django_filters.ChoiceFilter(choices=Ruta.TipoTransporte.choices)

    class Meta:
        model = Ruta
        fields = ['q', 'tipo_transporte']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(origen__icontains=value) |
            Q(destino__icontains=value)
        ).distinct()

class DespachoFilter(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search_filter',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar código, ruta...'})
    )
    estado = django_filters.ChoiceFilter(choices=Despacho.Estado.choices)
    ruta = django_filters.ModelChoiceFilter(queryset=Ruta.objects.all())

    class Meta:
        model = Despacho
        fields = ['q', 'estado', 'ruta']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(estado__icontains=value) |
            Q(ruta__codigo__icontains=value)
        ).distinct()