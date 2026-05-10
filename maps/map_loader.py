import random


def generate_map():
    # Build a simple straight-line map after the tutorial fight.
    # Later, each layer can hold several connected nodes.
    map_layers = []

    for layer in range(8):
        layer_nodes = []

        if layer == 0:
            node_type = "start"
        elif layer == 7:
            node_type = "boss"
        elif layer % 4 == 0:
            # Every fourth stop is a safe recovery/upgrade style node.
            node_type = "rest"
        else:
            # Battles appear twice to make them slightly more common.
            possible_types = ["battle", "battle", "shop", "upgrade", "event"]
            node_type = random.choice(possible_types)

        node = {
            "layer": layer,
            "index": 0,
            "type": node_type,
            "x": 550,
            "y": 80 + layer * 80,
            # completed/available control what the player has passed and can click.
            "completed": False,
            "available": layer == 1
        }

        layer_nodes.append(node)
        map_layers.append(layer_nodes)

    return map_layers
