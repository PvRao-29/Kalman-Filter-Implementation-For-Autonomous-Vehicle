import numpy as np
import pandas as pd

# Load stationary data for calibration
stationary_data = pd.read_csv('stationary.csv')
gps_latitude_var = stationary_data['Latitude'].var()
gps_longitude_var = stationary_data['Longitude'].var()

# Measurement noise covariance based on stationary data (add small epsilon for stability)
R = np.array([[gps_latitude_var + 1e-5, 0], [0, gps_longitude_var + 1e-5]])

# Initial state (latitude, longitude, velocity_lat, velocity_lon)
state = np.array([0, 0, 0, 0])

# Initial state covariance matrix (uncertainty)
P = np.eye(4) * 100  # Initial uncertainty in both position and velocity

# Process noise covariance
Q = np.array([[0.1, 0, 0, 0],  # We trust the position model a little more
              [0, 0.1, 0, 0],
              [0, 0, 1.0, 0],  # Higher uncertainty in velocity due to accelerometer data
              [0, 0, 0, 1.0]])

# Measurement matrix (GPS-based)
H = np.array([[1, 0, 0, 0],  # Latitude from state
              [0, 1, 0, 0]])  # Longitude from state

# Load movement data
movement_data = pd.read_csv('movement.csv')

# Ensure no NaNs in movement data for critical fields (Latitude, Longitude)
movement_data = movement_data.dropna(subset=['Latitude', 'Longitude'], how='all')

# Open a CSV file to store the refined position estimates
output_file = 'position.csv'
with open(output_file, 'w') as f:
    f.write('Latitude,Longitude\n')

# Kalman Filter loop over movement data
for i in range(len(movement_data)):
    # Time step between measurements (using seconds and nanoseconds)
    delta_t = (movement_data['Seconds'].iloc[i] + movement_data['Nanoseconds'].iloc[i] * 1e-9) if i > 0 else 1.0

    # Update the transition matrix to include the time step
    F = np.array([[1, 0, delta_t, 0],  # Latitude transition
                  [0, 1, 0, delta_t],  # Longitude transition
                  [0, 0, 1, 0],        # Lat velocity transition
                  [0, 0, 0, 1]])       # Long velocity transition

    # Prediction Step
    state = F.dot(state)  # Predict the next state
    P = F.dot(P).dot(F.T) + Q  # Update uncertainty

    # Check if GPS data is available for this step
    if pd.notna(movement_data['Latitude'].iloc[i]) and pd.notna(movement_data['Longitude'].iloc[i]):
        z = np.array([movement_data['Latitude'].iloc[i], movement_data['Longitude'].iloc[i]])  # GPS reading
        y = z - H.dot(state)  # Measurement residual
        S = H.dot(P).dot(H.T) + R + np.eye(2) * 1e-5  # Residual covariance with stability term
        K = P.dot(H.T).dot(np.linalg.inv(S))  # Kalman gain

        # Update state with measurement correction
        state = state + K.dot(y)
        P = (np.eye(4) - K.dot(H)).dot(P)  # Update uncertainty based on Kalman gain

    else:
        # If no GPS data, estimate movement using IMU or Wheel Speed data
        if pd.notna(movement_data['LinearAccel.x'].iloc[i]) and pd.notna(movement_data['LinearAccel.y'].iloc[i]):
            # Use IMU data (acceleration) to estimate velocity change
            state[2] += movement_data['LinearAccel.x'].iloc[i] * delta_t  # Estimate velocity from acceleration.x
            state[3] += movement_data['LinearAccel.y'].iloc[i] * delta_t  # Estimate velocity from acceleration.y

        # Use wheel speeds to estimate movement if IMU data isn't enough
        if pd.notna(movement_data['LeftFrontSpeed'].iloc[i]) and pd.notna(movement_data['RightFrontSpeed'].iloc[i]):
            # Use wheel speeds to estimate velocity if no acceleration is available
            average_speed = np.mean([
                movement_data['LeftFrontSpeed'].iloc[i], movement_data['RightFrontSpeed'].iloc[i],
                movement_data['LeftBackSpeed'].iloc[i], movement_data['RightBackSpeed'].iloc[i]
            ])
            state[2] = average_speed * delta_t  # Update latitude velocity
            state[3] = average_speed * delta_t  # Update longitude velocity

    # Store the estimated position (latitude, longitude)
    with open(output_file, 'a') as f:
        f.write(f"{state[0]},{state[1]}\n")


