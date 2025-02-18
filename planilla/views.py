from django.shortcuts import get_object_or_404, render, redirect
from .models import *
import re
from django.views import generic, View
from django.contrib.auth import login, authenticate, logout
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import get_current_timezone, is_naive, make_aware, localtime
from django.contrib import messages
from .forms import *
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.db.models import Sum, Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt
import logging
# Configuración de logging
logger = logging.getLogger(__name__)


def index(request):

    print("VISTA EJECUTÁNDOSE")
    grupo_usuario = request.user.groups.values_list('name', flat=True).first()
    print("user: ", request.user, flush=True)
    print("grupo: ",grupo_usuario)
    if grupo_usuario == "Móviles":
        movil = 1
        movil = Movil.objects.get(numero=movil)
        servicio = Servicio.objects.filter(estado='En curso').first()
        print(servicio)
        context ={
            "servicio" : servicio,
            "movil": movil,
        }
        return render (request, 'planilla/mobile.html', context)
    
    elif "Guardia" in grupo_usuario:
        print("entro a guardia")
        base = Base.objects.all().order_by('id')
        moviles = Movil.objects.all()
        bomberos1 = Bombero.objects.all()
        # Obtener los servicios "En curso"
        servicios_en_curso = Servicio.objects.filter(estado="En curso").prefetch_related(
            Prefetch(
                    "moviles_asignados",
                    queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                    to_attr="moviles_list"
                )
            )
        for servicio in servicios_en_curso:
            for movil_data in servicio.moviles_list:
                print(movil_data.movil)
                if movil_data.bomberos:
                    for bombero in movil_data.bomberos.all():  
                        print(bombero.nombre)
                else:
                    print("no hay bomberos")

        cuentas = Base.objects.annotate(
            en_servicio=Count('movil', filter=Q(movil__IDEstado=1)),
            condicional=Count('movil', filter=Q(movil__IDEstado=2)),
            ocupados=Count('movil', filter=Q(movil__IDEstado=4)),
            fuera_servicio=Count('movil', filter=Q(movil__IDEstado=3))
        )

        destacamento_usuario = request.session.get("usuario_destacamento", normalizar_destacamento(request.user.last_name))
        print("🔍 Destacamento del usuario:", destacamento_usuario)


        context = {
            'base': base,
            'moviles': moviles,
            'cuentas': cuentas,
            'servicios': servicios_en_curso,
            'bomberos1': bomberos1,
            'destacamento': destacamento_usuario
        }
        print("destacamento last:" ,destacamento_usuario)
        print("destacamento last:" ,type(destacamento_usuario))
        print(bomberos1)

        print("🔍 Destacamento en sesión tras la redirección:", destacamento_usuario)  # Debug
        return render (request, 'planilla/guardia.html', context)
    
    else:
        hace_10_dias = timezone.now() - timedelta(days=10)
        bases = Base.objects.all().order_by('id')
        novedades = Planilla.objects.filter(fecha__gte=hace_10_dias)
        moviles = Movil.objects.all().order_by('numero')
        servicios = Servicio.objects.filter(estado='En curso')

        # Contexto de la plantilla
        context = {
            "base": bases,
            "novedades": novedades,
            "moviles": moviles,
            "group": grupo_usuario,
            "servicios": servicios,
            }
        return render (request, 'planilla/index.html', context)

def mapa(request):
    return render (request, 'planilla/mapa.html')

def gps(request):
    grupo_usuario = request.user.groups.values_list('name', flat=True).first()

    if grupo_usuario == "Móviles":
        movil = int(request.user.last_name.strip())
        print(movil)
        movil = Movil.objects.get(numero=movil)
        servicio = Servicio.objects.filter(estado='En curso', movil_id=movil.id).first()
        print(servicio)
        context ={
            "servicio" : servicio,
            "movil": movil,
        }
        return render (request, 'planilla/mobile.html', context)
    else:
        return render (request, 'planilla/signin.html', {'error': 'El usuario no tiene permisos para entrar en ese sitio.'})
    
def get_geojson(request):
    # Ruta donde tienes el archivo GeoJSON en tu proyecto Django
    geojson_path = static('planilla/hidrantes.json')
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return JsonResponse(geojson_data, safe=False)

class PersonalView(generic.ListView):
    template_name = "planilla/personal.html" 
    context_object_name = "todo_el_personal"
    def get_queryset(self):
        """Devuelve todos los bomberos"""
        return Bombero.objects.order_by("legajo")

class PlanillaView(generic.ListView):
    template_name = "planilla/listado_planillas.html" 
    context_object_name = "todas_las_planillas"
    def get_queryset(self):
        """Devuelve todos las planillas"""
        return Planilla.objects.order_by("guardia_operativa")

