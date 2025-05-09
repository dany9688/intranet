from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from collections import OrderedDict
import re
from django.views import generic, View
from django.contrib.auth import login, authenticate, logout
from datetime import timedelta, datetime, time, date
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import get_current_timezone, is_naive, make_aware
from django.contrib import messages
from .forms import *
from django.http import JsonResponse
from django.urls import reverse
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.db.models import Sum, Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt
import requests
import logging
from operator import attrgetter

# Configuración de logging
logger = logging.getLogger(__name__)


def index(request):

    print("VISTA EJECUTÁNDOSE")
    grupo_usuario = request.user.groups.values_list('name', flat=True).first()
    print("user: ", request.user, flush=True)
    print("grupo: ",grupo_usuario)
    if "Guardia" in grupo_usuario:
        print("entro a guardia")
        base = Base.objects.all().order_by('id')
        moviles = Movil.objects.all().order_by('numero')
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


class NovedadesView(generic.View):
    template_name = "planilla/novedades.html"

    def get(self, request, *args, **kwargs):
        logger.info("Accediendo a novedades operativas")

        # 1. Rango de los últimos 30 días
        hace_15_dias = timezone.now() - timedelta(days=15)

        # 2. Planillas (día y noche) con sus relaciones de presentes/ausentes/refuerzos
        planillas = (
            Planilla.objects
            .filter(fecha__gte=hace_15_dias)
            .select_related("cuartel", "cabecera", "oficial", "encargado", "chofer")
            .prefetch_related(
                "guardia_presentes__bombero",
                "guardia_ausentes__bombero",
                "guardia_refuerzos__bombero",
            )
            .order_by("fecha", "guardia")
        )

        # 3. Servicios realizados vinculados por fecha de salida
        servicios = (
            Servicio.objects
            .filter(salida__date__gte=hace_15_dias)
            .select_related("tipo", "encargado")
            .order_by("salida")
        )

        # 4. Cambios de estado en materiales, cargas de combustible, controles de fluidos y reparaciones
        cambios_material = (
            CambioEstado.objects
            .filter(fecha__date__gte=hace_15_dias)
            .select_related("material", "estado", "encargado", "guardia_operativa")
            .order_by("fecha")
        )
        combustibles = (
            Combustible.objects
            .filter(fecha__date__gte=hace_15_dias)
            .select_related("movil", "encargado")
            .order_by("fecha")
        )
        fluidos = (
            Fluidos.objects
            .filter(fecha__date__gte=hace_15_dias)
            .select_related("movil", "encargado")
            .order_by("fecha")
        )
        reparaciones = (
            ReparacionMovil.objects
            .filter(fecha__date__gte=hace_15_dias)
            .select_related("movil", "encargado")
            .order_by("fecha")
        )

        # 5. Construcción de un dict ordenado por fecha
        timeline = OrderedDict()
        for p in planillas:
            fecha = p.fecha
            if fecha not in timeline:
                timeline[fecha] = {
                    "diurna": None,
                    "nocturna": None,
                    "presentes": [],
                    "ausentes": [],
                    "refuerzos": [],
                    "cambios_material": [],
                    "combustibles": [],
                    "fluidos": [],
                    "reparaciones": [],
                }
            turno = "diurna" if p.guardia.lower().startswith("d") else "nocturna"
            timeline[fecha][turno] = p
            timeline[fecha]["presentes"].extend(p.guardia_presentes.all())
            timeline[fecha]["ausentes"].extend(p.guardia_ausentes.all())
            timeline[fecha]["refuerzos"].extend(p.guardia_refuerzos.all())

        # Inicializar lista de servicios en cada planilla
        for fecha, data in timeline.items():
            for turno in ("diurna", "nocturna"):
                plan = data[turno]
                if plan:
                    plan.servicios = []
                    plan.cambios_material = []   # ← aquí
                    plan.combustibles = []
                    plan.fluidos = []
                    plan.reparaciones = []

        # Asignar cada cambio de estadod de materiales sólo a la planilla correcta
        for cambio in cambios_material:
            dt = cambio.fecha.date()
            if dt in timeline:
                for turno in ("diurna", "nocturna"):
                    plan = timeline[dt][turno]
                    # comparas la FK que acabas de agregar
                    if plan and cambio.guardia_operativa_id == plan.pk:
                        plan.cambios_material.append(cambio)
                        print(plan.cambios_material)

        # Asignar cada servicio sólo a la planilla correcta
        for s in servicios:
            dt = s.salida.date()
            if dt in timeline:
                for turno in ("diurna", "nocturna"):
                    plan = timeline[dt][turno]
                    if plan and s.guardia_operativa == plan.guardia_operativa:
                        plan.servicios.append(s)

        # Vincular eventos adicionales por fecha
        for ev, key in (
            (cambios_material, "cambios_material"),
            (combustibles, "combustibles"),
            (fluidos, "fluidos"),
            (reparaciones, "reparaciones"),
        ):
            for obj in ev:
                dt = getattr(obj, "fecha", obj).date()
                if dt in timeline:
                    timeline[dt][key].append(obj)

        turnos = ["diurna", "nocturna"]
        print(timeline)
        return render(request, self.template_name, {
            "timeline": timeline,
            "turnos": turnos,
        })

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
        context['bomberos'] = Bombero.objects.all()
        return context
        
