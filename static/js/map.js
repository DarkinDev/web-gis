/**
 * Bus Management WebGIS - Map JavaScript
 * LeafletJS integration with GIS functionality
 */

// Global variables
let map;
let stopsLayer;
let routesLayer;
let bufferLayer;
let userMarker;
let routeResultLayer;
let allStops = [];
let allRoutes = [];
let selectedRouteId = null;
let bufferMode = false;
let currentBufferRadius = 500;

// API endpoints
const API = {
    stops: '/api/stops/',
    stopsGeojson: '/api/stops/geojson/',
    routes: '/api/routes/',
    routesGeojson: '/api/routes/geojson/',
    nearestStops: '/api/gis/nearest/',
    buffer: '/api/gis/buffer/',
    stopsInRadius: '/api/gis/stops-in-radius/',
    findRoute: '/api/gis/find-route/',
    distance: '/api/gis/distance/'
};

// Initialize map
function initMap() {
    // Create map centered on Ho Chi Minh City
    map = L.map('map', {
        center: [10.8231, 106.6297],
        zoom: 13,
        zoomControl: false
    });

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors | BusGIS',
        maxZoom: 19
    }).addTo(map);

    // Initialize layer groups
    stopsLayer = L.layerGroup().addTo(map);
    routesLayer = L.layerGroup().addTo(map);
    bufferLayer = L.layerGroup().addTo(map);
    routeResultLayer = L.layerGroup().addTo(map);
}

// Load bus stops from API
async function loadStops() {
    try {
        const response = await fetch(API.stopsGeojson);
        const data = await response.json();

        if (data.features) {
            allStops = data.features;
            displayStops(data.features);
        }
    } catch (error) {
        console.error('Error loading stops:', error);
        showNotification('Không thể tải dữ liệu trạm dừng', 'error');
    }
}

// Display stops on map
function displayStops(features, filterRouteId = null) {
    stopsLayer.clearLayers();

    features.forEach(feature => {
        const coords = feature.geometry.coordinates;
        const props = feature.properties;

        // Filter by route if specified
        if (filterRouteId && filterRouteId !== 'all') {
            const hasRoute = props.routes.some(r => r.id === parseInt(filterRouteId));
            if (!hasRoute) return;
        }

        // Create custom marker
        const marker = L.circleMarker([coords[1], coords[0]], {
            radius: 8,
            fillColor: '#0066cc',
            color: '#ffffff',
            weight: 3,
            opacity: 1,
            fillOpacity: 1
        });

        // Create popup content
        const routeTags = props.routes.map(r =>
            `<span class="route-tag" style="background: ${r.color}20; color: ${r.color}; border-color: ${r.color}">${r.route_number}</span>`
        ).join('');

        const popupContent = `
            <div class="popup-content">
                <h5><i class="bi bi-geo-alt-fill me-1"></i>${props.name}</h5>
                ${props.address ? `<p><i class="bi bi-signpost me-1"></i>${props.address}</p>` : ''}
                ${props.routes.length > 0 ? `
                    <div class="popup-routes">
                        <div class="popup-routes-title">Tuyến đi qua:</div>
                        <div class="popup-route-tags">${routeTags}</div>
                        <button class="btn btn-sm btn-outline-primary mt-2 w-100" onclick="showRoutesForStop(${feature.id})">
                             <i class="bi bi-eye me-1"></i>Xem các tuyến này
                        </button>
                    </div>
                ` : ''}
                ${bufferMode ? `
                    <button class="btn btn-sm btn-primary mt-2" onclick="showBufferForStop(${feature.id}, ${coords[0]}, ${coords[1]})">
                        <i class="bi bi-circle me-1"></i>Hiển thị vùng phục vụ
                    </button>
                ` : ''}
            </div>
        `;

        marker.bindPopup(popupContent);
        marker.feature = feature;
        marker.addTo(stopsLayer);
    });
}

// Load bus routes from API
async function loadRoutes() {
    try {
        const response = await fetch(API.routesGeojson);
        const data = await response.json();

        if (data.features) {
            allRoutes = data.features;
            // displayRoutes(data.features); // Hide routes by default to avoid clutter
        }
    } catch (error) {
        console.error('Error loading routes:', error);
    }
}

