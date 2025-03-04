import numpy as np

# Based on sample images, pixels above this value could be metal hulls of ships
brightness_threshold = 1000.0

# Euclidean distance (in meters) from pixel to cluster center for it to be merged.
# Largest container ships are ~400 meters long.
cluster_threshold_m = 400.0

def detect_naive(band1, pixel_height_m):
    ship_coords = np.argwhere(band1 > brightness_threshold)

    cluster_threshold = cluster_threshold_m / pixel_height_m
    clusters = [np.array([coords]) for coords in ship_coords]
    clusters_merged = True
    while clusters_merged:
        clusters_merged = False
        for i in range(0, len(clusters)):
            if (len(clusters[i]) == 0):
                continue

            i_mean = np.mean(clusters[i], axis=0)
            for j in range(i + 1, len(clusters)):
                if (len(clusters[j]) == 0):
                    continue

                j_mean = np.mean(clusters[j], axis=0)
                dist = np.linalg.norm(i_mean - j_mean)
                if dist < cluster_threshold:
                    clusters[i] = np.concatenate((clusters[i], clusters[j]))
                    clusters[j] = np.array([])
                    clusters_merged = True

    bounding_boxes = np.empty((0, 4))
    for cluster in clusters:
        if (len(cluster) == 0):
            continue

        yx_min = np.min(cluster, axis=0)
        yx_max = np.max(cluster, axis=0)
        y = yx_min[0]
        x = yx_min[1]
        height = yx_max[0] - y
        width = yx_max[1] - x
        bounding_boxes = np.concatenate((bounding_boxes, [[x, y, width, height]]))

    # print(bounding_boxes)
    return bounding_boxes
