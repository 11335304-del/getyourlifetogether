from scheduler import Scheduler, Task
from datetime import datetime

def run_demo():
    print("=== 🚀 Automated Planning AI Demo ===\n")
    
    scheduler = Scheduler()
    
    # Scenario 1: Batch Input Parsing
    # "Tomorrow has math quiz, PE report due, night go to cram school"
    print("--- Scenario 1: Parsing User Input ---")
    user_input = """
    Tomorrow 10:00 Math Quiz
    Tomorrow 14:00 PE Report Due
    Tomorrow 19:00 Go to Cram School
    """
    print(f"Input:\n{user_input}")
    
    tasks = scheduler.parse_input(user_input)
    for t in tasks:
        scheduler.add_task(t)
    
    print("\nParsed Tasks:")
    for t in scheduler.tasks:
        print(f"  {t}")
        
    # Scenario 2: Conflict Check
    # "Afternoon 2pm meeting" vs "Afternoon 2pm ball game"
    print("\n--- Scenario 2: Conflict Detection ---")
    # We already have 14:00 PE Report. Let's add a conflicting task.
    # "Tomorrow 2pm Ball Game"
    conflict_input = "Tomorrow 14:00 Ball Game"
    print(f"Adding conflicting task: {conflict_input}")
    
    new_tasks = scheduler.parse_input(conflict_input)
    for t in new_tasks:
        scheduler.add_task(t)
        
    # Scenario 3: Break Recommendation
    # Let's add a task right after Math Quiz (10:00-11:00)
    # Say "Tomorrow 11:00 Study Group" -> No gap
    print("\n--- Scenario 3: Break Recommendations ---")
    tight_input = "Tomorrow 11:00 Study Group"
    print(f"Adding tight task: {tight_input}")
    
    tight_tasks = scheduler.parse_input(tight_input)
    for t in tight_tasks:
        scheduler.add_task(t)

    # Generate Final Report
    print("\n" + "="*30)
    report = scheduler.generate_schedule_report()
    print(report)
    print("="*30)

if __name__ == "__main__":
    run_demo()
