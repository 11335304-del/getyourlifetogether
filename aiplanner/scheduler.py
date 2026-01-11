import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Task:
    name: str
    start_time: datetime
    end_time: datetime
    is_fixed: bool = True
    
    @property
    def duration(self):
        return self.end_time - self.start_time

    def to_dict(self):
        return {
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

    def clear_tasks(self):
        self.tasks = []

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
            # Match 1: HH:MM
            time_match_colon = re.search(r'(\d{1,2}):(\d{2})', line)
            # Match 2: X點 / X pm
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
