from flask import Flask, request, jsonify, render_template
import googlemaps
import heapq
from datetime import datetime
app = Flask(__name__)

gmaps = googlemaps.Client(key='AIzaSyBnJKzKGqg4qjRpV_zFdrOxIoB4mOlXKJU')


def heuristic(a, b):
    """ Ước lượng chi phí giữa hai điểm (đơn giản là khoảng cách Euclidean). """
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def a_star(start, goal, graph):
    """ Thuật toán A* để tìm đường đi ngắn nhất trong đồ thị. """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor, cost in graph.get(current, []):
            tentative_g_score = g_score[current] + cost
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/directions', methods=['GET'])
def directions():
    start = request.args.get('start')
    goal = request.args.get('goal')
    travelMode = request.args.get('travelMode').lower()

    # Gọi Google Maps API để lấy dữ liệu chỉ đường
    directions_result = gmaps.directions(start, goal, travelMode)
    print(directions_result)
    # Bạn cần phải phân tích kết quả từ Google Maps API và chuyển đổi nó thành đồ thị cho A*
    # Ví dụ: graph = parse_directions_to_graph(directions_result)

    # Tính toán đường đi sử dụng A*
    # path = a_star(start_coordinates, goal_coordinates, graph)
    # directions_result = gmaps.directions(start, goal, mode=mode)

    def parse_directions_to_graph(directions_result):
        graph = {}
        for route in directions_result:
            legs = route['legs']
            for leg in legs:
                steps = leg['steps']
                for step in steps:
                    start_location = (step['start_location']['lat'], step['start_location']['lng'])
                    end_location = (step['end_location']['lat'], step['end_location']['lng'])
                    distance = step['distance']['value']  # Đo bằng mét
                    if start_location not in graph:
                        graph[start_location] = []
                    graph[start_location].append((end_location, distance))


        return graph
    if directions_result:
        # Phân tích kết quả để tạo đồ thị
        graph = parse_directions_to_graph(directions_result)

        # Lấy tọa độ bắt đầu và kết thúc
        start_coordinates = (directions_result[0]['legs'][0]['start_location']['lat'],
                             directions_result[0]['legs'][0]['start_location']['lng'])
        goal_coordinates = (directions_result[0]['legs'][0]['end_location']['lat'],
                            directions_result[0]['legs'][0]['end_location']['lng'])

        # Tính toán đường đi sử dụng A*
        path = a_star(start_coordinates, goal_coordinates, graph)

        # Trích xuất thông tin khoảng cách
        distance = directions_result[0]['legs'][0]['distance']['text']
        distance_value = directions_result[0]['legs'][0]['distance']['value']

        duration = directions_result[0]['legs'][0]['duration']['text']
        duration_value = directions_result[0]['legs'][0]['duration']['value']

        print(path)
        # Trả về chỉ đường cùng với khoảng cách và lộ trình
        return jsonify({
            'directions': directions_result,
            'distance': distance,
            'distance_value': distance_value,
            'duration': duration,
            'duration_value': duration_value,
            'path': path  # Lộ trình tính được bằng A*
        })
    else:
        return jsonify({'error': 'Không tìm thấy chỉ đường'}), 404


if __name__ == '__main__':
    app.run(debug=True)
