# Micah Millers code
import numpy as np
import matplotlib.pyplot as plt

# Load the data from the text file
data = np.loadtxt("reflexData.txt", dtype='str')


def velocity_magnitude(times, x_accelerations, y_accelerations):
    # Check if the input arrays have the same length
    if len(times) != len(x_accelerations) or len(times) != len(y_accelerations):
        raise ValueError("Arrays of time, x acceleration, and y acceleration must have the same length.")

    # Calculate the time step
    dt = times[1] - times[0]

    # Initialize variables
    velocity_magnitudes = []

    # Numerical integration using the trapezoidal rule
    for i in range(len(times)):
        # Calculate velocity components
        vx = np.cumsum(x_accelerations[:i+1]) * dt
        vy = np.cumsum(y_accelerations[:i+1]) * dt

        # Calculate magnitude of velocity
        v_magnitude = np.sqrt(vx[-1]**2 + vy[-1]**2)

        # Append the magnitude of velocity to the list
        velocity_magnitudes.append(v_magnitude)

    return np.array(velocity_magnitudes)


def reactiontime(timer, xacceleration, yacceleration):
    for i in range(len(timer)):
        if xacceleration[i] > .5 or yacceleration[i] > .5 or xacceleration[i] < -.5 or yacceleration[i] < -.5:
            index = i
            break
    return time[index]


c1 = data[:, 0]
time = c1.astype(float)
# Extract the 5th column and convert it to integers
c2 = data[:, 1]
accelx = c2.astype(float)
c3 = data[:, 2]
accely = c3.astype(float)

c4 = data[:, 3]
force = c4.astype(float)

# Generate x-axis values as indices
time_values = np.arange(len(time))

# Plot the data
plt.figure()
plt.plot(time_values, accelx)
plt.title(f'X accel at: {force[0]}N over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('X accel')
plt.grid(True)
plt.show()

plt.figure()
plt.plot(time_values, accely)
plt.title(f'Y accel at: {force[0]}N over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('Y accel')
plt.grid(True)
plt.show()

plt.figure()
plt.plot(time_values, velocity_magnitude(time, accelx, accely))
plt.title(f'Magnitude of velocity of leg from rest at: {force[0]}N over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('Velocity magnitude')
plt.grid(True)
plt.show()
print("the amount of time it takes a reaction to happen is ", reactiontime(time, accelx, accely))
