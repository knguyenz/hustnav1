from map_parser import Graph  # Import Graph từ map_parser

# Đọc dữ liệu bản đồ
graph = Graph()
graph.parse_osm("data/hust.osm")  # Đảm bảo đường dẫn file OSM chính xác
nodes, edges = graph.get_graph()

# Mở file output.txt để ghi kết quả
with open("output.txt", "w", encoding="utf8") as f:
    f.write("Danh sách các node và các cạnh của chúng:\n")
    
    # Duyệt qua tất cả các node và kiểm tra xem chúng có cạnh không
    for node_id, neighbors in edges.items():
        # Kiểm tra nếu node có cạnh
        if neighbors:
            f.write(f"Node {node_id} có các cạnh nối với:\n")
            for neighbor, distance in neighbors:
                f.write(f"    - {neighbor} với khoảng cách {round(distance, 2)}m\n")
            f.write("\n")
        else:
            f.write(f"Node {node_id} không có cạnh nối.\n")

print("Kết quả đã được ghi vào file output.txt")
