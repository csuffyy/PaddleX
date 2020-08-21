import os
import os.path as osp
import imghdr
import gdal
import numpy as np
from PIL import Image

from paddlex.seg import transforms


def read_img(img_path):
    img_format = imghdr.what(img_path)
    name, ext = osp.splitext(img_path)
    if img_format == 'tiff' or ext == '.img':
        dataset = gdal.Open(img_path)
        if dataset == None:
            raise Exception('Can not open', img_path)
        im_data = dataset.ReadAsArray()
        return im_data.transpose((1, 2, 0))
    elif img_format == 'png':
        return np.asarray(Image.open(img_path))
    elif ext == '.npy':
        return np.load(img_path)
    else:
        raise Exception('Image format {} is not supported!'.format(ext))


def decode_image(im, label):
    if isinstance(im, np.ndarray):
        if len(im.shape) != 3:
            raise Exception(
                "im should be 3-dimensions, but now is {}-dimensions".format(
                    len(im.shape)))
    else:
        try:
            im = read_img(im)
        except:
            raise ValueError('Can\'t read The image file {}!'.format(im))
    if label is not None:
        if not isinstance(label, np.ndarray):
            label = read_img(label)
    return (im, label)


class Clip(transforms.SegTransform):
    """
    对图像上超出一定范围的数据进行裁剪。

    Args:
        min_val (list): 裁剪的下限，小于min_val的数值均设为min_val. 默认值0.
        max_val (list): 裁剪的上限，大于max_val的数值均设为max_val. 默认值255.0.
    """

    def __init__(self, min_val=[0, 0, 0], max_val=[255.0, 255.0, 255.0]):
        self.min_val = min_val
        self.max_val = max_val
        if not (isinstance(self.min_val, list) and isinstance(self.max_val,
                                                              list)):
            raise ValueError("{}: input type is invalid.".format(self))

    def __call__(self, im, im_info=None, label=None):
        for k in range(im.shape[2]):
            np.clip(
                im[:, :, k], self.min_val[k], self.max_val[k], out=im[:, :, k])

        if label is None:
            return (im, im_info)
        else:
            return (im, im_info, label)
