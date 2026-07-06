import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import serial
import time

""" Kalman filter """
# Adapted from Laaraiedh
def kf_predict(X, P, A, Q, B, U):
    X = np.dot(A, X) + np.dot(B, U) 
    P = np.dot(A, np.dot(P, np.transpose(A))) + Q 
    return (X, P)

def kf_update(X, P, Y, H, R): 
    IM = np.dot(H, X) 
    IS = R + np.dot(H, np.dot(P, H.T)) 
    K = np.dot(P, np.dot(H.T, np.linalg.inv(IS))) 
    X = X + np.dot(K, (Y-IM)) 
    P = P - np.dot(K, np.dot(IS, np.transpose(K))) 
    return (X, P) 

X = np.zeros((3, 1))
P = np.identity(3)
A = np.identity(3)
B = np.identity(3)
U = np.zeros((3, 1))
A = np.identity(3)
H = np.identity(3)

# Parameters follow those listed in Rio Alfian et al
Q = np.identity(3) * 1
R = np.identity(3) * 100


""" Bluetooth Setup """
bluetooth_port = "COM6"
baud_rate = 9600

try:    # The bluetooth works every time, 50% of the time
    bt_serial = serial.Serial(bluetooth_port, baud_rate, timeout=1)
    print(f"Connected.")
except Exception:
    print(f"IT BROKE AGAIN!!!!")
    exit()


""" Mean centering """
print("CALIBRATING... LEAVE THE CART ALONE FOR A WHILE.")
SAMPLE_AMNT = 50
offset_x, offset_y, offset_z = 0, 0, 0
count = 0

while count < SAMPLE_AMNT:
    if bt_serial.in_waiting > 0:
        data_pts = bt_serial.readline().decode('utf-8', errors='ignore').strip().split(',')
        if len(data_pts) == 3:
            try:
                offset_x += float(data_pts[0])
                offset_y += float(data_pts[1])
                offset_z += float(data_pts[2])
                count += 1
            except ValueError:      # If ts worked properly, there wouldn't be so many try excepts but alas
                continue
offset_x /= SAMPLE_AMNT
offset_y /= SAMPLE_AMNT
offset_z /= SAMPLE_AMNT

print("Calibration complete:")
bt_serial.reset_input_buffer()


""" Plotting and Filtering """
PTS = 50
filtered_a = np.array([[0, 0, 0]])
t = np.array([0])
start = time.time()

fig, ax = plt.subplots()
a_x, = ax.plot(t[0], filtered_a[0][0], label="a_x")
a_y, = ax.plot(t[0], filtered_a[0][1], label="a_y")
a_z, = ax.plot(t[0], filtered_a[0][2], label="a_z")

def main(frame):                # Main loop used for Matplotlib's animations
    global X, P, filtered_a, t
    log = open("log.txt", "a")

    if bt_serial.in_waiting > 0:
        data_pts = bt_serial.readline().decode('utf-8', errors='ignore').strip().split(',')
        
        if len(data_pts) == 3:
            try:
                end = time.time()

                measured_a_x = float(data_pts[0]) - offset_x
                measured_a_y = float(data_pts[1]) - offset_y
                measured_a_z = float(data_pts[2]) - offset_z
                measured_a = np.array([[measured_a_x], [measured_a_y], [measured_a_z]])
                
                """ Applying the Filter """
                X_pred, P_pred = kf_predict(X, P, A, Q, B, U)
                X, P = kf_update(X_pred, P_pred, measured_a, H, R)
                output = f"{t[-1]:5.2f}: {X[0,0]:5.2f} {X[1,0]:5.2f} {X[2,0]:5.2f}"
                print(output) 
                log.write(output+'\n')
                filtered_a = np.append(filtered_a, np.reshape(X, (1, 3)), 0)

                t = np.append(t, end-start)
                if len(t) > PTS:
                    filtered_a = filtered_a[-PTS:]
                    t = t[-PTS:]
                
                ax.set_xlim(t[0], t[-1])
                """ax.set_ylim(-np.max(filtered_a)-0.5, np.max(filtered_a)+0.5)"""      # Changing y-limits
                ax.set_ylim(-12, 12)                                                    # Fixed y-limits

                a_x.set_data(t, filtered_a[:,0])
                a_y.set_data(t, filtered_a[:,1])
                a_z.set_data(t, filtered_a[:,2])
                
            except ValueError:
                pass

    return (a_x, a_y, a_z)

animation = anim.FuncAnimation(fig, main, interval=10, blit=False)
plt.legend(loc="upper left")
plt.show()