// Display routes on map
function displayRoutes(features, filterRouteId = null) {
    routesLayer.clearLayers();

    features.forEach(feature => {
        if (!feature.geometry) return;

        // Filter by route if specified
        if (filterRouteId && filterRouteId !== 'all') {
            // Check if feature ID matches filter
            if (feature.id !== parseInt(filterRouteId)) return;
        } else if (Array.isArray(filterRouteId)) {
            // Support filtering by array of IDs (e.g. routes passing through a stop)
            if (!filterRouteId.includes(feature.id)) return;
        } else {
            // If no filter matched and we want to hide by default for 'all', we return.
            // But displayRoutes might be called with a specific list features too. 
            // If 'all' is passed (default), we might want to NOT show anything if we want to hide all.
            // However, the function logic above assumes if filterRouteId is null/all, we show everything passed in 'features'.
            // So to hide all, we should just call displayRoutes([]) or not call it.
            return;
        }

        const props = feature.properties;
        const coords = feature.geometry.coordinates;

        // Convert coordinates to LatLng
        const latLngs = coords.map(c => [c[1], c[0]]);

        // Create polyline
        const polyline = L.polyline(latLngs, {
            color: props.color || '#00b894',
            weight: 5,
            opacity: 0.8
        });

        polyline.bindPopup(`
            <div class="popup-content">
                <h5 style="color: ${props.color}">Tuyến ${props.route_number}</h5>
                <p><strong>${props.name}</strong></p>
                <p>${props.start_point} → ${props.end_point}</p>
                <p><i class="bi bi-geo-alt"></i> ${props.total_stops} trạm</p>
            </div>
        `);

        polyline.addTo(routesLayer);
    });
}

// Search stops
async function searchStops() {
    const query = document.getElementById('search-input').value.trim();
    if (query.length < 2) {
        showNotification('Nhập ít nhất 2 ký tự để tìm kiếm', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API.stops}search/?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        displaySearchResults(data);
    } catch (error) {
        console.error('Error searching:', error);
        showNotification('Lỗi khi tìm kiếm', 'error');
    }
}

