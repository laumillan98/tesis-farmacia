# Agregar importaciones necesarias al inicio del archivo
from django.utils.timezone import now
from django.db.models.functions import TruncDay, TruncMonth
from django.db.models import Sum, F, FloatField    
from django.db.models.functions import Coalesce   
from django.utils import timezone
from datetime import timedelta
import datetime

from base.models import FarmaciaMedicamento, Salida 


def reporteEstadisticoMensual(farmacia_id):
    total_existencias = FarmaciaMedicamento.objects.filter(id_farma=farmacia_id)
    top_mas_vendidos = []
    ahora = timezone.now()
    # Calcular la fecha y hora de hace 24 horas
    hace_24_horas = ahora - timedelta(hours=24)
    # Filtrar las ventas de las últimas 24 horas
    ventas_ultimas_24_horas = Salida.objects.filter(
        fecha_movimiento__gte=hace_24_horas,
        id_farmaciaMedicamento__id_farma=farmacia_id
    ).annotate(
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField())
    )
    # Calcular el total recaudado en las últimas 24 horas
    total_recaudado_24_horas = ventas_ultimas_24_horas.aggregate(
        total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0)
    )['total_recaudado']
    total_de_entradas = 0

    for item in total_existencias:
        resultado = Salida.objects.filter(id_farmaciaMedicamento=item.pk).aggregate(total_cantidad=Coalesce(Sum('cantidad'), 0))['total_cantidad']
        porciento = (resultado / (item.existencia + resultado)) * 100 if item.existencia + resultado > 0 else 0
        total_de_entradas = total_de_entradas + (resultado+item.existencia)
        top_mas_vendidos.append({
            'medicamento': item.id_medic.nombre,
            'existencia': item.existencia,
            'vendidos': resultado,
            'porciento': f"{porciento}%"
        })

    top_mas_vendidos.sort(key=lambda x: x['vendidos'], reverse=True)

    # Filtrar las ventas del mes actual y calcular el total recaudado
    ventas_mes = Salida.objects.filter(
        fecha_movimiento__year=now().year,
        fecha_movimiento__month=now().month,
        id_farmaciaMedicamento__id_farma=farmacia_id
    ).annotate(
        dia=TruncDay('fecha_movimiento'),
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField()),
        total=F('cantidad')
    ).values('dia', 'total_por_salida', 'total').order_by('dia')

    total_recaudado_mes = ventas_mes.aggregate(total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0))['total_recaudado']

   
    # Preparar los datos para el gráfico
    ventas_por_dia = ventas_mes.values('dia').annotate(total_vendido=Sum('cantidad')).order_by('dia')
    fechas = [venta['dia'].strftime('%Y-%m-%d') for venta in ventas_por_dia]
    cantidades = [venta['total_vendido'] for venta in ventas_por_dia]
    
    # Pasar los datos al template
    contexto = {
        'fechas': fechas,
        'cantidades': cantidades,
        'top_vendidos': top_mas_vendidos[:5],
        'total_recaudado': total_recaudado_mes,
        'total_unidades': sum(cantidades),
        'total_24': total_recaudado_24_horas,
        'total_entradas': total_de_entradas
    }
    
    return contexto

def reporteEstadisticoAnual(farmacia_id):
    # Obtener el año actual
    year = now().year

    # Crear una lista de todos los meses del año actual
    meses_del_ano = [datetime.date(year, month, 1) for month in range(1, 13)]
    
    if farmacia_id is None:
        ventas_ano = Salida.objects.filter(fecha_movimiento__year=year).annotate(
            mes=TruncMonth('fecha_movimiento'),
            total_por_salida=F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad')
        ).values('mes').annotate(total_mes=Sum('total_por_salida')).order_by('mes')
    else: 
        ventas_ano = Salida.objects.filter(
            fecha_movimiento__year=year,
            id_farmaciaMedicamento__id_farma=farmacia_id
        ).annotate(
            mes=TruncMonth('fecha_movimiento'),
            total_por_salida=F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad')
        ).values('mes').annotate(total_mes=Sum('total_por_salida')).order_by('mes')

    # Convertir QuerySet a diccionario para acceso rápido
    ventas_por_mes = {venta['mes']: venta['total_mes'] for venta in ventas_ano}

    # Preparar los datos para el gráfico, asegurándose de que los meses sin ventas tengan un valor de 0
    totales_mes = [ventas_por_mes.get(mes, 0) for mes in meses_del_ano]

    # Formatear los meses para las etiquetas del gráfico
    meses = [mes.strftime('%Y-%m') for mes in meses_del_ano]

    # Pasar los datos al template
    contexto = {
        'meses': meses,
        'totales_mes': totales_mes,
    }
    
    return contexto

def reporteEstadisticoNivelProvincial():
    total_existencias = FarmaciaMedicamento.objects.all()
    top_mas_vendidos = []
    ahora = timezone.now()
    # Calcular la fecha y hora de hace 24 horas
    hace_24_horas = ahora - timedelta(hours=24)
    # Filtrar las ventas de las últimas 24 horas
    ventas_ultimas_24_horas = Salida.objects.filter(
        fecha_movimiento__gte=hace_24_horas,
    ).annotate(
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField())
    )
    # Calcular el total recaudado en las últimas 24 horas
    total_recaudado_24_horas = ventas_ultimas_24_horas.aggregate(
        total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0)
    )['total_recaudado']
    total_de_entradas = 0

    for item in total_existencias:
        resultado = Salida.objects.filter(id_farmaciaMedicamento=item.pk).aggregate(total_cantidad=Coalesce(Sum('cantidad'), 0))['total_cantidad']
        porciento = (resultado / (item.existencia + resultado)) * 100 if item.existencia + resultado > 0 else 0
        total_de_entradas = total_de_entradas + (resultado+item.existencia)
        top_mas_vendidos.append({
            'farmacia': item.id_farma.nombre,
            'medicamento': item.id_medic.nombre,
            'existencia': item.existencia,
            'vendidos': resultado,
            'porciento': f"{porciento}%"
        })

    top_mas_vendidos.sort(key=lambda x: x['vendidos'], reverse=True)

    # Filtrar las ventas del mes actual y calcular el total recaudado
    ventas_mes = Salida.objects.filter(
        fecha_movimiento__year=now().year,
        fecha_movimiento__month=now().month,
    ).annotate(
        dia=TruncDay('fecha_movimiento'),
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField()),
        total=F('cantidad')
    ).values('dia', 'total_por_salida', 'total').order_by('dia')

    total_recaudado_mes = ventas_mes.aggregate(total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0))['total_recaudado']

   
    # Preparar los datos para el gráfico
    ventas_por_dia = ventas_mes.values('dia').annotate(total_vendido=Sum('cantidad')).order_by('dia')
    fechas = [venta['dia'].strftime('%Y-%m-%d') for venta in ventas_por_dia]
    cantidades = [venta['total_vendido'] for venta in ventas_por_dia]
    
    # Pasar los datos al template
    contexto = {
        'fechas': fechas,
        'cantidades': cantidades,
        'top_vendidos': top_mas_vendidos[:5],
        'total_recaudado': total_recaudado_mes,
        'total_unidades': sum(cantidades),
        'total_24': total_recaudado_24_horas,
        'total_entradas': total_de_entradas
    }
    
    return contexto