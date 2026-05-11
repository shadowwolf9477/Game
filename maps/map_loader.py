import random


LAYER_COUNT = 8


def generate_nodes_per_layer(layer_count):
    nodes_per_layer = []

    for layer in range(layer_count):
        if layer == 0:
            nodes_per_layer.append(1)
        elif layer == layer_count - 1:
            nodes_per_layer.append(1)
        else:
            nodes_per_layer.append(random.randint(2, 4))

    return nodes_per_layer

def generate_map():
    # Build the full branching map after the tutorial fight.
    map_layers = []
    nodes_per_layer = generate_nodes_per_layer(LAYER_COUNT)

    for layer in range(LAYER_COUNT):
        nodes_in_layer = nodes_per_layer[layer]
        layer_nodes = []

        for index in range(nodes_in_layer):

            if layer == 0:
                node_type = "start"
            elif layer == LAYER_COUNT - 1:
                node_type = "boss"
            elif layer % 4 == 0:
                # Every fourth stop is a safe recovery/upgrade style node.
                node_type = "rest"
            else:
                # Battles appear twice to make them slightly more common.
                possible_types = ["battle", "battle", "battle", "shop", "upgrade", "event"]
                node_type = random.choice(possible_types)

            node = {
                "connections": [],
                "type": node_type,
                "layer": layer,
                "index": index,
                "x": get_node_x(index, nodes_in_layer),
                "y": 80 + layer * 80,
                # completed/available control what the player has passed and can click.
                "completed": False,
                "available": False
            }

            layer_nodes.append(node)

        map_layers.append(layer_nodes)

    add_connections(map_layers)
    start_node = map_layers[0][0]
    start_node["completed"] = True

    for connected_index in start_node["connections"]:
        map_layers[1][connected_index]["available"] = True

    return map_layers


def get_node_x(index, nodes_in_layer):
    center_x = 600
    spacing = 220
    total_width = (nodes_in_layer - 1) * spacing
    start_x = center_x - total_width // 2
    x = start_x + index * spacing
    return x


def add_connections(map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        for node in current_layer:
            possible_connections = []

            for next_index in range(len(next_layer)):
                if abs(next_index - node["index"]) <= 1:
                    possible_connections.append(next_index)

            if len(possible_connections) == 0:
                closest_index = get_closest_node_index(node["index"], next_layer)
                possible_connections.append(closest_index)

            max_connections = min(2, len(possible_connections))
            connection_count = random.randint(1, max_connections)
            node["connections"] = random.sample(possible_connections, connection_count)

        make_every_next_node_reachable(current_layer, next_layer)


def make_every_next_node_reachable(current_layer, next_layer):
    # The random pass can leave a visible node with no road into it.
    # Add one closest incoming road for every orphaned node.
    for next_node in next_layer:
        next_index = next_node["index"]
        has_incoming_connection = False

        for current_node in current_layer:
            if next_index in current_node["connections"]:
                has_incoming_connection = True
                break

        if not has_incoming_connection:
            closest_current_node = get_closest_current_node(next_node, current_layer)
            closest_current_node["connections"].append(next_index)
            closest_current_node["connections"].sort()


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
