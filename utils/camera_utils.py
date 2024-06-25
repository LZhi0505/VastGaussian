#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

from scene.cameras import Camera, SimpleCamera
import numpy as np
from utils.general_utils import PILtoTorch
from utils.graphics_utils import fov2focal
import os
from PIL import Image

WARNED = False


def loadCam(args, id, cam_info, resolution_scale):
    orig_w, orig_h = cam_info.image.size

    if args.resolution in [1, 2, 4, 8]:
        resolution = round(orig_w / (resolution_scale * args.resolution)), round(
            orig_h / (resolution_scale * args.resolution))  # 计算下采样后，图片的尺寸
    else:  # should be a type that converts to float 应该是转换为float的类型吗
        if args.resolution == -1:  # 即使没有设置下采样的倍率，也会自动判断图片的宽度是否大于1600，如果大于，则自动进行下采样，并计算下采样的倍率
            if orig_w > 1600:
                global WARNED
                if not WARNED:
                    print("[ INFO ] Encountered quite large input images (>1.6K pixels width), rescaling to 1.6K.\n "
                          "If this is not desired, please explicitly specify '--resolution/-r' as 1")
                    WARNED = True
                global_down = orig_w / 1600
            else:
                global_down = 1
        else:
            global_down = orig_w / args.resolution

        scale = float(global_down) * float(resolution_scale)
        resolution = (int(orig_w / scale), int(orig_h / scale))

    resized_image_rgb = PILtoTorch(cam_info.image, resolution)  # [C, H, W]

    gt_image = resized_image_rgb[:3, ...]  # [C, H, W]
    loaded_mask = None

    if resized_image_rgb.shape[1] == 4:
        loaded_mask = resized_image_rgb[3:4, ...]

    return Camera(colmap_id=cam_info.uid, R=cam_info.R, T=cam_info.T,
                  FoVx=cam_info.FovX, FoVy=cam_info.FovY,
                  image=gt_image, gt_alpha_mask=loaded_mask,
                  image_name=cam_info.image_name, uid=id, data_device=args.data_device, params=cam_info.params)

def loadCamPartition(args, id, cam_info, image_width, image_height):
    """

        args:
        id: 某个训练相机的id
        cam_info: 某个相机本身
        image_width:
        image_height:
        Returns:
    """
    # image_width //= args.resolution
    # image_height //= args.resolution
    return SimpleCamera(
        colmap_id=cam_info.uid, R=cam_info.R, T=cam_info.T, 
        FoVx=cam_info.FovX, FoVy=cam_info.FovY, image_name=cam_info.image_name,
        uid=id, width=image_width, height=image_height, data_device=args.data_device)


def cameraList_from_camInfos(cam_infos, resolution_scale, args):
    camera_list = []

    for id, c in enumerate(cam_infos):
        camera_list.append(loadCam(args, id, c, resolution_scale))   # 对图片进行缩放操作，scale=1表示没有对图片进行缩放

    return camera_list

def cameraList_from_camInfos_partition(cam_infos, args):
    """

        cam_infos: 所有场景的训练相机
        args:
        returns:
    """
    camera_list = []
    # 遍历的每个训练相机
    for id, c in enumerate(cam_infos):
        image_width = c.width
        image_height = c.height
        camera_list.append(loadCamPartition(args, id, c,
                                            image_width,
                                            image_height,
                                            ))   # 对图片进行缩放操作，scale=1表示没有对图片进行缩放

    return camera_list

def camera_to_JSON(id, camera: Camera):
    Rt = np.zeros((4, 4))  # 将旋转矩阵和平移向量 保存于 变换矩阵 中
    Rt[:3, :3] = camera.R.transpose()
    Rt[:3, 3] = camera.T
    Rt[3, 3] = 1.0

    W2C = np.linalg.inv(Rt)  # 从世界坐标系到相机坐标系的转换矩阵
    pos = W2C[:3, 3]
    rot = W2C[:3, :3]
    serializable_array_2d = [x.tolist() for x in rot]
    camera_entry = {
        'id': id,
        'img_name': camera.image_name,
        'width': camera.width,
        'height': camera.height,
        'position': pos.tolist(),
        'rotation': serializable_array_2d,
        'fy': fov2focal(camera.FovY, camera.height),  # 将fov转换为焦距
        'fx': fov2focal(camera.FovX, camera.width)
    }
    return camera_entry
