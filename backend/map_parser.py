import xml.etree.ElementTree as ET
from collections import defaultdict
import math

class Graph:
    def __init__(self):
        self.nodes = {}  # id -> (lat, lon)
        self.edges = defaultdict(list)  # id -> list of (neighbor_id, distance)

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = phi2 - phi1
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def parse_osm(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        for node in root.findall("node"):
            node_id = node.attrib["id"]
            lat = float(node.attrib["lat"])
            lon = float(node.attrib["lon"])
            self.nodes[node_id] = (lat, lon)

        for way in root.findall("way"):
            nds = way.findall("nd")
            if len(nds) < 2:
                continue
            for i in range(len(nds) - 1):
                a, b = nds[i].attrib["ref"], nds[i+1].attrib["ref"]
                if a in self.nodes and b in self.nodes:
                    lat1, lon1 = self.nodes[a]
                    lat2, lon2 = self.nodes[b]
                    dist = self.haversine(lat1, lon1, lat2, lon2)
                    self.edges[a].append((b, dist))
                    self.edges[b].append((a, dist))  # bidirectional

    def get_graph(self):
        return self.nodes, self.edges
    
    def debug_edges_for_two_nodes(self, node1, node2):
        # Lọc các cạnh có liên quan đến hai node cụ thể
        count = 0
        for neighbor, dist in self.edges.get(node1, []):
            if neighbor == node2:
                count += 1
        for neighbor, dist in self.edges.get(node2, []):
            if neighbor == node1:
                count += 1
        return count

# Hàm test nằm ngoài class Graph
def test_output():
    graph = Graph()
    graph.parse_osm("data/hust.osm")  # Cập nhật đúng đường dẫn file OSM của bạn

    nodes, edges = graph.get_graph()

    print("Tổng số node:", len(nodes))
    print("Tổng số cạnh:", sum(len(adj) for adj in edges.values()))

    # In 5 node đầu tiên
    print("\nVí dụ node:")
    for i, (nid, (lat, lon)) in enumerate(nodes.items()):
        print(f"{nid}: ({lat}, {lon})")
        if i == 4:
            break

    # In 5 cạnh đầu tiên
    print("\nVí dụ cạnh:")
    for i, (nid, neighbors) in enumerate(edges.items()):
        print(f"{nid} → {[f'{n}:{round(d,2)}m' for n, d in neighbors]}")
        if i == 4:
            break
             # Kiểm tra số lượng cạnh giữa hai node cụ thể
    node1 = "1494034258"
    node2 = "10126205567"
    edges_count = graph.debug_edges_for_two_nodes(node1, node2)
    print(f"Số lượng cạnh giữa {node1} và {node2}: {edges_count}")


# Gọi test nếu chạy trực tiếp
if __name__ == "__main__":
    test_output()
