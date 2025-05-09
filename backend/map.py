import folium # vẽ bản đồ với tất cả các node
from map_parser import Graph

# Parse dữ liệu OSM
graph = Graph()
graph.parse_osm(r"D:\hustnav\backend\data\hust.osm")
nodes, edges = graph.get_graph()

# Tìm node nào có liên kết (nằm trong cạnh)
connected_node_ids = set(edges.keys())
for neighbors in edges.values():
    for neighbor_id, _ in neighbors:
        connected_node_ids.add(neighbor_id)

# Tính trung tâm bản đồ
avg_lat = sum(float(nodes[nid][0]) for nid in connected_node_ids) / len(connected_node_ids)
avg_lon = sum(float(nodes[nid][1]) for nid in connected_node_ids) / len(connected_node_ids)
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=18)

# Vẽ node nằm trong way
for node_id in connected_node_ids:
    lat, lon = nodes[node_id]
    folium.CircleMarker(location=[lat, lon], radius=2, color='blue', fill=True).add_to(m)

# Vẽ cạnh
for from_node, neighbors in edges.items():
    for to_node, _ in neighbors:
        if from_node in nodes and to_node in nodes:
            lat1, lon1 = nodes[from_node]
            lat2, lon2 = nodes[to_node]
            folium.PolyLine(locations=[(lat1, lon1), (lat2, lon2)], color="green", weight=1).add_to(m)

# Lưu ra file HTML
m.save("connected_graph_map.html")
print("✅ Đã lưu bản đồ các node có way vào file connected_graph_map.html")