// Display search results
function displaySearchResults(results) {
    const container = document.getElementById('search-results');

    if (results.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-search" style="font-size: 2rem;"></i>
                <p class="mt-2 mb-0">Không tìm thấy kết quả</p>
            </div>
        `;
        return;
    }

    container.innerHTML = results.map(stop => `
        <div class="result-item" onclick="focusOnStop(${stop.latitude}, ${stop.longitude}, '${stop.name}')">
            <div class="result-icon">
                <i class="bi bi-geo-alt-fill"></i>
            </div>
            <div class="result-info">
                <h6>${stop.name}</h6>
                <p>${stop.address || 'Không có địa chỉ'}</p>
            </div>
        </div>
    `).join('');
}

// Focus on a stop
function focusOnStop(lat, lng, name) {
    map.setView([lat, lng], 17);

    // Find and open popup
    stopsLayer.eachLayer(layer => {
        if (layer.feature && layer.feature.properties.name === name) {
            layer.openPopup();
        }
    });
}

// Find nearest stops
async function findNearestStop() {
    if (!navigator.geolocation) {
        showNotification('Trình duyệt không hỗ trợ định vị', 'error');
        return;
    }

    showNotification('Đang xác định vị trí của bạn...', 'info');

    navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        // Add user marker
        if (userMarker) {
            map.removeLayer(userMarker);
        }

        userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'user-location-marker',
                html: '<div style="background: #e74c3c; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
            })
        }).addTo(map);

        userMarker.bindPopup('<div class="popup-content"><h5>Vị trí của bạn</h5></div>');

        try {
            const response = await fetch(`${API.nearestStops}?lat=${lat}&lng=${lng}&limit=5`);
            const data = await response.json();

            if (data.nearest_stops && data.nearest_stops.length > 0) {
                showNearestStopsResults(data.nearest_stops);

                // Zoom to show user and nearest stop
                const nearestStop = data.nearest_stops[0];
                const bounds = L.latLngBounds([
                    [lat, lng],
                    [nearestStop.latitude, nearestStop.longitude]
                ]);
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        } catch (error) {
            console.error('Error finding nearest stops:', error);
            showNotification('Lỗi khi tìm trạm gần nhất', 'error');
        }
    }, (error) => {
        showNotification('Không thể xác định vị trí: ' + error.message, 'error');
    });
}

// Show nearest stops results
function showNearestStopsResults(stops) {
    const container = document.getElementById('search-results');

    container.innerHTML = `
        <h6 class="mb-3"><i class="bi bi-crosshair me-2"></i>Trạm gần bạn nhất</h6>
        ${stops.map((stop, index) => `
            <div class="result-item" onclick="focusOnStop(${stop.latitude}, ${stop.longitude}, '${stop.name}')">
                <div class="result-icon" style="background: ${index === 0 ? '#00b894' : '#0066cc'}">
                    ${index + 1}
                </div>
                <div class="result-info">
                    <h6>${stop.name}</h6>
                    <p><i class="bi bi-arrows-move me-1"></i>${formatDistance(stop.distance_meters)}</p>
                </div>
            </div>
        `).join('')}
    `;
}

// Format distance
function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
}

// Toggle route finder
function toggleRouteMode() {
    const routeFinder = document.getElementById('route-finder');
    const isVisible = routeFinder.style.display !== 'none';

    routeFinder.style.display = isVisible ? 'none' : 'block';
    document.getElementById('buffer-tool').style.display = 'none';

    // Update button state
    document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('active'));
    if (!isVisible) {
        event.target.closest('.action-btn').classList.add('active');
    }
}

// Show buffer tool
function showBufferTool() {
    const bufferTool = document.getElementById('buffer-tool');
    const isVisible = bufferTool.style.display !== 'none';

    bufferTool.style.display = isVisible ? 'none' : 'block';
    document.getElementById('route-finder').style.display = 'none';
    bufferMode = !isVisible;

    // Update button state
    document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('active'));
    if (!isVisible) {
        event.target.closest('.action-btn').classList.add('active');
    }

    // Refresh stops to add buffer buttons
    if (bufferMode) {
        displayStops(allStops, selectedRouteId);
        showNotification('Click vào trạm để hiển thị vùng phục vụ', 'info');
    }
}

// Update radius label
function updateRadiusLabel() {
    const radius = document.getElementById('buffer-radius').value;
    document.getElementById('radius-value').textContent = radius + 'm';
    currentBufferRadius = parseInt(radius);
}

// Show buffer for a stop
async function showBufferForStop(stopId, lng, lat) {
    bufferLayer.clearLayers();

    try {
        const response = await fetch(`${API.stopsInRadius}?lng=${lng}&lat=${lat}&radius=${currentBufferRadius}`);
        const data = await response.json();

        // Draw buffer polygon
        if (data.buffer_geojson) {
            const bufferPolygon = L.geoJSON(data.buffer_geojson, {
                style: {
                    color: '#0066cc',
                    weight: 2,
                    fillColor: '#0066cc',
                    fillOpacity: 0.15
                }
            }).addTo(bufferLayer);
        }

        // Show info panel
        showInfoPanel('Vùng phục vụ', `
            <p><strong>Bán kính:</strong> ${currentBufferRadius}m</p>
            <p><strong>Trạm trong vùng:</strong> ${data.stops_count} trạm</p>
            <hr>
            <ul class="list-unstyled mb-0">
                ${data.stops.map(s => `
                    <li class="mb-2">
                        <i class="bi bi-geo-alt text-primary me-2"></i>
                        ${s.name}
                        <small class="text-muted">(${formatDistance(s.distance_meters)})</small>
                    </li>
                `).join('')}
            </ul>
        `);

    } catch (error) {
        console.error('Error creating buffer:', error);
        showNotification('Lỗi khi tạo vùng đệm', 'error');
    }
}

// Show routes passing through a stop
function showRoutesForStop(stopId) {
    const stop = allStops.find(s => s.id === stopId);
    if (!stop) return;

    const routeIds = stop.properties.routes.map(r => r.id);

    if (routeIds.length === 0) {
        showNotification('Trạm này không có tuyến nào đi qua', 'warning');
        return;
    }

    // Display specific routes
    displayRoutes(allRoutes, routeIds);

    // Fit bounds to these routes
    const routesToShow = allRoutes.filter(r => routeIds.includes(r.id));
    if (routesToShow.length > 0) {
        const latLngs = routesToShow.flatMap(r => r.geometry.coordinates.map(c => [c[1], c[0]]));
        if (latLngs.length > 0) {
            map.fitBounds(latLngs, { padding: [20, 20] });
        }
    }

    showNotification(`Đang hiển thị ${routesToShow.length} tuyến đi qua trạm`, 'success');
}

// Setup autocomplete for route finder
function setupRouteFinderAutocomplete() {
    const startInput = document.getElementById('start-stop-input');
    const endInput = document.getElementById('end-stop-input');

    setupAutocomplete(startInput, 'start-suggestions', 'start-stop-id');
    setupAutocomplete(endInput, 'end-suggestions', 'end-stop-id');
}

// Generic autocomplete setup
function setupAutocomplete(inputElement, suggestionsId, valueId) {
    if (!inputElement) return;

    let debounceTimer;

    inputElement.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        const suggestionsContainer = document.getElementById(suggestionsId);

        if (query.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                // Use standard search filter from backend
                const response = await fetch(`${API.stops}?search=${encodeURIComponent(query)}`);
                const data = await response.json();
                const results = data.results || data; // Handle pagination or list

                if (results.length > 0) {
                    suggestionsContainer.innerHTML = results.slice(0, 10).map(stop => `
                        <div class="suggestion-item" onclick="selectStop('${stop.id}', '${stop.name.replace(/'/g, "\\'")}', '${valueId}', '${inputElement.id}', '${suggestionsId}')">
                            <strong>${stop.name}</strong>
                            <small>${stop.address || 'Không có địa chỉ'}</small>
                        </div>
                    `).join('');
                    suggestionsContainer.style.display = 'block';
                } else {
                    suggestionsContainer.style.display = 'none';
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
            }
        }, 300);
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target !== inputElement && e.target.closest(`#${suggestionsId}`) === null) {
            document.getElementById(suggestionsId).style.display = 'none';
        }
    });
}