class PlanillaDetailView(View):
    def get(self, request, planilla_id, *args, **kwargs):
        # Log en lugar de print
        logger.info(f"Accediendo a Planilla ID: {planilla_id}")

        # Obtener planilla o lanzar 404
        planilla = get_object_or_404(Planilla, pk=planilla_id)

        # Optimización de consultas
        servicios = Servicio.objects.filter(guardia_operativa=planilla.guardia_operativa)
        bomberos = Bombero.objects.all()
        bom_presentes = GuardiaPresentes.objects.filter(guardia_op_id=planilla_id).select_related("bombero")
        bom_ausentes = GuardiaAusentes.objects.filter(guardia_op_id=planilla_id).select_related("bombero")
        bom_refuerzos = GuardiaRefuerzos.objects.filter(guardia_op_id=planilla_id).select_related("bombero")

        # Contexto de la plantilla
        context = {
            "planilla": planilla,
            "servicios": servicios,
            "bomberos": bomberos,
            "bom_presentes": bom_presentes,
            "bom_ausentes": bom_ausentes,
            "bom_refuerzos": bom_refuerzos,
        }
        
        return render(request, "planilla/planillapdf.html", context)

class MovilDetailView(generic.DetailView):
    model = Movil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.get_object().id
        context['id'] = id
        context['bomberos'] = Bombero.objects.all()
        context['combustible'] = Combustible.objects.filter(movil=id).order_by('fecha')
        context['fluidos'] = Fluidos.objects.filter(movil=id)
        context['reparaciones'] = ReparacionMovil.objects.filter(movil=id)
        return context

