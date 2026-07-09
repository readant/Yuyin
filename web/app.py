"""余音 - FastAPI Web应用"""
import os
import sys
import json
import shutil

from fastapi import FastAPI, Request, UploadFile, File
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


@app.get("/practice", response_class=HTMLResponse)
async def practice_page(request: Request):
    """跟吹练习"""
    return templates.TemplateResponse(request, "practice.html")


@app.get("/lyrics", response_class=HTMLResponse)
async def lyrics_page(request: Request):
    """歌词编辑"""
    return templates.TemplateResponse(request, "lyrics.html")


@app.get("/rhythm", response_class=HTMLResponse)
async def rhythm_page(request: Request):
    """节奏训练"""
    return templates.TemplateResponse(request, "rhythm.html")


@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    """音频工具"""
    return templates.TemplateResponse(request, "tools.html")


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


@app.get("/api/scan-dirs")
async def get_scan_dirs():
    """获取已扫描的目录列表"""
    dirs = music_library.get_scan_directories()
    return {"directories": dirs}


@app.delete("/api/scan-dirs")
async def clear_scan_dirs():
    """清空所有扫描目录和曲目"""
    music_library.clear_scan_directories()
    music_library._tracks.clear()
    music_library._id_counter = 0
    return {"success": True}


# ==================== 背景图片API ====================

BG_DIR = os.path.join(os.path.dirname(__file__), "static", "backgrounds")
os.makedirs(BG_DIR, exist_ok=True)
BG_CONFIG = os.path.join(BG_DIR, "config.json")