class MaterialesView(generic.ListView):
    model = Material
    template_name = "planilla/materiales.html" 
    context_object_name = "todo_los_materiales"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Estado.objects.all()
        context['bomberos'] = Bombero.objects.all()
        context["guardia_operativa"] = Planilla.objects.all().order_by('-fecha')
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
        movil=get_object_or_404(Movil, id=id)

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
        planillas = Planilla.objects.all().order_by('guardia_operativa').reverse()
        destacamento = request.session.get("destacamento", request.user.last_name)  # Recupera destacamento o usa last_name

        context = {
            "moviles": moviles,
            "bomberos": bomberos,
            "tipo_servicios": tipo_servicios,
            "destacamento": destacamento,
            "planillas": planillas
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
        # encargado_id = request.POST.get("encargado")
        nombre = request.POST.get("denunciante")
        telefono = request.POST.get("telefono")
        base = request.POST.get('zona')

        # Eliminar 'Provincia de Buenos Aires' y 'Argentina'
        address = re.sub(r",?\s*Provincia de Buenos Aires", "", address, flags=re.IGNORECASE)
        address = re.sub(r",?\s*Argentina", "", address, flags=re.IGNORECASE)

        # Eliminar espacios y comas sobrantes
        address = address.strip().strip(",")


        # Validar datos requeridos
        if not (guardia and address and latitude and longitude and numero and salida and tipo_servicio_id):
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
            # Enviar notificación a todos los clientes en "servicios"
            async_to_sync(channel_layer.group_send)(
                "servicios",  # 🔥 Notifica a todos los clientes
                {
                    "type": "send_servicio_update",
                    "data": {
                        "tipo": "nuevo_servicio",
                        "servicio": {
                            "id": servicios.id,
                            "numero": numero,
                            "tipo": {
                                "id": servicios.tipo.id,
                                "tipo": servicios.tipo.tipo,
                            },
                            "direccion": address,
                            "zona": base,
                            "latitud": latitude,
                            "longitud": longitude,
                            "estado": "En curso",
                            "salida": salida,
                            "encargado": {
                                "id": servicios.encargado.id,
                                "legajo": servicios.encargado.legajo,
                                "apellido": servicios.encargado.apellido,
                                "nombre": servicios.encargado.nombre,
                            } if servicios.encargado else None,  # Asegurar que no sea None
                        }
                    }
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

            return redirect ('/')
        
        except Exception as e:
                messages.error(request, f"Error al cargar el servicio: {e}")
                return redirect("cargar_servicio")

class ServicioDetail(View):
    def get(self, request, id):
        bomberos = Bombero.objects.all()
        moviles = Movil.objects.all()
        estados = Estado.objects.all()
        servicio = get_object_or_404(
            Servicio.objects.prefetch_related(
                Prefetch(
                    "moviles_asignados",
                    queryset=(
                        ServicioMovil.objects
                        .select_related(
                            "movil",          # tu Móvil
                            "chofer",         # tu chofer (ForeignKey)
                            "encargado_movil" # tu encargado (ForeignKey)
                        )
                        .prefetch_related("bomberos", "eventos")  # ManyToMany
                    ),
                    to_attr="moviles_list"
                )
            ),
            id=id
        )
            # 1) Evento inicial: alarma recibida
        timeline = []
        if servicio.salida:
            timeline.append({
                'time':        servicio.salida,
                'icon':        'fas fa-phone-volume bg-red',
                'description': 'Alarma recibida',
            })

        # 2) Por cada móvil, salida y luego sus eventos de estado
        for sm in servicio.moviles_list:
            if sm.salida_movil:
                timeline.append({
                    'time':        sm.salida_movil,
                    'icon':        'fas fa-truck-fast bg-success',
                    'description': (
                        f"Se desplaza móvil {sm.movil.numero}"
                        f"{' a cargo de ' + sm.encargado_movil.__str__() if sm.encargado_movil else ''}"
                    ),
                })
            # eventos de estado
            for ev in sm.eventos.all():
                timeline.append({
                    'time':        ev.timestamp,
                    'icon':        'fas fa-map-marker-alt bg-green',
                    'description': (
                        f"Móvil {sm.movil.numero} "
                        f"{ev.estado.estado}"   # ← aquí usamos el campo del FK
                    ),
                })

        # 3) Orden cronológico ascendente
        timeline = sorted(timeline, key=lambda e: e['time'])

        cantidad_moviles = len(servicio.moviles_list)
        cantidad_bomberos = sum(
            movil.bomberos.all().count()
            + (1 if movil.chofer else 0)
            + (1 if movil.encargado_movil else 0)
            for movil in servicio.moviles_list
        )
        
        fecha_formateada = servicio.salida.strftime("%Y-%m-%dT%H:%M") if servicio.salida else ""

        context = {
            "servicio": servicio,
            "fecha": fecha_formateada,
            "bomberos": bomberos,
            "moviles": moviles,
            'cantidad_moviles': cantidad_moviles,
            'cantidad_bomberos': cantidad_bomberos,
            'estados': estados,
            'timeline': timeline
        }
        return render (request, 'planilla/servicio_detail.html', context)

def asignarmovil(request, servicio_id):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=400)

    servicio = get_object_or_404(Servicio, id=servicio_id)
    movil    = get_object_or_404(Movil, id=request.POST["movil"])

    # 1) Obtener o crear la asignación
    sm, created = ServicioMovil.objects.get_or_create(servicio=servicio, movil=movil)

    # 2) Rellenar campos de la asignación y guardar
    sm.encargado_movil_id = int(request.POST["encargado"])
    sm.chofer_id          = int(request.POST["chofer"])
    sm.salida_movil       = datetime.strptime(request.POST["salida_movil"], "%Y-%m-%dT%H:%M")
    sm.save()
    sm.bomberos.set(request.POST.getlist("bomberos"))

    # ── Nuevo bloque: Cambiar el estado del móvil ──
    # Buscamos el objeto Estado cuyo campo 'estado' sea precisamente "En desplazamiento"
    estado_desplaz = get_object_or_404(Estado, estado="En desplazamiento")
    movil.IDEstado = estado_desplaz
    movil.intervenciones += 1  # si mantienes este contador
    movil.save()
    # ───────────────────────────────────────────────

    # 3) Reconstruimos el payload completo (igual que antes)…
    asigns = (ServicioMovil.objects
                .filter(servicio=servicio)
                .select_related("movil","encargado_movil","chofer")
                .prefetch_related("bomberos"))
    moviles_payload = []
    for a in asigns:
        moviles_payload.append({
            "movil":     {"id": a.movil.id, "numero": a.movil.numero},
            "salida":    a.salida_movil.strftime("%Y-%m-%dT%H:%M"),
            "encargado": a.encargado_movil and {
                "id": a.encargado_movil.id,
                "nombre": a.encargado_movil.nombre,
                "apellido": a.encargado_movil.apellido,
            },
            "chofer": a.chofer and {
                "id": a.chofer.id,
                "nombre": a.chofer.nombre,
                "apellido": a.chofer.apellido,
            },
            "bomberos": [
                {"id": b.id, "legajo": b.legajo,
                 "nombre": b.nombre, "apellido": b.apellido}
                for b in a.bomberos.all()
            ],
            # opcional: incluye aquí el estado actual del móvil
            "estado_actual": a.movil.IDEstado.estado,
        })

    servicio_data = {
      "id":        servicio.id,
      "numero":    servicio.numero,
      "zona":      servicio.zona,
      "moviles":   moviles_payload,
      "salida":    servicio.salida.strftime("%Y-%m-%dT%H:%M:%S"),
      "direccion": servicio.direccion,
      "encargado": servicio.encargado and {
          "legajo": servicio.encargado.legajo,
          "apellido": servicio.encargado.apellido,
          "nombre": servicio.encargado.nombre,
      },
      "tipo": {"tipo": servicio.tipo.tipo},
    }

    # 4) Emitir actualización por WebSocket
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
      "servicios",
      {
        "type": "send_servicio_update",
        "data": {
          "tipo":     "actualizar_servicio",
          "servicio": servicio_data
        }
      }
    )

    # 5) Redireccionar al detalle
    return redirect(f"/servicio_detail/{servicio_id}")

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
        anterior.salida = request.POST['salida']
        anterior.tipo_id = int(request.POST['tiposervicio'])
        print(anterior.tipo.id)
        anterior.encargado.id = int(request.POST['encargado'])
        anterior.nombre_denunciante = request.POST['denunciante']
        anterior.telefono_denunciante = request.POST['telefono']
        anterior.save()

        servicio_data = {
            "id": anterior.id,
            "numero": anterior.numero,
            "zona": anterior.zona,
            "salida": anterior.salida,
            "direccion": anterior.direccion,
            "latitud": anterior.latitud,
            "longitud": anterior.longitud,
            "encargado": {
                "legajo": anterior.encargado.legajo,
                "apellido": anterior.encargado.apellido,
                "nombre": anterior.encargado.nombre,
            },
            "tipo": {"tipo": anterior.tipo.tipo}
        }

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "servicios", 
            {"type": "send_servicio_update", "data": {
                "tipo": "actualizar_servicio",
                "servicio": servicio_data
            }}
            )

        return redirect ('guardia')
    