def movil_grafico(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data['numero']
        id = int(id)

        combustible = Combustible.objects.filter(movil=id)
        fechasC = {}
        for carga in combustible:
            mes = carga.fecha.month  # Obtener el mes de la fecha
            if mes not in fechasC:
                fechasC[mes] = 0  # Inicializar el mes en el diccionario si no existe

            fechasC[mes] += carga.cantidad  # Sumar la cantidad al mes correspondiente

        fluidos = Fluidos.objects.filter(movil=id)
        fechasA = {}
        fechasAC = {}
        fechasH = {}
        fechasF = {}
        for carga in fluidos:
            mes = carga.fecha.month  
            if mes not in fechasA:
                fechasA[mes] = 0
            if mes not in fechasAC:    
                fechasAC[mes] = 0
            if mes not in fechasH:
                fechasH[mes] = 0
            if mes not in fechasF:
                fechasF[mes] = 0
            fechasA[mes] += carga.agua
            fechasAC[mes] += carga.aceite
            fechasH[mes] += carga.hidraulico
            fechasF[mes] += carga.frenos
        return JsonResponse({"fechasC": fechasC, "fechasA": fechasA, "fechasAC": fechasAC, "fechasH": fechasH, "fechasF": fechasF})
    else:
        print("error")

def materiales_grafico(request):
    if request.method == "GET":
        materiales = Material.objects.all()
        tipos = TipoMaterial.objects.all()
        en_servicio = condicional = f_servicio = 0
        cuentas = {}

        for material in materiales:
            print(material)
            if material.estado.estado == "En servicio":
                en_servicio += material.cantidad
            elif material.estado.estado == "Condicional":
                condicional += material.cantidad
            elif material.estado.estado == "Fuera de servicio":
                condicional += material.cantidad
            else:
                f_servicio += material.cantidad


            for tipo in tipos:
                tipo_material = 0
                if tipo.tipo == material.tipo.tipo:
                    tipo_material += material.cantidad
                    cuentas.setdefault(tipo.tipo, tipo_material)
            
            labels = list(cuentas.keys())
            values = list(cuentas.values())

        print("cuenta: ",cuentas)

        return JsonResponse({"en_servicio": en_servicio, "condicional": condicional, "f_servicio": f_servicio, "labels": labels, "values": values})
    else:
        print("error")
        
class MovilView(generic.ListView):
    model = Movil
    template_name = "planilla/moviles.html" 
    context_object_name = "todo_los_moviles"
    ordering = ["numero"]  # Ordena de menor a mayor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bomberos'] = Bombero.objects.all()
        context['servicios'] = Servicio.objects.all()
        context['estados'] = Estado.objects.all()
        context['cuarteles'] = Base.objects.all()
        return context

class InventarioMovil(generic.ListView):
    model = Movil
    template_name = "planilla/inventario_movil.html" 
    context_object_name = "todo_los_moviles"
    ordering = ["numero"]  # Ordena de menor a mayor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Estado.objects.all()
        context['cuarteles'] = Base.objects.all()
        return context
        
class MaterialesView(generic.ListView):
    model = Material
    template_name = "planilla/materiales.html" 
    context_object_name = "todo_los_materiales"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Estado.objects.all()
        context['bomberos'] = Bombero.objects.all()
        context['cambios'] = CambioEstado.objects.all().order_by('-fecha')
        return context
    
class RepMaterialesView(View): #createView
    def get(self, request):
        materiales_por_estado = Material.objects.values('nombre', 'estado__estado') \
        .annotate(total_cantidad=Sum('cantidad')) \
        .order_by('nombre', 'estado__estado')
        materiales = []
        for item in materiales_por_estado:
            materiales.append({
                'nombre':item['nombre'],
                'estado': item['estado__estado'],
                'cantidad': item['total_cantidad']
            })
        print(materiales)
        return render (request, 'planilla/reporte_materiales.html', {'materiales': materiales})
    
class CheckMaterialesView(View): #createView
    def get(self, request, id):
        movil=id
        materiales = Material.objects.filter(movil=movil).order_by('cajonera')
        print(materiales)

        return render (request, 'planilla/check_materiales.html', {'materiales': materiales, 'movil': movil})

class ServicioView(View):
    def get(self, request):
        servicios = Servicio.objects.all().prefetch_related(
            Prefetch(
                    "moviles_asignados",
                    queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                    to_attr="moviles_list"
                )
            )
        print(servicios)
        context = {
            'servicios': servicios
        }
        return render (request, 'planilla/servicios.html', context)

class CargarServicio(View):
    def get(self, request):
        moviles = Movil.objects.all().order_by('numero')
        bomberos = Bombero.objects.all()
        tipo_servicios = TipoServicio.objects.all()
        destacamento = request.session.get("destacamento", request.user.last_name)  # Recupera destacamento o usa last_name

        context = {
            "moviles": moviles,
            "bomberos": bomberos,
            "tipo_servicios": tipo_servicios,
            "destacamento": destacamento
        }
        return render (request, 'planilla/cargar_servicio.html', context)
    
    def post(self, request):
        print("entro a post")

        guardia = request.POST.get("guardia")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        numero = request.POST.get("numero")
        salida = request.POST.get("salida")
        tipo_servicio_id = request.POST.get("tiposervicio")
        encargado_id = request.POST.get("encargado")
        nombre = request.POST.get("denunciante")
        telefono = request.POST.get("telefono")
        base = request.POST.get('zona')


        # Validar datos requeridos
        if not (guardia and address and latitude and longitude and numero and salida and tipo_servicio_id and encargado_id):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("cargar_servicio")

        try:

            servicios = Servicio(
                guardia_operativa = guardia,
                direccion=address,
                latitud=latitude,
                longitud=longitude,
                estado="En curso", 
                numero=numero,
                salida=salida,
                zona=base,
                tipo_id=tipo_servicio_id,
                encargado_id=encargado_id,
                nombre_denunciante=nombre,
                telefono_denunciante=telefono,
            )
            servicios.save()

            print(f"🔍 Comparando: normalizar_destacamento({request.user.last_name}) == {base}")
            print(f"🔍 Normalizado: {normalizar_destacamento(request.user.last_name)}")
            print(f"🔍 Base desde el POST: {base}")

            destacamento = normalizar_destacamento(base)  # 🔥 Usa `base`, no `request.user.last_name`

            mensaje = f'Se ha creado un nuevo servicio en {base}'

            print(f"🔍 Intentando enviar mensaje a: notificacion_{destacamento}")  # Debug
            print(f"🔍 Mensaje: {mensaje}")  # Debug

            # Enviar notificación vía WebSockets
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notificacion_{destacamento}',  # 🔥 Notifica al destacamento correcto
                {
                    'type': 'enviar_notificacion',
                    'mensaje': mensaje
                }
            )
            print("✅ `group_send()` ejecutado con éxito")  # Debug
            messages.success(request, "Servicio cargado correctamente.")
            messages.success(request, "Se envió la alerta.")
            # Guarda el destacamento del usuario logueado
            request.session["usuario_destacamento"] = normalizar_destacamento(request.user.last_name)

            # Guarda el destacamento del servicio creado
            request.session["servicio_destacamento"] = normalizar_destacamento(base)

            request.session.modified = True
            request.session.save()

            print(f"✅ Sesión usuario: {request.session['usuario_destacamento']}")
            print(f"✅ Sesión servicio: {request.session['servicio_destacamento']}")


            return redirect ('/')
        
        except Exception as e:
                messages.error(request, f"Error al cargar el servicio: {e}")
                return redirect("cargar_servicio")

class ServicioDetail(View):
    def get(self, request, id):
        bomberos = Bombero.objects.all()
        moviles = Movil.objects.all()
        servicio = get_object_or_404(
            Servicio.objects.prefetch_related(
                Prefetch(
                    "moviles_asignados",
                    queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                    to_attr="moviles_list"
                )
            ),
            id=id
        )
        cantidad_moviles = len(servicio.moviles_list)
        cantidad_bomberos = sum(len(movil.bomberos.all()) for movil in servicio.moviles_list)

        fecha_formateada = servicio.salida.strftime("%Y-%m-%dT%H:%M") if servicio.salida else ""

        context = {
            "servicio": servicio,
            "fecha": fecha_formateada,
            "bomberos": bomberos,
            "moviles": moviles,
            'cantidad_moviles': cantidad_moviles,
            'cantidad_bomberos': cantidad_bomberos
        }
        return render (request, 'planilla/servicio_detail.html', context)

