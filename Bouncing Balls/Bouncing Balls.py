import pygame
import numpy as np
import math


pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
CIRCLE_CENTER = np.array([WIDTH/2, HEIGHT/2], dtype = np.float64)
CIRCLE_RADIUS = WIDTH/3
BALL_RADIUS = 5
ball_pos = np.array([WIDTH/2, HEIGHT/2 - HEIGHT/6], dtype = np.float64)




running = True
GRAVITY = 0.2
ball_vel = np.array([0,0], dtype = np.float64)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
            
    ball_vel[1] += GRAVITY 
    ball_pos += ball_vel 

    dist = np.linalg.norm(ball_pos - CIRCLE_CENTER)
    if dist + BALL_RADIUS > CIRCLE_RADIUS:
        d = ball_pos - CIRCLE_CENTER
        d_unit = d/np.linalg.norm(d)
        ball_pos = CIRCLE_CENTER + (CIRCLE_RADIUS - BALL_RADIUS) * d_unit
        
        t = np.array([-d[1],d[0]], dtype = np.float64)
        proj_v_t = (np.dot(ball_vel, t)/np.dot(t,t)) * t
        ball_vel = 2* proj_v_t - ball_vel
    
    
    window.fill(BLACK)
    pygame.draw.circle(window, ORANGE, CIRCLE_CENTER, CIRCLE_RADIUS, 3)
    pygame.draw.circle(window, RED, ball_pos, BALL_RADIUS )
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()