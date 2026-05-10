import pygame

from settings import WHITE


def draw_map_screen(screen, font, map_layers):
    # Temporary map view; later nodes can become icon assets.
    title_text = font.render("Map", True, WHITE)
    screen.blit(title_text, (560, 30))

    for layer in map_layers:
        for node in layer:
            color = (90, 90, 90)

            if node["completed"]:
                color = (80, 220, 120)

            if node["available"]:
                color = (0, 180, 255)

            pygame.draw.circle(screen, color, (node["x"], node["y"]), 25)

            label_text = font.render(node["type"], True, WHITE)
            screen.blit(label_text, (node["x"] + 40, node["y"] - 15))


def get_clicked_map_node(map_layers, mouse_pos):
    # Return the available map node under the mouse, if any.
    for layer in map_layers:
        for node in layer:
            node_rect = pygame.Rect(node["x"] - 25, node["y"] - 25, 50, 50)

            if node["available"] and node_rect.collidepoint(mouse_pos):
                return node

    return None


def complete_map_node(map_layers, node):
    # Mark this node done and unlock the next straight-line layer.
    node["completed"] = True
    node["available"] = False

    next_layer_number = node["layer"] + 1

    if next_layer_number < len(map_layers):
        for next_node in map_layers[next_layer_number]:
            next_node["available"] = True
