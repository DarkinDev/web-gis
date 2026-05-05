/**
 * Bus Management WebGIS - Map JavaScript
 * LeafletJS integration with GIS functionality
 */

// ─── Global State ────────────────────────────────────────────────────────────
let map;
let stopsLayer;
let routesLayer;
let bufferLayer;
let routeResultLayer;
let userMarker;

let allStops    = [];   // GeoJSON features
let allRoutes   = [];   // GeoJSON features
let selectedRouteId = null;
let bufferMode  = false;
let currentBufferRadius = 500;

// ─── Loading State ────────────────────────────────────────────────────────────
function showLoading(msg = 'Đang tải dữ liệu...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.querySelector('.fw-bold').textContent = msg;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

const MIN_ZOOM_STOPS = 14;

// ─── API endpoints ────────────────────────────────────────────────────────────
const API = {
    stops:                  '/api/stops/',
    stopsGeojson:           '/api/stops/geojson/',
    routes:                 '/api/routes/',
    routesGeojson:          '/api/routes/geojson/',
    routesGeojsonFromStops: '/api/routes/geojson-from-stops/',
    nearestStops:           '/api/gis/nearest/',
    stopsInRadius:          '/api/gis/stops-in-radius/',
    findRoute:              '/api/gis/find-route/',
    distance:               '/api/gis/distance/'
};

const NOMINATIM = 'https://nominatim.openstreetmap.org';

// ─── Map Initialisation ───────────────────────────────────────────────────────
function initMap() {
    map = L.map('map', {
        center: [10.8231, 106.6297],
        zoom: 13,
        zoomControl: false
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/">CARTO</a> | BusGIS',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    stopsLayer       = L.layerGroup().addTo(map);
    routesLayer      = L.layerGroup().addTo(map);
    bufferLayer      = L.layerGroup().addTo(map);
    routeResultLayer = L.layerGroup().addTo(map);

    map.on('zoomend', () => displayStops(allStops, selectedRouteId));
}

// ─── Load Data from API ───────────────────────────────────────────────────────
async function loadStops() {
    showLoading('Đang tải danh sách trạm dừng...');
    try {
        const res  = await fetch(API.stopsGeojson);
        const data = await res.json();
        if (data.features) {
            allStops = data.features;
            displayStops(allStops);
        }
    } catch (e) {
        console.error('Error loading stops:', e);
        showNotification('Không thể tải dữ liệu trạm dừng', 'error');
    } finally {
        hideLoading();
    }
}

async function loadRoutes() {
    showLoading('Đang tải mạng lưới tuyến xe...');
    try {
        const res  = await fetch(API.routesGeojsonFromStops);
        const data = await res.json();
        if (data.features) {
            allRoutes = data.features;
            displayAllRoutes(allRoutes);  // Vẽ tất cả tuyến khi khởi tạo
        }
    } catch (e) {
        console.error('Error loading routes:', e);
        showNotification('Không thể tải dữ liệu tuyến xe', 'error');
    } finally {
        hideLoading();
    }
}

// ─── Display Stops ────────────────────────────────────────────────────────────
function displayStops(features, filterRouteId = null) {
    stopsLayer.clearLayers();

    const zoom = map.getZoom();
    if (zoom < MIN_ZOOM_STOPS && (!filterRouteId || filterRouteId === 'all')) {
        showZoomHint(true);
        return;
    }
    showZoomHint(false);

    features.forEach(feature => {
        const coords = feature.geometry.coordinates;
        const props  = feature.properties;

        if (filterRouteId && filterRouteId !== 'all') {
            const hasRoute = props.routes && props.routes.some(r => r.id === parseInt(filterRouteId));
            if (!hasRoute) return;
        }

        const marker = L.circleMarker([coords[1], coords[0]], {
            radius: 7,
            fillColor: '#0066cc',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        });

        const routeTags = (props.routes || []).map(r =>
            `<span class="route-tag" style="background:${r.color}20;color:${r.color};border-color:${r.color}">${r.route_number}</span>`
        ).join('');

        const popupContent = `
            <div class="popup-content">
                <h5><i class="bi bi-geo-alt-fill me-1"></i>${props.name}</h5>
                ${props.address ? `<p><i class="bi bi-signpost me-1"></i>${props.address}</p>` : ''}
                ${(props.routes || []).length > 0 ? `
                    <div class="popup-routes">
                        <div class="popup-routes-title">Tuyến đi qua:</div>
                        <div class="popup-route-tags">${routeTags}</div>
                        <button class="btn btn-sm btn-outline-primary mt-2 w-100"
                                onclick="showRoutesForStop(${feature.id})">
                            <i class="bi bi-eye me-1"></i>Xem tuyến trên bản đồ
                        </button>
                    </div>` : '<p class="text-muted small mb-0">Không có tuyến nào qua trạm này</p>'}
                ${bufferMode ? `
                    <button class="btn btn-sm btn-primary mt-2 w-100"
                            onclick="showBufferForStop(${feature.id}, ${coords[0]}, ${coords[1]})">
                        <i class="bi bi-circle me-1"></i>Hiển thị vùng phục vụ
                    </button>` : ''}
            </div>`;

        marker.bindPopup(popupContent);
        marker.feature = feature;
        marker.addTo(stopsLayer);
    });
}

function showZoomHint(show) {
    let hint = document.getElementById('zoom-hint');
    if (!hint) {
        hint = document.createElement('div');
        hint.id = 'zoom-hint';
        hint.style.cssText = 'position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.6);color:#fff;padding:6px 14px;border-radius:20px;font-size:0.82rem;z-index:900;pointer-events:none;';
        hint.textContent = '🔍 Phóng to để xem trạm dừng';
        document.body.appendChild(hint);
    }
    hint.style.display = show ? 'block' : 'none';
}

// ─── Display Routes ───────────────────────────────────────────────────────────

/**
 * Vẽ TẤT CẢ tuyến với độ mờ nhạt làm nền bản đồ
 */
function displayAllRoutes(features) {
    routesLayer.clearLayers();
    if (!features || features.length === 0) return;

    features.forEach(feature => {
        if (!feature.geometry) return;
        const props   = feature.properties;
        const featureId = feature.id || props.id;
        const latLngs = feature.geometry.coordinates.map(c => [c[1], c[0]]);

        L.polyline(latLngs, {
            color:   props.color || '#3388ff',
            weight:  4,
            opacity: 0.55
        }).bindPopup(`
            <div class="popup-content">
                <h5 style="color:${props.color}">Tuyến ${props.route_number}</h5>
                <p><strong>${props.name}</strong></p>
                <p>${props.start_point} → ${props.end_point}</p>
                <p><i class="bi bi-geo-alt"></i> ${props.total_stops} trạm</p>
            </div>
        `).addTo(routesLayer);
    });
}

/**
 * Vẽ tuyến theo filter — nếu có filterRouteId: CHỈ vẽ tuyến được chọn, ẩn phần còn lại
 * filterRouteId: null/'all' = tất cả | number | number[]
 */
function displayRoutes(features, filterRouteId = null) {
    routesLayer.clearLayers();
    if (!features || features.length === 0) return;

    // Không có filter → vẽ tất cả bình thường
    if (!filterRouteId || filterRouteId === 'all') {
        displayAllRoutes(features);
        return;
    }

    // Chuẩn hoá filterRouteId về string để so sánh linh hoạt
    const filterArr = Array.isArray(filterRouteId)
        ? filterRouteId.map(String)
        : [String(filterRouteId)];

    // Có filter → CHỈ vẽ tuyến được chọn
    let drawnCount = 0;
    features.forEach(feature => {
        if (!feature.geometry) return;

        const props     = feature.properties;
        const featureId = String(feature.id ?? props.id ?? '');

        const isSelected = filterArr.includes(featureId);

        // Bỏ qua tuyến không được chọn
        if (!isSelected) return;

        drawnCount++;
        const latLngs = feature.geometry.coordinates.map(c => [c[1], c[0]]);
        const color   = props.color || '#3388ff';

        L.polyline(latLngs, {
            color,
            weight:  6,
            opacity: 1,
        }).bindPopup(`
            <div class="popup-content">
                <h5 style="color:${color}">Tuyến ${props.route_number}</h5>
                <p><strong>${props.name}</strong></p>
                <p>${props.start_point} → ${props.end_point}</p>
                <p><i class="bi bi-geo-alt"></i> ${props.total_stops} trạm</p>
            </div>
        `).addTo(routesLayer);
    });

    console.log(`[displayRoutes] filter=${filterRouteId}, drawn=${drawnCount}/${features.length}`);
}

// ─── Address Search (Nominatim) ───────────────────────────────────────────────
let addressMarker = null;
let searchDebounceTimer = null;

async function searchAddress() {
    const query = document.getElementById('search-input').value.trim();
    if (query.length < 2) {
        showNotification('Nhập ít nhất 2 ký tự để tìm kiếm', 'warning');
        return;
    }

    showLoading('Đang tìm kiếm địa chỉ...');
    const container = document.getElementById('search-results');

    try {
        // Parallel: search address (Nominatim) + search stop name
        const [nomRes, stopRes] = await Promise.allSettled([
            fetch(`${NOMINATIM}/search?q=${encodeURIComponent(query)}&countrycodes=vn&format=json&limit=5&addressdetails=1`, {
                headers: { 'Accept-Language': 'vi' }
            }),
            fetch(`${API.stops}search/?q=${encodeURIComponent(query)}`)
        ]);

        const nomData  = nomRes.status === 'fulfilled'  ? await nomRes.value.json()  : [];
        const stopData = stopRes.status === 'fulfilled' ? await stopRes.value.json() : [];

        const results = [];

        // Address results
        nomData.forEach(item => {
            results.push({
                type:    'address',
                name:    item.display_name.split(',')[0],
                address: item.display_name,
                lat:     parseFloat(item.lat),
                lng:     parseFloat(item.lon),
            });
        });

        // Stop name results
        (Array.isArray(stopData) ? stopData : (stopData.results || [])).forEach(stop => {
            results.push({
                type:    'stop',
                name:    stop.name,
                address: stop.address || 'Trạm dừng xe buýt',
                lat:     stop.latitude,
                lng:     stop.longitude,
            });
        });

        displayAddressResults(results, container);
    } catch (e) {
        showNotification('Lỗi khi tìm kiếm', 'error');
        console.error(e);
    } finally {
        hideLoading();
    }
}

// Simple text search (old name kept for backwards compatibility)
async function searchStops() {
    await searchAddress();
}

function displayAddressResults(results, container) {
    if (!results || results.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-muted"><i class="bi bi-search" style="font-size:2rem"></i><p class="mt-2 mb-0">Không tìm thấy kết quả</p></div>`;
        return;
    }
    container.innerHTML = results.map(r => `
        <div class="result-item" onclick="focusOnLocation(${r.lat}, ${r.lng}, '${(r.name || '').replace(/'/g, "\\'")}', '${(r.address || '').replace(/'/g, "\\'")}')">
            <div class="result-icon" style="background:${r.type === 'stop' ? '#0066cc' : '#00b894'}">
                <i class="bi bi-${r.type === 'stop' ? 'geo-alt-fill' : 'map-pin-fill'}"></i>
            </div>
            <div class="result-info">
                <h6>${r.name}</h6>
                <p>${r.address}</p>
            </div>
        </div>`).join('');
}

function focusOnLocation(lat, lng, name, address) {
    map.setView([lat, lng], 17);

    if (addressMarker) map.removeLayer(addressMarker);
    addressMarker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: '',
            html: `<div style="background:#e74c3c;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,.5)"></div>`,
            iconSize: [16, 16], iconAnchor: [8, 8]
        })
    }).addTo(map);

    addressMarker.bindPopup(`
        <div class="popup-content">
            <h5><i class="bi bi-map-pin-fill text-danger me-1"></i>${name}</h5>
            <p class="small text-muted">${address}</p>
            <hr class="my-1">
            <div class="d-flex gap-2 small fw-semibold">
                <span><i class="bi bi-geo text-primary me-1"></i>Lng: <strong>${parseFloat(lng).toFixed(6)}</strong></span>
                <span><i class="bi bi-geo text-success me-1"></i>Lat: <strong>${parseFloat(lat).toFixed(6)}</strong></span>
            </div>
        </div>`).openPopup();

    showNotification(`📍 ${name} | Lng: ${parseFloat(lng).toFixed(5)}, Lat: ${parseFloat(lat).toFixed(5)}`, 'success');
}

