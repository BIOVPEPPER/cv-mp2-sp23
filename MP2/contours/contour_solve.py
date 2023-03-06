import numpy as np
from scipy import signal
import cv2
from scipy.ndimage import gaussian_filter
def compute_edges_dxdy(I):
  """Returns the norm of dx and dy as the edge response function."""
  I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
  I = I.astype(np.float32)/255.
  #I_padded = np.pad(I, ((1,1),(1,1)), 'constant', constant_values=0)
  #------------PART 1 START ---------------------
  # dx = signal.convolve2d(I, np.array([[-1, 0, 1]]), mode='same',boundary='symmetric')
  # dy = signal.convolve2d(I, np.array([[-1, 0, 1]]).T, mode='same',boundary='symmetric')
  #------------PART 1 END-----------------------

  #--------------PART2 START----------------
  I = np.pad(I,3,"reflect")
  I_after = gaussian_filter(I,2.5)
  
#   I = cv2.copyMakeBorder(I, 1, 1, 1, 1, cv2.BORDER_REFLECT_101)
#   I_after = gaussian_filter(I,2.5)
  dx = signal.convolve2d(I_after, np.array([[-1, 0, 1]]), mode='same')
  dy = signal.convolve2d(I_after, np.array([[-1, 0, 1]]).T, mode='same')
#   dx = cv2.Sobel(I_after, cv2.CV_32F, 1, 0, ksize=3)
#   dy = cv2.Sobel(I_after, cv2.CV_32F, 0, 1, ksize=3)
  #----------------PART2 END---------------
  mag = np.sqrt(dx**2 + dy**2)
  theta = np.arctan2(dy, dx)
  #--------------PART3 START----------------
  mag = max_supp(mag, theta)
  #--------------PART3 END----------------
  mag = mag / mag.max()
  mag = mag * 255.
  mag = np.clip(mag, 0, 255)
  mag = mag.astype(np.uint8)
  mag = mag[3:-3, 3:-3]
  return mag


def max_supp(img, theta):
    M, N = img.shape
    out = np.zeros((M, N))
    # convert angle from radians to degrees
    angle = theta * 180.0 / np.pi
    # round angle to the nearest 45 degrees
    angle[angle < -22.5] += 180.0
    angle = np.round(angle / 45.0) * 45.0

    for i in range(1, M - 1):
        for j in range(1, N - 1):
            if angle[i, j] == 0:
                if img[i, j] >= img[i, j - 1] and img[i, j] >= img[i, j + 1]:
                    out[i, j] = img[i, j]
            elif angle[i, j] == 45:
                if img[i, j] >= img[i - 1, j - 1] and img[i, j] >= img[i + 1, j + 1]:
                    out[i, j] = img[i, j]
            elif angle[i, j] == 90:
                if img[i, j] >= img[i - 1, j] and img[i, j] >= img[i + 1, j]:
                    out[i, j] = img[i, j]
            elif angle[i, j] == 135:
                if img[i, j] >= img[i - 1, j + 1] and img[i, j] >= img[i + 1, j - 1]:
                    out[i, j] = img[i, j]
    return out / out.max() * 255

