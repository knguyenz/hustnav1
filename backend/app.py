from flask import Flask, request, jsonify
from map_parser import Graph # Đảm bảo file map_parser.py tồn tại và đúng
from dijkstra import dijkstra   # Đảm bảo file dijkstra.py tồn tại và đúng
import json
import folium
import os

app = Flask(__name__, static_folder='static')

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Vui lòng cập nhật các đường dẫn này cho chính xác với máy của bạn!
PATH_TO_OSM_FILE = r"D:\hust_dsa\hustnav1_main_test\backend\data\hust.osm"
PATH_TO_LOCATIONS_FILE = r"D:\hust_dsa\hustnav1_main_test\backend\locations.json"
PATH_TO_INDEX_HTML = r"D:\hust_dsa\hustnav1_main_test\templates\index.html"
PATH_TO_SAVE_MAP_DIR = "save" # Thư mục lưu bản đồ, ví dụ: 'save/map.html' hoặc 'save/route_map.html'

# Khởi tạo và phân tích dữ liệu OSM
# Sử dụng tên biến 'graph' như trong code gốc của bạn
graph = Graph() # Giữ nguyên tên biến 'graph'
nodes, edges = {}, {} # Khởi tạo rỗng
try:
    graph.parse_osm(PATH_TO_OSM_FILE) # Sử dụng biến 'graph'
    nodes, edges = graph.get_graph()  # Sử dụng biến 'graph'
    if not nodes or not edges:
        print(f"CẢNH BÁO: Dữ liệu 'nodes' hoặc 'edges' rỗng sau khi phân tích OSM tại '{PATH_TO_OSM_FILE}'. Kiểm tra lại map_parser.py và tệp OSM.")
except FileNotFoundError:
    print(f"LỖI: Không tìm thấy tệp OSM tại '{PATH_TO_OSM_FILE}'.")
except Exception as e:
    print(f"LỖI nghiêm trọng khi phân tích tệp OSM: {e}")

# Load tên địa điểm → tọa độ từ file locations.json
locations = {} # Khởi tạo rỗng
try:
    with open(PATH_TO_LOCATIONS_FILE, encoding="utf-8") as f:
        locations = json.load(f)
    if not locations:
        print(f"CẢNH BÁO: Tệp locations.json tại '{PATH_TO_LOCATIONS_FILE}' rỗng hoặc không chứa dữ liệu.")
except FileNotFoundError:
    print(f"LỖI: Không tìm thấy tệp locations.json tại '{PATH_TO_LOCATIONS_FILE}'.")
except json.JSONDecodeError:
    print(f"LỖI: Tệp locations.json tại '{PATH_TO_LOCATIONS_FILE}' không phải là định dạng JSON hợp lệ.")
except Exception as e:
    print(f"LỖI không xác định khi tải locations.json: {e}")


@app.route('/')
def home():
    try:
        return open(PATH_TO_INDEX_HTML, encoding='utf-8').read() # Giữ nguyên cách mở file gốc
    except FileNotFoundError:
        return f"Lỗi: Không tìm thấy tệp index.html tại '{PATH_TO_INDEX_HTML}'. Vui lòng kiểm tra đường dẫn trong app.py.", 404
    except Exception as e:
        return f"Lỗi khi mở index.html: {e}", 500

