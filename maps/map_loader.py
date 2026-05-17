import random


LAYER_COUNT = 12
MAX_SHOPS = 6
MAX_EVENTS = 15
PATH_COUNT = 6
MIN_START_CHOICES = 2
SPLIT_CHANCE = 0.24

BASIC_NODE_TYPES = ["battle", "shop", "event"]
NON_REPEAT_NODE_TYPES = ["shop", "event", "rest"]


def generate_map():
    map_layers = []
    nodes_per_layer = generate_nodes_per_layer(LAYER_COUNT)

    for layer in range(LAYER_COUNT):
        nodes_in_layer = nodes_per_layer[layer]
        layer_nodes = []

        for index in range(nodes_in_layer):
            node = {
                "connections": [],
                "type": None,
                "layer": layer,
                "index": index,
                "x": get_node_x(index, nodes_in_layer),
                "y": 80 + layer * 70,
                "completed": False,
                "available": False
            }

            layer_nodes.append(node)

        map_layers.append(layer_nodes)

    add_spire_style_connections(map_layers)
    remove_pathless_nodes(map_layers)
    repair_all_dead_ends(map_layers)
    assign_map_node_types(map_layers)
    enforce_split_destination_variety(map_layers)

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


def assign_map_node_types(map_layers):
    shops_placed = 0
    events_placed = 0

    for layer_index, layer_nodes in enumerate(map_layers):
        for node in layer_nodes:
            node_type, shops_placed, events_placed = choose_node_type(
                map_layers,
                node,
                shops_placed,
                events_placed
            )
            node["type"] = node_type

        if layer_index != 0 and layer_index != len(map_layers) - 1:
            shops_placed, events_placed = guarantee_battle_in_layer(
                layer_nodes,
                shops_placed,
                events_placed
            )


def choose_node_type(map_layers, node, shops_placed, events_placed):
    layer = node["layer"]

    if layer == 0:
        return "start", shops_placed, events_placed

    if layer == len(map_layers) - 1:
        return "boss", shops_placed, events_placed

    if layer == 1:
        return "battle", shops_placed, events_placed

    if layer == len(map_layers) - 2:
        return "rest", shops_placed, events_placed

    if layer % 5 == 0:
        return "rest", shops_placed, events_placed

    possible_types = get_weighted_node_types(layer, shops_placed, events_placed)
    possible_types = remove_bad_repeat_types(map_layers, node, possible_types)

    node_type = random.choice(possible_types)

    if node_type == "shop":
        shops_placed += 1

    if node_type == "event":
        events_placed += 1

    return node_type, shops_placed, events_placed


def get_weighted_node_types(layer, shops_placed, events_placed):
    possible_types = ["battle", "battle", "battle", "battle", "battle"]

    if layer >= 3 and shops_placed < MAX_SHOPS:
        possible_types.extend(["shop", "shop"])

    if events_placed < MAX_EVENTS:
        possible_types.extend(["event", "event"])

    return possible_types


def remove_bad_repeat_types(map_layers, node, possible_types):
    previous_types = get_previous_node_types(map_layers, node)
    filtered_types = []

    for node_type in possible_types:
        if node_type in NON_REPEAT_NODE_TYPES and node_type in previous_types:
            continue

        filtered_types.append(node_type)

    if not filtered_types:
        return ["battle"]

    return filtered_types


def get_previous_node_types(map_layers, node):
    previous_layer_index = node["layer"] - 1
    previous_types = []

    if previous_layer_index < 0:
        return previous_types

    previous_layer = map_layers[previous_layer_index]

    for previous_node in previous_layer:
        if node["index"] in previous_node["connections"]:
            previous_types.append(previous_node["type"])

    return previous_types


def adjust_type_count(node_type, shops_placed, events_placed, amount):
    if node_type == "shop":
        shops_placed += amount

    if node_type == "event":
        events_placed += amount

    return shops_placed, events_placed


def set_node_type(node, new_type, shops_placed, events_placed):
    shops_placed, events_placed = adjust_type_count(
        node["type"],
        shops_placed,
        events_placed,
        -1
    )
    node["type"] = new_type
    shops_placed, events_placed = adjust_type_count(
        node["type"],
        shops_placed,
        events_placed,
        1
    )

    return shops_placed, events_placed


def guarantee_battle_in_layer(layer_nodes, shops_placed, events_placed):
    for node in layer_nodes:
        if node["type"] == "battle":
            return shops_placed, events_placed

    node_to_replace = random.choice(layer_nodes)
    return set_node_type(node_to_replace, "battle", shops_placed, events_placed)


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
    guarantee_start_choices(map_layers)
    repair_reached_dead_ends(map_layers)


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
            if random.random() > SPLIT_CHANCE:
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


