import pygame


class Button:
    def __init__(self, x, y, width, height, text):
        # The rect controls the button's position, size, and click area.
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (255, 255, 255)

    def draw(self, screen, font):
        # Draw the button box and center the text inside it.
        pygame.draw.rect(screen, self.color, self.rect)

        text_image = font.render(self.text, True, (0, 0, 0))
        text_rect = text_image.get_rect(center=self.rect.center)
        screen.blit(text_image, text_rect)

    def is_clicked(self, mouse_pos):
        # Returns True if the mouse click happened inside the button.
        return self.rect.collidepoint(mouse_pos)