def obtener_servicios(request):

    servicios = list(Servicio.objects.filter(estado="En curso").values("id","direccion", "latitud", "longitud", "tipo"))
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

        planilla = Planilla(guardia_operativa=request.POST['guardiaoperativa'], fecha=request.POST['fecha'], guardia=request.POST['guardia'], cabecera_id=int(request.POST['cabecera']), oficial_id=request.POST['oficial'], cuartelero=request.POST['cuartelero'], recibido=request.POST['recibido'], gastado=request.POST['gastos'], concepto=request.POST['concepto'], entregado=request.POST['entregado'], encargado_id=request.POST['encargado'], ingreso_encargado=request.POST["ingresoEncargado"], chofer_id=request.POST['chofer'], ingreso_chofer=ingresoChofer, tareas=request.POST['tareas'], novedades=request.POST['novedades'], cuartel_id=int(request.POST['base'])) 

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
            fecha = request.POST['fecha'],
            bombero_id=presente["bombero_id"], 
            ingreso=presente["ingreso"])
            print(personal_guardia)
        personal_guardia.save()

        encargado_guardia = GuardiaPresentes.objects.create(
            guardia_op_id=planilla.id, 
            fecha = request.POST['fecha'],
            bombero_id=request.POST['encargado'],
            ingreso=request.POST["ingresoEncargado"])
        encargado_guardia.save()

        if ingresoChofer == "":
            chofer_guardia = GuardiaPresentes.objects.create(
            guardia_op_id=planilla.id, 
            fecha = request.POST['fecha'],
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
        moviles = Movil.objects.all().order_by('numero')
        cuentas = Base.objects.annotate(
            en_servicio=Count('movil', filter=Q(movil__IDEstado=1)),
            condicional=Count('movil', filter=Q(movil__IDEstado=2)),
            ocupados=Count('movil', filter=Q(movil__IDEstado=4)),
            fuera_servicio=Count('movil', filter=Q(movil__IDEstado=3))
        )

        return render (request, 'planilla/guardia.html', {'servicios': servicios, 'base': base, 'moviles': moviles, 'cuentas': cuentas})


class TV(View):
    def get(self, request, base, *args, **kwargs):
        # 1) Cargo la Base seleccionada
        group = get_object_or_404(Base, pk=base)

        # 2) Defino el corte de 15 días atrás
        cutoff = timezone.now() - timedelta(days=15)

        # 3) Novedades: solo las Planillas de esta Base
        novedades = Planilla.objects.filter(
            fecha__gte=cutoff.date(),
            cuartel=group
        )

        # 4) Cambios de material: solo los que provienen de una Planilla de esta Base
        cambios_material = CambioEstado.objects.filter(
            fecha__gte=cutoff,
            guardia_operativa__cuartel=group
        ).select_related(
            'material', 'estado', 'encargado', 'guardia_operativa'
        )
        print(cambios_material)

        # 5) Reparaciones: solo las de móviles asignados a esta Base
        reparaciones = ReparacionMovil.objects.filter(
            fecha__gte=cutoff,
            movil__IDBase=group
        ).select_related(
            'movil', 'encargado'
        )

        # 6) Uno los tres QuerySets en una lista Python
        items = list(novedades) + list(cambios_material) + list(reparaciones)

        # 7) Si alguna Planilla tiene .fecha de tipo date en lugar de datetime, 
        #    la convierto a datetime a las 00:00 para ordenarlas homogéneamente
        for obj in items:
            if isinstance(obj.fecha, date) and not isinstance(obj.fecha, datetime):
                obj.fecha = datetime.combine(obj.fecha, time.min)

        # 8) Ordeno de más nuevo a más antiguo
        timeline = sorted(items, key=attrgetter('fecha'), reverse=True)

        # 9) Servicios en curso, filtrados también por Base
        servicios = Servicio.objects.filter(
            estado='En curso'
        ).prefetch_related(
            Prefetch(
                'moviles_asignados',
                queryset=ServicioMovil.objects
                         .select_related('movil')
                         .prefetch_related('bomberos'),
                to_attr='moviles_list'
            )
        ).distinct()

        return render(request, 'planilla/tv.html', {
            'destacamentos': Base.objects.order_by('id'),
            'group':          group,
            'timeline':       timeline,
            'servicios':      servicios,
        })
    
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
    if request.method != "POST":
        return redirect("moviles")

    movil = get_object_or_404(Movil, id=id)
    # 1) Cambio de estado del móvil
    nuevo_estado_id = int(request.POST["estado"])
    movil.IDEstado_id = nuevo_estado_id
    movil.save()

    # 2) Preparamos WebSocket
    layer     = get_channel_layer()
    timestamp = timezone.now().strftime("%H:%M:%S")

    # 3) Buscamos asignaciones activas usando el through model
    asignaciones = ServicioMovil.objects.filter(
        movil=movil,
        servicio__estado="En curso"
    )

    # 4) Para cada asignación, creamos un evento de timeline y lo enviamos
    for asign in asignaciones:
        # obtenemos la instancia de Estado que acabamos de asignar
        estado_obj = get_object_or_404(Estado, id=nuevo_estado_id)

        # creamos el evento en la base
        evento = ServicioMovilEvento.objects.create(
            servicio_movil=asign,
            estado=estado_obj   # aquí ya es FK correctamente
        )

        # preparamos la entrada para el timeline
        entry = {
            "time":        evento.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            "icon":        "fas fa-map-marker-alt bg-green",
            "description": (
            f"Móvil {asign.movil.numero} "
            f"{evento.estado.estado}"       # ← aquí usamos el texto del FK
        ),
        }

        # enviamos por WebSocket
        async_to_sync(layer.group_send)(
            "servicios",
            {
                "type": "send_movil_update",
                "data": {
                    "tipo":        "nuevo_evento_movil",
                    "servicio_id": asign.servicio.id,
                    "evento":      entry
                }
            }
        )

    # 5) redirección según next o fallback
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return redirect(next_url)
    return redirect("moviles")

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
        guardia = Planilla.objects.get(pk=int(request.POST['guardia']))
        material = Material.objects.get(id=id)
        material.estado = estado
        material.save()



        print(material, datetime.now(), int(request.POST['estado']), int(request.POST['bombero']), request.POST['motivo'], request.POST['guardia'] )
        novedad = CambioEstado(material=material, fecha=datetime.now(), estado=estado, encargado=bombero, motivo=request.POST['motivo'], guardia_operativa=guardia)
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

class TabletView(View):
    def get(self, request, movil, *args, **kwargs):
        print("movil", movil)
        movil = get_object_or_404(Movil, id=movil)
        servicio = Servicio.objects.prefetch_related(
            Prefetch(
                "moviles_asignados",
                queryset=ServicioMovil.objects.select_related("movil").prefetch_related("bomberos"),
                to_attr="moviles_list"
            )
        ).filter(
            moviles_asignados__movil=movil,  # Filtra servicios donde el móvil esté asignado
            estado="En curso"  # Ajusta esto según el campo que indica si el servicio está activo
        ).order_by("-salida").first()  # Ordena por fecha y obtiene el más reciente

        if servicio:
            context = {
                "servicio": servicio,
                "movil": movil,
            }
        else:
            context = {
                "servicio": None,
                "movil": movil,
            }
        return render(request, 'planilla/tablet.html', context)

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

            channel_layer = get_channel_layer()

            # Enviar mensaje para finalizar el servicio
            servicio_message = {
                "tipo": "finalizar_servicio",
                "servicio": {
                    "id": str(servicio.id)  # Solo el ID es necesario para eliminarlo en el cliente
                }
            }
            async_to_sync(channel_layer.group_send)(
                "servicios",
                {
                    "type": "send_servicio_update",
                    "data": servicio_message
                }
            )

            # Enviar mensaje para actualizar el estado del móvil
            movil_message = {
                "tipo": "actualizar_movil",
                "movil": {
                    "id": movil_data.movil.id,
                    "estado": "Ocupado",  # O el estado actualizado según corresponda
                    "numero": movil.numero
                }
            }
            async_to_sync(channel_layer.group_send)(
                "servicios",
                {
                    "type": "send_movil_update",
                    "data": movil_message
                }
            )

            return redirect('/')
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

def signinMovil(request):
    if request.method == "GET":
        get_token(request)
        moviles = Movil.objects.all()
        return render(request, 'planilla/signin_movil.html', {'moviles': moviles})
    elif request.method == "POST":
        try:
            movil = request.POST['movil']
            return redirect(reverse('tablet_view', kwargs={'movil': movil}))
        except Exception as err:
            print(f"Oops! {err}")
            return render(request, 'planilla/signin_movil.html', {'error': 'Algo falló.'})
        
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