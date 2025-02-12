from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Compania(models.Model):
    cuartel = models.CharField(max_length=2000, verbose_name="Cuartel")
    def __str__(self):
        return self.cuartel
    class Meta:
        verbose_name = "Cuartel"
        verbose_name_plural = "Cuarteles"

class Jerarquia(models.Model):
    jerarquia = models.CharField(max_length=100, verbose_name="Jerarquía")
    def __str__(self):
        return self.jerarquia
    class Meta:
        verbose_name = "Jerarquía"
        verbose_name_plural = "Jerarquías"

class Base(models.Model):
    base = models.CharField(max_length=100)
    estados = [
        ("Cubriendo zona", "Cubriendo zona"),
        ("En apoyo", "En apoyo"),
        ("Sin chofer","Sin chofer")
    ]
    estado = models.CharField(choices=estados, null=True, blank=True, max_length=20, default="Cubriendo zona", verbose_name="estado")
    def __str__(self):
        return self.base
    class Meta:
        verbose_name = "Base"
        verbose_name_plural = "Bases"

#CAMBIAR LAS MAYUSCULAS DEL VERBOSE NAME
class Bombero(models.Model):
    legajo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    es_chofer = models.BooleanField(default=False)
    IDJerarquia = models.ForeignKey(Jerarquia, null = True, on_delete=models.SET_NULL, verbose_name="Jerarquía")
    IDBase = models.ForeignKey(Base, null = True, on_delete=models.SET_NULL, verbose_name="Base")
    posicion = models.IntegerField(null=True, blank = True, default = 0)
    activo = models.BooleanField(default = True)
    def __str__(self):
        bombero = self.apellido+", "+self.nombre
        return bombero
    class Meta:
        verbose_name = "Bombero"
        verbose_name_plural = "Bomberos"
        ordering = ['apellido']

class TipoMovil(models.Model):
    tipo = models.CharField(max_length=100)
    def __str__(self):
        return self.tipo
    class Meta:
        verbose_name = "Tipo de móvil"
        verbose_name_plural = "Tipos de móvil"

class Estado(models.Model):
    estado = models.CharField(max_length=100)
    def __str__(self):
        return self.estado
    class Meta:
        verbose_name = "Estados"
        verbose_name_plural = "Estados"

class Movil(models.Model):
    numero = models.IntegerField(blank=True, null=True, verbose_name="número")
    IDTipo = models.ForeignKey(TipoMovil, null=True, on_delete=models.SET_NULL, verbose_name="tipo")
    litros = models.IntegerField(null=True, blank=True, verbose_name="litros de combustible")
    ultima_carga = models.DateTimeField(blank=True, null=True, auto_now_add=False, default=False)
    ultima_fluidos = models.DateTimeField(blank=True, null=True)
    intervenciones = models.IntegerField(blank=True, null=True, default=0)
    IDBase = models.ForeignKey(Base, null=True, on_delete=models.SET_NULL, verbose_name="base")
    IDEstado = models.ForeignKey(Estado, null=True, on_delete=models.SET_NULL, verbose_name="estado")
    def __str__(self):
        return "Móvil "+str(self.numero)
    class Meta:
        verbose_name = "Móvil"
        verbose_name_plural = "Móviles"