def asignarmovil(request, servicio_id):
    if request.method == "POST":
        servicio = get_object_or_404(Servicio, id=servicio_id)
        movil_id = request.POST['movil']
        bomberos_ids = request.POST.getlist("bomberos")  # Obtiene lista de IDs

        if movil_id:
            movil = get_object_or_404(Movil, id=movil_id)
            servicio_movil, created = ServicioMovil.objects.get_or_create(servicio=servicio, movil=movil)
            servicio_movil.bomberos.set(bomberos_ids)  # Asigna la lista de bomberos seleccionados
            servicio_movil.save()

            # Actualiza el estado del móvil
            movil.intervenciones += 1
            estado = get_object_or_404(Estado, estado="Ocupado")
            movil.IDEstado_id = int(estado.id)
            movil.save()

            # Obtiene los datos actualizados para enviar como JSON
            bomberos_data = list(servicio_movil.bomberos.values("id", "nombre", "apellido"))

            return redirect ('/servicio_detail/'+str(servicio_id))

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=400)

class ModificarServicio(View):
    def get(self, request, id):
        moviles = Movil.objects.all().order_by('numero')
        bomberos = Bombero.objects.all()
        tipo_servicios = TipoServicio.objects.all()
        servicio = get_object_or_404(
            Servicio.objects.prefetch_related(
                Prefetch(
                    "moviles_asignados",
                    queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                    to_attr="moviles_list"
                )
            ),
            id=id
        )
        cantidad_moviles = len(servicio.moviles_list)
        cantidad_bomberos = sum(len(movil.bomberos.all()) for movil in servicio.moviles_list)
        fecha_formateada = servicio.salida.strftime("%Y-%m-%dT%H:%M") if servicio.salida else ""

        context = {
            'fecha': fecha_formateada,
            'moviles': moviles,
            'bomberos': bomberos,
            'tipo_servicios': tipo_servicios,
            'servicio': servicio,
            'cantidad_moviles': cantidad_moviles,
            'cantidad_bomberos': cantidad_bomberos
        }
        return render (request, 'planilla/modificar_servicio.html', context)
    
    def post(self, request, id):
        print("entro a post")
        anterior = Servicio.objects.get(id=id)
        anterior.guardia_operativa = request.POST['guardia']
        anterior.direccion = request.POST['address']
        anterior.latitud = request.POST['latitude']
        anterior.longitud = request.POST['longitude']
        print('latitud', request.POST['latitude'])
        print('longitud', request.POST['longitude'])
        anterior.estado="En curso"
        anterior.zona = request.POST['zona']
        anterior.numero = request.POST['numero']
        # anterior.movil_id = int(request.POST['movil'])
        anterior.salida = request.POST['salida']
        anterior.tipo_id = int(request.POST['tiposervicio'])
        print(anterior.tipo.id)
        anterior.encargado.id = int(request.POST['encargado'])
        anterior.nombre_denunciante = request.POST['denunciante']
        anterior.telefono_denunciante = request.POST['telefono']
        anterior.save()

        return redirect ('guardia')
    
def obtener_servicios(request):

    servicios = list(Servicio.objects.filter(estado="En curso").values("direccion", "latitud", "longitud", "tipo"))
    tiposervicio = list(TipoServicio.objects.values("id", "tipo"))
    print(servicios)
    return JsonResponse({"servicios": servicios, "tiposervicio": tiposervicio})

def servicio_movil(request, movil):
    servicios = list(Servicio.objects.filter(estado="En curso", movil=movil).values("direccion", "latitud", "longitud", "movil", "tipo"))
    moviles = list(Movil.objects.values("id", "numero", "IDTipo"))
    tipomovil = list(TipoMovil.objects.values("id", "tipo"))
    tiposervicio = list(TipoServicio.objects.values("id", "tipo"))
    print(servicios)
    return JsonResponse({"servicios": servicios, "moviles": moviles, "tipomovil": tipomovil, "tiposervicio": tiposervicio})

