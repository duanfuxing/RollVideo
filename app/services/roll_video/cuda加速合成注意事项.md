使用 FFmpeg 和 CUDA 进行 NV12 格式图像合成叠加文档
1. 背景
在使用 GPU 加速（CUDA）做视频合成时，效率和稳定性极大依赖于输入数据格式和滤镜链匹配。NV12 是 CUDA 支持最好的 YUV 格式，适合用于加速图像上传与处理。为保证合成稳定且高效，所有输入素材应统一转换为 NV12 格式，且尺寸和帧率保持一致。

2. 关键点
NV12 格式是 GPU 硬件加速支持的主要 YUV 格式，适合 CUDA 加速滤镜。

输入图像或视频需统一尺寸和帧率，防止滤镜链报错。

静态图片需使用 -loop 1 循环生成持续帧流。

使用 hwupload_cuda 将 NV12 原始数据上传至 GPU。

使用 overlay_cuda 进行图层叠加。

叠加完成后使用 hwdownload,format=nv12 下载回 CPU 以便编码。

输出编码格式可用 h264_nvenc 进行硬件加速编码。

叠加图如果带透明通道（Alpha），需额外处理，透明图一般需要转成支持 Alpha 的格式，如 RGBA，再上传。

3. 操作步骤
3.1 预处理：将图片转换成 NV12 rawvideo 格式
bash
复制
编辑
ffmpeg -y -loop 1 -i input.png -pix_fmt nv12 -s WIDTHxHEIGHT -framerate FPS -t DURATION -f rawvideo input.yuv
-loop 1：将静态图转换成持续帧流，方便合成。

-pix_fmt nv12：转换成 NV12 格式。

-s WIDTHxHEIGHT：指定分辨率。

-framerate FPS：帧率，合成时需统一。

-t DURATION：帧流时长。

-f rawvideo：原始视频格式，纯裸数据。

示例：

bash
复制
编辑
ffmpeg -y -loop 1 -i background.png -pix_fmt nv12 -s 720x1280 -framerate 60 -t 300 -f rawvideo background.yuv
3.2 合成叠加命令
bash
复制
编辑
ffmpeg -y \
 -f rawvideo -pix_fmt nv12 -s 720x1280 -framerate 60 -i background.yuv \
 -f rawvideo -pix_fmt nv12 -s 720x1280 -framerate 60 -i overlay1.yuv \
 -f rawvideo -pix_fmt nv12 -s 720x1280 -framerate 60 -i overlay2.yuv \
 -filter_complex "
   [0:v]hwupload_cuda[bg];
   [1:v]hwupload_cuda[ol1];
   [bg][ol1]overlay_cuda=x=0:y=0[step1];
   [2:v]hwupload_cuda[ol2];
   [step1][ol2]overlay_cuda=x=50:y=50[final];
   [final]hwdownload,format=nv12[out]
 " \
 -map "[out]" \
 -c:v h264_nvenc -pix_fmt yuv420p output.mp4
使用 hwupload_cuda 上传每个 NV12 输入到 GPU。

使用 overlay_cuda 按顺序叠加图层。

使用 hwdownload,format=nv12 下载回 CPU。

最终用硬件编码器 h264_nvenc 编码输出。

4. 注意事项
分辨率和帧率要严格一致，否则 rawvideo 解码会报错。

静态图片需用 -loop 1 制作成帧流，保证合成时有持续帧输入。

带透明通道的图层需要特别处理，一般转成 RGBA 上传，或提前处理Alpha通道。

如果有格式转换或尺寸不匹配，会导致滤镜链初始化失败。

NV12 是常用GPU加速YUV格式，支持快速上传和硬件编码。

5. 结论
为了实现高效稳定的GPU加速视频合成，必须提前对所有素材做尺寸和格式的统一预处理（转成NV12原始视频流），并保证帧率一致；合成时使用 hwupload_cuda 上传、overlay_cuda 叠加，最后 hwdownload 输出，再用硬件编码器编码输出成成品视频。

