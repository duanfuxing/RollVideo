"""图片处理器模块"""

import os
import logging
import time
import traceback
from PIL import Image, ImageOps
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class ImageProcessor:
    """图片处理器，负责图片下载、处理、格式转换和压缩"""

    def __init__(self):
        """初始化图片处理器"""
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def download_image(self, image_url, save_path=None, max_retries=3, timeout=30):
        """
        从网络下载图片
        
        参数:
            image_url: 图片URL
            save_path: 保存路径，如果为None则不保存到本地文件
            max_retries: 最大重试次数
            timeout: 超时时间(秒)
            
        返回:
            image: 下载的PIL.Image对象，如果下载失败则返回None
            local_path: 如果提供了save_path则返回保存的路径，否则为None
        """
        if not image_url or not image_url.startswith(("http://", "https://", "ftp://")):
            # 如果不是网络URL，直接返回原路径作为本地路径
            logger.info(f"图片URL '{image_url}' 不是网络URL，假定为本地路径")
            return Image.open(image_url) if os.path.exists(image_url) else None, image_url
            
        headers = {
            'User-Agent': self.user_agent
        }
        
        retry_count = 0
        local_path = None
        
        while retry_count < max_retries:
            try:
                logger.info(f"开始下载图片: {image_url}，尝试 {retry_count + 1}/{max_retries}")
                response = requests.get(image_url, stream=True, timeout=timeout, headers=headers)
                response.raise_for_status()  # 确保请求成功
                
                # 检查内容类型是否为图片
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"下载的内容不是图片，Content-Type: {content_type}")
                    # 继续尝试，因为有些服务器可能不正确设置Content-Type
                
                # 读取图片到内存
                image_data = BytesIO(response.content)
                
                # 验证图片是否有效
                try:
                    image = Image.open(image_data)
                    image.verify()  # 校验图片
                    image_data.seek(0)  # 重置指针
                    image = Image.open(image_data)  # 重新打开图片
                    
                    # 如果需要保存到本地
                    if save_path:
                        # 确保目录存在
                        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                        
                        # 先不保存，返回图片对象供后续处理
                        local_path = save_path
                    
                    logger.info(f"图片下载成功: {image_url}")
                    return image, local_path
                    
                except Exception as e:
                    logger.warning(f"下载的文件不是有效图片: {e}")
                    retry_count += 1
                    time.sleep(1)
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"下载图片超时，重试 {retry_count + 1}/{max_retries}")
                retry_count += 1
                time.sleep(1)
            except requests.exceptions.RequestException as e:
                logger.warning(f"下载图片失败: {e}，重试 {retry_count + 1}/{max_retries}")
                retry_count += 1
                time.sleep(1)
        
        logger.error(f"经过 {max_retries} 次重试后仍无法下载图片: {image_url}")
        return None, None
    
    def process_image(self, image, target_width, target_height, keep_aspect_ratio=True, convert_to_rgb=True):
        """
        处理图片：缩放、裁剪、格式转换
        
        参数:
            image: PIL.Image对象
            target_width: 目标宽度
            target_height: 目标高度
            keep_aspect_ratio: 是否保持长宽比
            convert_to_rgb: 是否转换为RGB模式
            
        返回:
            processed_image: 处理后的PIL.Image对象
        """
        if image is None:
            logger.error("无法处理空图片")
            return None
            
        try:
            # 转换格式为RGB（如果需要）
            if convert_to_rgb and image.mode != 'RGBA':
                logger.info(f"转换图片格式从 {image.mode} 到 RGBA")
                image = image.convert('RGBA')
            
            # 是否保持长宽比
            if keep_aspect_ratio:
                # 如果图片尺寸超出目标尺寸，进行等比例缩放
                if image.width > target_width or image.height > target_height:
                    logger.info(f"图片尺寸({image.width}x{image.height})不符合目标尺寸({target_width}x{target_height})，进行等比例缩放")
                    # 等比例缩放
                    image.thumbnail((target_width, target_height), Image.LANCZOS)
                    logger.info(f"缩放后的图片尺寸: {image.width}x{image.height}")
                    
                    # 如果缩放后的尺寸小于目标尺寸，创建新画布并居中图片
                    if image.width < target_width or image.height < target_height:
                        new_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                        paste_x = (target_width - image.width) // 2
                        paste_y = (target_height - image.height) // 2
                        new_image.paste(image, (paste_x, paste_y))
                        image = new_image.convert('RGBA')
                        logger.info(f"将缩放后的图片居中放置在 {target_width}x{target_height} 画布上")
                # 如果图片尺寸小于目标尺寸，直接调整到目标大小
                if image.width < target_width or image.height < target_height:
                    logger.info(f"图片尺寸({image.width}x{image.height})小于目标尺寸({target_width}x{target_height})，直接调整到目标大小")
                    # 直接调整到目标大小
                    image = image.resize((target_width, target_height), Image.LANCZOS)
                    logger.info(f"调整图片尺寸至 {target_width}x{target_height}")
                else:
                    logger.info(f"图片尺寸({image.width}x{image.height})已经符合目标尺寸({target_width}x{target_height})，无需缩放")
            
            # 如果尺寸超出，进行左上角裁剪
            if image.width > target_width or image.height > target_height:
                # 计算裁剪区域，从左上角(0,0)开始
                left = 0
                top = 0
                right = min(image.width, target_width)
                bottom = min(image.height, target_height)
                
                # 裁剪
                image = image.crop((left, top, right, bottom))
                logger.info(f"从左上角裁剪图片至 {right}x{bottom}")
            
            return image
            
        except Exception as e:
            logger.error(f"处理图片时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def compress_image(self, image, quality=85, format="PNG", optimize=True):
        """
        压缩图片
        
        参数:
            image: PIL.Image对象
            quality: 质量参数 (1-95)，仅对JPEG有效
            format: 输出格式 ('PNG', 'JPEG', 等)
            optimize: 是否优化
            
        返回:
            compressed_image: 压缩后的PIL.Image对象
            image_data: 压缩后的图片数据 (BytesIO)
        """
        if image is None:
            logger.error("无法压缩空图片")
            return None, None
            
        try:
            # 创建输出缓冲区
            output = BytesIO()
            
            # 根据格式调整压缩参数
            if format.upper() == 'PNG':
                compression_params = {
                    'format': 'PNG',
                    'optimize': optimize,
                    'compress_level': 6  # PNG压缩级别 (1-9)
                }
                logger.info(f"压缩PNG图片，优化: {optimize}, 压缩级别: 6")
            elif format.upper() == 'JPEG':
                compression_params = {
                    'format': 'JPEG',
                    'quality': quality,
                    'optimize': optimize
                }
                logger.info(f"压缩JPEG图片，质量: {quality}, 优化: {optimize}")
            else:
                compression_params = {
                    'format': format
                }
                logger.info(f"保存为 {format} 格式")
            
            # 保存到缓冲区
            image.save(output, **compression_params)
            
            # 重置缓冲区位置
            output.seek(0)
            
            # 返回压缩后的图片和数据
            return Image.open(output), output
            
        except Exception as e:
            logger.error(f"压缩图片时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None, None
    
    def download_and_process_image(self, image_url, save_path, target_width, target_height, 
                                  keep_aspect_ratio=True, convert_to_rgb=True, 
                                  compress_quality=85, output_format="PNG"):
        """
        下载、处理并保存图片的综合方法
        
        参数:
            image_url: 图片URL
            save_path: 保存路径
            target_width: 目标宽度
            target_height: 目标高度
            keep_aspect_ratio: 是否保持长宽比
            convert_to_rgb: 是否转换为RGB模式
            compress_quality: 压缩质量
            output_format: 输出格式
            
        返回:
            local_path: 处理后的图片保存路径，如果处理失败则返回None
        """
        try:
            # 1. 下载图片
            image, _ = self.download_image(image_url)
            if image is None:
                return None
                
            # 2. 处理图片（缩放和裁剪）
            processed_image = self.process_image(
                image,
                target_width,
                target_height,
                keep_aspect_ratio,
                convert_to_rgb
            )
            if processed_image is None:
                return None
                
            # 3. 压缩图片
            compressed_image, _ = self.compress_image(
                processed_image,
                compress_quality,
                output_format,
                True
            )
            if compressed_image is None:
                return None
                
            # 4. 保存到本地
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            if output_format.upper() == 'PNG':
                compressed_image.save(save_path, format=output_format, optimize=True, compress_level=6)
            elif output_format.upper() == 'JPEG':
                compressed_image.save(save_path, format=output_format, quality=compress_quality, optimize=True)
            else:
                compressed_image.save(save_path, format=output_format)
                
            logger.info(f"图片处理完成，保存至: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"下载处理图片过程中出现异常: {str(e)}")
            logger.error(traceback.format_exc())
            return None 
