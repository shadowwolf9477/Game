import pygame

class Button:
    def __init__(self ,x, y, width, height , text):
        self.rect = pygame.Rect(x,y,width,height)
        self.text = text
        self.color = (255, 255, 255)
   
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        text_image = font.render(self.text, True, (0, 0, 0))
        text_rect = text_image.get_rect(center=self.rect.center)
        screen.blit(text_image, text_rect)





    
