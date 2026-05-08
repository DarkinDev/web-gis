from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, LineString
from bus.models import BusRoute, BusStop, RouteStop
import random

class Command(BaseCommand):
    help = 'Populate database with sample bus data for Ho Chi Minh City'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        RouteStop.objects.all().delete()
        BusStop.objects.all().delete()
        BusRoute.objects.all().delete()

        self.stdout.write('Creating Bus Routes...')
        
        # Route 1: Ben Thanh - Cho Lon (Sample)
        route1 = BusRoute.objects.create(
            route_number='01',
            name='Bến Thành - Chợ Lớn',
            description='Tuyến xe buýt trục chính nối trung tâm thành phố và khu vực Chợ Lớn.',
            start_point='Công trường Mê Linh',
            end_point='Bến xe Chợ Lớn',
            color='#007bff', # Blue
            geometry=LineString([
                (106.70425, 10.77665), # Bach Dang
                (106.70245, 10.77237), # Ham Nghi
                (106.69910, 10.77180), # Ben Thanh
                (106.69312, 10.76945), # Tran Hung Dao
                (106.68050, 10.76350), 
                (106.66624, 10.75620), 
                (106.65345, 10.75110)  # Cho Lon
            ], srid=4326)
        )

        # Route 2: Ben Thanh - Tan Son Nhat (Sample)
        route2 = BusRoute.objects.create(
            route_number='152',
            name='Khu dân cư Trung Sơn - Bến Thành - Sân bay Tân Sơn Nhất',
            description='Tuyến xe buýt chất lượng cao phục vụ sân bay.',
            start_point='Khu dân cư Trung Sơn',
            end_point='Sân bay Tân Sơn Nhất',
            color='#28a745', # Green
            ticket_price=5000,
            geometry=LineString([
                (106.69910, 10.77180), # Ben Thanh
                (106.69630, 10.77620), # Nam Ky Khoi Nghia
                (106.68520, 10.78510),
                (106.67410, 10.79550),
                (106.66350, 10.81220), # Airport approach
                (106.66010, 10.81680)  # Tan Son Nhat
            ], srid=4326)
        )

        self.stdout.write('Creating Bus Stops...')
        
        stops_data = [
            # Route 1 stops
            {'name': 'Bến Bạch Đằng', 'loc': (106.70425, 10.77665), 'addr': 'Đường Tôn Đức Thắng, Q1'},
            {'name': 'Trạm Hàm Nghi', 'loc': (106.70245, 10.77237), 'addr': 'Đường Hàm Nghi, Q1'},
            {'name': 'Trạm Bến Thành', 'loc': (106.69910, 10.77180), 'addr': 'Công trường Quách Thị Trang, Q1'},
            {'name': 'Trạm Trần Hưng Đạo', 'loc': (106.69312, 10.76945), 'addr': 'Đường Trần Hưng Đạo, Q1'},
            {'name': 'Trạm Nguyễn Văn Cừ', 'loc': (106.68050, 10.76350), 'addr': 'Ngã tư Nguyễn Văn Cừ, Q5'},
            {'name': 'Bến xe Chợ Lớn', 'loc': (106.65345, 10.75110), 'addr': 'Đường Lê Quang Sung, Q6'},
            
            # Route 2 stops additions
            {'name': 'Trạm Pasteur', 'loc': (106.69630, 10.77620), 'addr': 'Đường Pasteur, Q1'},
            {'name': 'Trạm Viện Pasteur', 'loc': (106.68520, 10.78510), 'addr': 'Đường Võ Thị Sáu, Q3'},
            {'name': 'Trạm Phú Nhuận', 'loc': (106.67410, 10.79550), 'addr': 'Ngã tư Phú Nhuận'},
            {'name': 'Sân bay Tân Sơn Nhất', 'loc': (106.66010, 10.81680), 'addr': 'Ga Quốc Nội, Tân Bình'},
        ]

        created_stops = []
        for i, data in enumerate(stops_data):
            stop = BusStop.objects.create(
                name=data['name'],
                code=f"BS{i+1:03d}",
                address=data['addr'],
                location=Point(data['loc'][0], data['loc'][1], srid=4326),
                has_shelter=random.choice([True, False]),
                has_bench=random.choice([True, False])
            )
            created_stops.append(stop)

        self.stdout.write('Linking Stops to Routes...')

        # Link Route 1
        r1_stops = [0, 1, 2, 3, 4, 5] # Indices from created_stops
        for order, idx in enumerate(r1_stops):
            stop = created_stops[idx]
            RouteStop.objects.create(
                route=route1,
                stop=stop,
                order=order + 1,
                distance_from_start=order * 1.5, # Fake distance
                estimated_time=order * 5 # Fake time
            )

        # Link Route 2
        r2_stops = [2, 6, 7, 8, 9] # Overlaps at Ben Thanh (idx 2)
        for order, idx in enumerate(r2_stops):
            stop = created_stops[idx]
            RouteStop.objects.create(
                route=route2,
                stop=stop,
                order=order + 1,
                distance_from_start=order * 2.0,
                estimated_time=order * 8
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
