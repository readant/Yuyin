"""PDF导出工具"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from typing import List
import os


class PDFExporter:
    """PDF导出器"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 15 * mm
        self.note_width = 12 * mm
        self.note_height = 30 * mm
    
    def export_score(self, notes_data: List[dict], title: str, subtitle: str, 
                     output_path: str, fingering_map: dict = None):
        """导出乐谱为PDF"""
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # 绘制标题
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.page_width / 2, self.page_height - 30 * mm, title)
        
        # 绘制副标题
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.page_width / 2, self.page_height - 40 * mm, subtitle)
        
        # 绘制音符
        x = self.margin
        y = self.page_height - 60 * mm
        
        c.setFont("Helvetica-Bold", 16)
        
        for i, note in enumerate(notes_data):
            note_value = note.get('value', '')
            
            if note_value == '|':
                # 小节线
                c.setStrokeColor(colors.grey)
                c.setLineWidth(1)
                c.line(x + 3 * mm, y - 5 * mm, x + 3 * mm, y + 15 * mm)
                x += 6 * mm
            elif note_value == ' ':
                x += 4 * mm
            else:
                # 绘制音符数字
                display_note = note_value.replace('(', '').replace(')', '')
                display_note = display_note.replace('[', '').replace(']', '')
                
                c.setFillColor(colors.black)
                c.drawCentredString(x + self.note_width / 2, y, display_note)
                
                # 绘制指法
                if fingering_map and note_value in fingering_map:
                    fingering = fingering_map[note_value]
                    self._draw_fingering(c, x + self.note_width / 2, y - 10 * mm, fingering)
                
                x += self.note_width + 2 * mm
            
            # 换行
            if x > self.page_width - self.margin:
                x = self.margin
                y -= 40 * mm
                
                if y < self.margin:
                    c.showPage()
                    y = self.page_height - 60 * mm
                    c.setFont("Helvetica-Bold", 16)
        
        c.save()
    
    def _draw_fingering(self, c, x: float, y: float, fingering: List[int]):
        """绘制指法图"""
        hole_spacing = 3 * mm
        hole_radius = 1.5 * mm
        
        for i, pressed in enumerate(fingering):
            hole_y = y - i * hole_spacing
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            
            if pressed:
                c.setFillColor(colors.black)
            else:
                c.setFillColor(colors.white)
            
            c.circle(x, hole_y, hole_radius, fill=1, stroke=1)
    
    def export_simple(self, notes_text: str, title: str, output_path: str):
        """简单导出"""
        notes_data = [{'value': n} for n in notes_text.split()]
        self.export_score(notes_data, title, '', output_path)
