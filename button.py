import pygame


class Button:
    def __init__(self, x, y, width, height, text):
        # The rect is both the drawn box and the clickable area.
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (255, 255, 255)

    def draw(self, screen, font):
        # Draw a simple white button with centered black text.
        pygame.draw.rect(screen, self.color, self.rect)

        text_image = font.render(self.text, True, (0, 0, 0))
        text_rect = text_image.get_rect(center=self.rect.center)
        screen.blit(text_image, text_rect)

    def is_clicked(self, mouse_pos):
        # Keep click detection inside the Button class.
        return self.rect.collidepoint(mouse_pos)