// Select a stop from suggestions
function selectStop(id, name, valueId, inputId, suggestionsId) {
    document.getElementById(valueId).value = id;
    document.getElementById(inputId).value = name;
    document.getElementById(suggestionsId).style.display = 'none';
}

// Use current location for route finder
function useCurrentLocation(type) {
    if (!navigator.geolocation) {
        showNotification('Trình duyệt không hỗ trợ định vị', 'error');
        return;
    }

    showNotification('Đang lấy vị trí...', 'info');

    navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        try {
            // Find nearest stop to use as start point
            const response = await fetch(`${API.nearestStops}?lat=${lat}&lng=${lng}&limit=1`);
            const data = await response.json();

            if (data.nearest_stops && data.nearest_stops.length > 0) {
                const stop = data.nearest_stops[0];
                const inputId = type === 'start' ? 'start-stop-input' : 'end-stop-input';
                const valueId = type === 'start' ? 'start-stop-id' : 'end-stop-id';

                document.getElementById(inputId).value = stop.name + ' (Gần bạn)';
                document.getElementById(valueId).value = stop.id;
                showNotification(`Đã chọn trạm gần nhất: ${stop.name}`, 'success');
            } else {
                showNotification('Không tìm thấy trạm nào gần bạn', 'warning');
            }
        } catch (error) {
            console.error('Error finding nearest stop:', error);
            showNotification('Lỗi khi tìm trạm gần nhất', 'error');
        }
    });
}

