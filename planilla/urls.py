from django.urls import path
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from . import views
from planilla.views import CargarPlanilla, PlanillaDetailView, ServicioView, RepMaterialesView, CheckMaterialesView, CargarServicio, ModificarPlanilla, eliminar_presente, Guia, finalizar_servicio, Guardia, ModificarServicio, ServicioDetail, eliminar_movil, TV, TabletView, NovedadesView

urlpatterns = [
    # path("", views.index, name="index"),
    path('', login_required(views.index, login_url='/signin/'), name='index'),
    path("mapa/", login_required(views.mapa, login_url='/signin/'), name="mapa"),
    path("gps/", login_required(views.gps, login_url='/signin/'), name="gps"),
    path('hidrantes/', login_required(views.get_geojson, login_url='/signin/'), name='get_geojson'),
    path("personal/", login_required(views.PersonalView.as_view(), login_url='/signin/'), name="personal"), 
    path("listado_planillas/", login_required(views.PlanillaView.as_view(), login_url='/signin/'), name="listado_planillas"), 
    path("novedades/", login_required(NovedadesView.as_view(), login_url='/signin/'), name="novedades"), 
    path("planilla_detail/<int:planilla_id>/", login_required(PlanillaDetailView.as_view(), login_url='/signin/'), name="planilla"), 
    path('eliminarpresente/<int:presente_id>/', login_required(eliminar_presente, login_url='/signin/'), name='eliminar_presente'),
    path("modificarplanilla/<int:id>/", login_required(ModificarPlanilla.as_view(), login_url='/signin/'), name="modificar_planilla"), 
    path("moviles/", login_required(views.MovilView.as_view(), login_url='/signin/'), name="moviles"), 
    path("materiales/", login_required(views.MaterialesView.as_view(), login_url='/signin/'), name="materiales"), 
    path("repmateriales/", login_required(RepMaterialesView.as_view(), login_url='/signin/'), name="reporte_materiales"),
    path("inventario_movil/", login_required(views.InventarioMovil.as_view(), login_url='/signin/'), name="listado_moviles_materiales"),
    path("check_material_movil/<int:id>/", views.CheckMaterialesView.as_view(), name="check_list_materiales"),
    path("servicios/", login_required(ServicioView.as_view(), login_url='/signin/'), name="servicios"),
    path("cargar_servicio/", login_required(CargarServicio.as_view(), login_url='/signin/'), name="cargar_servicios"), 
    path("servicio_detail/<int:id>", login_required(ServicioDetail.as_view(), login_url='/signin/'), name="servicio_detail"), 
    path("modificar_servicio/<int:id>/", login_required(ModificarServicio.as_view(), login_url='/signin/'), name="modificar_servicio"), 
    path("asignarmovil/<int:servicio_id>/", login_required(views.asignarmovil, login_url='/signin/'), name="planilla"), 
    path("eliminar_movil/<int:movil_id>/", eliminar_movil, name="eliminar_movil"),
    path("obtener_servicios/", login_required(views.obtener_servicios, login_url='/signin/'), name="obtener_servicios"),
    path("servicio_movil/<int:movil>", login_required(views.servicio_movil, login_url='/signin/'), name="servicio_movil"),
    path('finalizar_servicio/<int:servicio_id>/', login_required(finalizar_servicio, login_url='/signin/'), name='finalizar_servicio'),
    path("cargar_planilla/", login_required(CargarPlanilla.as_view(), login_url='/signin/'), name="cargar_planilla"),
    path("verificar-numero/", login_required(views.verificar_numero, login_url='/signin/'), name="verificar_numero"),
    path("cargarcombustible/<int:id>/", login_required(views.carga_combustible, login_url='/signin/'), name="carga_combustible"),
    path("reparacion_movil/<int:id>/", login_required(views.reparacion_movil, login_url='/signin/'), name="reparacion_movil"),
    path("cambiarestado/<int:id>/", login_required(views.estado_movil, login_url='/signin/'), name="cambiar_estado_movil"),
    path("cambiaestbase/", login_required(views.estado_base, login_url='/signin/'), name="cambiar_estado_base"),
    path("cambiarestadomat/<int:id>/", login_required(views.estado_mat, login_url='/signin/'), name="cambiar_estado_mat"),
    path("fluidos/<int:id>/", login_required(views.fluidos, login_url='/signin/'), name="control_fluidos"),
    path("movil/<int:pk>/", login_required(views.MovilDetailView.as_view(), login_url='/signin/'), name="movil"),
    path("ingresos/<int:id>/", login_required(views.ingresos, login_url='/signin/'), name="horario_ingresos"),
    path("movil_grafico/", login_required(views.movil_grafico, login_url='/signin/'), name="movil_grafico"),
    path("materiales_grafico/", login_required(views.materiales_grafico, login_url='/signin/'), name="materiales_grafico"),
    path("guia/", login_required(Guia.as_view(), login_url='/signin/'), name="guia"),
    path("guardia/", login_required(Guardia.as_view(), login_url='/signin/'), name="guardia"),
    path("tablet/<str:movil>/", views.TabletView.as_view(), name="tablet_view"),
    path("tv/<int:base>/", login_required(TV.as_view(), login_url='/signin/'), name="tv"),
    path("signin_movil/", views.signinMovil, name="signin_movil"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)