function focusOnStop(lat, lng, name) {
    focusOnLocation(lat, lng, name, '');
}

// ─── Nearest Stops ────────────────────────────────────────────────────────────
async function findNearestStop() {
    if (!navigator.geolocation) {
        showNotification('Trình duyệt không hỗ trợ định vị', 'error');
        return;
    }
    showLoading('Đang xác định vị trí của bạn...');
    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        placeUserMarker(lat, lng);

        try {
            const res  = await fetch(`${API.nearestStops}?lat=${lat}&lng=${lng}&limit=5`);
            const data = await res.json();
            routeResultLayer.clearLayers();

            if (data.nearest_stops && data.nearest_stops.length > 0) {
                showNearestStopsResults(data.nearest_stops);
                const nearest = data.nearest_stops[0];

                try {
                    const osrmRes  = await fetch(`https://router.project-osrm.org/route/v1/driving/${lng},${lat};${nearest.longitude},${nearest.latitude}?overview=full&geometries=geojson`);
                    const osrmData = await osrmRes.json();

                    if (osrmData.routes && osrmData.routes.length > 0) {
                        const route       = osrmData.routes[0];
                        const distance    = route.distance;
                        const travelMin   = Math.ceil(route.duration / 60);

                        L.geoJSON(route.geometry, {
                            style: { color: '#e74c3c', weight: 5, opacity: 0.8 }
                        }).addTo(routeResultLayer);

                        showInfoPanel('Thông tin dẫn đường', `
                            <div class="p-2">
                                <h6 class="mb-3"><i class="bi bi-geo-alt-fill text-danger me-2"></i>Đến: ${nearest.name}</h6>
                                <div class="mb-2"><i class="bi bi-shuffle me-2"></i><strong>Quãng đường:</strong> ${formatDistance(distance)}</div>
                                <div class="mb-2"><i class="bi bi-clock-history me-2"></i><strong>Thời gian (ô tô):</strong> ~${travelMin} phút</div>
                                <div class="mb-3 small text-muted">
                                    <i class="bi bi-pin-map me-2"></i><strong>Toạ độ trạm:</strong><br>
                                    Lng: ${nearest.longitude.toFixed(6)} | Lat: ${nearest.latitude.toFixed(6)}
                                </div>
                                <button class="btn btn-sm btn-outline-secondary w-100" onclick="clearRouteResult()">
                                    <i class="bi bi-trash me-1"></i>Xóa đường đi
                                </button>
                            </div>
                        `);
                        showNotification(`Tìm thấy đường đi (${formatDistance(distance)})`, 'success');
                    } else {
                        L.polyline([[lat, lng], [nearest.latitude, nearest.longitude]], {
                            color: '#e74c3c', weight: 3, opacity: 0.7, dashArray: '5, 10'
                        }).addTo(routeResultLayer);
                    }
                } catch (osrmErr) {
                    console.error('OSRM Error:', osrmErr);
                    L.polyline([[lat, lng], [nearest.latitude, nearest.longitude]], {
                        color: '#e74c3c', weight: 3, opacity: 0.7, dashArray: '5, 10'
                    }).addTo(routeResultLayer);
                }

                map.fitBounds([[lat, lng], [nearest.latitude, nearest.longitude]], { padding: [100, 100] });
            } else {
                showNotification('Không tìm thấy trạm nào gần đây', 'warning');
            }
        } catch (e) {
            showNotification('Lỗi khi tìm trạm gần nhất', 'error');
        } finally {
            hideLoading();
        }
    }, err => {
        hideLoading();
        showNotification('Không thể xác định vị trí: ' + err.message, 'error');
    });
}

