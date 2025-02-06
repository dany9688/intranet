from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from planilla.views import CargarPlanilla, PlanillaDetailView, ServicioView, RepMaterialesView, CheckMaterialesView, CargarServicio, ModificarPlanilla, eliminar_presente, Guia, finalizar_servicio, Guardia, ModificarServicio, custom_404_view

urlpatterns = [
    path("", views.index, name="index"),
    path("mapa/", views.mapa, name="mapa"),
    path('hidrantes/', views.get_geojson, name='get_geojson'),
    path("personal/", views.PersonalView.as_view(), name="personal"), 
    path("listado_planillas/", views.PlanillaView.as_view(), name="listado_planillas"), 
    path("planilla_detail/<int:planilla_id>/", PlanillaDetailView.as_view(), name="planilla"), 
    path('eliminarpresente/<int:presente_id>/', eliminar_presente, name='eliminar_presente'),
    path("modificarplanilla/<int:id>/", ModificarPlanilla.as_view(), name="modificar_planilla"), 
    path("moviles/", views.MovilView.as_view(), name="moviles"), 
    path("materiales/", views.MaterialesView.as_view(), name="materiales"), 
    path("repmateriales/", RepMaterialesView.as_view(), name="reporte_materiales"),
    path("check_materiales/", CheckMaterialesView.as_view(), name="checklist_materiales") ,
    path("servicios/", ServicioView.as_view(), name="servicios"), 
    path("cargar_servicio/", CargarServicio.as_view(), name="cargar_servicios"), 
    path("modificar_servicio/<int:id>/", ModificarServicio.as_view(), name="modificar_servicio"), 
    path("obtener_servicios/", views.obtener_servicios, name="obtener_servicios"),
    path('finalizar_servicio/<int:servicio_id>/', finalizar_servicio, name='finalizar_servicio'),
    path("cargar_planilla/", CargarPlanilla.as_view(), name="cargar_planilla"), 
    path("verificar-numero/", views.verificar_numero, name="verificar_numero"),
    path("cargarcombustible/<int:id>/", views.carga_combustible, name="carga_combustible"),
    path("reparacion_movil/<int:id>/", views.reparacion_movil, name="reparacion_movil"),
    path("cambiarestado/<int:id>/", views.estado_movil, name="cambiar_estado_movil"),
    path("cambiaestbase/", views.estado_base, name="cambiar_estado_base"),
    path("cambiarestadomat/<int:id>/", views.estado_mat, name="cambiar_estado_mat"),
    path("fluidos/<int:id>/", views.fluidos, name="control_fluidos"),
    path("movil/<int:pk>/", views.MovilDetailView.as_view(), name="movil"),
    path("ingresos/<int:id>/", views.ingresos, name="horario_ingresos"),
    path("movil_grafico/", views.movil_grafico, name="movil_grafico"),
    path("materiales_grafico/", views.materiales_grafico, name="materiales_grafico"),
    path("guia/", Guia.as_view(), name="guia"), 
    path("guardia/", Guardia.as_view(), name="guardia"), 
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
