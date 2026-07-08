"""数据库模型定义"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Score(Base):
    """乐谱表"""
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    artist = Column(String(100))
    key_signature = Column(String(10), default='D')
    time_signature = Column(String(10), default='4/4')
    tempo = Column(Integer, default=80)
    notes_data = Column(Text)  # JSON格式的音符数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    tags = Column(String(200))  # 逗号分隔的标签
    
    # 关联
    fingering_tables = relationship("FingeringTable", back_populates="score")


class FingeringTable(Base):
    """指法表"""
    __tablename__ = 'fingering_tables'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    score_id = Column(Integer, ForeignKey('scores.id'))
    instrument_type = Column(String(20))  # 笛子类型
    key_signature = Column(String(10))
    fingering_type = Column(String(10))  # 筒音作5/1/2
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联
    score = relationship("Score", back_populates="fingering_tables")


class PracticeRecord(Base):
    """练习记录"""
    __tablename__ = 'practice_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    score_id = Column(Integer, ForeignKey('scores.id'))
    duration = Column(Integer)  # 练习时长（秒）
    tempo = Column(Integer)  # 练习速度
    notes_played = Column(Integer)  # 弹奏的音符数
    accuracy = Column(Integer)  # 准确率（百分比）
    created_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)  # 备注


class Setting(Base):
    """应用设置"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path=None):
        if db_path is None:
            from ...config import settings
            db_path = settings.database.path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def add_score(self, title, artist=None, key_signature='D', time_signature='4/4', 
                  tempo=80, notes_data=None, tags=None):
        session = self.get_session()
        try:
            score = Score(
                title=title,
                artist=artist,
                key_signature=key_signature,
                time_signature=time_signature,
                tempo=tempo,
                notes_data=notes_data,
                tags=tags
            )
            session.add(score)
            session.commit()
            return score.id
        finally:
            session.close()
    
    def get_all_scores(self):
        session = self.get_session()
        try:
            return session.query(Score).order_by(Score.updated_at.desc()).all()
        finally:
            session.close()
    
    def get_score(self, score_id):
        session = self.get_session()
        try:
            return session.query(Score).filter(Score.id == score_id).first()
        finally:
            session.close()
    
    def update_score(self, score_id, **kwargs):
        session = self.get_session()
        try:
            score = session.query(Score).filter(Score.id == score_id).first()
            if score:
                for key, value in kwargs.items():
                    setattr(score, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_score(self, score_id):
        session = self.get_session()
        try:
            score = session.query(Score).filter(Score.id == score_id).first()
            if score:
                session.delete(score)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def add_practice_record(self, score_id, duration, tempo, notes_played, accuracy, notes=None):
        session = self.get_session()
        try:
            record = PracticeRecord(
                score_id=score_id,
                duration=duration,
                tempo=tempo,
                notes_played=notes_played,
                accuracy=accuracy,
                notes=notes
            )
            session.add(record)
            session.commit()
            return record.id
        finally:
            session.close()
    
    def get_practice_history(self, score_id=None, limit=50):
        session = self.get_session()
        try:
            query = session.query(PracticeRecord)
            if score_id:
                query = query.filter(PracticeRecord.score_id == score_id)
            return query.order_by(PracticeRecord.created_at.desc()).limit(limit).all()
        finally:
            session.close()