function placeUserMarker(lat, lng) {
    if (userMarker) map.removeLayer(userMarker);
    userMarker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: '',
            html: '<div style="background:#e74c3c;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,.4)"></div>',
            iconSize: [14, 14], iconAnchor: [7, 7]
        })
    }).bindPopup('<div class="popup-content"><h5>Vị trí của bạn</h5></div>').addTo(map);
}

function showNearestStopsResults(stops) {
    document.getElementById('search-results').innerHTML = `
        <h6 class="mb-3"><i class="bi bi-crosshair me-2"></i>Trạm gần bạn nhất</h6>
        ${stops.map((s, i) => `
            <div class="result-item" onclick="focusOnStop(${s.latitude}, ${s.longitude}, '${s.name.replace(/'/g, "\\'")}')">
                <div class="result-icon" style="background:${i === 0 ? '#00b894' : '#0066cc'}">${i + 1}</div>
                <div class="result-info">
                    <h6>${s.name}</h6>
                    <p><i class="bi bi-arrows-move me-1"></i>${formatDistance(s.distance_meters)}</p>
                </div>
            </div>`).join('')}`;
}

function formatDistance(m) {
    return m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(2)} km`;
}

// ─── Buffer Tool ──────────────────────────────────────────────────────────────
function toggleRouteMode() {
    const rf = document.getElementById('route-finder');
    const bt = document.getElementById('buffer-tool');
    const show = rf.style.display === 'none';
    rf.style.display = show ? 'block' : 'none';
    bt.style.display = 'none';
    bufferMode = false;
    _updateActionBtns(show ? event.target.closest('.action-btn') : null);
}

function showBufferTool() {
    const bt = document.getElementById('buffer-tool');
    const rf = document.getElementById('route-finder');
    const show = bt.style.display === 'none';
    bt.style.display = show ? 'block' : 'none';
    rf.style.display = 'none';
    bufferMode = show;
    _updateActionBtns(show ? event.target.closest('.action-btn') : null);
    if (bufferMode) {
        displayStops(allStops, selectedRouteId);
        showNotification('Click vào trạm để hiển thị vùng phục vụ', 'info');
    }
}

function _updateActionBtns(activeBtn) {
    document.querySelectorAll('.action-btn').forEach(b => b.classList.remove('active'));
    if (activeBtn) activeBtn.classList.add('active');
}

function updateRadiusLabel() {
    currentBufferRadius = parseInt(document.getElementById('buffer-radius').value);
    document.getElementById('radius-value').textContent = currentBufferRadius + 'm';
}

async function showBufferForStop(stopId, lng, lat) {
    bufferLayer.clearLayers();
    try {
        const res  = await fetch(`${API.stopsInRadius}?lng=${lng}&lat=${lat}&radius=${currentBufferRadius}`);
        const data = await res.json();
        if (data.buffer_geojson) {
            L.geoJSON(data.buffer_geojson, {
                style: { color: '#0066cc', weight: 2, fillColor: '#0066cc', fillOpacity: 0.12 }
            }).addTo(bufferLayer);
        }
        showInfoPanel('Vùng phục vụ', `
            <p><strong>Bán kính:</strong> ${currentBufferRadius} m</p>
            <p><strong>Số trạm trong vùng:</strong> ${data.stops_count}</p><hr>
            <ul class="list-unstyled mb-0">
                ${(data.stops || []).map(s => `
                    <li class="mb-2">
                        <i class="bi bi-geo-alt text-primary me-2"></i>${s.name}
                        <small class="text-muted">(${formatDistance(s.distance_meters)})</small>
                    </li>`).join('')}
            </ul>`);
    } catch (e) {
        showNotification('Lỗi khi tạo vùng đệm', 'error');
    }
}

// ─── Routes for a Stop ────────────────────────────────────────────────────────
function showRoutesForStop(stopId) {
    const stop = allStops.find(s => s.id === stopId);
    if (!stop) return;
    const routeIds = (stop.properties.routes || []).map(r => r.id);
    if (routeIds.length === 0) {
        showNotification('Trạm này không có tuyến nào đi qua', 'warning');
        return;
    }
    // Highlight các tuyến đi qua trạm, mờ phần còn lại
    displayRoutes(allRoutes, routeIds);
    // Zoom vào bounding box của các tuyến đó
    const features = allRoutes.filter(r => routeIds.includes(r.id || r.properties?.id));
    if (features.length > 0) {
        const latLngs = features.flatMap(r => (r.geometry?.coordinates || []).map(c => [c[1], c[0]]));
        if (latLngs.length) map.fitBounds(latLngs, { padding: [30, 30] });
    }
    showNotification(`Đang hiển thị ${routeIds.length} tuyến đi qua trạm`, 'success');
}

// ─── Route Filter ─────────────────────────────────────────────────────────────
function filterByRoute(routeId) {
    selectedRouteId = routeId;
    displayStops(allStops, routeId);

    if (!routeId || routeId === 'all') {
        displayAllRoutes(allRoutes); // Tất cả tuyến mờ nhạt
    } else {
        displayRoutes(allRoutes, routeId); // Highlight tuyến chọn, mờ phần còn lại

        // Zoom vào tuyến được chọn
        const selected = allRoutes.find(r => (r.id || r.properties?.id) === parseInt(routeId));
        if (selected && selected.geometry) {
            const latLngs = selected.geometry.coordinates.map(c => [c[1], c[0]]);
            if (latLngs.length) map.fitBounds(latLngs, { padding: [40, 40] });
        }
    }
}

// ─── Route Finder Autocomplete ────────────────────────────────────────────────
function setupRouteFinderAutocomplete() {
    setupStopAutocomplete(
        document.getElementById('start-stop-input'),
        'start-suggestions', 'start-stop-id');
    setupStopAutocomplete(
        document.getElementById('end-stop-input'),
        'end-suggestions', 'end-stop-id');
}

function setupStopAutocomplete(input, suggestionsId, valueId) {
    if (!input) return;
    let timer;

    input.addEventListener('input', function () {
        clearTimeout(timer);
        document.getElementById(valueId).value = '';
        const q   = this.value.trim();
        const box = document.getElementById(suggestionsId);
        if (q.length < 2) { box.style.display = 'none'; return; }

        timer = setTimeout(async () => {
            try {
                // Search both stops and addresses
                const [stopRes, nomRes] = await Promise.allSettled([
                    fetch(`${API.stops}?search=${encodeURIComponent(q)}`),
                    fetch(`${NOMINATIM}/search?q=${encodeURIComponent(q)}&countrycodes=vn&format=json&limit=3`, {
                        headers: { 'Accept-Language': 'vi' }
                    })
                ]);

                const stopData = stopRes.status === 'fulfilled' ? await stopRes.value.json() : [];
                const nomData  = nomRes.status === 'fulfilled'  ? await nomRes.value.json()  : [];

                const items = [];

                (Array.isArray(stopData) ? stopData : (stopData.results || [])).slice(0, 6).forEach(s => {
                    items.push({ id: `stop_${s.id}`, label: s.name, sub: s.address || 'Trạm dừng xe buýt', lat: s.latitude, lng: s.longitude, isStop: true, stopId: s.id });
                });

                nomData.slice(0, 3).forEach(item => {
                    items.push({ id: `addr_${item.place_id}`, label: item.display_name.split(',')[0], sub: item.display_name, lat: parseFloat(item.lat), lng: parseFloat(item.lon), isStop: false });
                });

                if (items.length > 0) {
                    box.innerHTML = items.map(s => `
                        <div class="suggestion-item"
                             onclick="selectRouteFinderStop('${s.id}', '${(s.label || '').replace(/'/g, "\\'")}', '${valueId}', '${input.id}', '${suggestionsId}', ${s.lat}, ${s.lng}, ${s.isStop})">
                            <i class="bi bi-${s.isStop ? 'geo-alt-fill text-primary' : 'map-pin text-success'} me-1"></i>
                            <strong>${s.label}</strong>
                            <small>${s.sub}</small>
                        </div>`).join('');
                    box.style.display = 'block';
                } else {
                    box.style.display = 'none';
                }
            } catch (e) { console.error('Autocomplete error', e); }
        }, 300);
    });

    input.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        const q = this.value.trim();
        if (q.length < 2) return;
        // auto-pick first suggestion visible
        const box = document.getElementById(suggestionsId);
        const first = box.querySelector('.suggestion-item');
        if (first) first.click();
    });

    document.addEventListener('click', e => {
        if (e.target !== input && !e.target.closest(`#${suggestionsId}`)) {
            document.getElementById(suggestionsId).style.display = 'none';
        }
    });
}

