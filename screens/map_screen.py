import pygame
from loaders.asset_paths import asset_path

MAP_SCROLL_Y = 0
NODE_RADIUS = 28

ICON_PATHS = {
    "start": "assets/Map_Icons/Battle.png",
    "battle": "assets/Map_Icons/Battle.png",
    "boss": "assets/Map_Icons/Boss.png",
    "event": "assets/Map_Icons/Event.png",
    "shop": "assets/Map_Icons/shop.webp",
    "rest": "assets/Map_Icons/Map-RestSite.png",
    "upgrade": "assets/Map_Icons/Map-RestSite.png",
}

ICON_CACHE = {}


def scroll_map(amount):
    global MAP_SCROLL_Y

    MAP_SCROLL_Y += amount

    if MAP_SCROLL_Y < 0:
        MAP_SCROLL_Y = 0

    if MAP_SCROLL_Y > 600:
        MAP_SCROLL_Y = 600


def get_icon(node_type):
    cache_key = node_type

    if cache_key in ICON_CACHE:
        return ICON_CACHE[cache_key]

    path = ICON_PATHS.get(node_type, ICON_PATHS["battle"])

    try:
        image = pygame.image.load(asset_path(path)).convert_alpha()
        image = pygame.transform.smoothscale(image, (42, 42))
    except Exception as error:
        print("Could not load map icon:", path, error)
        image = pygame.Surface((42, 42), pygame.SRCALPHA)
        pygame.draw.circle(image, (255, 255, 255), (21, 21), 18, 2)

    ICON_CACHE[cache_key] = image
    return image


def get_node_screen_pos(node):
    return node["x"], node["y"] - MAP_SCROLL_Y


def draw_map_screen(screen, font, map_layers):
    screen.fill((135, 135, 122))

    draw_connections(screen, map_layers)
    draw_nodes(screen, map_layers)


def draw_connections(screen, map_layers):
    for layer_index in range(len(map_layers) - 1):
        current_layer = map_layers[layer_index]
        next_layer = map_layers[layer_index + 1]

        for node in current_layer:
            start_x, start_y = get_node_screen_pos(node)

            for connected_index in node["connections"]:
                if connected_index >= len(next_layer):
                    continue

                connected_node = next_layer[connected_index]
                end_x, end_y = get_node_screen_pos(connected_node)

                line_color = (35, 35, 35)

                if node.get("completed", False):
                    line_color = (220, 220, 220)

                pygame.draw.line(
                    screen,
                    line_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    3
                )


def draw_nodes(screen, map_layers):
    for layer in map_layers:
        for node in layer:
            x, y = get_node_screen_pos(node)

            if y < -80 or y > screen.get_height() + 80:
                continue

            node_color = (20, 30, 40)
            border_color = (10, 10, 10)
            if node.get("locked", False):
                node_color = (55, 55, 55)
                border_color = (25, 25, 25)

            if node.get("available", False):
                node_color = (45, 80, 110)
                border_color = (245, 245, 245)

            if node.get("completed", False):
                node_color = (80, 80, 80)
                border_color = (160, 160, 160)

            pygame.draw.circle(screen, node_color, (int(x), int(y)), NODE_RADIUS)
            pygame.draw.circle(screen, border_color, (int(x), int(y)), NODE_RADIUS, 3)

            icon = get_icon(node["type"])
            icon_rect = icon.get_rect(center=(int(x), int(y)))
            screen.blit(icon, icon_rect)


def get_clicked_map_node(map_layers, mouse_pos):
    mouse_x, mouse_y = mouse_pos

    for layer in map_layers:
        for node in layer:
            if not node.get("available", False):
                continue

            x, y = get_node_screen_pos(node)

            distance_x = mouse_x - x
            distance_y = mouse_y - y

            if distance_x * distance_x + distance_y * distance_y <= NODE_RADIUS * NODE_RADIUS:
                return node

    return None


def complete_map_node(map_layers, clicked_node):
    clicked_layer = clicked_node["layer"]

    # Lock every other node on this same row.
    for node in map_layers[clicked_layer]:
        node["available"] = False

        if node is not clicked_node:
            node["locked"] = True

    # Mark the chosen node completed.
    clicked_node["completed"] = True
    clicked_node["available"] = False
    clicked_node["locked"] = False

    next_layer_index = clicked_layer + 1

    if next_layer_index >= len(map_layers):
        return

    # Lock all next-row nodes first.
    for node in map_layers[next_layer_index]:
        node["available"] = False

    # Only unlock nodes connected to the chosen path.
    for connected_index in clicked_node["connections"]:
        if connected_index < len(map_layers[next_layer_index]):
            map_layers[next_layer_index][connected_index]["available"] = True
            map_layers[next_layer_index][connected_index]["locked"] = False