class Combustible(models.Model):
    movil = models.ForeignKey(Movil, on_delete=models.SET_NULL, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    encargado = models.ForeignKey(Bombero, on_delete=models.SET_NULL, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return str(self.movil) + ' - ' + str(self.encargado) + ' - ' + str(self.fecha)
    class Meta:
        verbose_name = "Carga de combustible"
        verbose_name_plural = "Carga de combustible"

class Fluidos(models.Model):
    movil = models.ForeignKey(Movil, on_delete=models.SET_NULL, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    encargado = models.ForeignKey(Bombero, on_delete=models.SET_NULL, blank=True, null=True)
    agua = models.IntegerField(blank=True, null=True)
    aceite = models.IntegerField(blank=True, null=True)
    hidraulico = models.IntegerField(blank=True, null=True)
    frenos = models.IntegerField(blank=True, null=True)
    tanque = models.CharField(max_length=50,blank=True, null=True)
    bomba = models.CharField(max_length=50,blank=True, null=True)
    sirena = models.CharField(max_length=50,blank=True, null=True)
    luces = models.CharField(max_length=50,blank=True, null=True)
    
    def __str__(self):
        return str(self.movil) + ' - ' + str(self.encargado) + ' - ' +str(self.fecha)
    class Meta:
        verbose_name = "Fluidos"
        verbose_name_plural = "Fluidos"

class TipoServicio(models.Model):
    tipo = models.CharField(max_length=100, verbose_name="tipo de servicio")
    def __str__(self):
        return self.tipo
    class Meta:
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicios"


class Planilla(models.Model):
    guardia_operativa = models.IntegerField(verbose_name="Guardia operativa", default=0, unique=True)
    cuartel = models.ForeignKey(Base, blank=True, on_delete=models.SET_NULL, null=True, verbose_name="cuartel")
    fecha = models.DateField(null=True)
    guardia = models.CharField(max_length=10, null=True)
    cabecera = models.ForeignKey(Compania, blank=True, on_delete=models.SET_NULL, null=True, verbose_name="Cabecera de compañia")
    oficial = models.ForeignKey(Bombero, blank=True, on_delete=models.SET_NULL, null=True, verbose_name="Oficial de semana")
    cuartelero = models.CharField(max_length=100, blank=True, null=True)
    recibido = models.IntegerField(blank=True, null=True)
    gastado = models.IntegerField(blank=True, null=True)
    entregado = models.IntegerField(blank=True, null=True)
    concepto = models.CharField(max_length=200, blank=True, null=True)
    encargado = models.ForeignKey(Bombero, related_name="encargado", blank=True, on_delete=models.SET_NULL, null=True, verbose_name="Encargado de guardia")
    ingreso_encargado = models.TimeField(blank=True, null=True, verbose_name="ingreso encargado")
    chofer = models.ForeignKey(Bombero, related_name="chofer", blank=True, on_delete=models.SET_NULL, null=True, verbose_name="Chofer")
    ingreso_chofer = models.TimeField(blank=True, null=True, verbose_name="ingreso chofer")
    tareas = models.TextField(blank=True, null=True, verbose_name="Tareas realizadas")
    novedades = models.TextField(blank=True, null=True, verbose_name="Novedades")
    
    def __str__(self):
        return 'Guardia operativa: ' + str(self.guardia_operativa) + ' - ' + str(self.fecha) + ' - ' + str(self.guardia)

    class Meta:
        verbose_name = "Planilla"
        verbose_name_plural = "Planillas"

#onetomany

class GuardiaPresentes(models.Model):
    guardia_op = models.ForeignKey(Planilla, related_name="guardia_presentes", blank=True, on_delete=models.SET_NULL, null=True)
    bombero = models.ForeignKey(Bombero, blank=True, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(blank=True, null=True, verbose_name="ingreso")
    ingreso = models.TimeField(blank=True, null=True, verbose_name="ingreso")
    encargado = models.BooleanField(blank=True, null=True, default=False, verbose_name="encargado")
    chofer = models.BooleanField(blank=True, null=True, default=False, verbose_name="chofer")
    def __str__(self):
        return str(self.bombero)

    class Meta:
        verbose_name = "Presente"
        verbose_name_plural = "Presentes"

class GuardiaAusentes(models.Model):
    guardia_op = models.ForeignKey(Planilla, related_name="guardia_ausentes", blank=True, on_delete=models.SET_NULL, null=True)
    bombero = models.ForeignKey(Bombero, blank=True, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.bombero)

    class Meta:
        verbose_name = "Ausente"
        verbose_name_plural = "Ausentes"

class GuardiaRefuerzos(models.Model):
    guardia_op = models.ForeignKey(Planilla, related_name="guardia_refuerzos", blank=True, on_delete=models.SET_NULL, null=True)
    bombero = models.ForeignKey(Bombero, blank=True, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.bombero)

    class Meta:
        verbose_name = "Refuerzo"
        verbose_name_plural = "Refuerzos"

class Servicio(models.Model):
    guardia_operativa = models.IntegerField(blank=True, null=True, verbose_name="Número") #cambiar a foreignkey
    numero = models.IntegerField(blank=True, null=True, verbose_name="Número")
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name="direccion")
    latitud = models.CharField(max_length=200, blank=True, null=True, verbose_name="latitud")
    longitud = models.CharField(max_length=200, blank=True, null=True, verbose_name="longitud")
    movil = models.ForeignKey(Movil, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Móvil")
    tipo = models.ForeignKey(TipoServicio, null=True, on_delete=models.SET_NULL, verbose_name="Tipo de servicio")
    salida = models.DateTimeField(blank=True, null=True, verbose_name="Horario de salida")
    regreso = models.DateTimeField(blank=True, null=True, verbose_name="Horario de regreso")
    estado = models.CharField(max_length=50, blank=True, null=True, verbose_name="estado")
    zona = models.CharField(max_length=40, blank=True, null=True)
    encargado = models.ForeignKey(Bombero, blank = True, on_delete=models.SET_NULL, null=True, verbose_name="Encargado")
    def __str__(self):
        return str(self.numero)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

class ServicioPresentes(models.Model):
    servicio = models.ForeignKey(Servicio, blank=True, on_delete=models.SET_NULL, null=True)
    bombero = models.ForeignKey(Bombero, blank=True, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.bombero)

    class Meta:
        verbose_name = "Presente en servicio"
        verbose_name_plural = "Presentes en servicio"

class Ubicacion(models.Model):
    base = models.ForeignKey(Base, null=True, on_delete=models.SET_NULL, verbose_name="Base")
    ubicacion = models.CharField(max_length=200, blank=True, null=True, verbose_name="ubicacion")
    def __str__(self):
        return str(self.base) + ' - ' + self.ubicacion

    class Meta:
        verbose_name = "Ubicacion"
        verbose_name_plural = "Ubicaciones"

class TipoMotor(models.Model):
    tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="tipo de motor")
    def __str__(self):
        return str(self.tipo)

    class Meta:
        verbose_name = "Tipo de motor"
        verbose_name_plural = "Tipos de motores"

class TipoMaterial(models.Model):
    tipo = models.CharField(max_length=200, blank=True, null=True, verbose_name="tipo de material")
    def __str__(self):
        return str(self.tipo)

    class Meta:
        verbose_name = "Tipo de material"
        verbose_name_plural = "Tipos de materiales"

class Material(models.Model):
    nombre = models.CharField(max_length=200,blank=True, null=True, verbose_name="nombre")
    tipo = models.ForeignKey(TipoMaterial, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="tipo")
    motor = models.ForeignKey(TipoMotor, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="tipo de motor")
    potencia = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True, verbose_name="cantidad")
    movil = models.ForeignKey(Movil, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="móvil")
    ubicacion = models.ForeignKey(Ubicacion, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="ubicacion")
    cajonera = models.CharField(max_length=200, blank=True, null=True)
    estado = models.ForeignKey(Estado, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="estado")
    image = models.ImageField(upload_to='materiales/', null=True, blank=True)
    def __str__(self):
        return str(self.nombre) + ' - ' + str(self.ubicacion)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"

class CambioEstado(models.Model):
    material = models.ForeignKey(Material, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="material")
    fecha = models.DateTimeField(blank=True, null=True, verbose_name="fecha de cambio")
    estado = models.ForeignKey(Estado, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="estado")
    encargado = models.ForeignKey(Bombero, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="encargado")
    motivo = models.TextField(max_length=200, blank=True, null=True, verbose_name="tipo de material")
    def __str__(self):
        return str(self.material)

    class Meta:
        verbose_name = "Cambio de estado"
        verbose_name_plural = "Cambios de estado"

class Agenda(models.Model):
    tipos = [
        ("Policia", "Policia"),
        ("Bomberos", "Bomberos"),
        ("Ambulancia","Ambulancia"),
        ("Defensa Civil", "Defensa Civil"),
        ("Otros", "Otros")
    ]
    contacto = models.CharField(max_length=140, blank=True, null=True, verbose_name="nombre")
    tipo = models.CharField(choices=tipos, null=True, blank=True, max_length=120, verbose_name="tipo")
    descripcion = models.CharField(max_length=140, blank=True, null=True, verbose_name="descripcion")
    direccion = models.CharField(max_length=140, blank=True, null=True, verbose_name="direccion")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="teléfono")
    telefono2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="teléfono 2")
    frecuencia = models.CharField(max_length=50, blank=True, null=True, verbose_name="frecuencia")

    def __str__(self):
        return str(self.contacto)

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agenda"

class ReparacionMovil(models.Model):
    movil = models.ForeignKey(Movil, on_delete=models.SET_NULL, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    encargado = models.ForeignKey(Bombero, on_delete=models.SET_NULL, blank=True, null=True)
    tarea = models.CharField(max_length=50, blank=True, null=True, verbose_name="tarea")
    
    def __str__(self):
        return str(self.movil) + ' - ' + str(self.encargado) + ' - ' + str(self.fecha)
    class Meta:
        verbose_name = "Reparación"
        verbose_name_plural = "Reparaciones"