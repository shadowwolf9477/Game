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


def load_strip_frames(sheet_path, frame_width, frame_height, frame_count, scale_size, normalize=False, frame_indices=None):
    # Slice a single-row sprite strip into animation frames.
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []

    if frame_indices is None:
        frame_indices = range(frame_count)

    for frame_index in frame_indices:
        frame_x = frame_index * frame_width
        frame = sheet.subsurface((frame_x, 0, frame_width, frame_height))
        if normalize:
            frame = normalize_frame(frame, frame_width, frame_height)

        frame = pygame.transform.scale(frame, scale_size)
        frames.append(frame)

    return frames


def make_flipped_frames(frames):
    # Prebuild mirrored sprites so draw_battle does not transform images every frame.
    flipped_frames = []

    for frame in frames:
        flipped_frames.append(pygame.transform.flip(frame, True, False))

    return flipped_frames


def normalize_frame(frame, frame_width, frame_height):
    # Some sprite strips shift the character inside each frame.
    # Center the visible pixels so attack animations do not slide across the tile.
    visible_rect = frame.get_bounding_rect(1)

    if visible_rect.width == 0 or visible_rect.height == 0:
        return frame

    normalized_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    visible_frame = frame.subsurface(visible_rect)
    draw_x = (frame_width - visible_rect.width) // 2
    draw_y = frame_height - visible_rect.height
    normalized_frame.blit(visible_frame, (draw_x, draw_y))

    return normalized_frame
