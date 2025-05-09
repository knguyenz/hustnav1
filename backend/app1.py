from flask import Flask, request, jsonify
from map_parser import Graph
from dijkstra import dijkstra
import json

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

    # Kiểm tra xem tên địa điểm có hợp lệ không trong locations.json
    if start not in locations or end not in locations:
        return jsonify({"error": "Tên địa điểm không hợp lệ."}), 400

    # Lấy thông tin node gần nhất đã ánh xạ sẵn
    start_node_info = locations[start]
    end_node_info = locations[end]

    print(f"Start Node Info: {start_node_info}, End Node Info: {end_node_info}")

    start_node_id = start_node_info['node_id']
    end_node_id = end_node_info['node_id']

    print(f"Start Node ID: {start_node_id}, End Node ID: {end_node_id}")

    # Kiểm tra xem node có tồn tại trong đồ thị và có cạnh không
    if start_node_id not in edges or not edges[start_node_id]:
        return jsonify({"error": f"Start node {start_node_id} không có kết nối."}), 400
    if end_node_id not in edges or not edges[end_node_id]:
        return jsonify({"error": f"End node {end_node_id} không có kết nối."}), 400

    # Gọi thuật toán Dijkstra với các node ID
    dist, path = dijkstra(start_node_id, end_node_id, nodes, edges)

    print(f"Distance: {dist}, Path: {path}")

    if dist == float('inf') or not path:
        return jsonify({"error": "Không tìm được đường đi."}), 404

    return jsonify({'distance': dist, 'path': path})

if __name__ == '__main__':
    app.run(debug=True)
