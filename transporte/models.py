from django.db import models


class Vehiculo(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        MANTENCION = "MANTENCION", "En mantención"
        INACTIVO = "INACTIVO", "Inactivo"

    patente = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, blank=True)
    capacidad_kg = models.PositiveIntegerField()
    anio = models.PositiveIntegerField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )

    def __str__(self) -> str:
        return f"{self.patente} - {self.marca}"


class Aeronave(models.Model):
    class Estado(models.TextChoices):
        OPERATIVA = "OPERATIVA", "Operativa"
        MANTENCION = "MANTENCION", "En mantención"
        FUERA = "FUERA", "Fuera de servicio"

    matricula = models.CharField(max_length=50, unique=True)
    fabricante = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    capacidad_kg = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.OPERATIVA
    )

    def __str__(self) -> str:
        return f"{self.matricula} - {self.modelo or 'Sin modelo'}"


class Conductor(models.Model):
    run = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    licencia = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.run})"


class Piloto(models.Model):
    run = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    licencia = models.CharField(max_length=50)
    horas_vuelo = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.run})"


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.rut})"


class Carga(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    peso_kg = models.PositiveIntegerField()
    tipo = models.CharField(max_length=100, blank=True)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f"Carga {self.descripcion} para {self.cliente.nombre}"


class Ruta(models.Model):
    class TipoTransporte(models.TextChoices):
        TERRESTRE = "TERRESTRE", "Terrestre"
        AEREO = "AEREO", "Aéreo"

    codigo = models.CharField(max_length=50, unique=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    tipo_transporte = models.CharField(
        max_length=20, choices=TipoTransporte.choices
    )
    duracion_estimada_min = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.codigo}: {self.origen} -> {self.destino}"


class Despacho(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_RUTA = "EN_RUTA", "En ruta"
        ENTREGADO = "ENTREGADO", "Entregado"

    codigo = models.CharField(max_length=50, unique=True)
    fecha = models.DateField()
    ruta = models.ForeignKey(Ruta, on_delete=models.PROTECT)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, blank=True, null=True)
    aeronave = models.ForeignKey(Aeronave, on_delete=models.SET_NULL, blank=True, null=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, blank=True, null=True)
    piloto = models.ForeignKey(Piloto, on_delete=models.SET_NULL, blank=True, null=True)
    carga = models.ForeignKey(Carga, on_delete=models.SET_NULL, blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    observaciones = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Despacho {self.codigo} - {self.estado}"
