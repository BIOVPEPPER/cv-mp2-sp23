import numpy as np
from scipy import ndimage, signal

def compute_corners(I):
  # Currently this code proudces a dummy corners and a dummy corner response
  # map, just to illustrate how the code works. Your task will be to fill this
  # in with code that actually implements the Harris corner detector. You
  # should return th ecorner response map, and the non-max suppressed corners.
  # Input:
  #   I: input image, H x W x 3 BGR image
  # Output:
  #   response: H x W response map in uint8 format
  #   corners: H x W map in uint8 format _after_ non-max suppression. Each
  #   pixel stores the score for being a corner. Non-max suppressed pixels
  #   should have a low / zero-score.
    sigma=1
    k=0.04
    threshold=0.01
    window_size=3
    image = np.mean(I, axis=2)
    filter = np.array([[-1, 0, 1.]])

    # compute derivatives
    dx = signal.convolve2d(image, filter, mode='same', boundary='symm')
    dy = signal.convolve2d(image, filter.T, mode='same', boundary='symm')

    # compute products of derivatives
    Ixx = ndimage.gaussian_filter(dx**2, sigma)
    Iyy = ndimage.gaussian_filter(dy**2, sigma)
    Ixy = ndimage.gaussian_filter(dx*dy, sigma)

    # compute corner response function
    det = Ixx*Iyy - Ixy**2
    trace = Ixx + Iyy
    response = det - k*trace**2

    # threshold the response map
    response[response < threshold*np.max(response)] = 0

    # perform non-maximum suppression
    corners = np.zeros_like(response)
    pad = window_size // 2
    for i in range(pad, response.shape[0]-pad):
        for j in range(pad, response.shape[1]-pad):
            if response[i, j] == np.max(response[i-pad:i+pad+1, j-pad:j+pad+1]):
                corners[i, j] = response[i, j]

    # normalize and convert to uint8 format
    corners = corners / np.max(corners) * 255
    corners = corners.astype(np.uint8)

    response = response / np.max(response) * 255
    response = response.astype(np.uint8)

    return response, corners
