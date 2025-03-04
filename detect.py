import sys
import rasterio
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms
import numpy as np
import math

from detect_naive import detect_naive
from detect_model import detect_model, ship_length_to_width_ratio

if len(sys.argv) < 3:
    print('Provide detection method (naive, model) and path to a GeoTIFF file (.tif) as arguments.')
    sys.exit(1)

detection_method = sys.argv[1]
input_path = sys.argv[2]

with rasterio.open(input_path) as src:
    band1 = src.read(1) # Amplitudes in first band (assuming grayscale)
    pixel_lat_deg = -src.transform.e # One pixel in degrees of latitude
    lat_deg_m = 110540 # Degree of latitude in meters
    pixel_height_m = lat_deg_m * pixel_lat_deg

band1_h, band1_w = np.shape(band1)

# Histogram
# plt.hist(band1.flatten(), bins=256)
# plt.yscale('log')
# plt.grid(True)
# plt.show()

# Make dim details visible by clipping off extreme values.
# Then gamma-correct to make ships even brighter.
img = np.clip(band1, 0, 255) # uint8 range
gamma = 1.5 # gamma > 1 makes bright pixels brighter while keeping dimmer pixels same-ish
img = np.power(img, gamma)

# Display image
plt.imshow(img, cmap='gray')
plt.colorbar()
plt.axis('off')

# Detect ships
if (detection_method == "model"):
    bounding_boxes_naive = detect_naive(band1, pixel_height_m)

    params = []
    costs = []

    padding_px = 100 / pixel_height_m

    for bounding_box in bounding_boxes_naive:
        x, y, width, height = bounding_box

        # Uncomment to skip dock structures when testing:
        # if y < band1_h * 0.65 or height < 20:
        #     continue

        crop_x1 = max(0, math.floor(x - padding_px))
        crop_y1 = max(0, math.floor(y - padding_px))
        crop_x2 = min(band1_w, math.floor(crop_x1 + width + 2*padding_px))
        crop_y2 = min(band1_h, math.floor(crop_y1 + height + 2*padding_px))
        band1_crop = np.log(1 + band1[crop_y1:crop_y2, crop_x1:crop_x2])

        params0 = [
            padding_px,
            padding_px,
            max(width, height) / ship_length_to_width_ratio,
            -math.atan(width/height)/math.atan(ship_length_to_width_ratio),
            np.max(band1_crop),
            np.min(band1_crop)
        ]

        params_final, cost_final, _ = detect_model(band1_crop, params0)
        params_final[0] += crop_x1
        params_final[1] += crop_y1

        params.append(params_final)
        costs.append(cost_final)

    print("costs", sorted(costs))

    cost_threshold = 15000 # Change this based on dataset
    bounding_boxes = np.empty((0, 5))

    for i in range(len(params)):
        if (costs[i] <= cost_threshold):
            ship_x, ship_y, ship_scale, ship_angle, _, _ = params[i]

            ship_l = ship_length_to_width_ratio * ship_scale
            ship_w = ship_scale

            bounding_boxes = np.concatenate((bounding_boxes, [[ship_x, ship_y, ship_w, ship_l, ship_angle]]))
elif (detection_method == "naive"):
    bounding_boxes = detect_naive(band1, pixel_height_m)
    # Adds zero angle to all bounding boxes
    bounding_boxes = np.hstack([bounding_boxes, np.zeros((bounding_boxes.shape[0], 1))])
else:
    bounding_boxes = np.array([])

# Highlight detected ships
ax = plt.gca()
for bounding_box in bounding_boxes:
    x, y, width, height, angle = bounding_box

    rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor='r', facecolor='none')
    t = mtransforms.Affine2D().rotate_deg_around(x + width/2, y + height/2, -360*angle/(2*math.pi)) + ax.transData
    rect.set_transform(t)

    ax.add_patch(rect)

plt.show()