// Store lat/lng for non-stop locations used in route finding
const _tempLocations = {};

function selectRouteFinderStop(id, name, valueId, inputId, suggestionsId, lat, lng, isStop) {
    document.getElementById(valueId).value   = id;
    document.getElementById(inputId).value   = name;
    document.getElementById(suggestionsId).style.display = 'none';
    _tempLocations[id] = { lat, lng, name };
}

function selectStop(id, name, valueId, inputId, suggestionsId) {
    selectRouteFinderStop(`stop_${id}`, name, valueId, inputId, suggestionsId, null, null, true);
}

async function useCurrentLocation(type) {
    if (!navigator.geolocation) { showNotification('Trình duyệt không hỗ trợ định vị', 'error'); return; }
    showNotification('Đang lấy vị trí...', 'info');
    navigator.geolocation.getCurrentPosition(async pos => {
        try {
            const res  = await fetch(`${API.nearestStops}?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}&limit=1`);
            const data = await res.json();
            if (data.nearest_stops && data.nearest_stops.length > 0) {
                const s       = data.nearest_stops[0];
                const inputId = type === 'start' ? 'start-stop-input' : 'end-stop-input';
                const valueId = type === 'start' ? 'start-stop-id'    : 'end-stop-id';
                const sugId   = type === 'start' ? 'start-suggestions' : 'end-suggestions';
                selectRouteFinderStop(`stop_${s.id}`, s.name + ' (Gần bạn)', valueId, inputId, sugId, s.latitude, s.longitude, true);
                showNotification(`Đã chọn: ${s.name}`, 'success');
            }
        } catch (e) { showNotification('Lỗi khi tìm trạm', 'error'); }
    }, err => showNotification('Không thể xác định vị trí', 'error'));
}

