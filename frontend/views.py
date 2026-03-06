"""
Frontend Views - User-facing views
"""
from django.shortcuts import render
from django.http import JsonResponse
from bus.models import BusRoute, BusStop


def home_view(request):
    """Home page with full-screen map"""
    try:
        routes = BusRoute.objects.filter(is_active=True).order_by('route_number')
        context = {
            'routes': routes,
            'total_routes': routes.count(),
            'total_stops': BusStop.objects.filter(is_active=True).count(),
        }
    except Exception as e:
        # Temporary workaround: Return empty data if tables don't exist yet
        # This happens when migrations haven't run yet (PostGIS not installed)
        context = {
            'routes': [],
            'total_routes': 0,
            'total_stops': 0,
            'migration_error': 'Database tables not created yet. Please install PostGIS and run migrations.',
        }
    return render(request, 'frontend/home.html', context)


def routes_list_view(request):
    """List all bus routes"""
    try:
        routes = BusRoute.objects.filter(is_active=True).order_by('route_number')
    except Exception:
        routes = []
    context = {
        'routes': routes,
    }
    return render(request, 'frontend/routes.html', context)


def route_detail_view(request, pk):
    """Detail view for a specific route"""
    try:
        route = BusRoute.objects.get(pk=pk)
        stops = route.routestop_set.order_by('order').select_related('stop')
    except BusRoute.DoesNotExist:
        from django.http import Http404
        raise Http404("Route not found")
    except Exception:
        from django.http import Http404
        raise Http404("Database tables not created yet")
    context = {
        'route': route,
        'stops': stops,
    }
    return render(request, 'frontend/route_detail.html', context)


def stops_list_view(request):
    """List all bus stops"""
    try:
        stops = BusStop.objects.filter(is_active=True).order_by('name')
    except Exception:
        stops = []
    context = {
        'stops': stops,
    }
    return render(request, 'frontend/stops.html', context)
