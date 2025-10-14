from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# 初始化 Flask 应用
app = Flask(__name__)

@app.route("/")
def home():
    """根路由，显示 API 状态和用法示例。"""
    # 部署到 Render 后，这个域名会变化，但代码不变
    example_link = (
        f"https://your-render-domain.onrender.com/get_subtitle?"
        f"video_id=VIDEO_ID&lang=LANG_CODE"
    )
    return jsonify({
        "message": "Youtube Subtitle API is ready. Use the following link format in your Android App:",
        "app_api_link_example": example_link,
        "required_parameters": ["video_id", "lang"],
        "status": "running"
    })

@app.route("/get_subtitle", methods=["GET"])
def get_subtitle():
    """获取指定视频ID和语言的字幕。"""
    
    video_id = request.args.get("video_id")
    lang_code = request.args.get("lang")

    if not video_id or not lang_code:
        return jsonify({
            "error": "Missing parameters. Required: video_id and lang."
        }), 400

    try:
        # 核心逻辑：直接调用 get_transcript，兼容性最好
        subtitles = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=[lang_code]
        )
        
        # 成功响应
        return jsonify({
            "status": "success",
            "video_id": video_id,
            "lang": lang_code,
            "subtitles": subtitles 
        }), 200

    except TranscriptsDisabled:
        return jsonify({
            "error": "TranscriptsDisabled",
            "message": "The YouTube video has transcripts disabled."
        }), 404
        
    except NoTranscriptFound:
        return jsonify({
            "error": "NoTranscriptFound",
            "message": f"No transcript found for language code: {lang_code}"
        }), 404
        
    except Exception as e:
        # 捕获所有其他错误，并记录到日志
        app.logger.error(f"Error processing video {video_id}: {e}")
        return jsonify({
            "error": "InternalServerError",
            "message": f"An internal server error occurred. Error details: {e}"
        }), 500
