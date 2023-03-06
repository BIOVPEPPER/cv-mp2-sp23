import numpy as np
import matplotlib.pyplot as plt

def get_wall_z_image(Z_val, fx, fy, cx, cy, szx, szy):
    Z = Z_val*np.ones((szy, szx), dtype=np.float32)
    return Z


def get_road_z_image(H_val, fx, fy, cx, cy, szx, szy):
    y = np.arange(szy).reshape(-1,1)*1.
    y = np.tile(y, (1, szx))
    Z = np.zeros((szy, szx), dtype=np.float32)
    Z[y > cy] = H_val*fy / (y[y>cy]-cy)
    Z[y <= cy] = np.NaN
    return Z


def plot_optical_flow(ax, Z, u, v, cx, cy, szx, szy, s=16):
    # Here is a function for plotting the optical flow. Feel free to modify this 
    # function to work well with your inputs, for example if your predictions are
    # in a different coordinate frame, etc.

    x, y = np.meshgrid(np.arange(szx), np.arange(szy))
    ax.imshow(Z, alpha=0.5, origin='upper')
    # ax.quiver is to used to plot a 2D field of arrows. 
    # please check https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.quiver.html to
    # understand the detials of the plotting with ax.quiver
    q = ax.quiver(x[::s,::s], y[::s,::s], u[::s,::s], v[::s, ::s], angles='xy')
    ax.axvline(cx)
    ax.axhline(cy)
    ax.set_xlim([0, szx])
    ax.set_ylim([szy, 0])
    ax.axis('equal')

def calculate_opticflow_translation(tx,ty,tz,Z,wy):
    #Since in 3.4, we only have wy not equals to 0, I will not bother my self trying other terms...
    project_u = -tx/Z + tz/Z*coordinates[:, :, 0]+(-(1 + coordinates[:, :, 0]**2)*wy)
    project_v = -ty/Z + tz/Z*coordinates[:, :, 1]+(-coordinates[:, :, 0]*coordinates[:, :, 1]*wy)
    return project_u,project_v


if __name__ == "__main__":
    # Focal length along X and Y axis. In class we assumed the same focal length 
    # for X and Y axis. but in general they could be different. We are denoting 
    # these by fx and fy, and assume that they are the same for the purpose of
    # this MP.
    fx = fy = 128.

    # Size of the image
    szy = 256
    szx = 384

    # Center of the image. We are going to assume that the principal point is at 
    # the center of the image.
    cx = 192
    cy = 128

    coordinates = np.zeros((szy, szx, 2))
    for y in range(szy):
        for x in range(szx):
            coordinates[y, x, :] = np.array([x - cx, y - cy])*1.0

    # Gets the image of a wall 2m in front of the camera.
    Z1 = get_wall_z_image(2., fx, fy, cx, cy, szx, szy)


    # Gets the image of the ground plane that is 3m below the camera.
    Z2 = get_road_z_image(3., fx, fy, cx, cy, szx, szy)

    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(14,7))
    ax1.imshow(Z1)
    ax2.imshow(Z2)

    # Plotting function.
    f = plt.figure(figsize=(13.5,9))
    u = np.random.rand(*Z1.shape)
    v = np.random.rand(*Z1.shape)
    plot_optical_flow(f.gca(), Z1, u, v, cx, cy, szx, szy, s=16)
    f.savefig('optical_flow_output.png', bbox_inches='tight')

    #3.2 
    f = plt.figure(figsize=(13.5,9))
    u,v= calculate_opticflow_translation(1,0,0,Z2,0)
    plot_optical_flow(f.gca(), Z2, u, v, cx, cy, szx, szy, s=16)
    f.savefig('optical3.2.png', bbox_inches='tight')

    #3.3
    f = plt.figure(figsize=(13.5,9))
    u,v= calculate_opticflow_translation(0,0,1,Z1,0)
    plot_optical_flow(f.gca(), Z1, u, v, cx, cy, szx, szy, s=16)
    f.savefig('optical3.3.png', bbox_inches='tight')

    #3.4
    f = plt.figure(figsize=(13.5,9))
    u,v= calculate_opticflow_translation(20,20,1,Z1,0)
    plot_optical_flow(f.gca(), Z1, u, v, cx, cy, szx, szy, s=16)
    f.savefig('optical3.4.png', bbox_inches='tight')

    #3.5
    f = plt.figure(figsize=(13.5,9))
    u,v= calculate_opticflow_translation(0,0,0,Z1,1)
    plot_optical_flow(f.gca(), Z1, u, v, cx, cy, szx, szy, s=16)
    f.savefig('optical3.5.png', bbox_inches='tight')