import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Roguelike Game")
BLACK= (0, 0, 0)
WHITE = (255, 255, 255)
font = pygame.font.Font(None, 50)
quit_button = pygame.Rect(300, 250, 200, 60)
Start_button = pygame.Rect(300, 170, 200, 60)




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button.collidepoint(event.pos):
                running = False
            if Start_button.collidepoint(event.pos):
                running = False
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 30))
    
    pygame.draw.rect(screen, WHITE, quit_button)
    text = font.render("Quit", True, BLACK)
    screen.blit(text, (350, 265))
    pygame.draw.rect(screen, WHITE, Start_button)
    text = font.render("Start", True, BLACK)
    screen.blit(text, (350, 190))
    pygame.display.flip()

 


pygame.quit()

