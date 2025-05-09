$(document).ready(function() {
    // Khởi tạo bản đồ với Leaflet
    var map = L.map('map').setView([21.0085, 105.5524], 13); // Thay đổi lat và lon cho vị trí bạn muốn hiển thị, đây là ví dụ của Hà Nội
  
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  
    let routeLayer;
  
    // Xử lý khi nhấn nút "Tìm đường"
    $('#findRoute').click(function() {
      const start = $('#start').val();
      const end = $('#end').val();
      
      // Gửi yêu cầu đến backend
      $.get(`/find_route?start=${start}&end=${end}`, function(data) {
        // Nếu đã có đường cũ, xóa đi
        if (routeLayer) {
          map.removeLayer(routeLayer);
        }
  
        // Vẽ đường đi trên bản đồ
        const latlngs = data.route.map(coord => [coord.lat, coord.lon]);
        routeLayer = L.polyline(latlngs, { color: 'blue' }).addTo(map);
  
        // Căn chỉnh zoom theo đường đi
        map.fitBounds(routeLayer.getBounds());
      });
    });
  });
  