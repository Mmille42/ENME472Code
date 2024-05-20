import smbus					#import SMBus module of I2C
from time import sleep   
import time  
import numpy as np
import matplotlib.pyplot as plt
import random
import os
from gpiozero import LED


 #import

#some MPU6050 Registers and their Address
relay= LED(17)
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_ZOUT_H  = 0x47
accelx=[]
accelz=[]
gyrox=[]
gyroz=[]

# Start a while loop to continuously read the sensor data
def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value
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
		vx = np.cumsum(x_accelerations[:i + 1]) * dt
		vy = np.cumsum(y_accelerations[:i + 1]) * dt

		# Calculate magnitude of velocity
		v_magnitude = np.sqrt(vx[-1] ** 2 + vy[-1] ** 2)

		# Append the magnitude of velocity to the list
		velocity_magnitudes.append(v_magnitude)

	return np.array(velocity_magnitudes)


def reactiontime(timer, xacceleration, yacceleration):
	for i in range(len(timer)):
		if abs(xacceleration[i])>.5 or abs(yacceleration[i])>.5:
			index = i
			break
	return timer[index]
	
	
	
def gyroposition(zgyro):
	zangle=[]
	gyroz=0
	for i in range (len(zgyro)):
		if i==0:
			gyroz=zgyro*.005
			zangle.append(gyroz)
		else:
			gyroz=zgyro[i]*.005+zangle[i-1] 
			zangle.append(gyroz)
	return zangle
	


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68  
time.sleep(1) # MPU6050 device address

MPU_Init()
initialxacc=read_raw_data(ACCEL_XOUT_H)/16384.0
initialzacc=read_raw_data(ACCEL_ZOUT_H)/16384.0
initialgyrox=read_raw_data(GYRO_XOUT_H)/131.0
initialgyroz=read_raw_data(GYRO_ZOUT_H)/131.0
trigger = random.randint(1, 7)
time.sleep(trigger)
relay.on()
time.sleep(.1)
endtime=time.time()+3

while time.time()<endtime:
	relay.off()
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)
	
	#Read Gyroscope raw value
	gyro_x = read_raw_data(GYRO_XOUT_H)
	
	gyro_z = read_raw_data(GYRO_ZOUT_H)
	accelx.append(acc_x/16384.0-initialxacc)
	
	accelz.append(acc_z/16384.0-initialzacc)
	gyrox.append(gyro_x/131.0-initialgyrox)
	gyroz.append(gyro_z/131.0-initialgyroz)
	time.sleep(.0015)
timestr=time.strftime("%Y-%m-%d_%H-%M-%S")

with open(timestr+"mpudata.txt", 'w') as file:
    for i in range(0,len(accelx)):
        file.write(str(i*.005)+" "+str(accelx[i]) + " " + str(accelz[i]) + " " + str(gyrox[i])+ " " +str(gyroz[i]) +"\n")
    file.close()
data=np.loadtxt(timestr+'mpudata.txt', dtype='str')
#Take the data document and covert it to arrays 
c1 = data[:, 0]
times = c1.astype(float)

c2 = data[:, 1]
accelerationx = c2.astype(float)
c3 = data[:, 2]
accelerationz = c3.astype(float)

c4 = data[:, 3]
gyroscopex = c4.astype(float)

c5=data[:, 4]
gyroscopez=c5.astype(float)


# Plot the data
plt.figure()
plt.plot(times, accelerationx)
plt.title(f'X accel over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('X accel')
plt.grid(True)
plt.savefig(timestr+'xaccel.jpg')

plt.figure()
plt.plot(times, accelerationz)
plt.title(f'Y accel over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('Y accel')
plt.grid(True)
plt.savefig(timestr+'yaccel.jpg')

plt.figure()
plt.plot(times, velocity_magnitude(times, accelerationx, accelerationz))
plt.title(f' Velocty over time after impact with tendon')
plt.xlabel('Time')
plt.ylabel('Velocity magnitude')
plt.grid(True)
plt.savefig(timestr+'velo.jpg')

plt.figure()
plt.plot(times, gyroposition(gyroscopez))
plt.title(f' Gyro Z vs Time')
plt.xlabel('Time')
plt.ylabel('Z Gyro (radians)')
plt.grid(True)
plt.savefig(timestr+'gyro.jpg')


fullDirectory='/home/mmill/'+timestr+'xaccel.jpg'
command1='/home/mmill/Dropbox-Uploader/dropbox_uploader.sh upload '+ fullDirectory + ' /'
os.system(command1)
command2='/home/mmill/Dropbox-Uploader/dropbox_uploader.sh upload '+timestr+ 'yaccel.jpg /'
os.system(command2)
command3='/home/mmill/Dropbox-Uploader/dropbox_uploader.sh upload '+timestr+ 'velo.jpg /'
os.system(command3)
command4='/home/mmill/Dropbox-Uploader/dropbox_uploader.sh upload '+timestr+ 'gyro.jpg /'
os.system(command4)
command5='/home/mmill/Dropbox-Uploader/dropbox_uploader.sh upload '+timestr+ 'mpudata.txt /'
os.system(command5)
os.remove('/home/mmill/' +timestr+'mpudata.txt')
os.remove('/home/mmill/'+timestr+'velo.jpg')
os.remove('/home/mmill/'+timestr+'xaccel.jpg')
os.remove('/home/mmill/'+timestr+'yaccel.jpg')
os.remove('/home/mmill/'+timestr+'gyro.jpg')
print("Files Removed")
