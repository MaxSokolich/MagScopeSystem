import numpy as np
import pygame

# Define the global control actuation field
control_field = np.zeros((10,10,2))  # 10x10 grid, 2D vector field
control_field[:,:,0] = 1  # x-direction control
control_field[:,:,1] = 0.5  # y-direction control

# Define the microrobots and their initial positions
num_robots = 3
robots = np.zeros((num_robots,2))  # 2D positions
robots[0,:] = [1,1]  # initial position for robot 1
robots[1,:] = [5,5]  # initial position for robot 2
robots[2,:] = [8,8]  # initial position for robot 3

# Define the virtual markers for each microrobot
markers = np.zeros((num_robots,2))  # 2D positions
markers[0,:] = [3,3]  # desired position for robot 1
markers[1,:] = [6,6]  # desired position for robot 2
markers[2,:] = [9,9]  # desired position for robot 3

# Define the local control law for each microrobot
kp = .5  # proportional gain
kd = 1  # derivative gain
ki = .001
prev_error = 0
integral_error = 0
def local_control(robot, control_field, marker, kp, kd, ki, dt):
    global prev_error, integral_error
    error = marker - robot

    integral_error += error 

    derivative_error = (error - prev_error) 

    velocity = kp * error + ki * integral_error + kd * derivative_error


    prev_error = error
    return velocity + control_field[int(robot[0]),int(robot[1]),:]

# Initialize the Pygame environment
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Microrobot Control")

# Define some colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

# Define a function to draw the microrobots and their markers on the screen
def draw_robots(robots, markers):
    for i in range(num_robots):
        pygame.draw.circle(screen, blue, robots[i,:]*60+30, 10)
        pygame.draw.circle(screen, red, markers[i,:]*60+30, 10)

# Define a function to update the microrobot positions and velocities
def update_robots(robots, markers, control_field, kp, kd, dt):
    for i in range(num_robots):
        # Update the microrobot position using the local control law
        robots[i,:] += local_control(robots[i,:], control_field, markers[i,:], kp, kd, ki, dt) * dt
        
        # Wrap the microrobot position if it goes beyond the workspace boundaries
        robots[i,:] = np.mod(robots[i,:], np.array([10,10]))

# Define the main loop of the simulation
running = True
clock = pygame.time.Clock()
num_steps = 1000
dt = 0.01

while running:
    # Handle events (quit, keypresses, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Update the microrobot positions and velocities
    update_robots(robots, markers, control_field, kp, kd, dt)
    
    # Clear the screen and draw the microrobots and their markers
    screen.fill(white)
    draw_robots(robots, markers)

    # Update the display and wait for the next time step
    pygame.display.flip()
    clock.tick(30)

    # Exit the loop if the desired number of time steps has been reached
    num_steps -= 1
    if num_steps == 0:
        running = False

pygame.quit()
