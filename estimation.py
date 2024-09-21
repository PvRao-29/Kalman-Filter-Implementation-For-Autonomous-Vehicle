import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def load_position_data(csv_file):
    """
    Load position data from CSV and determine if 'Time' column exists.

    Parameters:
    - csv_file: Path to the CSV file.

    Returns:
    - data: pandas DataFrame containing the position data.
    - has_time: Boolean indicating presence of 'Time' column.
    """
    try:
        data = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{csv_file}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: The file '{csv_file}' does not appear to be in CSV format.")
        sys.exit(1)

    # Check for required columns
    required_columns = {'Latitude', 'Longitude'}
    if not required_columns.issubset(data.columns):
        missing = required_columns - set(data.columns)
        print(f"Error: Missing columns in '{csv_file}': {missing}")
        sys.exit(1)

    # Determine if 'Time' column exists
    has_time = 'Time' in data.columns

    return data, has_time

def get_user_input(has_time):
    """
    Get user input based on the presence of 'Time' column.

    Parameters:
    - has_time: Boolean indicating presence of 'Time' column.

    Returns:
    - input_time: The time input by the user.
    - start_time: (Only if has_time is False) The start time.
    - delta_t: (Only if has_time is False) The time interval between positions.
    """
    if has_time:
        while True:
            try:
                input_time = float(input("Enter the time (in seconds) for which you want the position: "))
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value for time.")
        return input_time, None, None
    else:
        print("The 'position.csv' does not contain a 'Time' column.")
        while True:
            try:
                start_time = float(input("Enter the start time (in seconds) corresponding to the first position: "))
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value for start time.")
        while True:
            try:
                delta_t = float(input("Enter the time interval (in seconds) between consecutive positions: "))
                if delta_t <= 0:
                    print("Time interval must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value for time interval.")
        while True:
            try:
                input_time = float(input("Enter the time (in seconds) for which you want the position: "))
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value for time.")
        return input_time, start_time, delta_t

def interpolate_position(input_time, times, latitudes, longitudes):
    """
    Interpolate latitude and longitude for the given input_time.

    Parameters:
    - input_time: The time for which to interpolate the position.
    - times: numpy array of time values.
    - latitudes: numpy array of latitude values.
    - longitudes: numpy array of longitude values.

    Returns:
    - interp_lat: Interpolated latitude.
    - interp_lon: Interpolated longitude.
    """
    if input_time < times[0] or input_time > times[-1]:
        print("Warning: Input time is outside the range of the data. Extrapolation will be performed.")
    
    interp_lat = np.interp(input_time, times, latitudes)
    interp_lon = np.interp(input_time, times, longitudes)
    
    return interp_lat, interp_lon

def main():
    # File path for the final position estimates (from the enhanced Kalman filter)
    csv_file = 'position.csv'
    
    # Load position data
    data, has_time = load_position_data(csv_file)
    
    # Get user input
    input_time, start_time, delta_t = get_user_input(has_time)
    
    if has_time:
        times = data['Time'].values
    else:
        num_positions = len(data)
        times = start_time + delta_t * np.arange(num_positions)
    
    latitudes = data['Latitude'].values
    longitudes = data['Longitude'].values
    
    # Retrieve position
    interp_lat, interp_lon = interpolate_position(input_time, times, latitudes, longitudes)
    
    print(f"\nPosition at time {input_time} seconds:")
    print(f"Latitude: {interp_lat}")
    print(f"Longitude: {interp_lon}")
    
    # Optional: Plotting
    plot_choice = input("\nWould you like to see this position on a scatter plot? (yes/no): ").strip().lower()
    if plot_choice in ['yes', 'y']:
        plt.figure(figsize=(14, 8))
        
        # Plot all positions
        plt.scatter(
            longitudes, 
            latitudes, 
            c=range(len(longitudes)),  # Color based on index
            cmap='viridis',
            edgecolor='blue',
            s=50,
            alpha=0.6,
            linewidth=0.5,
            label='Position Estimates'
        )
        
        # Highlight the interpolated position
        plt.scatter(
            interp_lon, 
            interp_lat, 
            color='red', 
            edgecolor='black', 
            s=100, 
            marker='X', 
            label='Queried Position'
        )
        
        # Highlight start and end points if applicable
        if len(longitudes) > 0 and len(latitudes) > 0:
            plt.scatter(
                longitudes[0], 
                latitudes[0], 
                color='green', 
                edgecolor='black', 
                s=150, 
                marker='*', 
                label='Start Point'
            )
            plt.scatter(
                longitudes[-1], 
                latitudes[-1], 
                color='red', 
                edgecolor='black', 
                s=150, 
                marker='*', 
                label='End Point'
            )
        
        # Annotate the queried position
        plt.annotate(
            f'Position at {input_time} s', 
            xy=(interp_lon, interp_lat), 
            xytext=(interp_lon + 0.01, interp_lat + 0.01),
            arrowprops=dict(facecolor='red', shrink=0.05),
            fontsize=10, 
            fontweight='bold'
        )
        
        # Set labels and title
        plt.xlabel("Longitude", fontsize=14, fontweight='bold')
        plt.ylabel("Latitude", fontsize=14, fontweight='bold')
        plt.title("Position Estimates from Kalman Filter", fontsize=16, fontweight='bold')
        
        # Customize grid
        plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray', alpha=0.6)
        
        # Adjust axis limits with margins
        margin_lon = (max(longitudes) - min(longitudes)) * 0.05
        margin_lat = (max(latitudes) - min(latitudes)) * 0.05
        plt.xlim(min(longitudes) - margin_lon, max(longitudes) + margin_lon)
        plt.ylim(min(latitudes) - margin_lat, max(latitudes) + margin_lat)
        
        # Aspect ratio
        plt.gca().set_aspect('auto', adjustable='box')
        
        # Background color
        plt.gca().set_facecolor('whitesmoke')
        
        # Legend
        plt.legend(fontsize=12, loc='best')
        
        # Tight layout
        plt.tight_layout()
        
        # Show plot
        plt.show()

if __name__ == "__main__":
    main()