class ModificarPlanilla(View):
    def get(self, request, id):
        print(request.user.first_name)
        try:
            base = Base.objects.get(base=request.user.groups.values_list('name', flat=True).first())
            if base:
                print("uscarga: ", base.id)
            else:
                print("no se encontró")
            planilla = Planilla.objects.get(id=id)
            guardia = planilla.id
            print('guardia', guardia)
            print('ingreso encar', planilla.ingreso_encargado)
            fecha_formateada = planilla.fecha.strftime("%Y-%m-%d") if planilla.fecha else ""
            print(fecha_formateada)

            presentes = GuardiaPresentes.objects.filter(guardia_op=guardia)
            ausentes = GuardiaAusentes.objects.filter(guardia_op=guardia)
            refuerzos = GuardiaRefuerzos.objects.filter(guardia_op=guardia)
            bomberos = Bombero.objects.filter(IDBase_id=base.id)
            moviles =  Movil.objects.all()
            compania = Compania.objects.all()
            tipo_servicios = TipoServicio.objects.all()        

            return render (request, 'planilla/modificar_planilla.html', {'planilla': planilla, 'fecha':fecha_formateada, 'bomberos': bomberos, 'presentes': presentes, 'ausentes': ausentes, 'refuerzos': refuerzos, 'moviles': moviles, 'compania':compania, 'tipo_servicios':tipo_servicios, 'base': base.base, 'base_id': base.id})
        except Exception as err:
            print(f"Oops! {err}")

    def post(self, request, id):

        ingresoChofer = request.POST['ingresoChofer']
        if ingresoChofer == "":
            ingresoChofer = None

        print("BASE: ", request.POST.get('base', False))

        # Obtener la instancia de la planilla
        planilla = Planilla.objects.get(id=id)

        ingresoChofer = request.POST['ingresoChofer']
        if ingresoChofer == "":
            ingresoChofer = None
        # Actualizar los valores manualmente
        planilla.guardia_operativa = request.POST['guardiaoperativa']
        planilla.fecha = request.POST['fecha']
        planilla.guardia = request.POST['guardia']
        planilla.cabecera_id = int(request.POST['cabecera'])
        planilla.oficial_id = request.POST['oficial']
        planilla.cuartelero = request.POST['cuartelero']
        planilla.recibido = request.POST['recibido']
        planilla.gastado = request.POST['gastos']
        planilla.concepto = request.POST['concepto']
        planilla.entregado = request.POST['entregado']
        planilla.encargado_id = request.POST['encargado']
        planilla.ingreso_encargado = request.POST["ingresoEncargado"]
        planilla.chofer_id = request.POST['chofer']
        planilla.ingreso_chofer = ingresoChofer
        planilla.tareas = request.POST['tareas']
        planilla.novedades = request.POST['novedades']
        planilla.cuartel_id = int(request.POST['base'])

        # Guardar los cambios en la base de datos
        planilla.save()

        data = request.POST
        resultadoPresentes = {}
        index = 0
        while True:
            presente_key = f"presente-{index}"
            time_key = f"time-{index}"
            fecha_key = f"fecha-{index}"

            if presente_key in data and time_key in data:
                # Agregar al diccionario organizado
                resultadoPresentes[index] = {
                    "bombero_id": int(data[presente_key]),
                    "ingreso": data[time_key],
                    "fecha": request.POST["fecha"]
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("PRESENTES: ", resultadoPresentes)
        if resultadoPresentes:
            for presente in resultadoPresentes.values():
                personal_guardia = GuardiaPresentes.objects.create(
                    guardia_op_id=planilla.id, 
                fecha = presente['fecha'],
                bombero_id=presente["bombero_id"], 
                ingreso=presente["ingreso"],
                encargado = False)
                print(personal_guardia)
            personal_guardia.save()

            encargado_guardia = GuardiaPresentes.objects.create(
                guardia_op_id=planilla.id, 
                fecha = presente['fecha'],
                bombero_id=request.POST['encargado'],
                ingreso=request.POST["ingresoEncargado"],
                encargado = True)
            encargado_guardia.save()

            if ingresoChofer == "":
                chofer_guardia = GuardiaPresentes.objects.create(
                guardia_op_id=planilla.id, 
                fecha = presente['fecha'],
                bombero_id=request.POST["chofer"], 
                ingreso=ingresoChofer,
                chofer = True)
                chofer_guardia.save()

        resultadoAusente = {}
        index = 0
        while True:
            ausente_key = f"ausente-{index}"
            time_key = f"time-{index}"
            
            if ausente_key in data:
                # Agregar al diccionario organizado
                resultadoAusente[index] = {
                    "bombero_id": int(data[ausente_key])
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("Ausente: ", resultadoAusente)
        if resultadoAusente:
            for ausente in resultadoAusente.values():
                ausente_guardia = GuardiaAusentes.objects.create(
                    guardia_op_id=planilla.id, 
                    bombero_id=ausente["bombero_id"]
                )
                print(ausente_guardia)
            ausente_guardia.save()

        resultadoRefuerzo = {}
        index = 0
        while True:
            refuerzo_key = f"refuerzo-{index}"
            
            if refuerzo_key in data:
                # Agregar al diccionario organizado
                resultadoRefuerzo[index] = {
                    "bombero_id": int(data[refuerzo_key])
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("Refuerzo: ", resultadoRefuerzo)
        if resultadoRefuerzo:
            for refuerzo in resultadoRefuerzo.values():
                refuerzo_guardia = GuardiaRefuerzos.objects.create(
                    guardia_op_id=planilla.id, 
                    bombero_id=refuerzo["bombero_id"]
                    )
                print(refuerzo_guardia)
            refuerzo_guardia.save()

        return redirect ('listado_planillas')
    
class CargarPlanilla(View):
    def get(self, request):
        print(request.user.first_name)
        try:
            base = Base.objects.get(base=request.user.groups.values_list('name', flat=True).first())
            if base:
                print("uscarga: ", base.id)
            else:
                print("no se encontró")
            bomberos = Bombero.objects.filter(IDBase_id=base.id)
            moviles =  Movil.objects.all()
            compania = Compania.objects.all()
            tipo_servicios = TipoServicio.objects.all()        

            return render (request, 'planilla/cargar_planilla.html', {'bomberos': bomberos, 'moviles': moviles, 'compania':compania, 'tipo_servicios':tipo_servicios, 'base': base.base, 'base_id': base.id})
        except Exception as err:
            print(f"Oops! {err}")

    def post(self, request):

        ingresoChofer = request.POST['ingresoChofer']
        if ingresoChofer == "":
            ingresoChofer = None

        print("BASE: ", request.POST.get('base', False))

        planilla = Planilla(guardia_operativa=request.POST['guardiaoperativa'], fecha=request.POST['fecha'], guardia=request.POST['guardia'], cabecera_id=int(request.POST['cabecera']), oficial_id=request.POST['oficial'], cuartelero=request.POST['cuartelero'], recibido=request.POST['recibido'], gastado=request.POST['gastos'], concepto=request.POST['concepto'], entregado=request.POST['entregado'], encargado_id=request.POST['encargado'], ingreso_encargado=request.POST["ingresoEncargado"], chofer_id=request.POST['chofer'], ingreso_chofer=ingresoChofer, tareas = request.POST['tareas'], novedades=request.POST['novedades'], cuartel_id=int(request.POST['base'])) 

        planilla.save()

        data = request.POST
        resultadoPresentes = {}
        index = 0
        while True:
            presente_key = f"presente-{index}"
            time_key = f"time-{index}"
            fecha_key = f"fecha-{index}"

            if presente_key in data and time_key in data:
                # Agregar al diccionario organizado
                resultadoPresentes[index] = {
                    "bombero_id": int(data[presente_key]),
                    "ingreso": data[time_key],
                    "fecha": request.POST["fecha"]
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("PRESENTES: ", resultadoPresentes)
        for presente in resultadoPresentes.values():
            personal_guardia = GuardiaPresentes.objects.create(
                guardia_op_id=planilla.id, 
            fecha = presente['fecha'],
            bombero_id=presente["bombero_id"], 
            ingreso=presente["ingreso"])
            print(personal_guardia)
        personal_guardia.save()

        encargado_guardia = GuardiaPresentes.objects.create(
            guardia_op_id=planilla.id, 
            fecha = presente['fecha'],
            bombero_id=request.POST['encargado'],
            ingreso=request.POST["ingresoEncargado"])
        encargado_guardia.save()

        if ingresoChofer == "":
            chofer_guardia = GuardiaPresentes.objects.create(
            guardia_op_id=planilla.id, 
            fecha = presente['fecha'],
            bombero_id=request.POST["chofer"], 
            ingreso=ingresoChofer)
            chofer_guardia.save()

        resultadoAusente = {}
        index = 0
        while True:
            ausente_key = f"ausente-{index}"
            time_key = f"time-{index}"
            
            if ausente_key in data:
                # Agregar al diccionario organizado
                resultadoAusente[index] = {
                    "bombero_id": int(data[ausente_key])
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("Ausente: ", resultadoAusente)
        if resultadoAusente:
            for ausente in resultadoAusente.values():
                ausente_guardia = GuardiaAusentes.objects.create(
                    guardia_op_id=planilla.id, 
                    bombero_id=ausente["bombero_id"]
                )
                print(ausente_guardia)
            ausente_guardia.save()

        resultadoRefuerzo = {}
        index = 0
        while True:
            refuerzo_key = f"refuerzo-{index}"
            
            if refuerzo_key in data:
                # Agregar al diccionario organizado
                resultadoRefuerzo[index] = {
                    "bombero_id": int(data[refuerzo_key])
                }
                index += 1
            else:
                # Salir del bucle si no hay más claves
                break

        print("Refuerzo: ", resultadoRefuerzo)
        if resultadoRefuerzo:
            for refuerzo in resultadoRefuerzo.values():
                refuerzo_guardia = GuardiaRefuerzos.objects.create(
                    guardia_op_id=planilla.id, 
                    bombero_id=refuerzo["bombero_id"]
                    )
                print(refuerzo_guardia)
            refuerzo_guardia.save()

        return render (request, 'planilla/servicios.html')

class Guia(View):
    def get(self, request):
        contactos = Agenda.objects.all()
        return render (request, 'planilla/guia.html', {'contactos': contactos})

class Guardia(View):
    def get(self, request):
        servicios = Servicio.objects.all()
        base = Base.objects.all().order_by('id')
        moviles = Movil.objects.all()
        cuentas = Base.objects.annotate(
            en_servicio=Count('movil', filter=Q(movil__IDEstado=1)),
            condicional=Count('movil', filter=Q(movil__IDEstado=2)),
            ocupados=Count('movil', filter=Q(movil__IDEstado=4)),
            fuera_servicio=Count('movil', filter=Q(movil__IDEstado=3))
        )

        return render (request, 'planilla/guardia.html', {'servicios': servicios, 'base': base, 'moviles': moviles, 'cuentas': cuentas})

def verificar_numero(request):
    if request.method == "POST":
        data = json.loads(request.body)
        numero = data.get("numero")
        print(numero)
        # Verificar si el número ya existe en la base de datos
        existePlanilla = Planilla.objects.filter(guardia_operativa=numero).exists()
        existeServicio = Servicio.objects.filter(numero=numero).exists()
        
        print("Planilla:", existePlanilla)
        print("Servicio: ", existeServicio)

        # Retornar la respuesta en formato JSON
        return JsonResponse({"existePlanilla": existePlanilla, "existeServicio": existeServicio})
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

def carga_combustible(request, id):
    if request.method == "POST":
        movil = Movil.objects.get(id=id)
        tz = get_current_timezone()  # Obtener la zona horaria de Django

        # Convertir la fecha del formulario
        fecha = datetime.strptime(request.POST['fecha'], "%Y-%m-%dT%H:%M")
        if is_naive(fecha):  # Si la fecha es naive, la convertimos a aware
            fecha = make_aware(fecha, timezone=tz)

        # Verificar si movil.ultima_carga es None
        if movil.ultima_carga is None:
            ultima_carga = make_aware(datetime.min, timezone=tz)  # Usar fecha mínima
        else:
            ultima_carga = movil.ultima_carga
            if is_naive(ultima_carga):
                ultima_carga = make_aware(ultima_carga, timezone=tz)

        # Contar los servicios desde la última carga hasta ahora
        servicios_realizados = Servicio.objects.filter(
            moviles_asignados__movil_id=movil.id,
            salida__gte=ultima_carga,  # Servicios desde la última carga (asegurado que no es None)
            regreso__lte=fecha  # Hasta la fecha del formulario
        ).count()

        print(f"Servicios realizados desde la última carga: {servicios_realizados}")

        movil.ultima_carga = fecha
        movil.intervenciones = servicios_realizados  # Actualizar con el conteo real
        movil.save()

        combustible = Combustible(
            fecha=fecha, 
            cantidad=request.POST['cantidad'], 
            movil_id=id, 
            encargado_id=request.POST['encargado']
        )
        combustible.save()
        
        return redirect('moviles')
    else:
        print("NO CORRESPONDE EL MÉTODO")

def reparacion_movil(request, id):
    if request.method == "POST":
        ahora = datetime.now().replace(microsecond=0)

        reparacion = ReparacionMovil(movil_id=int(id), fecha=ahora, encargado_id=int(request.POST['encargado']), tarea=request.POST['tarea'])
        reparacion.save()
        return redirect(f'/movil/{id}')
    else:
        print("NO CORRESPONDE EL METODO")

def fluidos(request, id):
    if request.method == "POST":
        print("paso por carga")
        ahora = datetime.now()

        movil = Movil.objects.get(id=id)
        movil.ultima_fluidos = ahora
        movil.save()

        fluidos = Fluidos(fecha=ahora, agua=request.POST['agua'], aceite=request.POST['aceite'], hidraulico=request.POST['hidraulico'], frenos=request.POST['frenos'], movil_id=id, encargado_id=request.POST['encargado'], tanque=request.POST['tanque'], bomba=request.POST['bomba'], luces=request.POST['luces'], sirena=request.POST['sirena'], comentario=request.POST['comentario'])
        fluidos.save()
        return redirect('moviles')
    else:
        print("NO CORRESPONDE EL METODO")

def estado_movil(request, id):
    if request.method == "POST":
        movil = Movil.objects.get(id=id)
        movil.IDEstado_id = int(request.POST['estado'])
        movil.save()

        return redirect('moviles')
    else:
        print("NO CORRESPONDE EL METODO")

def estado_base(request):
    if request.method == "POST":
        base = Base.objects.get(id=request.POST['base'])
        base.estado = request.POST['estado']
        base.save()

        return redirect('guardia')
    else:
        print("NO CORRESPONDE EL METODO")

def estado_mat(request, id):
    if request.method == "POST":
        # Obtener la instancia del estado
        estado = Estado.objects.get(pk=int(request.POST['estado']))
        # Obtener la instancia del bombero

        bombero = Bombero.objects.get(pk=int(request.POST['bombero']))
        material = Material.objects.get(id=id)
        material.estado = estado
        material.save()



        print(material, datetime.now(), int(request.POST['estado']), int(request.POST['bombero']), request.POST['motivo'])
        novedad = CambioEstado(material=material, fecha=datetime.now(), estado=estado, encargado=bombero, motivo=request.POST['motivo'])
        novedad.save()

        return redirect('materiales')
    else:
        print("NO CORRESPONDE EL METODO")

def ingresos(request, id):
    if request.method == "GET":
        print("paso por carga")

        guardias = GuardiaPresentes.objects.filter(bombero_id=id)
        bombero = Bombero.objects.get(id=id)
        
        anio = request.GET['anio']
        mes = request.GET['mes']
        ingresos = []
        for guardia in guardias:
            print("mes",guardia.fecha.month)
            print("mes",guardia.fecha.year)
            print(id)
            if guardia.fecha.year == int(anio):
                if guardia.fecha.month == int(mes):
                    ingresos.append(guardia)
        print("INGRESOS: ", ingresos)
        return render(request, 'planilla/ingresos.html', {'ingresos':ingresos, 'bombero': bombero})
    else:
        print("NO CORRESPONDE EL METODO")

def eliminar_presente(request, presente_id):
    if request.method == "DELETE":
        presente = GuardiaPresentes.objects.get(id=presente_id)
        presente.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def eliminar_movil(request, movil_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Cargar el JSON del request
            servicio_id = data.get("servicio")  # Obtener el ID del servicio
            # Verifica que se obtuvo el servicio_id
            if not servicio_id:
                return JsonResponse({"error": "No se recibió el ID del servicio"}, status=400)
            print(list(ServicioMovil.objects.all()))

            servicio_movil = ServicioMovil.objects.get(movil_id=movil_id, servicio_id=servicio_id)
            servicio_movil.delete()

            movil = get_object_or_404(Movil, id=movil_id)
            movil.intervenciones -= 1
            estado = get_object_or_404(Estado, estado="En servicio")
            movil.IDEstado_id = int(estado.id)
            movil.save()

            return JsonResponse({"success": True}, status=200)
        except ServicioMovil.DoesNotExist:
            return JsonResponse({"error": "Móvil no encontrado"}, status=404)

    return JsonResponse({"error": "Método no permitido"}, status=405)

def finalizar_servicio(request, servicio_id):
    if request.method == "GET":
        servicio = Servicio.objects.get(id=servicio_id)
        servicio.regreso = datetime.now()
        servicio.estado = "Cerrado"
        servicio.save()

        servicio_moviles = get_object_or_404(
            Servicio.objects.prefetch_related(
                Prefetch(
                    "moviles_asignados",
                    queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                    to_attr="moviles_list"
                )
            ),
            id=servicio_id
        )

        for movil_data in servicio_moviles.moviles_list:
            print(movil_data.movil)
            movil = get_object_or_404(Movil, id=movil_data.movil.id)
            estado = get_object_or_404(Estado, estado="En servicio")
            movil.IDEstado_id = int(estado.id)
            movil.save()

        return redirect ('/')
    return JsonResponse({"error": "Método no permitido"}, status=405)

def signin(request):
    if request.method == "GET":
        # Regenerar el token CSRF para evitar problemas con cookies antiguas

        get_token(request)
        return render(request, 'planilla/signin.html')
    elif request.method == "POST":
        try:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'planilla/signin.html', {'error': 'El usuario no existe en la base de datos.'})
            login(request, user)
            return redirect('/')
        except Exception as err:
            print(f"Oops! {err}")
            return render(request, 'planilla/signin.html', {'error': 'Algo falló.'})
        
def signout(request):
    logout(request)
    
    # Crear una nueva respuesta para eliminar cookies CSRF y sesión
    response = redirect('signin')
    response.delete_cookie('csrftoken')
    response.delete_cookie('sessionid')  # También eliminamos la sesión
    return response

def normalizar_destacamento(nombre):
    """ Convierte nombres como 'Destacamento N°2' en 'destacamento_2' """
    if not nombre:
        return ""  # Si es None o vacío, devuelve string vacío
    
    nombre = nombre.lower().replace("°", "").strip()  # Minúsculas, sin espacios extras
    nombre = re.sub(r"\s+", "_", nombre)  # Reemplaza espacios por "_"
    nombre = re.sub(r"[^a-z0-9_]", "", nombre)  # Elimina caracteres especiales excepto "_"
    return nombre

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)