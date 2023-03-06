import numpy as np
import cv2
from scipy.ndimage import gaussian_filter
from skimage.filters import gaussian


#JUST REALIZED WE NEED TO ACHIEVE THE PYRDOWN AND PYRUP ON OUR OWN..I STILL HAVE 6HRS, I mean, really?


    #Gaussian Pyramids
    # levels = 5
    # height, width, channels = im1.shape
    # im2 = cv2.resize(im2, (width, height))
    # G1 = im1.copy()
    # G2 = im2.copy()
    # gp1 = [G1]
    # gp2 = [G2]
    # for i in range(levels):
    #     G1 = cv2.pyrDown(G1)
    #     G2 = cv2.pyrDown(G2)
    #     gp1.append(G1)
    #     gp2.append(G2)

    # # generate Laplacian Pyramid for image 1 and 2
    # lp1 = [gp1[levels-1]]
    # lp2 = [gp2[levels-1]]
    # for i in range(levels-1, 0, -1):
    #     size = (gp1[i-1].shape[1], gp1[i-1].shape[0])
    #     GE1 = cv2.pyrUp(gp1[i], dstsize=size)
    #     GE2 = cv2.pyrUp(gp2[i], dstsize=size)
    #     L1 = cv2.subtract(gp1[i-1], GE1)
    #     L2 = cv2.subtract(gp2[i-1], GE2)
    #     lp1.append(L1)
    #     lp2.append(L2)

    # # blend the two Laplacian Pyramids
    # blended = []
    # for l1, l2 in zip(lp1, lp2):
    #     rows, cols, dpt = l1.shape
    #     #Uncomment For vertical seams
    #     #blended.append(np.hstack((l1[:, 0:cols//2], l2[:, cols//2:])))
    #     blended.append(np.vstack((l1[0:rows//2,: ], l2[rows//2:,: ])))
    # # reconstruct the final image
    # blended_image = blended[0]
    # for i in range(1, levels):
    #     size = (blended[i].shape[1], blended[i].shape[0])
    #     blended_image = cv2.pyrUp(blended_image, dstsize=size)
    #     blended_image = cv2.add(blended_image, blended[i])

    # return blended_image


def blend(im1, im2, mask):
    height, width, channels = im1.shape
    im2 = cv2.resize(im2, (width, height))
    mask = cv2.resize(mask,(width,height))
    print(im2.shape)
    print(im1.shape)
    print(mask.shape)
    init_sigma = 15
    def gaussian_difference(img, low_sigma, high_sigma,mode = 'reflect'):
        return gaussian(img, low_sigma, mode=mode) - gaussian(img, high_sigma, mode=mode) 

    def generate_pyramids(img,init_sigma):
        level1 = gaussian_difference(img,0,init_sigma,mode='reflect')
        level2 = gaussian_difference(img,init_sigma,init_sigma*2,mode='reflect')
        level3 = gaussian_difference(img,init_sigma*2,init_sigma*4,mode='reflect')
        level4 = gaussian_difference(img,init_sigma*4,init_sigma*8,mode='reflect')
        level5 = gaussian_difference(img,init_sigma*8,init_sigma*16,mode='reflect')
        level6 = gaussian_difference(img,init_sigma*16,init_sigma*32,mode='reflect')
        print(level6.shape)
        return level1,level2,level3,level4,level5,level6

    def mask_pyramids(mask,init_sigma):
        ml_1 = gaussian(mask,init_sigma,channel_axis=-1)
        ml_2 = gaussian(mask,init_sigma*2,channel_axis=-1)
        ml_3 = gaussian(mask,init_sigma*4,channel_axis=-1)
        ml_4 = gaussian(mask,init_sigma*8,channel_axis=-1)
        ml_5 = gaussian(mask,init_sigma*16, channel_axis=-1)
        ml_6 = gaussian(mask,init_sigma*32, channel_axis=-1)
        return ml_1,ml_2,ml_3,ml_4,ml_5,ml_6

    level1_im1,level2_im1,level3_im1,level4_im1,level5_im1,level6_im1 = generate_pyramids(im1,init_sigma)
    level1_im2,level2_im2,level3_im2,level4_im2,level5_im2,level6_im2 = generate_pyramids(im2,init_sigma)
    ml_1,ml_2,ml_3,ml_4,ml_5,ml_6 = mask_pyramids(mask,init_sigma)
    print(((1-ml_1)*level1_im2).shape)
    #Generate output
    blends = []
    levels_im1 = [level1_im1, level2_im1, level3_im1, level4_im1, level5_im1, level6_im1]
    levels_im2 = [level1_im2, level2_im2, level3_im2, level4_im2, level5_im2, level6_im2]
    mls = [ml_1, ml_2, ml_3, ml_4, ml_5, ml_6]

    for i in range(len(levels_im1)):
        blend = levels_im1[i]*mls[i] + (1-mls[i])*levels_im2[i]
        blends.append(blend)

    final_blend = sum(blends)

    final_blend = ((final_blend - np.min(final_blend)) / (np.max(final_blend) - np.min(final_blend))) * 255.0
    final_blend = final_blend.astype('uint8')
    return final_blend