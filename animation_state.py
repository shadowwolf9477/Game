def update_animation_frame(timer, frame_index, speed, frame_count):
    # Advance animation by game frames, not real time.
    timer += 1

    if timer >= speed:
        # Reset the timer whenever the sprite frame changes.
        timer = 0
        frame_index += 1

        if frame_index >= frame_count:
            frame_index = 0

    return timer, frame_index
