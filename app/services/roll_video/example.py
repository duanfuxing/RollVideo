#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RollVideo测试示例

此脚本演示了如何使用RollVideo服务创建滚动文本视频
"""

import os
import sys
import logging
import time
from datetime import datetime
import json
import zipfile

# 添加父目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 导入RollVideo服务
from app.services.roll_video.roll_video_service import RollVideoService

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

def main():
    # 示例文本 - 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_text_path = os.path.join(current_dir, "example.txt")
    sample_text = open(sample_text_path, "r").read()

    # 路径
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # 初始化报告相关变量
    report_lines = [] # 用于存储报告条目
    report_file_name = f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    report_file_path = os.path.join(output_dir, report_file_name)

    # 创建服务实例
    service = RollVideoService()

    # 定义测试场景参数列表
    # test_cases = [
    #     {
    #         "description": "正常大图(1242x2208) - 无边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 0, # 上边距
    #             "bottom_margin": 0, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/1242x2208.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "正常大图(1242x2208) - 有上下边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 120, # 上边距
    #             "bottom_margin": 80, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/1242x2208.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "正常大小图(720x1280) - 无边距遮罩（尺寸刚好匹配视频尺寸）",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 0, # 上边距
    #             "bottom_margin": 0, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/720x1280.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "正常大小图(720x1280) - 仅有顶部边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 100, # 上边距
    #             "bottom_margin": 0, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/720x1280.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "正常小图(264x640) - 无边距遮罩（尺寸小于视频尺寸）",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 0, # 上边距
    #             "bottom_margin": 0, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/264x640.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "正常小图(264x640) - 仅有底部边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 0, # 上边距
    #             "bottom_margin": 80, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi-production.tos-cn-guangzhou.volces.com/264x640.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "非RGBA格式图片 - 无边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 0, # 上边距
    #             "bottom_margin": 0, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi.tos-cn-guangzhou.volces.com/file/b432b5b314bd8ff3acb409e0b56457ba/51c68aa0-319a-11f0-9a22-f3251006fbf4.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "非RGBA格式图片 - 同时有上下边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [255,255,255,1.0],  # 不透明白色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 150, # 上边距
    #             "bottom_margin": 100, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": "https://aigc-miaobi.tos-cn-guangzhou.volces.com/file/b432b5b314bd8ff3acb409e0b56457ba/51c68aa0-319a-11f0-9a22-f3251006fbf4.png", # 背景图
    #         }
    #     },
    #     {
    #         "description": "无背景图片 - 纯色背景带边距遮罩",
    #         "method": "overlay_cuda", 
    #         "params": {
    #             "text": sample_text,
    #             "width": 720,
    #             "height": 1280,
    #             "font_path": "方正黑体简体.ttf",
    #             "font_size": 30,
    #             "font_color": [0,0,0],
    #             "bg_color": [200,200,255,1.0],  # 浅蓝色背景
    #             "line_spacing": 20,
    #             "char_spacing": 10,
    #             "fps": 30,
    #             "roll_px": 1.6,
    #             "top_margin": 120, # 上边距
    #             "bottom_margin": 80, # 下边距
    #             "left_margin": 0, # 左边距
    #             "right_margin": 0, # 右边距
    #             "background_url": None, # 无背景图
    #         }
    #     }
    # ]

    test_cases = [
        {
            "description": "无背景图片 - 纯色背景带边距遮罩",
            "method": "overlay_cuda", 
            "params": {
                "text": sample_text,
                "width": 720,
                "height": 1280,
                "font_path": "方正黑体简体.ttf",
                "font_size": 30,
                "font_color": [0, 0, 0],
                "bg_color": [255, 255, 255, 1.0],  # 白色背景
                "line_spacing": 20,
                "char_spacing": 10,
                "fps": 60,
                "roll_px": 1,
                "top_margin": 120, # 上边距
                "bottom_margin": 80, # 下边距
                "left_margin": 0, # 左边距
                "right_margin": 0, # 右边距
                "background_url": None, # 无背景图
            }
        }
    ]

    # 循环生成不同场景的视频
    for i, test_case in enumerate(test_cases):
        logger.info(f"--- 开始生成场景 {i+1}: {test_case['description']} ---")
        
        # 输出文件名
        base_file_name = f"test_case_{i+1}_{time.strftime('%Y%m%d_%H%M%S')}"
        output_path_base = os.path.join(output_dir, base_file_name + ".tmp") 

        # 根据方法选择不同的生成函数
        method = test_case.get("method", "crop")
        
        # 记录开始时间
        start_time = time.time()
        
        if method == "crop":
            # crop滤镜
            result = service.create_roll_video_crop(
                output_path=output_path_base,
                **test_case['params']
            )
        elif method == "overlay_cuda":
            # overlay_cuda滤镜 (只支持基础匀速滚动和从下到上滚动)
            params = test_case['params'].copy()
            result = service.create_roll_video_overlay_cuda(
                output_path=output_path_base,
                **params
            )
        else:
            # overlay_cuda滤镜
            result = service.create_roll_video_overlay_cuda(
                output_path=output_path_base,
                **test_case['params']
            )
        
        # 记录结束时间和总耗时
        end_time = time.time()
        total_time = end_time - start_time
        
        # 输出结果
        if result.get("status") == "success":
            logger.info(f"场景 {i+1} 成功: 视频创建完成")
            logger.info(f"最终输出视频路径: {result.get('output_path')}")
            logger.info(f"总耗时: {total_time:.2f}秒")

            output_video_path = result.get('output_path')
            file_size = "N/A"

            if output_video_path and os.path.exists(output_video_path):
                # 获取文件大小
                try:
                    file_size_bytes = os.path.getsize(output_video_path)
                    file_size = f"{file_size_bytes} bytes ({file_size_bytes / (1024*1024):.2f} MB)"
                except Exception as e:
                    logger.error(f"获取文件大小出错 {output_video_path}: {e}")
                    file_size = "获取文件大小出错"
            else:
                logger.error(f"输出视频路径未找到或无效: {output_video_path}")
                file_size = "N/A (文件未找到)"

            report_entry = (
                f"测试用例: {test_case['description']}\n"
                f"方法: {test_case.get('method', 'N/A')}\n"
                f"参数:\n{json.dumps(test_case['params'], indent=4, ensure_ascii=False)}\n"
                f"渲染时间: {total_time:.2f}秒\n"
                f"文件大小: {file_size}\n"
                f"输出文件: {output_video_path}\n"
                f"--------------------------------------------------\n"
            )
            report_lines.append(report_entry)

        else:
            logger.error(f"场景 {i+1} 失败: {result.get('message')}")
            report_entry = (
                f"测试用例: {test_case['description']}\n"
                f"方法: {test_case.get('method', 'N/A')}\n"
                f"参数:\n{json.dumps(test_case['params'], indent=4, ensure_ascii=False)}\n"
                f"状态: 失败\n"
                f"信息: {result.get('message')}\n"
                f"渲染时间: {total_time:.2f}秒\n"
                f"--------------------------------------------------\n"
            )
            report_lines.append(report_entry)

        logger.info(f"--- 场景 {i+1} 生成结束 ---")
        
        # 在不同场景之间添加一个间隔
        if i < len(test_cases) - 1:
            logger.info("\n" + "-"*80 + "\n")

    # 写入报告文件
    try:
        with open(report_file_path, "w", encoding="utf-8") as f_report:
            f_report.write("RollVideo 测试报告\n")
            f_report.write(f"生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f_report.write("="*80 + "\n\n")
            for entry in report_lines:
                f_report.write(entry)
        logger.info(f"测试报告生成于: {report_file_path}")
    except Exception as e:
        logger.error(f"写入测试报告失败: {e}")

if __name__ == "__main__":
    main()