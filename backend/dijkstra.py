import heapq

def dijkstra(start_id, end_id, nodes, edges):
    """
    Tính toán đường đi ngắn nhất giữa start_id và end_id bằng thuật toán Dijkstra.

    :param start_id: ID của node bắt đầu
    :param end_id: ID của node đích
    :param nodes: Dictionary chứa thông tin về các node, key là node_id, value là (lat, lon)
    :param edges: Dictionary chứa thông tin về các cạnh (edges), key là node_id, value là list các tuple (neighbor_id, distance)

    :return: tuple (distance, path)
        - distance: Khoảng cách ngắn nhất từ start_id đến end_id
        - path: Đường đi ngắn nhất dưới dạng danh sách các node_id
    """
    # Khởi tạo hàng đợi ưu tiên (priority queue) với distance = 0 tại node bắt đầu
    queue = [(0, start_id, [])]  # (distance, current_node, path)
    
    # Set để theo dõi các node đã duyệt
    visited = set()

    # Duyệt qua các node trong hàng đợi
    while queue:
        # Pop node có giá trị nhỏ nhất (distance)
        dist, current, path = heapq.heappop(queue)

        # Nếu node đã được duyệt thì bỏ qua
        if current in visited:
            continue
        
        # Đánh dấu node đã duyệt
        visited.add(current)
        path = path + [current]

        # Nếu đã đến đích, trả về kết quả
        if current == end_id:
            return dist, path

        # Duyệt qua các neighbor (láng giềng) của node hiện tại
        for neighbor, weight in edges.get(current, []):
            if neighbor not in visited:
                # Thêm vào hàng đợi với distance mới
                heapq.heappush(queue, (dist + weight, neighbor, path))

    # Nếu không tìm thấy đường đi, trả về vô cùng và đường đi rỗng
    return float("inf"), []
