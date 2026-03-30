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

const MIN_ZOOM_STOPS = 14;   // only render stop markers at this zoom or above

// ─── API endpoints ────────────────────────────────────────────────────────────
const API = {
    stops:         '/api/stops/',
    stopsGeojson:  '/api/stops/geojson/',
    routes:        '/api/routes/',
    routesGeojson: '/api/routes/geojson/',
    nearestStops:  '/api/gis/nearest/',
    stopsInRadius: '/api/gis/stops-in-radius/',
    findRoute:     '/api/gis/find-route/',
    distance:      '/api/gis/distance/'
};

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

    stopsLayer      = L.layerGroup().addTo(map);
    routesLayer     = L.layerGroup().addTo(map);
    bufferLayer     = L.layerGroup().addTo(map);
    routeResultLayer = L.layerGroup().addTo(map);

    // Refresh stops on every zoom change
    map.on('zoomend', () => displayStops(allStops, selectedRouteId));
}

// ─── Load Data from API ───────────────────────────────────────────────────────
async function loadStops() {
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
    }
}

async function loadRoutes() {
    try {
        const res  = await fetch(API.routesGeojson);
        const data = await res.json();
        if (data.features) allRoutes = data.features;
        // Routes are hidden by default – only shown when a filter or search fires.
    } catch (e) {
        console.error('Error loading routes:', e);
    }
}

