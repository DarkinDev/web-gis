"""
Bus Admin - Django Admin với Soft Delete, Email Notifications và RBAC
"""
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html
from django.utils import timezone
from leaflet.admin import LeafletGeoAdmin
from .models import BusRoute, BusStop, RouteStop, UserProfile, Review
from . import notifications


# ─── Phân quyền RBAC ──────────────────────────────────────────────────────────
# Ẩn User/Group admin khỏi nhân viên (non-superuser staff)

class StaffRestrictedUserAdmin(admin.ModelAdmin):
    """Chỉ superuser mới xem/quản lý User"""
    def has_module_perms(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser


# Ghi đè ModelAdmin của User và Group
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class RestrictedUserAdmin(StaffRestrictedUserAdmin):
    """Admin User – chỉ superuser mới thấy"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']
    fieldsets = (
        ('Thông tin tài khoản', {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'email')}),
        ('Phân quyền', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': '⚠️ Chỉ Admin mới có thể phân quyền.'
        }),
        ('Thời gian', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )


@admin.register(Group)
class RestrictedGroupAdmin(StaffRestrictedUserAdmin):
    """Admin Group – chỉ superuser mới thấy"""
    list_display = ['name']
    search_fields = ['name']


# ─── RouteStop Inline ─────────────────────────────────────────────────────────

class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['stop']


# ─── BusRoute Admin ───────────────────────────────────────────────────────────

@admin.register(BusRoute)
class BusRouteAdmin(LeafletGeoAdmin):
    """Admin BusRoute với soft delete, email notification và phục hồi"""
    list_display = [
        'route_number', 'name', 'start_point', 'end_point',
        'operating_hours', 'ticket_price', 'total_stops',
        'is_active', 'deleted_badge'
    ]
    list_filter = ['is_active', 'is_deleted', 'created_at']
    search_fields = ['route_number', 'name', 'start_point', 'end_point']
    ordering = ['route_number']
    inlines = [RouteStopInline]
    actions = ['restore_selected']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('route_number', 'name', 'description')
        }),
        ('Lộ trình', {
            'fields': ('start_point', 'end_point', 'geometry')
        }),
        ('Thông tin hoạt động', {
            'fields': ('operating_hours', 'frequency', 'ticket_price')
        }),
        ('Hiển thị', {
            'fields': ('color', 'is_active')
        }),
    )

    def get_queryset(self, request):
        """Dùng all_objects để Admin thấy cả bản ghi đã xóa"""
        return BusRoute.all_objects.all()

    def deleted_badge(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="background:#e74c3c;color:white;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">🗑 Đã xóa</span>'
            )
        return format_html(
            '<span style="background:#27ae60;color:white;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">✓ Hoạt động</span>'
        )
    deleted_badge.short_description = 'Trạng thái'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            notifications.notify_route_updated(obj)
        else:
            notifications.notify_new_route(obj)

    def delete_model(self, request, obj):
        """Soft delete thay vì hard delete"""
        name = str(obj)
        obj.soft_delete()
        notifications.notify_item_deleted('Tuyến xe', name, obj.pk)
        self.message_user(
            request,
            f'Tuyến "{name}" đã được xóa mềm. Có thể khôi phục trong trang Restore.',
            messages.WARNING
        )

    def delete_queryset(self, request, queryset):
        """Soft delete khi chọn nhiều và xóa hàng loạt"""
        for obj in queryset:
            name = str(obj)
            obj.soft_delete()
            notifications.notify_item_deleted('Tuyến xe', name, obj.pk)
        self.message_user(
            request,
            f'{queryset.count()} tuyến đã được xóa mềm. Có thể khôi phục trong trang Restore.',
            messages.WARNING
        )

    @admin.action(description='♻️ Khôi phục tuyến đã xóa')
    def restore_selected(self, request, queryset):
        restored = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                restored += 1
        self.message_user(request, f'Đã khôi phục {restored} tuyến xe.', messages.SUCCESS)

    # Chỉ superuser mới được Restore
    def has_restore_permission(self, request):
        return request.user.is_superuser


# ─── BusStop Admin ────────────────────────────────────────────────────────────

@admin.register(BusStop)
class BusStopAdmin(LeafletGeoAdmin):
    """Admin BusStop với soft delete, email notification"""
    list_display = [
        'name', 'code', 'address', 'has_shelter', 'has_bench',
        'is_active', 'get_routes_display', 'deleted_badge'
    ]
    list_filter = ['is_active', 'is_deleted', 'has_shelter', 'has_bench']
    search_fields = ['name', 'code', 'address']
    ordering = ['name']
    actions = ['restore_selected']

    fieldsets = (
        ('Thông tin trạm', {
            'fields': ('name', 'code', 'address')
        }),
        ('Vị trí', {
            'fields': ('location',)
        }),
        ('Tiện ích', {
            'fields': ('has_shelter', 'has_bench', 'is_active')
        }),
    )

    def get_queryset(self, request):
        return BusStop.all_objects.all()

    def deleted_badge(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="background:#e74c3c;color:white;padding:2px 8px;'
                'border-radius:12px;font-size:11px;">🗑 Đã xóa</span>'
            )
        return format_html(
            '<span style="background:#27ae60;color:white;padding:2px 8px;'
            'border-radius:12px;font-size:11px;">✓ Hoạt động</span>'
        )
    deleted_badge.short_description = 'Trạng thái'

    def get_routes_display(self, obj):
        routes = obj.get_routes()
        return ', '.join([r.route_number for r in routes[:5]])
    get_routes_display.short_description = 'Tuyến đi qua'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            notifications.notify_stop_updated(obj)
        else:
            notifications.notify_new_stop(obj)

    def delete_model(self, request, obj):
        name = str(obj)
        obj.soft_delete()
        notifications.notify_item_deleted('Trạm dừng', name, obj.pk)
        self.message_user(
            request,
            f'Trạm "{name}" đã được xóa mềm. Có thể khôi phục trong trang Restore.',
            messages.WARNING
        )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            name = str(obj)
            obj.soft_delete()
            notifications.notify_item_deleted('Trạm dừng', name, obj.pk)
        self.message_user(
            request,
            f'{queryset.count()} trạm đã được xóa mềm.',
            messages.WARNING
        )

    @admin.action(description='♻️ Khôi phục trạm đã xóa')
    def restore_selected(self, request, queryset):
        # Chỉ superuser mới được restore
        if not request.user.is_superuser:
            self.message_user(request, 'Bạn không có quyền khôi phục dữ liệu.', messages.ERROR)
            return
        restored = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                restored += 1
        self.message_user(request, f'Đã khôi phục {restored} trạm dừng.', messages.SUCCESS)


# ─── RouteStop Admin ──────────────────────────────────────────────────────────

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'route', 'stop', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')

@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'stop', 'order', 'distance_from_start', 'estimated_time']
    list_filter = ['route']
    search_fields = ['route__route_number', 'stop__name']
    ordering = ['route', 'order']
    autocomplete_fields = ['route', 'stop']
