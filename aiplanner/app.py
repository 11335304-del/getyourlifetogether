from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import re
import uuid

# ==========================
# Core Logic (Scheduler)
# ==========================

@dataclass
class Task:
    name: str
    start_time: datetime
    end_time: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_fixed: bool = True
    
    @property
    def duration(self):
        return self.end_time - self.start_time

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": int(self.duration.total_seconds() / 60)
        }

    def __repr__(self):
        return f"[{self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')}] {self.name}"

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.tasks.sort(key=lambda x: x.start_time)

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def update_task(self, task_id: str, name: str, start_time: datetime, end_time: datetime):
        for t in self.tasks:
            if t.id == task_id:
                t.name = name
                t.start_time = start_time
                t.end_time = end_time
                break
        self.tasks.sort(key=lambda x: x.start_time)

    def clear_tasks(self):
        self.tasks = []

    def find_best_slot(self, duration_minutes: int) -> Tuple[datetime, datetime]:
        """
        Finds the first available slot for the given duration.
        Logic:
        - Search within working hours (8 AM - 10 PM).
        - Start from NOW (rounded up to next 15 min).
        - Skip existing tasks.
        """
        now = datetime.now()
        # Round up to next 15 minutes
        delta = timedelta(minutes=15 - (now.minute % 15))
        start_search = (now + delta).replace(second=0, microsecond=0)
        
        # Define working hours
        WORK_START = 8
        WORK_END = 22
        
        current_pointer = start_search
        duration = timedelta(minutes=duration_minutes)
        
        # Limit search to next 7 days to avoid infinite loops
        days_searched = 0
        while days_searched < 7:
            # If pointer is before working hours, move to working hours
            if current_pointer.hour < WORK_START:
                current_pointer = current_pointer.replace(hour=WORK_START, minute=0)
            
            # If pointer + duration is after working hours, move to next day
            if (current_pointer + duration).hour >= WORK_END and (current_pointer + duration).minute > 0:
                current_pointer = (current_pointer + timedelta(days=1)).replace(hour=WORK_START, minute=0)
                days_searched += 1
                continue

            # Check for conflicts with existing tasks
            potential_end = current_pointer + duration
            conflict = False
            for task in self.tasks:
                # Check overlap: (StartA < EndB) and (EndA > StartB)
                if task.start_time < potential_end and task.end_time > current_pointer:
                    conflict = True
                    # Jump to end of this conflicting task
                    current_pointer = task.end_time
                    break
            
            if not conflict:
                return current_pointer, potential_end
            
        # Fallback: Just return now + duration if nothing found (shouldn't happen often)
        return start_search, start_search + duration

    def parse_input(self, text: str, reference_date: datetime = None) -> List[Task]:
        """
        Parses natural language input into Task objects.
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        lines = text.split('\n')
        new_tasks = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Determine Date
            target_date = reference_date
            if "明天" in line or "tomorrow" in line.lower():
                target_date += timedelta(days=1)
            
            # Determine Time
            hour = 9 # Default start time
            minute = 0
            duration_hours = 1
            
            # Regex for explicit time (e.g., 14:00, 2:30pm, 下午2點)
            time_match_colon = re.search(r'(\d{1,2}):(\d{2})', line)
            time_match_hour = re.search(r'(\d{1,2})\s*(點|pm|am|PM|AM)', line)
            
            if time_match_colon:
                hour = int(time_match_colon.group(1))
                minute = int(time_match_colon.group(2))
            elif time_match_hour:
                h_val = int(time_match_hour.group(1))
                indicator = time_match_hour.group(2).lower()
                if indicator in ['pm', '下午'] and h_val < 12:
                    h_val += 12
                elif indicator in ['am', '早上'] and h_val == 12:
                    h_val = 0
                hour = h_val
            else:
                # Keyword based fallback
                if "晚上" in line or "night" in line.lower():
                    hour = 19 # 7 PM
                elif "下午" in line or "afternoon" in line.lower():
                    hour = 14 # 2 PM
                elif "早上" in line or "morning" in line.lower():
                    hour = 9 # 9 AM
            
            start_dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=duration_hours)
            
            task = Task(line, start_dt, end_dt)
            new_tasks.append(task)
            
        return new_tasks

    def check_conflicts(self) -> List[Tuple[Task, Task]]:
        """Returns a list of conflicting task pairs."""
        conflicts = []
        sorted_tasks = sorted(self.tasks, key=lambda t: t.start_time)
        
        for i in range(len(sorted_tasks) - 1):
            current = sorted_tasks[i]
            next_task = sorted_tasks[i+1]
            
            # Check overlap: Start of next < End of current
            if next_task.start_time < current.end_time:
                conflicts.append((current, next_task))
        
        return conflicts

    def suggest_breaks(self) -> List[str]:
        """Suggests breaks between tight schedules."""
        suggestions = []
        sorted_tasks = sorted(self.tasks, key=lambda t: t.start_time)
        
        for i in range(len(sorted_tasks) - 1):
            current = sorted_tasks[i]
            next_task = sorted_tasks[i+1]
            
            # Calculate gap
            gap = next_task.start_time - current.end_time
            
            # If gap is 0 or very small, suggest a break
            if gap < timedelta(minutes=15) and gap >= timedelta(seconds=0):
                suggestions.append(
                    f"⚠️ High Intensity: Only {int(gap.total_seconds()/60)} min between '{current.name}' and '{next_task.name}'. "
                    f"Recommendation: Insert a 15-min break/exercise."
                )
            
        return suggestions

# ==========================
# Web App (Flask)
# ==========================

app = Flask(__name__)
scheduler = Scheduler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def plan():
    data = request.json
    text = data.get('text', '')
    
    # Parse and add tasks
    new_tasks = scheduler.parse_input(text)
    for t in new_tasks:
        scheduler.add_task(t)
        
    return jsonify({
        "status": "success",
        "added": [t.to_dict() for t in new_tasks]
    })

@app.route('/api/auto_plan', methods=['POST'])
def auto_plan():
    data = request.json
    name = data.get('name')
    duration = int(data.get('duration', 60))
    
    start_time, end_time = scheduler.find_best_slot(duration)
    
    new_task = Task(name, start_time, end_time, is_fixed=False)
    scheduler.add_task(new_task)
    
    return jsonify({
        "status": "success",
        "task": new_task.to_dict(),
        "message": f"Automatically scheduled '{name}' at {start_time.strftime('%H:%M')}"
    })

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    scheduler.remove_task(task_id)
    return jsonify({"status": "success"})

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    # Expecting ISO format strings
    try:
        start_time = datetime.fromisoformat(data['start_time']).replace(tzinfo=None)
        end_time = datetime.fromisoformat(data['end_time']).replace(tzinfo=None)
        name = data['name']
        
        scheduler.update_task(task_id, name, start_time, end_time)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    tasks = [t.to_dict() for t in scheduler.tasks]
    conflicts = []
    for t1, t2 in scheduler.check_conflicts():
        conflicts.append({
            "task1": t1.to_dict(),
            "task2": t2.to_dict(),
            "message": f"Conflict between {t1.name} and {t2.name}"
        })
        
    breaks = scheduler.suggest_breaks()
    
    return jsonify({
        "tasks": tasks,
        "conflicts": conflicts,
        "breaks": breaks
    })

    scheduler.clear_tasks()
    return jsonify({"status": "cleared"})

# ==========================
# AI Wellness Coach (Gemini)
# ==========================
import google.generativeai as genai
import os

# Configure API Key
GEMINI_API_KEY = "AIzaSyBlw_P8JGQ9TTWKgviiuJ_XZoW3n0_z1eU"
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/api/analyze_wellness', methods=['POST'])
def analyze_wellness():
    if not GEMINI_API_KEY:
        return jsonify({
            "status": "mock",
            "message": "AI Coach is in Demo Mode (No API Key). <br><br>Tip: You have a balanced schedule! Remember to drink water."
        })
    
    try:
        data = request.json
        tasks = data.get('tasks', [])
        
        # Construct Prompt
        schedule_text = "\n".join([f"- {t['name']} ({t['start_time']} to {t['end_time']})" for t in tasks])
        prompt = f"""
        You are a supportive wellness coach. Analyze this daily schedule and provide 3 specific, actionable wellness tips.
        Focus on energy management, breaks, and mindset. Keep it brief (max 50 words per tip).
        
        Schedule:
        {schedule_text}
        
        Format output as HTML bullet points.
        """
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return jsonify({
            "status": "success",
            "message": response.text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


        return jsonify({
            "status": "success",
            "message": response.text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==========================
# Posture Guard (CV)
# ==========================
try:
    from aiplanner.camera import VideoCamera
except ImportError:
    from camera import VideoCamera

def gen(camera):
    while True:
        frame, is_slouching = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting Flask Server...")
    app.run(debug=True, port=5000)