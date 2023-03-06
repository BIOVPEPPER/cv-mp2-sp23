import numpy as np
from generate_scene import get_ball
import matplotlib.pyplot as plt

# specular exponent
k_e = 50

def render(Z, N, A, S, 
           point_light_loc, point_light_strength, 
           directional_light_dirn, directional_light_strength,
           ambient_light, k_e):
  # To render the images you will need the camera parameters, you can assume
  # the following parameters. (cx, cy) denote the center of the image (point
  # where the optical axis intersects with the image, f is the focal length.
  # These parameters along with the depth image will be useful for you to
  # estimate the 3D points on the surface of the sphere for computing the
  # angles between the different directions.
  h, w = A.shape
  cx, cy = w / 2, h /2
  f = 128
  def normalize(array):
    magnitude = np.linalg.norm(array)
    return array / magnitude

  def point_on_sphere(h,w):
    coordinates = np.zeros((h,w,3))
    for y in range(h):
      for x in range(w):
        depth = Z[y, x]
        coord = [(x - cx)*depth/f, (y - cy)*depth/f, depth]
        coordinates[y, x, :] = np.array(coord)
    return coordinates
  

  directional_light_dirn = normalize(directional_light_dirn)
  
  coordinates = point_on_sphere(h,w)

  # Ambient Term
  I = A * ambient_light
  
  # Diffuse Term
  print(np.array(point_light_loc).shape)
  print(np.array(coordinates).shape)
  point_light_dirns = np.array(point_light_loc) - coordinates
  #Normalize the point light directions vector.
  point_light_transpose = point_light_dirns.T
  point_light_norm_tanspose = np.linalg.norm(point_light_dirns,axis = 2).T
  #Calculate the light vector for point lights
  point_light_dirns = (point_light_transpose/point_light_norm_tanspose).T
  point_diffuse = np.sum(point_light_dirns*N, axis=2)
  directional_diffuse = np.sum(directional_light_dirn*N, axis=2)
  for i in range(len(point_diffuse)):
    for j in range(len(point_diffuse[0])):
      if point_diffuse[i][j] < 0:
        point_diffuse[i][j] = 0
  for i in range(len(directional_diffuse)):
    for j in range(len(directional_diffuse[0])):
      if directional_diffuse[i][j] < 0:
        directional_diffuse[i][j] = 0
  diffuse_term = A*(point_diffuse*np.array(point_light_strength) + directional_diffuse*np.array(directional_light_strength))

  # Specular Term
  zeros = np.zeros_like(coordinates)
  reflection_factor = zeros - coordinates
  print('This is reflection factor')
  print(reflection_factor)
  reflection_factor = (reflection_factor.T/np.linalg.norm(reflection_factor, axis=2).T).T

  point_reflection = (2*np.sum(point_light_dirns*N, axis=2).T*N.T).T - point_light_dirns
  directional_reflection = (2*np.sum(directional_light_dirn*N, axis=2).T*N.T).T - directional_light_dirn

  point_specular = np.sum(point_reflection*reflection_factor, axis=2)
  directional_specular = np.sum(directional_reflection*reflection_factor, axis=2)

  for i in range(len(point_specular)):
    for j in range(len(point_specular[0])):
      if point_specular[i][j] < 0:
        point_specular[i][j] = 0

  for i in range(len(directional_specular)):
    for j in range(len(directional_specular[0])):
      if directional_specular[i][j] < 0:
        directional_specular[i][j] = 0

  specular_term = S*(np.array(point_light_strength)*(point_specular)**k_e + np.array(directional_light_strength)*(directional_specular)**k_e)
  I = I + specular_term + diffuse_term 

  
  I = np.minimum(I, 1)*255
  I = I.astype(np.uint8)
  I = np.repeat(I[:,:,np.newaxis], 3, axis=2)
  return I

def main():
  for specular in [True, False]:
    # get_ball function returns:
    # - Z (depth image: distance to scene point from camera center, along the
    # Z-axis)
    # - N is the per pixel surface normals (N[:,:,0] component along X-axis
    # (pointing right), N[:,:,1] component along Y-axis (pointing down),
    # N[:,:,2] component along Z-axis (pointing into the scene)),
    # - A is the per pixel ambient and diffuse reflection coefficient per pixel,
    # - S is the per pixel specular reflection coefficient.
    Z, N, A, S = get_ball(specular=specular)

    # Strength of the ambient light.
    ambient_light = 0.5

    
    # For the following code, you can assume that the point sources are located
    # at point_light_loc and have a strength of point_light_strength. For the
    # directional light sources, you can assume that the light is coming _from_
    # the direction indicated by directional_light_dirn (i.e., \hat{v}_i =
    # directional_light_dirn), and with strength directional_light_strength.
    # The coordinate frame is centered at the camera, X axis points to the
    # right, Y-axis point down, and Z-axis points into the scene.
    
    # Case I: No directional light, only point light source that moves around
    # the object. 
    point_light_strength = [1.5]
    directional_light_dirn = [[1, 0, 0]]
    directional_light_strength = [0.0]
    
    fig, axes = plt.subplots(4, 4, figsize=(15,10))
    axes = axes.ravel()[::-1].tolist()
    for theta in np.linspace(0, np.pi*2, 16): 
      point_light_loc = [[10*np.cos(theta), 10*np.sin(theta), -3]]
      I = render(Z, N, A, S, point_light_loc, point_light_strength, 
                 directional_light_dirn, directional_light_strength,
                 ambient_light, k_e)
      ax = axes.pop()
      ax.imshow(I)
      ax.set_axis_off()
    plt.savefig(f'specular{specular:d}_move_point.png', bbox_inches='tight')
    plt.close()

    # Case II: No point source, just a directional light source that moves
    # around the object.
    point_light_loc = [[0, -10, 2]]
    point_light_strength = [0.0]
    directional_light_strength = [2.5]
    
    fig, axes = plt.subplots(4, 4, figsize=(15,10))
    axes = axes.ravel()[::-1].tolist()
    for theta in np.linspace(0, np.pi*2, 16): 
      directional_light_dirn = [np.array([np.cos(theta), np.sin(theta), .1])]
      directional_light_dirn[0] = \
      directional_light_dirn[0] / np.linalg.norm(directional_light_dirn[0])
      I = render(Z, N, A, S, point_light_loc, point_light_strength, 
                 directional_light_dirn, directional_light_strength,
                 ambient_light, k_e) 
      ax = axes.pop()
      ax.imshow(I)
      ax.set_axis_off()
    plt.savefig(f'specular{specular:d}_move_direction.png', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
  main()
