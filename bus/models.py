"""
Bus Models - Core models for bus management system
"""
from django.contrib.gis.db import models


class BusRoute(models.Model):
    """Tuyến xe buýt"""
    route_number = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name='Số hiệu tuyến'
    )
    name = models.CharField(
        max_length=200, 
        verbose_name='Tên tuyến'
    )
    description = models.TextField(
        blank=True, 
        verbose_name='Mô tả'
    )
    start_point = models.CharField(
        max_length=200, 
        verbose_name='Điểm đầu'
    )
    end_point = models.CharField(
        max_length=200, 
        verbose_name='Điểm cuối'
    )
    operating_hours = models.CharField(
        max_length=100, 
        default='05:00 - 22:00',
        verbose_name='Giờ hoạt động'
    )
    frequency = models.CharField(
        max_length=50, 
        default='10-15 phút/chuyến',
        verbose_name='Tần suất'
    )
    ticket_price = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=7000,
        verbose_name='Giá vé (VNĐ)'
    )
    color = models.CharField(
        max_length=7, 
        default='#3388ff',
        verbose_name='Màu tuyến'
    )
    geometry = models.LineStringField(
        srid=4326, 
        null=True, 
        blank=True,
        verbose_name='Đường đi'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tuyến xe buýt'
        verbose_name_plural = 'Tuyến xe buýt'
        ordering = ['route_number']

    def __str__(self):
        return f"Tuyến {self.route_number}: {self.name}"
    
    @property
    def total_stops(self):
        return self.routestop_set.count()


class BusStop(models.Model):
    """Trạm dừng xe buýt"""
    name = models.CharField(
        max_length=200, 
        verbose_name='Tên trạm'
    )
    code = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name='Mã trạm'
    )
    address = models.CharField(
        max_length=500, 
        blank=True,
        verbose_name='Địa chỉ'
    )
    location = models.PointField(
        srid=4326,
        verbose_name='Vị trí'
    )
    has_shelter = models.BooleanField(
        default=False,
        verbose_name='Có mái che'
    )
    has_bench = models.BooleanField(
        default=False,
        verbose_name='Có ghế ngồi'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trạm dừng'
        verbose_name_plural = 'Trạm dừng'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

    def get_routes(self):
        """Lấy danh sách tuyến đi qua trạm này"""
        return BusRoute.objects.filter(
            routestop__stop=self, 
            is_active=True
        ).distinct()


class RouteStop(models.Model):
    """Liên kết giữa tuyến và trạm (M2M with extra fields)"""
    route = models.ForeignKey(
        BusRoute, 
        on_delete=models.CASCADE,
        verbose_name='Tuyến'
    )
    stop = models.ForeignKey(
        BusStop, 
        on_delete=models.CASCADE,
        verbose_name='Trạm dừng'
    )
    order = models.PositiveIntegerField(
        verbose_name='Thứ tự dừng'
    )
    distance_from_start = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Khoảng cách từ điểm đầu (km)'
    )
    estimated_time = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name='Thời gian ước tính (phút)'
    )

    class Meta:
        verbose_name = 'Điểm dừng trên tuyến'
        verbose_name_plural = 'Điểm dừng trên tuyến'
        ordering = ['route', 'order']
        unique_together = [['route', 'stop'], ['route', 'order']]

    def __str__(self):
        return f"{self.route.route_number} - {self.stop.name} (#{self.order})"
