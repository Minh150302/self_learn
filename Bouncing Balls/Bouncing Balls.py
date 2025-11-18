import pygame
import numpy as np
import math
import random


class Ball:
    def __init__(self, position, velocity):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.is_in = True


    def update(self, gravity):
        self.velocity[1] += gravity
        self.position += self.velocity

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.position.astype(int), self.radius)


def is_ball_in_arc(ball_pos, CIRCLE_CENTER, start_angle, end_angle):
    dx = ball_pos[0] - CIRCLE_CENTER[0]
    dy = ball_pos[1] - CIRCLE_CENTER[1]
    ball_angle = math.atan2(dy, dx)
    start_angle = start_angle % (2 * math.pi)
    end_angle = end_angle % (2 * math.pi)
    if start_angle > end_angle:
        end_angle += 2 * math.pi

    if start_angle <= ball_angle <= end_angle or start_angle <= ball_angle + 2 * math.pi <= end_angle:
        return True

def draw_arc(window, center, radius, start_angle, end_angle):
    p1 = center + (radius + 1000) * np.array([math.cos(start_angle), math.sin(start_angle)])
    p2 = center + (radius + 1000) * np.array([math.cos(end_angle), math.sin(end_angle)])
    pygame.draw.polygon(window, BLACK, [center, p1, p2], 0)



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
ball_vel = np.array([0, 0],dtype=np.float64)
arc_degrees = 60
start_angle = math.radians(-arc_degrees/2)
end_angle = math.radians(arc_degrees/2)
spinning_speed = 0.01
balls = [Ball(ball_pos, ball_vel)]


running = True
GRAVITY = 0.2
# ball_vel = np.array([0,0], dtype = np.float64)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    start_angle += spinning_speed
    end_angle += spinning_speed
    for ball in balls:
        if ball.position[1] > HEIGHT or ball.position[0] < 0 or ball.position[0] > WIDTH or ball.position[1] < 0:
            balls.remove(ball)
            balls.append(Ball(ball_pos, velocity=[random.uniform(-2,2), random.uniform(-1,1)]))
            balls.append(Ball(ball_pos, velocity=[random.uniform(-2,2), random.uniform(-1,1)]))

        ball.velocity[1] += GRAVITY 
        ball.position += ball.velocity 

        dist = np.linalg.norm(ball.position - CIRCLE_CENTER)
        if dist + BALL_RADIUS > CIRCLE_RADIUS:
            if is_ball_in_arc(ball.position, CIRCLE_CENTER, start_angle, end_angle):
                ball.is_in = False
            if ball.is_in:
                d = ball.position - CIRCLE_CENTER
                d_unit = d/np.linalg.norm(d)
                ball.position = CIRCLE_CENTER + (CIRCLE_RADIUS - BALL_RADIUS) * d_unit
                
                t = np.array([-d[1],d[0]], dtype = np.float64)
                proj_v_t = (np.dot(ball.velocity, t)/np.dot(t,t)) * t
                ball.velocity = 2* proj_v_t - ball.velocity
                ball.velocity += t * spinning_speed
    
    window.fill(BLACK)
    pygame.draw.circle(window, ORANGE, CIRCLE_CENTER, CIRCLE_RADIUS, 3)
    draw_arc(window, CIRCLE_CENTER, CIRCLE_RADIUS, start_angle, end_angle)
    for ball in balls:
        pygame.draw.circle(window, ball.color, ball.position, BALL_RADIUS )
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()