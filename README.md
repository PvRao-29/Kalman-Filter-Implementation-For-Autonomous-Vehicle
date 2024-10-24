Kalman, Bayesian, and Particle Filters are methods for fusing many sources of noisy data into a better state estimate using statistics. 
For linear systems with Gaussian noise, Kalman filters are mathematically optimal. I implemented a Kalman Filter on sensor data for a car
made by Formula Electric @ Berkeley

🚀 Overview
This project is designed to estimate key values from datasets and visualize those results through robust and customizable Python scripts. By leveraging mathematical algorithms and powerful visualization techniques, this project aims to provide meaningful insights into data patterns and trends. It is composed of three key modules:

estimation.py: Core logic for estimating values.
main.py: Entry point for data processing and estimation.
plot.py: Visualization of the results using Matplotlib.

## ⚙️ **Technical Details**

### **Kalman Filter Overview**

The Kalman filter used in this project is specifically designed to handle linear dynamic systems with Gaussian noise. The algorithm follows two major steps:

1. **Prediction**:
   - The state vector `x(k|k-1)` is predicted based on the system's model using the equation:
     ```
     x̂(k|k-1) = A * x̂(k-1) + B * u(k-1)
     ```
     Where:
     - `A` is the state transition matrix.
     - `x̂(k-1)` is the previous estimated state.
     - `B` is the control input matrix.
     - `u(k-1)` is the control input at the previous step.

   - The covariance of the state estimate is updated using:
     ```
     P(k|k-1) = A * P(k-1) * Aᵀ + Q
     ```

2. **Update**:
   - The new measurement `z(k)` corrects the prediction:
     ```
     K(k) = P(k|k-1) * Hᵀ * (H * P(k|k-1) * Hᵀ + R)⁻¹
     ```
   - The estimated state is updated with:
     ```
     x̂(k) = x̂(k|k-1) + K(k) * (z(k) - H * x̂(k|k-1))
     ```

   - Finally, the covariance is updated:
     ```
     P(k) = (I - K(k) * H) * P(k|k-1)
     ```

### **System Modeling**

The Kalman filter in this project is designed for systems where position, velocity, or other dynamic states must be tracked accurately despite noisy observations. Common applications include:

- **Position estimation** in GPS tracking or robotic navigation.
- **Velocity and acceleration prediction** in dynamic systems like drones or self-driving vehicles.
- **Sensor fusion**, where data from multiple sensors (e.g., accelerometers, gyroscopes) are combined for more accurate state estimation.

If you made it this far, thanks for reading!
