import sys
import rasterio
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 2:
    print('Provide path to a GeoTIFF file (.tif) as an argument.')
    sys.exit(1)

input_path = sys.argv[1]

# Below code vomited with ❤️ by ChatGPT 🙏

# Step 1: Read the image
with rasterio.open(input_path) as src:
    band1 = src.read(1)  # Read the first band (assuming grayscale)

# Step 2: Apply Gamma Correction
gamma = 1.5  # Adjust this value to control the dimming effect
dimmed_img = np.clip(band1 / 255.0, 0, 1)  # Normalize to [0, 1]
dimmed_img = np.power(dimmed_img, gamma)  # Apply gamma correction
dimmed_img *= 255  # Scale back to [0, 255]

# Step 3: Normalize the dimmed image
min_val = np.min(dimmed_img)
max_val = np.max(dimmed_img)
normalized_img = (dimmed_img - min_val) / (max_val - min_val)

# Step 4: Display the image
plt.imshow(normalized_img, cmap='gray')
plt.colorbar()  # Optional: Show color scale
plt.title('Grayscale Image with Dimmed Bright Pixels')
plt.axis('off')  # Turn off axis labels
plt.show()