@app.route('/find_route', methods=['GET'])
def find_route():
    start_location_name = request.args.get('start') # Giữ tên biến gốc là 'start'
    end_location_name = request.args.get('end')       # Giữ tên biến gốc là 'end'

    if not start_location_name or not end_location_name:
        return jsonify({"error": "Vui lòng cung cấp điểm bắt đầu và điểm kết thúc."}), 400

    # Kiểm tra tên địa điểm hợp lệ
    if start_location_name not in locations or end_location_name not in locations:
        missing = []
        if start_location_name not in locations: missing.append(f"'{start_location_name}' (điểm bắt đầu)")
        if end_location_name not in locations: missing.append(f"'{end_location_name}' (điểm kết thúc)")
        return jsonify({"error": f"Tên địa điểm không hợp lệ: {', '.join(missing)}."}), 400

    # Lấy node_id từ file locations
    start_node_info = locations[start_location_name]
    end_node_info = locations[end_location_name]
    
    start_node_id = start_node_info.get('node_id') # Sử dụng .get() để an toàn hơn
    end_node_id = end_node_info.get('node_id')   # Sử dụng .get() để an toàn hơn

    if not start_node_id or not end_node_id:
        return jsonify({"error": "Một trong các địa điểm thiếu thông tin 'node_id' trong locations.json."}), 400

    print(f"Tìm đường: Từ '{start_location_name}' (Node ID: {start_node_id}) đến '{end_location_name}' (Node ID: {end_node_id})")


    # Chạy thuật toán Dijkstra
    dist, path = dijkstra(start_node_id, end_node_id, nodes, edges)
    print(f"Dijkstra cho /find_route: Khoảng cách = {dist}, Path IDs = {path}")

    if dist == float('inf') or not path:
        return jsonify({"error": "Không tìm được đường đi giữa hai địa điểm này."}), 404

    # Vẽ bản đồ bằng folium
    # Đặt tên file cụ thể cho bản đồ tìm đường
    map_file_name = 'map.html'
    map_file_path = os.path.join(PATH_TO_SAVE_MAP_DIR, map_file_name)
    create_route_map(path, nodes, output_path=map_file_path)

    return jsonify({
        'distance': dist,
        'path': path, # Trả về danh sách ID node như ban đầu
        'map_url': f'/map/{map_file_name}', # URL cụ thể của bản đồ đã tạo
        'start_location_name': start_location_name,
        'end_location_name': end_location_name
    })

@app.route('/find_nearest_parking', methods=['GET'])
def find_nearest_parking():
    start_location_name = request.args.get('start')

    if not start_location_name:
        return jsonify({"error": "Vui lòng cung cấp vị trí bắt đầu."}), 400

    if start_location_name not in locations:
        return jsonify({"error": f"Tên địa điểm bắt đầu '{start_location_name}' không hợp lệ."}), 400

    start_node_info = locations[start_location_name]
    start_node_id = start_node_info.get('node_id')

    if not start_node_id:
        return jsonify({"error": f"Địa điểm bắt đầu '{start_location_name}' thiếu thông tin 'node_id' trong locations.json."}), 400
    
    print(f"Tìm nhà xe gần nhất từ: '{start_location_name}' (Node ID: {start_node_id})")

    parking_spots = []
    for name, details in locations.items():
        if details.get("type") == "parking":
            parking_node_id = details.get("node_id")
            if parking_node_id and parking_node_id in nodes:
                parking_spots.append({
                    "name": name,
                    "node_id": parking_node_id,
                })
            else:
                print(f"CẢNH BÁO: Nhà xe '{name}' với node_id '{parking_node_id}' không hợp lệ hoặc không tồn tại trong đồ thị.")
    
    if not parking_spots:
        return jsonify({"error": "Không có thông tin nhà xe nào được định nghĩa (với type='parking' và node_id hợp lệ) trong locations.json."}), 404
    
    print(f"Tìm thấy {len(parking_spots)} nhà xe: {[p['name'] for p in parking_spots]}")

    shortest_dist = float('inf')
    shortest_path_to_parking = []
    nearest_parking_info = None

    for parking in parking_spots:
        parking_node_id = parking["node_id"]
        
        print(f"Tính đường từ '{start_location_name}' đến nhà xe '{parking['name']}' (Node ID: {parking_node_id})")
        dist, path = dijkstra(start_node_id, parking_node_id, nodes, edges)
        print(f"Kết quả Dijkstra đến '{parking['name']}': Khoảng cách = {dist}, Path IDs = {path}")

        if dist < shortest_dist:
            shortest_dist = dist
            shortest_path_to_parking = path
            nearest_parking_info = parking

    if shortest_dist == float('inf') or not shortest_path_to_parking:
        return jsonify({"error": "Không tìm thấy đường đi đến nhà xe nào từ vị trí của bạn."}), 404

    print(f"Nhà xe gần nhất tìm thấy cho '{start_location_name}': '{nearest_parking_info['name']}', Khoảng cách: {shortest_dist}")
    
    # Vẽ bản đồ cho lộ trình đến nhà xe gần nhất
    map_file_name = 'map.html' # Tên file khác cho bản đồ nhà xe
    map_file_path = os.path.join(PATH_TO_SAVE_MAP_DIR, map_file_name)
    create_route_map(shortest_path_to_parking, nodes, output_path=map_file_path)

    return jsonify({
        'distance': shortest_dist,
        'path': shortest_path_to_parking, # Danh sách ID node
        'map_url': f'/map/{map_file_name}', # URL cụ thể của bản đồ
        'parking_name': nearest_parking_info['name'],
        'start_location_name': start_location_name
    })

