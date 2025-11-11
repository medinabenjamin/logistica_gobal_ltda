from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AeronaveViewSet,
    CargaViewSet,
    ClienteViewSet,
    ConductorViewSet,
    DespachoViewSet,
    PilotoViewSet,
    ReporteCargasView,
    ReporteRutasView,
    RutaViewSet,
    VehiculoViewSet,
    ping,
)

router = DefaultRouter()
router.register("vehiculos", VehiculoViewSet)
router.register("aeronaves", AeronaveViewSet)
router.register("conductores", ConductorViewSet)
router.register("pilotos", PilotoViewSet)
router.register("clientes", ClienteViewSet)
router.register("cargas", CargaViewSet)
router.register("rutas", RutaViewSet)
router.register("despachos", DespachoViewSet)

app_name = "transporte"

urlpatterns = [
    path("", include(router.urls)),
    path("ping/", ping, name="ping"),
    path("reportes/cargas/", ReporteCargasView.as_view(), name="reporte-cargas"),
    path("reportes/rutas/", ReporteRutasView.as_view(), name="reporte-rutas"),
]