def guarantee_start_choices(map_layers):
    if len(map_layers) < 2:
        return

    start_node = map_layers[0][0]
    next_layer = map_layers[1]
    possible_indexes = [node["index"] for node in next_layer]
    random.shuffle(possible_indexes)

    while len(start_node["connections"]) < MIN_START_CHOICES and possible_indexes:
        next_index = possible_indexes.pop()

        if next_index not in start_node["connections"]:
            start_node["connections"].append(next_index)

    start_node["connections"].sort()


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


def repair_reached_dead_ends(map_layers):
    reached_indexes_by_layer = get_reached_indexes_by_layer(map_layers)

    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]
        reached_indexes = reached_indexes_by_layer[layer_index]

        for current_node in current_layer:
            if current_node["index"] not in reached_indexes:
                continue

            if len(current_node["connections"]) > 0:
                continue

            closest_index = get_closest_node_index(current_node["index"], next_layer)
            current_node["connections"].append(closest_index)


def repair_all_dead_ends(map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        for current_node in current_layer:
            if len(current_node["connections"]) > 0:
                continue

            closest_index = get_closest_node_index(current_node["index"], next_layer)
            current_node["connections"].append(closest_index)


def get_reached_indexes_by_layer(map_layers):
    reached_indexes_by_layer = []

    for layer in map_layers:
        reached_indexes_by_layer.append(set())

    reached_indexes_by_layer[0].add(0)

    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_reached = reached_indexes_by_layer[layer_index + 1]
        current_reached = reached_indexes_by_layer[layer_index]

        for node in current_layer:
            if node["index"] not in current_reached:
                continue

            for connected_index in node["connections"]:
                next_reached.add(connected_index)

    return reached_indexes_by_layer


def remove_pathless_nodes(map_layers):
    reached_indexes_by_layer = get_reached_indexes_by_layer(map_layers)
    old_to_new_indexes_by_layer = []

    for layer_index, layer_nodes in enumerate(map_layers):
        reached_indexes = reached_indexes_by_layer[layer_index]
        old_to_new = {}
        kept_nodes = []

        for node in layer_nodes:
            if node["index"] not in reached_indexes:
                continue

            old_to_new[node["index"]] = len(kept_nodes)
            kept_nodes.append(node)

        if not kept_nodes:
            fallback_node = get_fallback_node_for_layer(layer_nodes)
            old_to_new[fallback_node["index"]] = 0
            kept_nodes.append(fallback_node)

        map_layers[layer_index] = kept_nodes
        old_to_new_indexes_by_layer.append(old_to_new)

    for layer_index, layer_nodes in enumerate(map_layers):
        for new_index, node in enumerate(layer_nodes):
            node["layer"] = layer_index
            node["index"] = new_index

            if layer_index >= len(map_layers) - 1:
                node["connections"] = []
                continue

            next_old_to_new = old_to_new_indexes_by_layer[layer_index + 1]
            new_connections = []

            for old_connected_index in node["connections"]:
                if old_connected_index not in next_old_to_new:
                    continue

                new_connections.append(next_old_to_new[old_connected_index])

            node["connections"] = sorted(list(dict.fromkeys(new_connections)))


def get_fallback_node_for_layer(layer_nodes):
    center_index = len(layer_nodes) // 2
    return layer_nodes[center_index]


def enforce_split_destination_variety(map_layers):
    shops_placed = count_node_type(map_layers, "shop")
    events_placed = count_node_type(map_layers, "event")

    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        if is_forced_type_layer(map_layers, layer_index + 1):
            continue

        for node in current_layer:
            if len(node["connections"]) < 2:
                continue

            used_types = []

            for connected_index in node["connections"]:
                connected_node = next_layer[connected_index]

                if connected_node["type"] not in used_types:
                    used_types.append(connected_node["type"])
                    continue

                new_type = get_unique_destination_type(used_types, connected_node["layer"])

                if new_type is None:
                    continue

                shops_placed, events_placed = set_node_type(
                    connected_node,
                    new_type,
                    shops_placed,
                    events_placed
                )
                used_types.append(new_type)


def get_unique_destination_type(used_types, layer):
    possible_types = BASIC_NODE_TYPES[:]

    if layer < 3:
        possible_types = ["battle", "event"]

    random.shuffle(possible_types)

    for node_type in possible_types:
        if node_type not in used_types:
            return node_type

    return None


def is_forced_type_layer(map_layers, layer_index):
    if layer_index == 0:
        return True

    if layer_index == 1:
        return True

    if layer_index == len(map_layers) - 1:
        return True

    if layer_index == len(map_layers) - 2:
        return True

    if layer_index % 5 == 0:
        return True

    return False


def count_node_type(map_layers, node_type):
    count = 0

    for layer in map_layers:
        for node in layer:
            if node["type"] == node_type:
                count += 1

    return count


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
