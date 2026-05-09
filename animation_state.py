def update_animation_frame(timer, frame_index, speed, frame_count):
    # Count frames until it is time to swap to the next animation image.
    timer += 1

    if timer >= speed:
        timer = 0
        frame_index += 1

        if frame_index >= frame_count:
            frame_index = 0

    return timer, frame_index