// Helper: parse stop ID from composed ID like "stop_5" or "addr_xxx"
function _parseStopId(composedId) {
    if (!composedId) return null;
    if (composedId.startsWith('stop_')) return parseInt(composedId.replace('stop_', ''));
    return null;
}

// ─── Find Route ───────────────────────────────────────────────────────────────
async function findRoute() {
    const startId  = document.getElementById('start-stop-id').value;
    const endId    = document.getElementById('end-stop-id').value;

    if (!startId || !endId) {
        showNotification('Vui lòng chọn điểm đi và điểm đến từ danh sách gợi ý', 'warning');
        return;
    }

    const startStopId = _parseStopId(startId);
    const endStopId   = _parseStopId(endId);

    if (!startStopId || !endStopId) {
        showNotification('Tìm đường chỉ hỗ trợ giữa hai trạm xe buýt. Vui lòng chọn trạm xe buýt (icon xanh dương)', 'warning');
        return;
    }
    if (startStopId === endStopId) {
        showNotification('Điểm đi và điểm đến không được trùng nhau', 'warning');
        return;
    }

    showLoading('Đang tính toán lộ trình tối ưu...');

    try {
        const res  = await fetch(`${API.findRoute}?start_stop_id=${startStopId}&end_stop_id=${endStopId}`);
        const data = await res.json();
        routeResultLayer.clearLayers();

        // Ẩn tuyến nền để bản đồ clean
        routesLayer.clearLayers();

        if (!data.routes || data.routes_found === 0) {
            showNotification('Không tìm thấy tuyến xe nối hai trạm này', 'warning');
            hideLoading();
            return;
        }

        const allLatLngs = [];

        data.routes.forEach((route, routeIdx) => {
            if (route.type === 'direct') {
                _drawSegment(route.stops, route.color, routeResultLayer, allLatLngs);
                _markTerminals(route.stops, route.color, routeResultLayer);

            } else if (route.type === 'transfer') {
                // Draw 2 segments
                route.segments.forEach(seg => {
                    _drawSegment(seg.stops, seg.color, routeResultLayer, allLatLngs);
                });
                // Transfer stop marker
                const ts = route.transfer_stop;
                if (ts) {
                    allLatLngs.push([ts.lat, ts.lng]);
                    L.circleMarker([ts.lat, ts.lng], {
                        radius: 13, fillColor: '#f59e0b', color: '#fff', weight: 3, fillOpacity: 1
                    }).bindPopup(`<div class="popup-content"><strong>🔄 Chuyển tuyến tại:<br>${ts.name}</strong></div>`).addTo(routeResultLayer);
                }

            } else if (route.type === 'transfer2') {
                // Draw 3 segments
                route.segments.forEach(seg => {
                    _drawSegment(seg.stops, seg.color, routeResultLayer, allLatLngs);
                });
                // 2 transfer stop markers
                (route.transfer_stops || []).forEach(ts => {
                    if (!ts) return;
                    allLatLngs.push([ts.lat, ts.lng]);
                    L.circleMarker([ts.lat, ts.lng], {
                        radius: 13, fillColor: '#a78bfa', color: '#fff', weight: 3, fillOpacity: 1
                    }).bindPopup(`<div class="popup-content"><strong>🔄 Chuyển tuyến tại:<br>${ts.name}</strong></div>`).addTo(routeResultLayer);
                });
            }
        });

        // Start / End markers
        const startStop = data.start_stop;
        const endStop   = data.end_stop;
        if (startStop) {
            allLatLngs.push([startStop.lat, startStop.lng]);
            L.circleMarker([startStop.lat, startStop.lng], { radius: 12, fillColor: '#27ae60', color: '#fff', weight: 3, fillOpacity: 1 })
              .bindPopup(`<div class="popup-content"><h6>🟢 Điểm đi<br>${startStop.name}</h6></div>`).addTo(routeResultLayer);
        }
        if (endStop) {
            allLatLngs.push([endStop.lat, endStop.lng]);
            L.circleMarker([endStop.lat, endStop.lng], { radius: 12, fillColor: '#e74c3c', color: '#fff', weight: 3, fillOpacity: 1 })
              .bindPopup(`<div class="popup-content"><h6>🔴 Điểm đến<br>${endStop.name}</h6></div>`).addTo(routeResultLayer);
        }

        if (allLatLngs.length > 0) map.fitBounds(allLatLngs, { padding: [60, 60] });

        // Build info panel HTML
        const routeHtml = data.routes.map((r, idx) => {
            if (r.type === 'direct') {
                return `
                <div class="mb-2 p-2 border rounded">
                    <div class="d-flex align-items-center gap-2 mb-1">
                        <span class="route-tag" style="background:${r.color};color:#fff;border-color:${r.color};padding:.2rem .6rem">${r.route_number}</span>
                        <div class="small"><div class="fw-semibold">${r.route_name}</div><div class="text-muted">Đi thẳng – ${r.total_stops} trạm</div></div>
                    </div>
                </div>`;
            } else if (r.type === 'transfer') {
                return `
                <div class="mb-2 p-2 border rounded bg-light">
                    <div class="small text-muted mb-1">Chuyển 1 tuyến tại: <strong>${r.transfer_stop?.name || ''}</strong></div>
                    <div class="d-flex align-items-center gap-1 flex-wrap">
                        <span class="route-tag" style="background:${r.segments[0].color};color:#fff;border-color:${r.segments[0].color}">${r.segments[0].route_number}</span>
                        <span class="small text-muted">${r.segments[0].total_stops} trạm</span>
                        <i class="bi bi-arrow-right text-warning"></i>
                        <span class="route-tag" style="background:${r.segments[1].color};color:#fff;border-color:${r.segments[1].color}">${r.segments[1].route_number}</span>
                        <span class="small text-muted">${r.segments[1].total_stops} trạm</span>
                    </div>
                </div>`;
            } else if (r.type === 'transfer2') {
                const ts = r.transfer_stops || [];
                return `
                <div class="mb-2 p-2 border rounded bg-light">
                    <div class="small text-muted mb-1">Chuyển 2 tuyến</div>
                    <div class="d-flex align-items-center gap-1 flex-wrap">
                        ${r.segments.map((s, si) => `
                            <span class="route-tag" style="background:${s.color};color:#fff;border-color:${s.color}">${s.route_number}</span>
                            ${si < r.segments.length-1 ? `<i class="bi bi-arrow-right text-purple"></i>` : ''}
                        `).join('')}
                    </div>
                    <div class="small text-muted mt-1">Chuyển tại: ${ts.map(t => t?.name || '').filter(Boolean).join(' → ')}</div>
                </div>`;
            }
            return '';
        }).join('');

        // Warnings khi trạm gốc không thuộc tuyến
        const warningHtml = (data.warnings && data.warnings.length > 0)
            ? `<div class="alert alert-warning py-1 px-2 small mb-2">
                <i class="bi bi-exclamation-triangle me-1"></i>
                ${data.warnings.map(w => `<div>${w}</div>`).join('')}
               </div>`
            : '';

        showInfoPanel('Kết quả tìm đường', `
            ${warningHtml}
            <p><strong>Từ:</strong> ${startStop?.name || ''}</p>
            <p><strong>Đến:</strong> ${endStop?.name || ''}</p><hr>
            <p><strong>Tìm thấy ${data.routes_found} lộ trình:</strong></p>
            ${routeHtml}
            <button class="btn btn-sm btn-outline-secondary mt-2 w-100" onclick="clearRouteResult()">
                <i class="bi bi-x me-1"></i>Xóa kết quả
            </button>`);

        if (data.warnings && data.warnings.length > 0) {
            showNotification(data.warnings[0], 'warning');
        }
        showNotification(`Tìm thấy ${data.routes_found} lộ trình`, 'success');

    } catch (e) {
        console.error('findRoute error:', e);
        showNotification('Lỗi khi tìm tuyến', 'error');
    } finally {
        hideLoading();
    }
}

