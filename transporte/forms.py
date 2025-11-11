from django import forms

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


class DateInput(forms.DateInput):
    input_type = "date"


class BaseModelForm(forms.ModelForm):
    """Base form to provide consistent styles and widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault("class", "form-control")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.setdefault("class", "form-control")
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
                field.widget.attrs.setdefault("rows", 3)

            if self.is_bound and self.errors.get(name):
                existing_classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (
                    f"{existing_classes} is-invalid".strip()
                )


class VehiculoForm(BaseModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            "patente",
            "marca",
            "modelo",
            "capacidad_kg",
            "anio",
            "estado",
        ]


class AeronaveForm(BaseModelForm):
    class Meta:
        model = Aeronave
        fields = [
            "matricula",
            "fabricante",
            "modelo",
            "capacidad_kg",
            "estado",
        ]


class ConductorForm(BaseModelForm):
    class Meta:
        model = Conductor
        fields = ["run", "nombre", "licencia", "telefono", "activo"]
        widgets = {
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PilotoForm(BaseModelForm):
    class Meta:
        model = Piloto
        fields = ["run", "nombre", "licencia", "horas_vuelo", "activo"]
        widgets = {
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ClienteForm(BaseModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "rut", "direccion", "telefono", "email"]


class CargaForm(BaseModelForm):
    class Meta:
        model = Carga
        fields = ["cliente", "descripcion", "peso_kg", "tipo", "valor_estimado"]


class RutaForm(BaseModelForm):
    class Meta:
        model = Ruta
        fields = [
            "codigo",
            "origen",
            "destino",
            "tipo_transporte",
            "duracion_estimada_min",
        ]


class DespachoForm(BaseModelForm):
    class Meta:
        model = Despacho
        fields = [
            "codigo",
            "fecha",
            "ruta",
            "vehiculo",
            "aeronave",
            "conductor",
            "piloto",
            "carga",
            "estado",
            "observaciones",
        ]
        widgets = {
            "fecha": DateInput(),
        }

