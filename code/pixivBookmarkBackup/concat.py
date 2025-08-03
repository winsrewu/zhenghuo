from PIL import Image
import os
from tqdm import tqdm

def combine_images_vertically(image_folder, max_image_width=1920):
    """
    将指定文件夹中非__开头的图片垂直拼接为一张长图。
    图片会被缩放至最大宽度 max_image_width，保持宽高比。
    使用进度条显示处理过程，并减少内存占用。

    :param image_folder: 图片所在文件夹路径
    :param max_image_width: 图片最大宽度，超过则等比缩放
    """
    # 获取所有符合条件的图片文件
    supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    images = [
        img for img in os.listdir(image_folder)
        if not img.startswith('__') and img.lower().endswith(supported_formats)
    ]

    if not images:
        print("未找到符合条件的图片文件。")
        return

    print(f"找到 {len(images)} 张图片，开始处理...")

    # 第一步：扫描所有图片，获取尺寸并计算缩放后总高度
    image_paths = [os.path.join(image_folder, img) for img in images]
    total_height = 0
    image_sizes = []  # 存储缩放后的 (width, height)

    print("正在分析图片尺寸...")
    for img_path in image_paths:
        with Image.open(img_path) as im:
            # 计算缩放尺寸
            if im.width > max_image_width:
                new_width = max_image_width
                new_height = int(im.height * (max_image_width / im.width))
            else:
                new_width = im.width
                new_height = im.height
            image_sizes.append((new_width, new_height))
            total_height += new_height

    # 确定最终画布宽度（即所有图片缩放后的最大宽度）
    final_width = max((size[0] for size in image_sizes), default=0)
    if final_width == 0:
        print("所有图片尺寸无效。")
        return

    # 创建透明背景的最终图像
    combined_image = Image.new('RGBA', (final_width, total_height), (0, 0, 0, 0))
    y_offset = 0

    # 第二步：逐个加载、缩放、粘贴图片（带进度条）
    print("正在合并图片...")
    for img_path, (new_width, new_height) in tqdm(list(zip(image_paths, image_sizes)), desc="处理图片"):
        with Image.open(img_path) as im:
            # 转换为RGBA模式
            if im.mode != 'RGBA':
                im = im.convert('RGBA')
            # 缩放图片
            im_resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # 居中粘贴（可选：如果想居中，x偏移）
            x_offset = (final_width - new_width) // 2
            combined_image.paste(im_resized, (x_offset, y_offset), mask=im_resized if im_resized.mode == 'RGBA' else None)
            y_offset += new_height

    # 保存结果
    output_path = os.path.join(image_folder, 'combined_image.png')
    print(f"保存合并后的图片到 {output_path}")
    combined_image.save(output_path, format='PNG', compress_level=6)
    print("完成！")

# 使用函数
combine_images_vertically('./img/', max_image_width=1920)