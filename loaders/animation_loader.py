import pygame


def load_animation_frames(sheet_path, frame_width, frame_height, row, frame_count, scale_size):
    # Load one sprite sheet and slice a single animation row into frames.
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []

    frame_y = row * frame_height

    for frame_index in range(frame_count):
        # Each frame sits next to the previous one across the chosen row.
        frame_x = frame_index * frame_width
        frame = sheet.subsurface((frame_x, frame_y, frame_width, frame_height))
        frame = pygame.transform.scale(frame, scale_size)
        frames.append(frame)

    return frames
