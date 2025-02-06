from django.contrib import admin
from .models import *

admin.site.register(Bombero)
admin.site.register(Jerarquia)
admin.site.register(Base)
admin.site.register(TipoMovil)
admin.site.register(Movil)
admin.site.register(Estado)
admin.site.register(TipoServicio)
admin.site.register(Servicio)
admin.site.register(Compania)
admin.site.register(Planilla)
admin.site.register(Fluidos)
admin.site.register(Combustible)
admin.site.register(GuardiaPresentes)
admin.site.register(GuardiaAusentes)
admin.site.register(GuardiaRefuerzos)
admin.site.register(Ubicacion)
admin.site.register(Material)
admin.site.register(TipoMaterial)
admin.site.register(TipoMotor)
admin.site.register(Agenda)


# Register your models here.
admin.site.site_header = 'Bomberos Voluntarios de Morón'
admin.site.index_title = 'Administración de la Intranet'
admin.site.site_title = 'Intranet'