function _drawSegment(stops, color, layer, latLngsAccum) {
    if (!stops || stops.length < 2) return;
    const latLngs = stops.map(s => [s.lat, s.lng]);
    latLngsAccum.push(...latLngs);
    L.polyline(latLngs, { color, weight: 6, opacity: 0.9, dashArray: '10,6' }).addTo(layer);
    stops.forEach((stop, idx) => {
        if (idx === 0 || idx === stops.length - 1) return; // terminals
        L.circleMarker([stop.lat, stop.lng], {
            radius: 5, fillColor: color, color: '#fff', weight: 1.5, fillOpacity: 0.9
        }).bindPopup(`<div class="popup-content"><small>${stop.name}</small></div>`).addTo(layer);
    });
}

function _markTerminals(stops, color, layer) {
    // Internal use for direct routes only - terminals handled separately
}

function clearRouteResult() {
    routeResultLayer.clearLayers();
    closeInfoPanel();
    // Khôi phục tuyến nền
    const sel = document.getElementById('route-select-filter');
    const filterVal = sel ? sel.value : 'all';
    if (filterVal && filterVal !== 'all') {
        displayRoutes(allRoutes, filterVal);
    } else {
        displayAllRoutes(allRoutes);
    }
}

// ─── Info Panel ───────────────────────────────────────────────────────────────
function showInfoPanel(title, content) {
    document.getElementById('info-title').textContent = title;
    document.getElementById('info-content').innerHTML = content;
    document.getElementById('info-panel').style.display = 'block';
}

