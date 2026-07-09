"""余音 - FastAPI Web应用"""
import os
import sys
import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

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
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2模板
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 服务实例
from src.application.services.music_service import music_library
from src.application.services.score_service import ScoreService
from src.domain.models.database import DatabaseManager

score_service = ScoreService()

# ==================== 请求模型 ====================

class ScanRequest(BaseModel):
    path: str

class ScoreRequest(BaseModel):
    title: str
    artist: Optional[str] = None
    key: str = "D"
    time_signature: str = "4/4"
    tempo: int = 80
    notes_data: Optional[str] = None

class ParseNotesRequest(BaseModel):
    text: str

# ==================== Favicon ====================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(content={}, status_code=204)


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页（曲库）"""
    return templates.TemplateResponse(request, "index.html")


@app.get("/player", response_class=HTMLResponse)
async def player_page(request: Request):
    """播放器页面"""
    return templates.TemplateResponse(request, "player.html")


@app.get("/editor", response_class=HTMLResponse)
async def editor_page(request: Request):
    """简谱编辑器"""
    return templates.TemplateResponse(request, "editor.html")


@app.get("/fingering", response_class=HTMLResponse)
async def fingering_page(request: Request):
    """指法速查"""
    return templates.TemplateResponse(request, "fingering.html")


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """设置页面"""
    return templates.TemplateResponse(request, "settings.html")


# ==================== 音乐API ====================

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
async def scan_directory(req: ScanRequest):
    """扫描音乐目录"""
    if req.path and os.path.isdir(req.path):
        music_library.add_scan_directory(req.path)
        count = music_library.scan()
        return {"success": True, "count": count}
    return JSONResponse({"success": False, "error": "Invalid directory"}, status_code=400)


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


# ==================== 简谱API ====================

@app.get("/api/scores")
async def get_scores():
    """获取所有简谱"""
    scores = score_service.get_all_scores()
    return {"scores": scores}


@app.get("/api/score/{score_id}")
async def get_score(score_id: int):
    """获取单个简谱"""
    db = DatabaseManager()
    session = db.get_session()
    try:
        from src.domain.models.database import Score
        score = session.query(Score).filter(Score.id == score_id).first()
        if score:
            return {
                "id": score.id,
                "title": score.title,
                "artist": score.artist,
                "key": score.key_signature,
                "time_signature": score.time_signature,
                "tempo": score.tempo,
                "notes_data": score.notes_data,
                "created_at": str(score.created_at) if score.created_at else None,
            }
        return JSONResponse({"error": "Score not found"}, status_code=404)
    finally:
        session.close()


@app.post("/api/score")
async def create_or_update_score(req: ScoreRequest):
    """创建或更新简谱"""
    db = DatabaseManager()
    session = db.get_session()
    try:
        from src.domain.models.database import Score
        score = Score(
            title=req.title,
            artist=req.artist,
            key_signature=req.key,
            time_signature=req.time_signature,
            tempo=req.tempo,
            notes_data=req.notes_data,
        )
        session.add(score)
        session.commit()
        return {"success": True, "id": score.id}
    except Exception as e:
        session.rollback()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    finally:
        session.close()


@app.delete("/api/score/{score_id}")
async def delete_score(score_id: int):
    """删除简谱"""
    success = score_service.delete_score(score_id)
    if success:
        return {"success": True}
    return JSONResponse({"success": False, "error": "Delete failed"}, status_code=500)


@app.post("/api/parse-notes")
async def parse_notes(req: ParseNotesRequest):
    """解析简谱文本为音符序列"""
    from src.domain.models.notes import parse_notes
    notes = parse_notes(req.text)
    return {
        "notes": [
            {
                "value": n.value,
                "duration": n.duration,
                "is_bar": n.is_bar,
                "is_space": n.is_space,
            }
            for n in notes
        ]
    }


# ==================== 指法API ====================

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


# ==================== 练习记录API ====================

@app.get("/api/practice/stats")
async def get_practice_stats():
    """获取练习统计"""
    from src.application.services.zhudi_service import zhudi_service
    stats = zhudi_service.get_practice_stats()
    return stats


@app.get("/api/practice/recent")
async def get_recent_practices(limit: int = 10):
    """获取最近练习记录"""
    from src.application.services.zhudi_service import zhudi_service
    records = zhudi_service.get_recent_practices(limit)
    return {"records": records}
