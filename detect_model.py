import numpy as np
import math
import matplotlib.pyplot as plt

ship_length_to_width_ratio = 5

def rotate(model, angle, pivot_x, pivot_y, bg_amplitude):
    h, w = np.shape(model)

    # Create coordinate grid
    y_idx, x_idx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")

    # Shift pivot to center
    x_shifted = x_idx - pivot_x
    y_shifted = y_idx - pivot_y

    # Rotation around Z
    orig_x = pivot_x + (math.cos(angle) * x_shifted + -math.sin(angle) * y_shifted)
    orig_y = pivot_y + (math.sin(angle) * x_shifted + math.cos(angle) * y_shifted)

    # Filter out of bounds pixels
    valid_mask = (0 <= orig_x) & (orig_x < w) & (0 <= orig_y) & (orig_y < h)

    # Copy pixels to rotated positions
    rotated = bg_amplitude * np.ones([h, w])
    rotated[valid_mask] = model[orig_y[valid_mask].astype(int), orig_x[valid_mask].astype(int)]

    return rotated

def build_model(w, h, params):
    ship_x, ship_y, ship_scale, ship_angle, ship_amplitude, bg_amplitude = params

    ship_l = ship_length_to_width_ratio * ship_scale
    ship_w = ship_scale

    model = bg_amplitude * np.ones([h, w])

    y_idx, x_idx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    ship_mask = (y_idx >= ship_y) & (y_idx < ship_y + ship_l) & \
                (x_idx >= ship_x) & (x_idx < ship_x + ship_w)
    model[ship_mask] = ship_amplitude

    pivot_x = ship_x + ship_w / 2
    pivot_y = ship_y + ship_l / 2

    rotated = rotate(model, ship_angle, pivot_x, pivot_y, bg_amplitude)

    return rotated

def calculate_cost(img, params):
    h, w = np.shape(img)

    model = build_model(w, h, params)

    cost = np.sum((img - model)**2)

    return cost, model

def detect_model(img, params0):
    h, w = np.shape(img)
    n_params = 6
    max_ship_scale = max(h, w) / ship_length_to_width_ratio

    if len(params0) != n_params:
        raise Exception(f'Expected {0} model parameters.', n_params)

    params = params0

    epsilon = [1, 1, 0.01, 0.05, 0.01, 0.01]
    learning_rate = [1e-2, 1e-2, 1e-5, 1e-5, 1e-6, 1e-6]

    img_min = np.min(img)
    img_max = np.max(img)

    # plt.imshow(img, cmap='gray')
    # plt.colorbar()
    # plt.axis('off')
    # plt.show()

    max_iterations = 100
    for i in range(max_iterations):
        # print("params", params)

        cost, model = calculate_cost(img, params)
        # print("cost", cost)

        # if i % 10 == 0:
        #     plt.imshow(model, cmap='gray', vmin=img_min, vmax=img_max)
        #     plt.colorbar()
        #     plt.axis('off')
        #     plt.show()

        grad = np.zeros(n_params)
        for p in range(len(params)):
            d_params = np.copy(params)
            d_params[p] = params[p] + epsilon[p]
            d_cost, _ = calculate_cost(img, d_params)
            grad[p] = (d_cost - cost) / epsilon[p]

        # print("grad", grad)
        params = params - learning_rate * grad

        params[0] = max(0, min(w, params[0]))
        params[1] = max(0, min(h, params[1]))
        params[2] = max(1, min(max_ship_scale, params[2]))
        # params[3]: no bounds for rotation
        params[4] = max(img_min, min(img_max, params[4]))
        params[5] = max(img_min, min(img_max, params[5]))

        # print("grad norm", np.linalg.norm(grad))
        if (np.linalg.norm(grad) < 0.5):
            break

    # plt.imshow(model, cmap='gray', vmin=img_min, vmax=img_max)
    # plt.colorbar()
    # plt.axis('off')
    # plt.show()

    cost, model = calculate_cost(img, params)

    return params, cost, model