function closeInfoPanel() {
    document.getElementById('info-panel').style.display = 'none';
}

function toggleSearchPanel() {
    const panel = document.querySelector('.search-panel');
    panel.classList.toggle('collapsed');
    // On mobile, close navbar when opening panel
    if (window.innerWidth <= 768) {
        const navCollapse = document.getElementById('navbarNav');
        if (navCollapse && navCollapse.classList.contains('show')) {
            bootstrap.Collapse.getOrCreateInstance(navCollapse).hide();
        }
    }
}

// Auto-collapse search panel on mobile
function _autoCollapseOnMobile() {
    const panel = document.querySelector('.search-panel');
    if (!panel) return;
    if (window.innerWidth <= 768) {
        panel.classList.add('collapsed');
    } else {
        panel.classList.remove('collapsed');
    }
}
window.addEventListener('load', _autoCollapseOnMobile);

// ─── Map Controls ─────────────────────────────────────────────────────────────
function locateUser() {
    if (!navigator.geolocation) { showNotification('Trình duyệt không hỗ trợ định vị', 'error'); return; }
    navigator.geolocation.getCurrentPosition(pos => {
        placeUserMarker(pos.coords.latitude, pos.coords.longitude);
        map.setView([pos.coords.latitude, pos.coords.longitude], 16);
        showNotification('Đã xác định vị trí của bạn', 'success');
    }, () => showNotification('Không thể xác định vị trí', 'error'));
}

