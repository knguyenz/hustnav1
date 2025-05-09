import xml.etree.ElementTree as ET
import json
from map_parser import Graph
from geopy.distance import geodesic

# Bước 1: Parse đồ thị để lấy các node hợp lệ
graph = Graph()
graph.parse_osm("data/hust.osm")
nodes, edges = graph.get_graph()  # nodes = {node_id: (lat, lon)}, edges = {node_id: [(neighbor_id, distance), ...]}

# Bước 2: Parse địa điểm có tag 'name' từ file OSM gốc
tree = ET.parse('data/hust.osm')
root = tree.getroot()

locations = {}

def find_closest_node(lat, lon, nodes, edges):
    min_dist = float('inf')
    closest_id = None
    for node_id, (n_lat, n_lon) in nodes.items():
        if node_id not in edges or not edges[node_id]:
            continue  # Bỏ qua các node không có kết nối
        dist = geodesic((lat, lon), (n_lat, n_lon)).meters
        if dist < min_dist:
            min_dist = dist
            closest_id = node_id
    return closest_id, min_dist

# Duyệt tất cả các node có tag 'name' trong file .osm
for node in root.findall('node'):
    lat = float(node.get('lat'))
    lon = float(node.get('lon'))
    for tag in node.findall('tag'):
        if tag.get('k') == 'name':
            name = tag.get('v')
            # Tìm node gần nhất có trong đồ thị và có cạnh
            closest_node_id, dist = find_closest_node(lat, lon, nodes, edges)
            locations[name] = {
                "node_id": closest_node_id,
                "lat": lat,
                "lon": lon,
                "distance_to_graph_node_m": round(dist, 2)
            }

# Ghi file kết quả
with open('locations.json', 'w', encoding="utf-8") as f:
    json.dump(locations, f, ensure_ascii=False, indent=4)

print("✅ locations.json đã được tạo thành công với các node nằm trong đồ thị có kết nối.")
