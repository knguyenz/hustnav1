from flask import Flask, request, jsonify
from map_parser import Graph
from dijkstra import dijkstra
import json
import folium
import os

app = Flask(__name__, static_folder='static')

# Khởi tạo và phân tích dữ liệu OSM
graph = Graph()
graph.parse_osm(r"D:\hustnav\backend\data\hust.osm")
nodes, edges = graph.get_graph()

# Load tên địa điểm → tọa độ từ file locations.json
with open(r"D:\hustnav\backend\locations.json", encoding="utf-8") as f:
    locations = json.load(f)

@app.route('/')
def home():
    return open(r"D:\hustnav\templates\index.html", encoding='utf-8')

@app.route('/find_route', methods=['GET'])
def find_route():
    start = request.args.get('start')
    end = request.args.get('end')

    # Kiểm tra tên địa điểm hợp lệ
    if start not in locations or end not in locations:
        return jsonify({"error": "Tên địa điểm không hợp lệ."}), 400

    # Lấy node từ locations.json
    start_node_id = locations[start]['node_id']
    end_node_id = locations[end]['node_id']

    print(f"Start Node ID: {start_node_id}, End Node ID: {end_node_id}")

    if start_node_id not in edges or not edges[start_node_id]:
        return jsonify({"error": f"Start node {start_node_id} không có kết nối."}), 400
    if end_node_id not in edges or not edges[end_node_id]:
        return jsonify({"error": f"End node {end_node_id} không có kết nối."}), 400

    dist, path = dijkstra(start_node_id, end_node_id, nodes, edges)
    print(f"Distance: {dist}, Path: {path}")

    create_route_map(path, nodes)

    return jsonify({
        'distance': dist,
        'path': path,
        'map_url': '/map'
    })


# ✅ Route mới: Tìm đường bằng node ID trực tiếp
@app.route('/find_route_by_id', methods=['GET'])
def find_route_by_id():
    try:
        start_node_id = int(request.args.get('start_id'))
        end_node_id = int(request.args.get('end_id'))
    except:
        return jsonify({"error": "ID phải là số nguyên."}), 400

    print(f"[TEST] Start Node ID: {start_node_id}, End Node ID: {end_node_id}")

    if start_node_id not in nodes:
        return jsonify({"error": f"Node {start_node_id} không tồn tại trong graph."}), 400
    if end_node_id not in nodes:
        return jsonify({"error": f"Node {end_node_id} không tồn tại trong graph."}), 400
    if start_node_id not in edges or not edges[start_node_id]:
        return jsonify({"error": f"Start node {start_node_id} không có kết nối."}), 400
    if end_node_id not in edges or not edges[end_node_id]:
        return jsonify({"error": f"End node {end_node_id} không có kết nối."}), 400

    dist, path = dijkstra(start_node_id, end_node_id, nodes, edges)
    print(f"[TEST] Distance: {dist}, Path: {path}")

    if dist == float('inf') or not path:
        return jsonify({"error": "Không tìm được đường đi."}), 404

    create_route_map(path, nodes)

    return jsonify({
        'distance': dist,
        'path': path,
        'map_url': '/map'
    })


@app.route('/map')
def show_map():
    return open('save/map.html', encoding='utf-8').read()

def create_route_map(path, nodes, output_path='save/map.html'):
    if not path:
        return

    start_coords = nodes[path[0]]
    fmap = folium.Map(location=start_coords, zoom_start=18)

    # Vẽ các node
    for node_id in path:
        lat, lon = nodes[node_id]
        folium.CircleMarker(
            location=(lat, lon),
            radius=4,
            color='blue',
            fill=True,
            fill_opacity=0.7,
            popup=f'Node ID: {node_id}'
        ).add_to(fmap)

    # Vẽ đường nối
    route_coords = [nodes[node_id] for node_id in path]
    folium.PolyLine(route_coords, color='red', weight=4).add_to(fmap)

    fmap.save(output_path)

if __name__ == '__main__':
    app.run(debug=True)
