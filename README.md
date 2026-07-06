# MPU6050-Preprocessing
This program uses mean-centering to remove offsets and a Kalman filter to reduce background noise in the MPU6050 accelerometer.

I wrote this for a lab project that involved measuring acceleration on a spinning disc. Due to how short it is, I don't see much point in splitting the program into serveral parts.

# Usage
1. Change **bluetooth_port** to whichever COM port your shoddy Bluetooth module connects to and run it.
2. For mean-centering to be accurate, you have to lay the accelerometer on a flat table until the message "Calibration complete:" is printed.
3. I would *not* recommend switching the baud rate. Half the time you get garbage output, the other half your Bluetooth module breaks and you have to reset it

# References
1. Rio Alfian, Alfian Ma’arif, and Sunardi Sunardi. “Noise Reduction in the Accelerometer and Gyroscope Sensor with the Kalman Filter Algorithm”
2. Mohamed Laaraiedh. “Implementation of Kalman Filter with Python Language”.
