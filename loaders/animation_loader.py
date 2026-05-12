import pygame

from loaders.asset_paths import asset_path


def load_animation_frames(sheet_path, frame_width, frame_height, row, frame_count, scale_size):
    # Load one sprite sheet and slice a single animation row into frames.
    sheet = pygame.image.load(asset_path(sheet_path)).convert_alpha()
    frames = []

    frame_y = row * frame_height

    for frame_index in range(frame_count):
        # Each frame sits next to the previous one across the chosen row.
        frame_x = frame_index * frame_width
        frame = sheet.subsurface((frame_x, frame_y, frame_width, frame_height))
        frame = pygame.transform.scale(frame, scale_size)
        frames.append(frame)

    return frames


def load_strip_frames(
    sheet_path,
    frame_width,
    frame_height,
    frame_count,
    scale_size,
    normalize=False,
    frame_indices=None,
    stable_normalize=False
):
    # Slice a single-row sprite strip into animation frames.
    sheet = pygame.image.load(asset_path(sheet_path)).convert_alpha()
    frames = []

    if frame_indices is None:
        frame_indices = range(frame_count)

    raw_frames = []

    for frame_index in frame_indices:
        frame_x = frame_index * frame_width
        frame = sheet.subsurface((frame_x, 0, frame_width, frame_height))
        raw_frames.append(frame)

    if normalize and stable_normalize:
        raw_frames = normalize_frames_stable(raw_frames, frame_width, frame_height)
    elif normalize:
        raw_frames = [normalize_frame(frame, frame_width, frame_height) for frame in raw_frames]

    for frame in raw_frames:
        frame = pygame.transform.scale(frame, scale_size)
        frames.append(frame)

    return frames


def load_full_strip_frames(sheet_path, frame_width, frame_height, scale_size, normalize=False, stable_normalize=False):
    # Tiny RPG sprites use one horizontal strip per animation.
    # Count frames from the image width so each character can have different attack lengths.
    sheet = pygame.image.load(asset_path(sheet_path)).convert_alpha()
    frame_count = sheet.get_width() // frame_width

    return load_strip_frames(
        sheet_path,
        frame_width,
        frame_height,
        frame_count,
        scale_size,
        normalize,
        None,
        stable_normalize
    )


def make_flipped_frames(frames):
    # Prebuild mirrored sprites so draw_battle does not transform images every frame.
    flipped_frames = []

    for frame in frames:
        flipped_frames.append(pygame.transform.flip(frame, True, False))

    return flipped_frames


def normalize_frame(frame, frame_width, frame_height):
    # Some sprite strips shift the character inside each frame.
    # Crop and enlarge the visible pixels so sheets with huge transparent padding
    # still read clearly on an 85px battle tile.
    visible_rect = frame.get_bounding_rect(1)

    if visible_rect.width == 0 or visible_rect.height == 0:
        return frame

    normalized_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    visible_frame = frame.subsurface(visible_rect)
    target_width = int(frame_width * 0.92)
    target_height = int(frame_height * 0.96)
    scale = min(
        target_width / visible_rect.width,
        target_height / visible_rect.height
    )
    scaled_size = (
        max(1, int(visible_rect.width * scale)),
        max(1, int(visible_rect.height * scale))
    )
    visible_frame = pygame.transform.scale(visible_frame, scaled_size)
    draw_x = (frame_width - visible_frame.get_width()) // 2
    draw_y = frame_height - visible_frame.get_height()
    normalized_frame.blit(visible_frame, (draw_x, draw_y))

    return normalized_frame


def normalize_frames_stable(frames, frame_width, frame_height):
    visible_rects = [frame.get_bounding_rect(1) for frame in frames]
    non_empty_rects = [rect for rect in visible_rects if rect.width > 0 and rect.height > 0]

    if not non_empty_rects:
        return frames

    min_x = min(rect.x for rect in non_empty_rects)
    max_width = max(rect.width for rect in non_empty_rects)
    max_height = max(rect.height for rect in non_empty_rects)
    max_bottom = max(rect.bottom for rect in non_empty_rects)

    target_width = int(frame_width * 0.92)
    target_height = int(frame_height * 0.96)
    scale = min(target_width / max_width, target_height / max_height)
    shared_box_width = int(max_width * scale)
    shared_box_x = (frame_width - shared_box_width) // 2

    normalized_frames = []

    for frame, visible_rect in zip(frames, visible_rects):
        if visible_rect.width == 0 or visible_rect.height == 0:
            normalized_frames.append(frame)
            continue

        visible_frame = frame.subsurface(visible_rect)
        scaled_size = (
            max(1, int(visible_rect.width * scale)),
            max(1, int(visible_rect.height * scale))
        )
        visible_frame = pygame.transform.scale(visible_frame, scaled_size)

        draw_x = shared_box_x + int((visible_rect.x - min_x) * scale)
        draw_y = frame_height - int((max_bottom - visible_rect.y) * scale)

        normalized_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        normalized_frame.blit(visible_frame, (draw_x, draw_y))
        normalized_frames.append(normalized_frame)

    return normalized_frames
