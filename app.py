import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 核心逻辑：执行 yt-dlp 并解析 URL ---
# 这是一个 GET 请求，完整的 API 地址将是：
# https://[你的服务名].onrender.com/get_subtitle_url?url=...&lang=...
@app.route('/get_subtitle_url', methods=['GET'])
def get_subtitle_url():
    # 1. 从 App 的请求中获取参数
    video_url = request.args.get('url')
    lang_code = request.args.get('lang')

    if not video_url or not lang_code:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数: url 或 lang'
        }), 400

    try:
        # 2. 构建 yt-dlp 命令
        command = [
            'yt-dlp',
            '--dump-json',     # 打印完整的视频信息 JSON
            '--skip-download', # 只解析，不下载视频
            '--sub-langs', lang_code, # 指定要解析的字幕语言
            '--sub-format', 'json3',  # 请求 JSON3 格式的字幕
            video_url
        ]
        
        # 3. 执行命令
        result = subprocess.run(
            command,
            capture_output=True, # 捕获标准输出和错误输出
            text=True,           # 解码输出为字符串
            check=True           # 如果 yt-dlp 失败，抛出异常
        )

        # 4. 解析 yt-dlp 输出 (JSON 格式)
        video_info = json.loads(result.stdout)
        
        # 5. 查找字幕的直接下载链接
        subtitle_url = None
        
        # 从解析结果中找到 requested_subtitles 字段并提取 URL
        if 'requested_subtitles' in video_info and lang_code in video_info['requested_subtitles']:
            subtitle_url = video_info['requested_subtitles'][lang_code]['url']
        
        if subtitle_url:
            # 6. 成功：返回提取到的直链给 Android App
            return jsonify({
                'success': True,
                'subtitle_url': subtitle_url,
                'error': None
            })
        else:
            # 失败：找不到指定的字幕
            return jsonify({
                'success': False,
                'error': f'未找到 {lang_code} 字幕，请检查语言代码或视频是否包含该字幕。'
            }), 404

    except subprocess.CalledProcessError as e:
        # 7. yt-dlp 命令执行失败
        return jsonify({
            'success': False,
            'error': f"yt-dlp 命令执行失败。错误信息: {e.stderr.strip()}"
        }), 500
    except Exception as e:
        # 8. 其他服务器内部错误
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

# 启动 Flask 应用
if __name__ == '__main__':
    # Render 将设置 PORT 环境变量
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
