"""余音 - FastAPI Web应用"""
import os
import sys

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from src.config import settings

# 创建FastAPI应用
app = FastAPI(title="余音", version="0.2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 音乐库
from src.application.services.music_service import music_library


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    return _render("index.html")


@app.get("/player")
async def player():
    """播放器页面"""
    return _render("player.html")


@app.get("/library")
async def library():
    """音乐库页面"""
    return _render("library.html")


@app.get("/fingering")
async def fingering():
    """指法查询页面"""
    return _render("fingering.html")


@app.get("/settings")
async def settings_page():
    """设置页面"""
    return _render("settings.html")


@app.get("/listen")
async def listen():
    """欣赏音乐页面"""
    return _render("listen.html")


# ==================== API接口 ====================

@app.get("/api/tracks")
async def get_tracks():
    """获取音乐列表"""
    tracks = []
    for track in music_library.tracks:
        tracks.append({
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "duration": track.duration,
        })
    return {"tracks": tracks}


@app.get("/api/track/{track_id}")
async def get_track(track_id: int):
    """获取单个曲目"""
    track = music_library.get_track_by_id(track_id)
    if track:
        return {
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "duration": track.duration,
            "file_path": track.file_path,
        }
    return JSONResponse({"error": "Track not found"}, status_code=404)


@app.post("/api/scan")
async def scan_directory(request: Request):
    """扫描音乐目录"""
    data = await request.json()
    dir_path = data.get("path", "")

    if dir_path and os.path.isdir(dir_path):
        music_library.add_scan_directory(dir_path)
        count = music_library.scan()
        return {"success": True, "count": count}

    return JSONResponse({"success": False, "error": "Invalid directory"}, status_code=400)


@app.get("/api/fingering/{note}")
async def get_fingering(note: str, type: str = "5"):
    """获取指法信息"""
    from src.domain.models.notes import get_fingering_map, get_fingering_display

    fingering_map = get_fingering_map(type)
    if note in fingering_map:
        fingering = fingering_map[note]
        return {
            "note": note,
            "fingering": fingering,
            "display": get_fingering_display(fingering),
        }
    return JSONResponse({"error": "Note not found"}, status_code=404)


@app.get("/api/notes")
async def get_notes(type: str = "5"):
    """获取所有音符"""
    from src.domain.models.notes import get_all_notes_for_fingering

    notes = get_all_notes_for_fingering(type)
    return {"notes": notes}


@app.get("/audio/{filename:path}")
async def serve_audio(filename: str):
    """提供音频文件"""
    for scan_dir in music_library._scan_dirs:
        file_path = os.path.join(scan_dir, filename)
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                media_type="audio/mpeg",
                headers={"Accept-Ranges": "bytes"},
            )
    return JSONResponse({"error": "File not found"}, status_code=404)


@app.get("/api/serve-audio/{track_id}")
async def serve_audio_by_id(track_id: int):
    """通过ID提供音频文件"""
    track = music_library.get_track_by_id(track_id)
    if track and os.path.exists(track.file_path):
        return FileResponse(
            track.file_path,
            media_type="audio/mpeg",
            headers={"Accept-Ranges": "bytes"},
        )
    return JSONResponse({"error": "Track not found"}, status_code=404)


# ==================== 工具函数 ====================

def _render(template_name: str) -> str:
    """读取模板文件"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", template_name)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
