import random


LAYER_COUNT = 12
MAX_SHOPS = 6
MAX_EVENTS = 15
PATH_COUNT = 3


def generate_map():
    map_layers = []
    nodes_per_layer = generate_nodes_per_layer(LAYER_COUNT)

    shops_placed = 0
    events_placed = 0

    for layer in range(LAYER_COUNT):
        nodes_in_layer = nodes_per_layer[layer]
        layer_nodes = []

        for index in range(nodes_in_layer):
            node_type, shops_placed, events_placed = choose_node_type(
                layer,
                shops_placed,
                events_placed
            )

            node = {
                "connections": [],
                "type": node_type,
                "layer": layer,
                "index": index,
                "x": get_node_x(index, nodes_in_layer),
                "y": 80 + layer * 70,
                "completed": False,
                "available": False
            }

            layer_nodes.append(node)

        if layer != 0 and layer != LAYER_COUNT - 1:
            shops_placed, events_placed = guarantee_battle_in_layer(
                layer_nodes,
                shops_placed,
                events_placed
            )

        map_layers.append(layer_nodes)

    add_spire_style_connections(map_layers)

    start_node = map_layers[0][0]
    start_node["completed"] = True

    for connected_index in start_node["connections"]:
        map_layers[1][connected_index]["available"] = True

    return map_layers


def generate_nodes_per_layer(layer_count):
    nodes_per_layer = []

    for layer in range(layer_count):
        if layer == 0:
            nodes_per_layer.append(1)
        elif layer == layer_count - 1:
            nodes_per_layer.append(1)
        else:
            nodes_per_layer.append(random.randint(3, 5))

    return nodes_per_layer


def choose_node_type(layer, shops_placed, events_placed):
    if layer == 0:
        return "start", shops_placed, events_placed

    if layer == LAYER_COUNT - 1:
        return "boss", shops_placed, events_placed

    if layer % 5 == 0:
        return "rest", shops_placed, events_placed

    possible_types = [
        "battle",
        "battle",
        "battle",
        "battle",
        "upgrade"
    ]

    if shops_placed < MAX_SHOPS:
        possible_types.append("shop")

    if events_placed < MAX_EVENTS:
        possible_types.append("event")

    node_type = random.choice(possible_types)

    if node_type == "shop":
        shops_placed += 1

    if node_type == "event":
        events_placed += 1

    return node_type, shops_placed, events_placed


def guarantee_battle_in_layer(layer_nodes, shops_placed, events_placed):
    for node in layer_nodes:
        if node["type"] == "battle":
            return shops_placed, events_placed

    node_to_replace = random.choice(layer_nodes)
    old_type = node_to_replace["type"]

    if old_type == "shop":
        shops_placed -= 1

    if old_type == "event":
        events_placed -= 1

    node_to_replace["type"] = "battle"

    return shops_placed, events_placed


def get_node_x(index, nodes_in_layer):
    center_x = 600
    spacing = 170
    total_width = (nodes_in_layer - 1) * spacing
    start_x = center_x - total_width // 2

    jitter = random.randint(-20, 20)

    return start_x + index * spacing + jitter


def add_spire_style_connections(map_layers):
    for path_index in range(PATH_COUNT):
        current_index = 0

        for layer_index in range(len(map_layers) - 1):
            current_layer = map_layers[layer_index]
            next_layer = map_layers[layer_index + 1]

            current_index = clamp(current_index, 0, len(current_layer) - 1)

            if layer_index == 0:
                current_index = 0

            current_node = current_layer[current_index]

            possible_next_indexes = get_nearby_next_indexes(
                current_node,
                next_layer
            )

            next_index = random.choice(possible_next_indexes)

            if next_index not in current_node["connections"]:
                current_node["connections"].append(next_index)
                current_node["connections"].sort()

            current_index = next_index

    add_extra_splits(map_layers)
    remove_crossing_connections(map_layers)
    make_every_next_node_reachable(map_layers)


def get_nearby_next_indexes(current_node, next_layer):
    possible = []

    for next_node in next_layer:
        index_distance = abs(next_node["index"] - current_node["index"])

        if index_distance <= 1:
            possible.append(next_node["index"])

    if not possible:
        possible.append(get_closest_node_index(current_node["index"], next_layer))

    return possible


def add_extra_splits(map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        if layer_index == 0:
            continue

        if layer_index == len(map_layers) - 2:
            continue

        for node in current_layer:
            if random.random() > 0.28:
                continue

            if len(node["connections"]) >= 2:
                continue

            nearby = get_nearby_next_indexes(node, next_layer)
            random.shuffle(nearby)

            for next_index in nearby:
                if next_index not in node["connections"]:
                    node["connections"].append(next_index)
                    node["connections"].sort()
                    break


def remove_crossing_connections(map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]

        for left_node in current_layer:
            for right_node in current_layer:
                if left_node["index"] >= right_node["index"]:
                    continue

                for left_connection in left_node["connections"][:]:
                    for right_connection in right_node["connections"][:]:
                        if left_connection > right_connection:
                            if random.random() < 0.5:
                                left_node["connections"].remove(left_connection)
                            else:
                                right_node["connections"].remove(right_connection)


def make_every_next_node_reachable(map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        for next_node in next_layer:
            has_incoming_connection = False

            for current_node in current_layer:
                if next_node["index"] in current_node["connections"]:
                    has_incoming_connection = True
                    break

            if not has_incoming_connection:
                closest_current_node = get_closest_current_node(next_node, current_layer)

                if next_node["index"] not in closest_current_node["connections"]:
                    closest_current_node["connections"].append(next_node["index"])
                    closest_current_node["connections"].sort()

        for current_node in current_layer:
            if len(current_node["connections"]) == 0:
                closest_index = get_closest_node_index(current_node["index"], next_layer)
                current_node["connections"].append(closest_index)


def get_closest_current_node(next_node, current_layer):
    closest_node = current_layer[0]
    closest_distance = abs(current_layer[0]["x"] - next_node["x"])

    for current_node in current_layer:
        distance = abs(current_node["x"] - next_node["x"])

        if distance < closest_distance:
            closest_node = current_node
            closest_distance = distance

    return closest_node


def get_closest_node_index(current_index, next_layer):
    closest_index = 0
    closest_distance = abs(next_layer[0]["index"] - current_index)

    for next_node in next_layer:
        distance = abs(next_node["index"] - current_index)

        if distance < closest_distance:
            closest_index = next_node["index"]
            closest_distance = distance

    return closest_index


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))