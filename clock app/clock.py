import pygame

pygame.init()


GREY = (200, 200, 200)
WHITE = (255, 255, 255)
WScreen = 500
HScreen = 600

screen = pygame.display.set_mode((WScreen, HScreen))




running = True

while True:
    screen.fill(GREY)

    pygame.draw.rect

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                print("xxx")

    pygame.display.flip()


pygame.quit()