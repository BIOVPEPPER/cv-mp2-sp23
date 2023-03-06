import os
import imageio
import numpy as np
from absl import flags, app

FLAGS = flags.FLAGS
flags.DEFINE_string('test_name_hard', 'hard_almastatue', 
                    'what set of shreads to load')


def load_imgs(name):
    file_names = os.listdir(os.path.join('shredded-images', name))
    file_names.sort()
    Is = []
    for f in file_names:
        I = imageio.v2.imread(os.path.join('shredded-images', name, f))
        Is.append(I)
    return Is


def solve(Is):
    '''
    :param Is: list of N images
    :return order: order list of N images
    :return offsets: offset list of N ordered images
    '''
    order = [0, 24, 2, 9, 6, 16, 3, 5, 19, 7, 1, 21, 10, 11, 25, 15, 14, 13, 4,
             18, 23, 20, 17, 22, 8, 12]
    offsets = [120, 3, 27, 37, 58, 23, 55, 67, 53, 16, 35, 84, 2, 33, 121, 67,
               53, 79, 60, 61, 18, 101, 104, 0, 108, 98]
    # We are returning the order and offsets that will work for 
    # hard_almastatue, you need to write code that works in general for any given
    # Is. Use the solution for hard_almastatue to understand the format for
    # what you need to return
    return order, offsets


def composite(Is, order, offsets):
    Is = [Is[o] for o in order]
    strip_width = 1
    W = np.sum([I.shape[1] for I in Is]) + len(Is) * strip_width
    H = np.max([I.shape[0] + o for I, o in zip(Is, offsets)])
    H = int(H)
    W = int(W)
    I_out = np.ones((H, W, 3), dtype=np.uint8) * 255
    w = 0
    for I, o in zip(Is, offsets):
        I_out[o:o + I.shape[0], w:w + I.shape[1], :] = I
        w = w + I.shape[1] + strip_width
    return I_out

def main(_):
    Is = load_imgs(FLAGS.test_name_hard)
    order, offsets = solve(Is)
    I = composite(Is, order, offsets)
    import matplotlib.pyplot as plt
    plt.imshow(I)
    plt.show()

if __name__ == '__main__':
    app.run(main)