function zoomIn()   { map.zoomIn();  }
function zoomOut()  { map.zoomOut(); }
function resetView() {
    map.setView([10.8231, 106.6297], 13);
    bufferLayer.clearLayers();
    routeResultLayer.clearLayers();
    selectedRouteId = null;
    // Vẽ lại tất cả tuyến mờ nhạt
    displayAllRoutes(allRoutes);
    // Hiển thị lại tất cả trạm
    displayStops(allStops);
    if (addressMarker) { map.removeLayer(addressMarker); addressMarker = null; }
    if (userMarker)    { map.removeLayer(userMarker);    userMarker    = null; }
    closeInfoPanel();
    // Reset dropdown
    const sel = document.getElementById('route-select-filter');
    if (sel) sel.value = 'all';
    showNotification('Bản đồ đã được đặt lại', 'info');
}

// ─── Notifications ────────────────────────────────────────────────────────────
function showNotification(message, type = 'info') {
    const n = document.createElement('div');
    const colours = { success: '#00b894', error: '#e74c3c', warning: '#fdcb6e', info: '#0066cc' };
    const icons   = { success: 'check-circle', error: 'x-circle', warning: 'exclamation-circle', info: 'info-circle' };
    n.innerHTML = `<i class="bi bi-${icons[type]}"></i> <span>${message}</span>`;
    n.style.cssText = `
        position:fixed;top:75px;right:20px;
        background:${colours[type]};color:#fff;
        padding:10px 18px;border-radius:8px;
        display:flex;align-items:center;gap:10px;
        box-shadow:0 4px 16px rgba(0,0,0,.2);z-index:9999;
        animation:slideIn .3s ease-out;font-size:.9rem;max-width:340px;word-break:break-word;`;
    document.body.appendChild(n);
    setTimeout(() => { n.style.animation = 'slideOut .3s ease-out'; setTimeout(() => n.remove(), 300); }, 4000);
}

(function injectAnimations() {
    const s = document.createElement('style');
    s.textContent = `
        @keyframes slideIn  { from{transform:translateX(110%);opacity:0} to{transform:translateX(0);opacity:1} }
        @keyframes slideOut { from{transform:translateX(0);opacity:1} to{transform:translateX(110%);opacity:0} }`;
    document.head.appendChild(s);
})();

// ─── DOM Ready ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    setupRouteFinderAutocomplete();

    const urlParams  = new URLSearchParams(window.location.search);
    const focusRoute = urlParams.get('focus_route');

    await loadStops();
    await loadRoutes(); // tự động gọi displayAllRoutes() bên trong

    if (focusRoute) {
        // Highlight tuyến được focus, mờ phần còn lại
        displayRoutes(allRoutes, focusRoute);
        const routeSelect = document.getElementById('route-select-filter');
        if (routeSelect) routeSelect.value = focusRoute;
        const route = allRoutes.find(r => (r.id || r.properties?.id) == focusRoute);
        if (route && route.geometry) {
            const latLngs = route.geometry.coordinates.map(c => [c[1], c[0]]);
            map.fitBounds(latLngs, { padding: [50, 50] });
        }
    }

    const si = document.getElementById('search-input');
    if (si) si.addEventListener('keypress', e => { if (e.key === 'Enter') searchStops(); });
});
