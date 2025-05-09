import folium
from map_parser import Graph

# Parse OSM
graph = Graph()
graph.parse_osm("data/hust.osm")
nodes, edges = graph.get_graph()

# Lấy node có liên kết (nằm trên các way)
connected_node_ids = set(edges.keys())
for neighbors in edges.values():
    for neighbor_id, _ in neighbors:
        connected_node_ids.add(neighbor_id)

# Trung tâm bản đồ
avg_lat = sum(float(nodes[nid][0]) for nid in connected_node_ids) / len(connected_node_ids)
avg_lon = sum(float(nodes[nid][1]) for nid in connected_node_ids) / len(connected_node_ids)
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=18)

# Hiển thị node với popup
for node_id in connected_node_ids:
    lat, lon = nodes[node_id]
    folium.Marker(
        location=[lat, lon],
        popup=f"Node ID: {node_id}<br>Lat: {lat}<br>Lon: {lon}",
        icon=folium.Icon(icon='info-sign', icon_color='white', color='blue')
    ).add_to(m)

# Vẽ cạnh
for from_node, neighbors in edges.items():
    for to_node, _ in neighbors:
        if from_node in nodes and to_node in nodes:
            lat1, lon1 = nodes[from_node]
            lat2, lon2 = nodes[to_node]
            folium.PolyLine(locations=[(lat1, lon1), (lat2, lon2)], color="green", weight=1).add_to(m)

# Lưu file HTML
m.save("connected_graph_with_popup.html")
print("✅ Đã lưu bản đồ có chức năng click hiển thị lat/lon.")