# Sửa đổi route /map để chấp nhận tên file động
@app.route('/map/<filename>')
def show_map(filename):
    map_file_path = os.path.join(PATH_TO_SAVE_MAP_DIR, filename)
    try:
        # Kiểm tra xem tệp có tồn tại không trước khi mở
        if not os.path.exists(map_file_path):
            print(f"Lỗi: Tệp bản đồ không tìm thấy tại '{map_file_path}'")
            return "Lỗi: Không tìm thấy tệp bản đồ.", 404
        return open(map_file_path, encoding='utf-8').read()
    except Exception as e:
        print(f"Lỗi khi mở tệp bản đồ '{map_file_path}': {e}")
        return f"Lỗi khi mở tệp bản đồ: {e}", 500

# Giữ nguyên hàm create_route_map như ban đầu
# nhưng thêm kiểm tra và tạo thư mục 'save' nếu chưa có
def create_route_map(path, nodes_data, output_path='save/map.html'): # Giữ nguyên nodes_data
    # Đảm bảo thư mục lưu trữ tồn tại
    save_dir = os.path.dirname(output_path)
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print(f"Đã tạo thư mục: {save_dir}")
        except OSError as exc:
            print(f"Lỗi khi tạo thư mục {save_dir}: {exc}")
            # Không thể tạo thư mục, không thể lưu bản đồ
            return
            
    if not path or not path[0] in nodes_data :
        print(f"Lỗi: Lộ trình không hợp lệ hoặc node đầu tiên '{path[0] if path else 'None'}' không có tọa độ để tạo bản đồ tại '{output_path}'.")
        # Ghi một file HTML thông báo lỗi
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("<html><head><title>Lỗi Bản Đồ</title></head><body><h1>Không thể tạo bản đồ: Lộ trình không hợp lệ hoặc thiếu dữ liệu node.</h1></body></html>")
        except Exception as e_write:
            print(f"Lỗi khi ghi file thông báo lỗi bản đồ: {e_write}")
        return
            
    start_coords = nodes_data[path[0]]
    fmap = folium.Map(location=start_coords, zoom_start=18)

    # Vẽ các node
    for node_id in path:
        if node_id in nodes_data:
            lat, lon = nodes_data[node_id]
            folium.CircleMarker(
                location=(lat, lon),
                radius=4,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=f'Node ID: {node_id}'
            ).add_to(fmap)
        else:
            print(f"Cảnh báo: Node ID {node_id} trong lộ trình không có tọa độ trong nodes_data.")

    # Vẽ đường nối
    route_coords = []
    for node_id in path:
        if node_id in nodes_data:
            route_coords.append(nodes_data[node_id])
    
    if route_coords:
        folium.PolyLine(route_coords, color='red', weight=4).add_to(fmap)

    # Lưu bản đồ
    try:
        fmap.save(output_path)
        print(f"Bản đồ đã được lưu tại: {output_path}")
    except Exception as e:
        print(f"Lỗi khi lưu bản đồ tại '{output_path}': {e}")


if __name__ == '__main__':
    # Đảm bảo thư mục PATH_TO_SAVE_MAP_DIR tồn tại khi khởi động
    if not os.path.exists(PATH_TO_SAVE_MAP_DIR):
        try:
            os.makedirs(PATH_TO_SAVE_MAP_DIR)
            print(f"Đã tạo thư mục '{PATH_TO_SAVE_MAP_DIR}' để lưu bản đồ.")
        except OSError as exc:
            print(f"Lỗi khi tạo thư mục '{PATH_TO_SAVE_MAP_DIR}': {exc}")
    
    app.run(debug=True, port=5000) # Bạn có thể thay đổi port nếu muốn