// Find route between two stops
async function findRoute() {
    const startId = document.getElementById('start-stop-id').value;
    const endId = document.getElementById('end-stop-id').value;

    if (!startId || !endId) {
        showNotification('Vui lòng chọn điểm đi và điểm đến từ danh sách gợi ý', 'warning');
        return;
    }

    if (startId === endId) {
        showNotification('Điểm đi và điểm đến không được trùng nhau', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API.findRoute}?start_stop_id=${startId}&end_stop_id=${endId}`);
        const data = await response.json();

        routeResultLayer.clearLayers();

        if (data.routes_found === 0) {
            showNotification('Không tìm thấy tuyến xe nối hai trạm này', 'warning');
            return;
        }

        // Display routes on map
        data.routes.forEach(route => {
            const latLngs = route.stops.map(s => [s.lat, s.lng]);

            const polyline = L.polyline(latLngs, {
                color: route.color,
                weight: 6,
                opacity: 0.9,
                dashArray: '10, 10'
            }).addTo(routeResultLayer);

            // Add markers for stops
            route.stops.forEach((stop, index) => {
                L.circleMarker([stop.lat, stop.lng], {
                    radius: 10,
                    fillColor: route.color,
                    color: '#fff',
                    weight: 2,
                    fillOpacity: 1
                }).bindPopup(`<div class="popup-content"><h6>${index + 1}. ${stop.name}</h6></div>`)
                    .addTo(routeResultLayer);
            });
        });

        // Fit bounds
        const allLatLngs = data.routes.flatMap(r => r.stops.map(s => [s.lat, s.lng]));
        if (allLatLngs.length > 0) {
            map.fitBounds(allLatLngs, { padding: [50, 50] });
        }

        // Show info panel
        showInfoPanel('Kết quả tìm đường', `
            <p><strong>Từ:</strong> ${data.start_stop.name}</p>
            <p><strong>Đến:</strong> ${data.end_stop.name}</p>
            <hr>
            <p><strong>Tìm thấy ${data.routes_found} tuyến:</strong></p>
            ${data.routes.map(r => `
                <div class="d-flex align-items-center mb-2">
                    <span class="route-tag me-2" style="background: ${r.color}; color: white; border-color: ${r.color}; padding: 0.25rem 0.75rem;">
                        ${r.route_number}
                    </span>
                    <span>${r.total_stops} trạm</span>
                </div>
            `).join('')}
            <button class="btn btn-sm btn-outline-secondary mt-2" onclick="clearRouteResult()">
                <i class="bi bi-x me-1"></i>Xóa kết quả
            </button>
        `);

    } catch (error) {
        console.error('Error finding route:', error);
        showNotification('Lỗi khi tìm tuyến', 'error');
    }
}

// Clear route result
function clearRouteResult() {
    routeResultLayer.clearLayers();
    closeInfoPanel();
}

// Filter by route
function filterByRoute(routeId) {
    // Update active state
    document.querySelectorAll('.route-chip').forEach(chip => {
        chip.classList.remove('active');
        if (chip.dataset.route == routeId) {
            chip.classList.add('active');
        }
    });

    selectedRouteId = routeId;

    // Filter stops and routes
    displayStops(allStops, routeId);
    displayRoutes(allRoutes, routeId === 'all' ? [] : routeId); // Hide all if 'all' is selected (reset), or show specific
}

// Show info panel
function showInfoPanel(title, content) {
    const panel = document.getElementById('info-panel');
    document.getElementById('info-title').textContent = title;
    document.getElementById('info-content').innerHTML = content;
    panel.style.display = 'block';
}

// Close info panel
function closeInfoPanel() {
    document.getElementById('info-panel').style.display = 'none';
}

// Toggle search panel
function toggleSearchPanel() {
    const panel = document.querySelector('.search-panel');
    panel.classList.toggle('collapsed');
}

// Map controls
function locateUser() {
    if (!navigator.geolocation) {
        showNotification('Trình duyệt không hỗ trợ định vị', 'error');
        return;
    }

    navigator.geolocation.getCurrentPosition((position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        if (userMarker) {
            map.removeLayer(userMarker);
        }

        userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'user-location-marker',
                html: '<div style="background: #e74c3c; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
            })
        }).addTo(map);

        map.setView([lat, lng], 16);
        showNotification('Đã xác định vị trí của bạn', 'success');
    }, (error) => {
        showNotification('Không thể xác định vị trí', 'error');
    });
}

function zoomIn() {
    map.zoomIn();
}

function zoomOut() {
    map.zoomOut();
}

function resetView() {
    map.setView([10.8231, 106.6297], 13);
    bufferLayer.clearLayers();
    routeResultLayer.clearLayers();
    closeInfoPanel();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#00b894' : type === 'error' ? '#e74c3c' : type === 'warning' ? '#fdcb6e' : '#0066cc'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', function () {
    // Setup autocomplete
    setupRouteFinderAutocomplete();

    // Handle main search on Enter key
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                searchStops();
            }
        });
    }
});
