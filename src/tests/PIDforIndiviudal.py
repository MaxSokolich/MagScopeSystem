import numpy as np

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
kp = 0.5  # proportional gain
kd = 0.1  # derivative gain

def local_control(robot, control_field, marker, kp, kd):
    error = marker - robot
    velocity = kp * error + kd * (error - robot.prev_error)
    robot.prev_error = error
    return velocity + control_field[int(robot[0]),int(robot[1]),:]

# Move the microrobots to their desired positions
num_steps = 100
dt = 0.1

for t in range(num_steps):
    for i in range(num_robots):
        # Update the microrobot position using the local control law
        robots[i,:] += local_control(robots[i,:], control_field, markers[i,:], kp, kd) * dt
        
        # Wrap the microrobot position if it goes beyond the workspace boundaries
        robots[i,:] = np.mod(robots[i,:], np.array([10,10]))
        
    # Plot the microrobots and their markers (for visualization purposes)
    plt.figure()
    plt.quiver(control_field[:,:,0], control_field[:,:,1])
    plt.plot(robots[:,0], robots[:,1], 'bo')
    plt.plot(markers[:,0], markers[:,1], 'ro')
    plt.xlim([0,10])
    plt.ylim([0,10])
    plt.show()
