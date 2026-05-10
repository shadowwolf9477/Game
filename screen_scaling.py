from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def scale_mouse_pos(mouse_pos, window_size):
    # Convert mouse position from real window pixels to internal game pixels.
    mouse_x, mouse_y = mouse_pos
    window_width, window_height = window_size

    scale_x = SCREEN_WIDTH / window_width
    scale_y = SCREEN_HEIGHT / window_height

    return (mouse_x * scale_x, mouse_y * scale_y)
