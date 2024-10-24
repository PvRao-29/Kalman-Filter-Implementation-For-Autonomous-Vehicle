import pandas as pd
import matplotlib.pyplot as plt
import math
import matplotlib.cm as cm
import matplotlib.colors as colors

csv_file = 'data/position.csv'

try:
    data = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found.")
    exit(1)
except pd.errors.EmptyDataError:
    print(f"Error: The file '{csv_file}' is empty.")
    exit(1)
except pd.errors.ParserError:
    print(f"Error: The file '{csv_file}' does not appear to be in CSV format.")
    exit(1)

# Verify that necessary columns exist
required_columns = {'Latitude', 'Longitude'}
if not required_columns.issubset(data.columns):
    missing = required_columns - set(data.columns)
    print(f"Error: Missing columns in '{csv_file}': {missing}")
    exit(1)

# Extract latitude and longitude columns
latitudes = data['Latitude'].values
longitudes = data['Longitude'].values

# Check if there are data points to plot
if len(latitudes) == 0 or len(longitudes) == 0:
    print("Error: No data points found in the CSV file.")
    exit(1)

# Calculate margins based on data range
def calculate_margin(values, percentage=0.05):
    range_val = max(values) - min(values)
    return range_val * percentage if range_val != 0 else 0.01  # Avoid zero margin

margin_lon = calculate_margin(longitudes)
margin_lat = calculate_margin(latitudes)

# Create a wider figure for better horizontal space
plt.figure(figsize=(14, 8))  # Increased width from 12 to 14 inches

# Create a color map based on the index to show progression
cmap = cm.get_cmap('viridis')
norm = colors.Normalize(vmin=0, vmax=len(longitudes))
colors_map = cmap(norm(range(len(longitudes))))

# Plot the scatter plot with color mapping
scatter = plt.scatter(
    longitudes, 
    latitudes, 
    c=range(len(longitudes)),  # Color based on point index
    cmap='viridis',
    edgecolor='blue',           # Edge color of markers
    s=50,                       # Marker size
    alpha=0.7,                  # Transparency
    linewidth=0.5,              # Edge width
    label='Position Estimate'   # Label for legend
)

# Add a colorbar to indicate progression
cbar = plt.colorbar(scatter, pad=0.02)
cbar.set_label('Point Index', fontsize=12)

# Highlight start and end points
if len(longitudes) > 0 and len(latitudes) > 0:
    # Start Point
    plt.scatter(
        longitudes[0], 
        latitudes[0], 
        color='green', 
        edgecolor='black', 
        s=150, 
        marker='*', 
        label='Start Point'
    )
    # End Point
    plt.scatter(
        longitudes[-1], 
        latitudes[-1], 
        color='red', 
        edgecolor='black', 
        s=150, 
        marker='*', 
        label='End Point'
    )


# Set the correct axis labels and title
plt.xlabel("Longitude", fontsize=14, fontweight='bold')
plt.ylabel("Latitude", fontsize=14, fontweight='bold')
plt.title("Position Estimates from Kalman Filter", fontsize=16, fontweight='bold')

# Customize the grid appearance
plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray', alpha=0.6)

# Adjust axis limits for better proportionality
plt.xlim(min(longitudes) - margin_lon, max(longitudes) + margin_lon)
plt.ylim(min(latitudes) - margin_lat, max(latitudes) + margin_lat)

# adjust aspect ratio to prevent horizontal shrinkage
plt.gca().set_aspect('auto', adjustable='box')

# background color for better contrast
plt.gca().set_facecolor('whitesmoke')

# legend with larger font size, avoiding duplicate labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), fontsize=12, loc='best')

plt.tight_layout()

plt.annotate('Start', 
             xy=(longitudes[0], latitudes[0]), 
             xytext=(longitudes[0] + margin_lon*0.5, latitudes[0] + margin_lat*0.5),
             arrowprops=dict(facecolor='green', shrink=0.05),
             fontsize=12, 
             fontweight='bold')

plt.annotate('End', 
             xy=(longitudes[-1], latitudes[-1]), 
             xytext=(longitudes[-1] + margin_lon*0.5, latitudes[-1] + margin_lat*0.5),
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=12, 
             fontweight='bold')

# Show the plot
plt.show()
