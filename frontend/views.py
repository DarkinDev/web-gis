"""
Frontend Views - User-facing views
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from bus.models import BusRoute, BusStop, RouteStop


def home_view(request):
    """Home page with full-screen map"""
    routes = BusRoute.objects.filter(is_active=True).order_by('route_number')
    context = {
        'routes': routes,
        'total_routes': routes.count(),
        'total_stops': BusStop.objects.filter(is_active=True).count(),
    }
    return render(request, 'frontend/home.html', context)


def routes_list_view(request):
    """List all bus routes"""
    routes = BusRoute.objects.filter(is_active=True).order_by('route_number')
    context = {'routes': routes}
    return render(request, 'frontend/routes.html', context)


def route_detail_view(request, pk):
    """Detail view for a specific route"""
    route = get_object_or_404(BusRoute, pk=pk)
    stops = route.routestop_set.order_by('order').select_related('stop')
    context = {'route': route, 'stops': stops}
    return render(request, 'frontend/route_detail.html', context)


def stops_list_view(request):
    """List all bus stops"""
    stops = BusStop.objects.filter(is_active=True).order_by('name')
    context = {'stops': stops}
    return render(request, 'frontend/stops.html', context)


def management_view(request):
    """Management dashboard for CRUD operations"""
    routes = BusRoute.objects.all().order_by('route_number')
    stops  = BusStop.objects.all().order_by('name')
    context = {
        'routes': routes,
        'stops': stops,
        'total_routes': routes.count(),
        'total_stops': stops.count(),
    }
    return render(request, 'frontend/management.html', context)


# ─── CRUD API endpoints ────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_create_route(request):
    try:
        data = json.loads(request.body)
        route = BusRoute.objects.create(
            route_number=data['route_number'],
            name=data['name'],
            start_point=data.get('start_point', ''),
            end_point=data.get('end_point', ''),
            description=data.get('description', ''),
            operating_hours=data.get('operating_hours', '05:00 - 22:00'),
            frequency=data.get('frequency', '10-15 phút/chuyến'),
            ticket_price=data.get('ticket_price', 7000),
            color=data.get('color', '#3388ff'),
            is_active=data.get('is_active', True),
        )
        return JsonResponse({'success': True, 'id': route.id, 'message': f'Đã tạo tuyến {route.route_number}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_route(request, pk):
    try:
        route = get_object_or_404(BusRoute, pk=pk)
        data  = json.loads(request.body)
        for field in ['route_number', 'name', 'start_point', 'end_point',
                      'description', 'operating_hours', 'frequency',
                      'ticket_price', 'color', 'is_active']:
            if field in data:
                setattr(route, field, data[field])
        route.save()
        return JsonResponse({'success': True, 'message': f'Đã cập nhật tuyến {route.route_number}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_delete_route(request, pk):
    try:
        route = get_object_or_404(BusRoute, pk=pk)
        num   = route.route_number
        route.delete()
        return JsonResponse({'success': True, 'message': f'Đã xóa tuyến {num}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_stop(request):
    try:
        from django.contrib.gis.geos import Point
        data  = json.loads(request.body)
        lat   = float(data['latitude'])
        lng   = float(data['longitude'])
        stop  = BusStop.objects.create(
            name=data['name'],
            code=data.get('code', None) or None,
            address=data.get('address', ''),
            location=Point(lng, lat, srid=4326),
            has_shelter=data.get('has_shelter', False),
            has_bench=data.get('has_bench', False),
            is_active=data.get('is_active', True),
        )
        return JsonResponse({'success': True, 'id': stop.id, 'message': f'Đã tạo trạm "{stop.name}"'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_stop(request, pk):
    try:
        from django.contrib.gis.geos import Point
        stop  = get_object_or_404(BusStop, pk=pk)
        data  = json.loads(request.body)
        for field in ['name', 'code', 'address', 'has_shelter', 'has_bench', 'is_active']:
            if field in data:
                setattr(stop, field, data[field])
        if 'latitude' in data and 'longitude' in data:
            stop.location = Point(float(data['longitude']), float(data['latitude']), srid=4326)
        stop.save()
        return JsonResponse({'success': True, 'message': f'Đã cập nhật trạm "{stop.name}"'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_delete_stop(request, pk):
    try:
        stop = get_object_or_404(BusStop, pk=pk)
        name = stop.name
        stop.delete()
        return JsonResponse({'success': True, 'message': f'Đã xóa trạm "{name}"'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def api_get_route(request, pk):
    try:
        route = get_object_or_404(BusRoute, pk=pk)
        return JsonResponse({
            'id': route.id, 'route_number': route.route_number, 'name': route.name,
            'start_point': route.start_point, 'end_point': route.end_point,
            'description': route.description, 'operating_hours': route.operating_hours,
            'frequency': route.frequency, 'ticket_price': str(route.ticket_price),
            'color': route.color, 'is_active': route.is_active,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_get_stop(request, pk):
    try:
        stop = get_object_or_404(BusStop, pk=pk)
        return JsonResponse({
            'id': stop.id, 'name': stop.name, 'code': stop.code or '',
            'address': stop.address, 'latitude': stop.latitude,
            'longitude': stop.longitude, 'has_shelter': stop.has_shelter,
            'has_bench': stop.has_bench, 'is_active': stop.is_active,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