def _load_bg_config():
    if os.path.exists(BG_CONFIG):
        with open(BG_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    # 默认使用项目中的笛箫两隔.png
    default_bg = os.path.join(ROOT_DIR, "笛箫两隔.png")
    if os.path.exists(default_bg):
        import shutil
        dest = os.path.join(BG_DIR, "default.png")
        if not os.path.exists(dest):
            shutil.copy2(default_bg, dest)
        return {"current": "/static/backgrounds/default.png", "uploads": [{"filename": "default.png", "url": "/static/backgrounds/default.png", "name": "笛箫两隔.png"}]}
    return {"current": None, "uploads": []}

def _save_bg_config(config):
    with open(BG_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

@app.get("/api/background")
async def get_background():
    """获取当前背景图片"""
    config = _load_bg_config()
    return {"current": config.get("current"), "uploads": config.get("uploads", [])}

@app.post("/api/background/upload")
async def upload_background(file: UploadFile = File(...)):
    """上传背景图片"""
    if not file.content_type or not file.content_type.startswith("image/"):
        return JSONResponse({"success": False, "error": "只能上传图片文件"}, status_code=400)

    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"bg_{len(os.listdir(BG_DIR))}{ext}"
    filepath = os.path.join(BG_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    config = _load_bg_config()
    bg_url = f"/static/backgrounds/{filename}"
    config["uploads"].append({"filename": filename, "url": bg_url, "name": file.filename})
    config["current"] = bg_url
    _save_bg_config(config)

    return {"success": True, "url": bg_url}

@app.post("/api/background/select")
async def select_background(req: ScanRequest):
    """选择已上传的背景图片"""
    config = _load_bg_config()
    config["current"] = req.path if req.path else None
    _save_bg_config(config)
    return {"success": True}

@app.delete("/api/background/{filename}")
async def delete_background(filename: str):
    """删除背景图片"""
    filepath = os.path.join(BG_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    config = _load_bg_config()
    config["uploads"] = [u for u in config["uploads"] if u["filename"] != filename]
    if config["current"] and filename in config["current"]:
        config["current"] = None
    _save_bg_config(config)
    return {"success": True}


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


@app.get("/api/score/track/{track_id}")
async def get_score_for_track(track_id: int):
    """根据曲目ID查找匹配的简谱"""
    track = music_library.get_track_by_id(track_id)
    if not track:
        return {"score": None}

    db = DatabaseManager()
    session = db.get_session()
    try:
        from src.domain.models.database import Score
        # 按标题模糊匹配
        score = session.query(Score).filter(Score.title.contains(track.title)).first()
        if not score:
            score = session.query(Score).order_by(Score.updated_at.desc()).first()
        if score:
            return {
                "score": {
                    "id": score.id,
                    "title": score.title,
                    "notes_data": score.notes_data,
                    "tempo": score.tempo,
                    "key": score.key_signature,
                }
            }
        return {"score": None}
    finally:
        session.close()


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


class PracticeRequest(BaseModel):
    score_id: int = 0
    score_title: str = ""
    duration: float = 0
    notes_played: int = 0
    accuracy: float = 0


@app.post("/api/practice/record")
async def record_practice(req: PracticeRequest):
    """记录一次练习"""
    from src.application.services.zhudi_service import zhudi_service
    zhudi_service.record_practice(
        score_id=req.score_id,
        score_title=req.score_title,
        duration=req.duration,
        notes_played=req.notes_played,
        accuracy=req.accuracy
    )
    return {"success": True}


@app.get("/api/practice/today")
async def get_today_practice():
    """获取今日练习统计"""
    from src.application.services.zhudi_service import zhudi_service
    import time
    today_start = time.time() - (time.time() % 86400)
    today_records = [r for r in zhudi_service.practice_records if r.timestamp >= today_start]
    total_time = sum(r.duration for r in today_records)
    total_sessions = len(today_records)
    return {
        "total_time": round(total_time / 60, 1),
        "total_sessions": total_sessions,
        "total_time_formatted": f"{round(total_time / 60, 1)}分钟"
    }


# ==================== 歌词API ====================

from src.application.services.lyrics_service import lyrics_manager, LyricsParser

class LyricsRequest(BaseModel):
    text: str
    format: str = "lrc"

@app.get("/api/lyrics")
async def get_lyrics():
    """获取当前歌词"""
    return {
        "lyrics": [{"time": l.time, "text": l.text, "index": l.index} for l in lyrics_manager.lyrics],
        "has_lyrics": lyrics_manager.has_lyrics,
        "current_index": lyrics_manager.current_index,
    }

@app.post("/api/lyrics")
async def load_lyrics(req: LyricsRequest):
    """加载歌词（从文本）"""
    success = lyrics_manager.load_from_text(req.text, req.format)
    return {"success": success, "count": lyrics_manager.count}

@app.delete("/api/lyrics")
async def clear_lyrics():
    """清空歌词"""
    lyrics_manager.clear()
    return {"success": True}

@app.get("/api/lyrics/export")
async def export_lyrics():
    """导出LRC格式歌词"""
    return {"lrc": lyrics_manager.get_all_as_text()}


# ==================== 节奏训练API ====================

from src.application.services.rhythm_service import (
    rhythm_coach, BEAT_PATTERNS, RHYTHM_EXERCISES, TimeSignature
)

@app.get("/api/rhythm/patterns")
async def get_rhythm_patterns():
    """获取所有节拍模式"""
    patterns = []
    for key, p in BEAT_PATTERNS.items():
        patterns.append({
            "key": key,
            "name": p.name,
            "time_signature": f"{p.time_signature.value[0]}/{p.time_signature.value[1]}",
            "accents": p.accents,
            "description": p.description,
        })
    return {"patterns": patterns}

@app.get("/api/rhythm/exercises")
async def get_rhythm_exercises():
    """获取所有节奏练习"""
    exercises = []
    for e in RHYTHM_EXERCISES:
        exercises.append({
            "name": e.name,
            "description": e.description,
            "pattern_name": e.pattern.name,
            "bpm_range": list(e.bpm_range),
            "difficulty": e.difficulty,
        })
    return {"exercises": exercises}

@app.post("/api/rhythm/start")
async def start_rhythm(req: ScanRequest):
    """开始节拍（传入BPM）"""
    bpm = int(req.path) if req.path.isdigit() else 80
    rhythm_coach.metronome.set_bpm(bpm)
    rhythm_coach.metronome.play()
    return {"success": True, "bpm": bpm}

@app.post("/api/rhythm/stop")
async def stop_rhythm():
    """停止节拍"""
    rhythm_coach.metronome.stop()
    return {"success": True}

@app.post("/api/rhythm/tap")
async def tap_rhythm():
    """Tap测速"""
    bpm = rhythm_coach.metronome.tap()
    return {"bpm": bpm}

@app.get("/api/rhythm/stats")
async def get_rhythm_stats():
    """获取节奏练习统计"""
    return rhythm_coach.get_practice_stats()


# ==================== 音频工具API ====================

AUDIO_TOOLS_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_TOOLS_DIR, exist_ok=True)

@app.post("/api/audio/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """上传音频文件，分析并生成简谱"""
    import librosa
    import numpy as np

    filepath = os.path.join(AUDIO_TOOLS_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        y, sr = librosa.load(filepath, sr=22050)
        f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C3'), fmax=librosa.note_to_hz('C6'), sr=sr)
        times = librosa.times_like(f0, sr=sr)

        notes = []
        last_note = None
        for t, freq in zip(times, f0):
            if np.isnan(freq) or freq < 50:
                continue
            note_name = librosa.hz_to_note(freq)
            # 映射到简谱
            note_map = {'C':'1','D':'2','E':'3','F':'4','G':'5','A':'6','B':'7'}
            simple = note_name[:1] + note_name[1:].replace('#','') if note_name else '1'
            pitch_class = note_name[0] if note_name else 'C'
            simple_note = note_map.get(pitch_class, '1')

            if simple_note != last_note:
                notes.append({"note": simple_note, "time": round(t, 2), "freq": round(freq, 1)})
                last_note = simple_note

        # 生成简谱文本
        score_text = " ".join(n["note"] for n in notes)
        return {"success": True, "notes": notes, "score_text": score_text}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/audio/trim")
async def trim_audio(file: UploadFile = File(...), start: float = 0, end: float = 10):
    """裁剪音频"""
    import soundfile as sf
    import numpy as np

    filepath = os.path.join(AUDIO_TOOLS_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        y, sr = sf.read(filepath)
        start_idx = int(start * sr)
        end_idx = int(end * sr)
        trimmed = y[start_idx:end_idx]

        out_name = f"trimmed_{file.filename}"
        out_path = os.path.join(AUDIO_TOOLS_DIR, out_name)
        sf.write(out_path, trimmed, sr)
        return {"success": True, "url": f"/static/audio/{out_name}"}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/audio/normalize")
async def normalize_audio(file: UploadFile = File(...)):
    """归一化音频"""
    import soundfile as sf
    import numpy as np

    filepath = os.path.join(AUDIO_TOOLS_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        y, sr = sf.read(filepath)
        peak = np.max(np.abs(y))
        if peak > 0:
            y = y / peak * 0.9

        out_name = f"normalized_{file.filename}"
        out_path = os.path.join(AUDIO_TOOLS_DIR, out_name)
        sf.write(out_path, y, sr)
        return {"success": True, "url": f"/static/audio/{out_name}"}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