// ─── Display Stops ────────────────────────────────────────────────────────────
function displayStops(features, filterRouteId = null) {
    stopsLayer.clearLayers();

    const zoom = map.getZoom();

    // Hide dots at low zoom unless a specific route is chosen
    if (zoom < MIN_ZOOM_STOPS && (!filterRouteId || filterRouteId === 'all')) {
        showZoomHint(true);
        return;
    }
    showZoomHint(false);

    features.forEach(feature => {
        const coords = feature.geometry.coordinates;   // [lng, lat]
        const props  = feature.properties;

        // Route filter
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
function displayRoutes(features, filterRouteId = null) {
    routesLayer.clearLayers();
    if (!filterRouteId) return;   // Nothing to show

    features.forEach(feature => {
        if (!feature.geometry) return;

        if (filterRouteId !== 'all') {
            if (Array.isArray(filterRouteId)) {
                if (!filterRouteId.includes(feature.id)) return;
            } else {
                if (feature.id !== parseInt(filterRouteId)) return;
            }
        }

        const props  = feature.properties;
        const latLngs = feature.geometry.coordinates.map(c => [c[1], c[0]]);

        L.polyline(latLngs, {
            color:   props.color || '#3388ff',
            weight:  5,
            opacity: 0.85
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

// ─── Search ───────────────────────────────────────────────────────────────────
async function searchStops() {
    const query = document.getElementById('search-input').value.trim();
    if (query.length < 2) {
        showNotification('Nhập ít nhất 2 ký tự', 'warning');
        return;
    }
    try {
        const res  = await fetch(`${API.stops}search/?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        displaySearchResults(data);
    } catch (e) {
        showNotification('Lỗi khi tìm kiếm', 'error');
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    if (!results || results.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-muted"><i class="bi bi-search" style="font-size:2rem"></i><p class="mt-2 mb-0">Không tìm thấy kết quả</p></div>`;
        return;
    }
    container.innerHTML = results.map(stop => `
        <div class="result-item" onclick="focusOnStop(${stop.latitude}, ${stop.longitude}, '${stop.name.replace(/'/g,"\\'")}')">
            <div class="result-icon"><i class="bi bi-geo-alt-fill"></i></div>
            <div class="result-info">
                <h6>${stop.name}</h6>
                <p>${stop.address || 'Không có địa chỉ'}</p>
            </div>
        </div>`).join('');
}

function focusOnStop(lat, lng, name) {
    map.setView([lat, lng], 17);
    stopsLayer.eachLayer(layer => {
        if (layer.feature && layer.feature.properties.name === name) {
            layer.openPopup();
        }
    });
}

// ─── Nearest Stops ────────────────────────────────────────────────────────────
async function findNearestStop() {
    if (!navigator.geolocation) {
        showNotification('Trình duyệt không hỗ trợ định vị', 'error');
        return;
    }
    showNotification('Đang xác định vị trí...', 'info');
    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        placeUserMarker(lat, lng);
        try {
            const res  = await fetch(`${API.nearestStops}?lat=${lat}&lng=${lng}&limit=5`);
            const data = await res.json();
            if (data.nearest_stops && data.nearest_stops.length > 0) {
                showNearestStopsResults(data.nearest_stops);
                const nearest = data.nearest_stops[0];
                map.fitBounds([[lat, lng], [nearest.latitude, nearest.longitude]], { padding: [50, 50] });
            } else {
                showNotification('Không tìm thấy trạm nào gần đây', 'warning');
            }
        } catch (e) {
            showNotification('Lỗi khi tìm trạm gần nhất', 'error');
        }
    }, err => showNotification('Không thể xác định vị trí: ' + err.message, 'error'));
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
            <div class="result-item" onclick="focusOnStop(${s.latitude}, ${s.longitude}, '${s.name.replace(/'/g,"\\'")}')">
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
    displayRoutes(allRoutes, routeIds);
    const features = allRoutes.filter(r => routeIds.includes(r.id));
    if (features.length > 0) {
        const latLngs = features.flatMap(r => (r.geometry?.coordinates || []).map(c => [c[1], c[0]]));
        if (latLngs.length) map.fitBounds(latLngs, { padding: [20, 20] });
    }
    showNotification(`Đang hiển thị ${routeIds.length} tuyến đi qua trạm`, 'success');
}

// ─── Route Filter Chips ───────────────────────────────────────────────────────
function filterByRoute(routeId) {
    document.querySelectorAll('.route-chip').forEach(c => {
        c.classList.toggle('active', c.dataset.route == routeId);
    });
    selectedRouteId = routeId;
    displayStops(allStops, routeId);
    displayRoutes(allRoutes, routeId === 'all' ? null : routeId);
}

// ─── Route Finder Autocomplete ────────────────────────────────────────────────
function setupRouteFinderAutocomplete() {
    setupAutocomplete(
        document.getElementById('start-stop-input'),
        'start-suggestions', 'start-stop-id');
    setupAutocomplete(
        document.getElementById('end-stop-input'),
        'end-suggestions', 'end-stop-id');
}

function setupAutocomplete(input, suggestionsId, valueId) {
    if (!input) return;
    let timer;
    let lastResults = [];

    input.addEventListener('input', function () {
        clearTimeout(timer);
        // Clear the hidden ID when user modifies the text manually
        document.getElementById(valueId).value = '';
        const q = this.value.trim();
        const box = document.getElementById(suggestionsId);
        if (q.length < 2) { box.style.display = 'none'; return; }
        timer = setTimeout(async () => {
            try {
                const res  = await fetch(`${API.stops}?search=${encodeURIComponent(q)}`);
                const data = await res.json();
                lastResults = data.results || data;
                if (lastResults.length > 0) {
                    // Auto-select if exactly 1 result
                    if (lastResults.length === 1) {
                        selectStop(lastResults[0].id, lastResults[0].name, valueId, input.id, suggestionsId);
                        return;
                    }
                    box.innerHTML = lastResults.slice(0, 10).map(s => `
                        <div class="suggestion-item"
                             onclick="selectStop('${s.id}','${s.name.replace(/'/g,"\\'")}','${valueId}','${input.id}','${suggestionsId}')">
                            <strong>${s.name}</strong>
                            <small>${s.address || 'Không có địa chỉ'}</small>
                        </div>`).join('');
                    box.style.display = 'block';
                } else {
                    box.style.display = 'none';
                }
            } catch (e) { console.error('Autocomplete error', e); }
        }, 300);
    });

    // On Enter: auto-pick the first result if no ID is set yet
    input.addEventListener('keydown', async function(e) {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        const currentId = document.getElementById(valueId).value;
        if (currentId) return; // already selected
        const q = this.value.trim();
        if (q.length < 2) return;
        try {
            const res  = await fetch(`${API.stops}?search=${encodeURIComponent(q)}`);
            const data = await res.json();
            const list = data.results || data;
            if (list.length > 0) {
                selectStop(list[0].id, list[0].name, valueId, input.id, suggestionsId);
                showNotification(`Đã chọn: ${list[0].name}`, 'info');
            } else {
                showNotification('Không tìm thấy trạm phù hợp', 'warning');
            }
        } catch(e) {}
    });

    document.addEventListener('click', e => {
        if (e.target !== input && !e.target.closest(`#${suggestionsId}`)) {
            document.getElementById(suggestionsId).style.display = 'none';
        }
    });
}

function selectStop(id, name, valueId, inputId, suggestionsId) {
    document.getElementById(valueId).value = id;
    document.getElementById(inputId).value = name;
    document.getElementById(suggestionsId).style.display = 'none';
}

async function useCurrentLocation(type) {
    if (!navigator.geolocation) { showNotification('Trình duyệt không hỗ trợ định vị', 'error'); return; }
    showNotification('Đang lấy vị trí...', 'info');
    navigator.geolocation.getCurrentPosition(async pos => {
        try {
            const res  = await fetch(`${API.nearestStops}?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}&limit=1`);
            const data = await res.json();
            if (data.nearest_stops && data.nearest_stops.length > 0) {
                const s = data.nearest_stops[0];
                const inputId = type === 'start' ? 'start-stop-input' : 'end-stop-input';
                const valueId = type === 'start' ? 'start-stop-id'    : 'end-stop-id';
                document.getElementById(inputId).value = s.name + ' (Gần bạn)';
                document.getElementById(valueId).value = s.id;
                showNotification(`Đã chọn: ${s.name}`, 'success');
            }
        } catch (e) { showNotification('Lỗi khi tìm trạm', 'error'); }
    }, err => showNotification('Không thể xác định vị trí', 'error'));
}

// ─── Find Route ───────────────────────────────────────────────────────────────
async function findRoute() {
    const startId = document.getElementById('start-stop-id').value;
    const endId   = document.getElementById('end-stop-id').value;
    if (!startId || !endId) {
        showNotification('Vui lòng chọn điểm đi và điểm đến từ danh sách gợi ý', 'warning');
        return;
    }
    if (startId === endId) {
        showNotification('Điểm đi và điểm đến không được trùng nhau', 'warning');
        return;
    }

    showNotification('Đang tìm tuyến...', 'info');

    try {
        const res  = await fetch(`${API.findRoute}?start_stop_id=${startId}&end_stop_id=${endId}`);
        const data = await res.json();
        routeResultLayer.clearLayers();

        if (data.routes_found === 0) {
            showNotification('Không tìm thấy tuyến xe nối hai trạm này', 'warning');
            return;
        }

        const allLatLngs = [];

        data.routes.forEach(route => {
            if (route.type === 'direct') {
                const latLngs = route.stops.map(s => [s.lat, s.lng]);
                allLatLngs.push(...latLngs);
                L.polyline(latLngs, { color: route.color, weight: 6, opacity: 0.9, dashArray: '10,8' }).addTo(routeResultLayer);
                route.stops.forEach((stop, idx) => {
                    L.circleMarker([stop.lat, stop.lng], {
                        radius: 9, fillColor: route.color, color: '#fff', weight: 2, fillOpacity: 1
                    }).bindPopup(`<div class="popup-content"><h6>${idx + 1}. ${stop.name}</h6></div>`).addTo(routeResultLayer);
                });
            } else if (route.type === 'transfer') {
                // Draw transfer stop marker
                const ts = route.transfer_stop;
                allLatLngs.push([ts.lat, ts.lng]);
                L.circleMarker([ts.lat, ts.lng], {
                    radius: 12, fillColor: '#f39c12', color: '#fff', weight: 3, fillOpacity: 1
                }).bindPopup(`<div class="popup-content"><strong>Điểm chuyển: ${ts.name}</strong></div>`).addTo(routeResultLayer);
            }
        });

        // Also mark start / end
        const startStop = data.start_stop;
        const endStop   = data.end_stop;
        allLatLngs.push([startStop.lat, startStop.lng], [endStop.lat, endStop.lng]);

        L.circleMarker([startStop.lat, startStop.lng], { radius: 12, fillColor:'#27ae60', color:'#fff', weight:3, fillOpacity:1 })
          .bindPopup(`<div class="popup-content"><h6>🟢 Điểm đi<br>${startStop.name}</h6></div>`).addTo(routeResultLayer);
        L.circleMarker([endStop.lat, endStop.lng], { radius: 12, fillColor:'#e74c3c', color:'#fff', weight:3, fillOpacity:1 })
          .bindPopup(`<div class="popup-content"><h6>🔴 Điểm đến<br>${endStop.name}</h6></div>`).addTo(routeResultLayer);

        if (allLatLngs.length > 0) map.fitBounds(allLatLngs, { padding: [60, 60] });

        // Info panel
        showInfoPanel('Kết quả tìm đường', `
            <p><strong>Từ:</strong> ${startStop.name}</p>
            <p><strong>Đến:</strong> ${endStop.name}</p><hr>
            <p><strong>Tìm thấy ${data.routes_found} kết quả:</strong></p>
            ${data.routes.map(r => r.type === 'direct' ? `
                <div class="d-flex align-items-center mb-2 p-2 border rounded">
                    <span class="route-tag me-2" style="background:${r.color};color:#fff;border-color:${r.color};padding:.25rem .75rem">${r.route_number}</span>
                    <div><div class="small fw-semibold">${r.route_name}</div><div class="small text-muted">Đi thẳng – ${r.total_stops} trạm</div></div>
                </div>` : `
                <div class="mb-2 p-2 border rounded bg-light">
                    <div class="small text-muted mb-1">Cần chuyển 1 tuyến tại:</div>
                    <div class="fw-semibold small mb-1">${r.transfer_stop.name}</div>
                    <div class="d-flex align-items-center gap-1">
                        <span class="route-tag" style="background:${r.segments[0].color};color:#fff;border-color:${r.segments[0].color}">${r.segments[0].route_number}</span>
                        <i class="bi bi-arrow-right"></i>
                        <span class="route-tag" style="background:${r.segments[1].color};color:#fff;border-color:${r.segments[1].color}">${r.segments[1].route_number}</span>
                    </div>
                </div>`).join('')}
            <button class="btn btn-sm btn-outline-secondary mt-2 w-100" onclick="clearRouteResult()">
                <i class="bi bi-x me-1"></i>Xóa kết quả
            </button>`);

        showNotification(`Tìm thấy ${data.routes_found} tuyến`, 'success');

    } catch (e) {
        console.error('findRoute error:', e);
        showNotification('Lỗi khi tìm tuyến', 'error');
    }
}

function clearRouteResult() {
    routeResultLayer.clearLayers();
    closeInfoPanel();
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
    document.querySelector('.search-panel').classList.toggle('collapsed');
}

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
    routesLayer.clearLayers();
    closeInfoPanel();
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
        animation:slideIn .3s ease-out;font-size:.9rem;`;
    document.body.appendChild(n);
    setTimeout(() => { n.style.animation = 'slideOut .3s ease-out'; setTimeout(() => n.remove(), 300); }, 3000);
}

// Keyframe styles injected once
(function injectAnimations() {
    const s = document.createElement('style');
    s.textContent = `
        @keyframes slideIn  { from{transform:translateX(110%);opacity:0} to{transform:translateX(0);opacity:1} }
        @keyframes slideOut { from{transform:translateX(0);opacity:1} to{transform:translateX(110%);opacity:0} }`;
    document.head.appendChild(s);
})();

// ─── DOM Ready ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupRouteFinderAutocomplete();
    const si = document.getElementById('search-input');
    if (si) si.addEventListener('keypress', e => { if (e.key === 'Enter') searchStops(); });
});
