import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from config import Config

def generate_report_charts(report_id: int, ats_metrics: dict) -> dict:
    charts_dir = Config.CHARTS_FOLDER
    os.makedirs(charts_dir, exist_ok=True)
    
    chart_paths = {}
    
    # 1. Circular Gauge / Donut Chart
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect="equal"))
        score = ats_metrics.get("ats_score", 85)
        sizes = [score, max(0, 100 - score)]
        colors = ['#4edea3', '#2a2a2a']
        
        wedges, _ = ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
                           wedgeprops=dict(width=0.3, edgecolor='#131313'))
        
        plt.text(0, 0, f"{int(score)}%", ha='center', va='center', fontsize=24, fontweight='bold', color='#4edea3')
        ax.set_title("ATS Score", color='#e5e2e1', fontsize=12)
        fig.patch.set_facecolor('#131313')
        
        gauge_path = os.path.join(charts_dir, f"gauge_{report_id}.png")
        plt.savefig(gauge_path, bbox_inches='tight', facecolor=fig.get_facecolor(), transparent=False)
        plt.close(fig)
        chart_paths["gauge"] = gauge_path
    except Exception:
        pass

    # 2. Skill Match Bar Chart
    try:
        fig, ax = plt.subplots(figsize=(6, 3))
        categories = ['Skills', 'Keywords', 'Education', 'Experience', 'Format']
        values = [
            ats_metrics.get("skill_match", 85),
            ats_metrics.get("keyword_match", 90),
            ats_metrics.get("education_match", 95),
            ats_metrics.get("experience_match", 80),
            ats_metrics.get("formatting_score", 100)
        ]
        
        bars = ax.barh(categories, values, color='#4cd7f6')
        ax.set_xlim(0, 100)
        ax.set_facecolor('#131313')
        fig.patch.set_facecolor('#131313')
        ax.tick_params(colors='#e5e2e1')
        ax.spines['bottom'].set_color('#464554')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color('#464554')
        
        bars_path = os.path.join(charts_dir, f"bars_{report_id}.png")
        plt.savefig(bars_path, bbox_inches='tight', facecolor=fig.get_facecolor(), transparent=False)
        plt.close(fig)
        chart_paths["bars"] = bars_path
    except Exception:
        pass

    return chart_paths
