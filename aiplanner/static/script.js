document.addEventListener('DOMContentLoaded', () => {
    const taskNameInput = document.getElementById('task-name');
    const taskDurationInput = document.getElementById('task-duration');
    const planBtn = document.getElementById('plan-btn');
    const clearBtn = document.getElementById('clear-btn');
    const timeline = document.getElementById('timeline');
    const wellnessList = document.getElementById('wellness-list');
    const currentDate = document.getElementById('current-date');

    // Set Date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    currentDate.textContent = new Date().toLocaleDateString('en-US', options);

    // Load initial schedule
    fetchSchedule();

    planBtn.addEventListener('click', async () => {
        const name = taskNameInput.value;
        const duration = taskDurationInput.value;

        if (!name.trim()) {
            alert("Please enter a task name!");
            return;
        }

        try {
            const response = await fetch('/api/auto_plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, duration })
            });
            const data = await response.json();
            if (data.status === 'success') {
                taskNameInput.value = '';
                // Keep duration as 60 or reset? Let's keep it.
                fetchSchedule();
            } else {
                alert("Error: " + data.message);
            }
        } catch (error) {
            console.error('Error planning tasks:', error);
        }
    });

    clearBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear all tasks?')) {
            await fetch('/api/clear', { method: 'POST' });
            fetchSchedule();
        }
    });

    async function fetchSchedule() {
        const response = await fetch('/api/schedule');
        const data = await response.json();
        renderTimeline(data);
        renderWellness(data.breaks, data.conflicts);
    }

    function renderTimeline(data) {
        timeline.innerHTML = '';

        // Group tasks by day
        const tasksByDay = {};
        data.tasks.forEach(task => {
            const date = new Date(task.start_time).toLocaleDateString();
            if (!tasksByDay[date]) tasksByDay[date] = [];
            tasksByDay[date].push(task);
        });

        // Render
        for (const [date, tasks] of Object.entries(tasksByDay)) {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'timeline-day';

            const header = document.createElement('div');
            header.className = 'day-header';
            header.textContent = date;
            dayDiv.appendChild(header);

            tasks.forEach(task => {
                const card = document.createElement('div');
                card.className = 'task-card';

                const timeStr = new Date(task.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const endTimeStr = new Date(task.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                card.innerHTML = `
                    <div class="task-info">
                        <span class="task-time">${timeStr} - ${endTimeStr}</span>
                        <span class="task-name">${task.name}</span>
                    </div>
                    <div class="task-actions">
                        <button class="icon-btn edit-btn" data-id="${task.id}" data-name="${task.name}" data-start="${task.start_time}" data-end="${task.end_time}">✏️</button>
                        <button class="icon-btn delete-btn" data-id="${task.id}">🗑️</button>
                    </div>
                `;
                dayDiv.appendChild(card);
            });

            timeline.appendChild(dayDiv);
        }

        // Attach event listeners to new buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                deleteTask(id);
            });
        });

        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                const name = e.target.dataset.name;
                const start = e.target.dataset.start;
                const end = e.target.dataset.end;
                editTask(id, name, start, end);
            });
        });

        // Render Conflicts globally for now
        if (data.conflicts.length > 0) {
            const conflictDiv = document.createElement('div');
            conflictDiv.className = 'conflict-section';
            data.conflicts.forEach(conflict => {
                const alert = document.createElement('div');
                alert.className = 'conflict-alert';
                alert.textContent = `⚠️ ${conflict.message}`;
                conflictDiv.appendChild(alert);
            });
            timeline.prepend(conflictDiv);
        }
    }

    async function deleteTask(id) {
        if (confirm("Delete this task?")) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            fetchSchedule();
        }
    }

    async function editTask(id, currentName, start, end) {
        const newName = prompt("Edit task name:", currentName);
        if (!newName) return;

        try {
            await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: newName,
                    start_time: start,
                    end_time: end
                })
            });
            fetchSchedule();
        } catch (error) {
            console.error("Error updating task:", error);
        }
    }

    function renderWellness(breaks, conflicts) {
        wellnessList.innerHTML = '';

        if (conflicts.length > 0) {
            const li = document.createElement('li');
            li.textContent = `Found ${conflicts.length} conflicts! Check the timeline.`;
            li.style.color = '#e94560';
            wellnessList.appendChild(li);
        }

        if (breaks.length > 0) {
            breaks.forEach(b => {
                const li = document.createElement('li');
                li.className = 'wellness-tip';
                li.textContent = b;
                wellnessList.appendChild(li);
            });
        } else if (conflicts.length === 0) {
            const li = document.createElement('li');
            li.textContent = "Your schedule is balanced. Great job! 🌟";
            wellnessList.appendChild(li);
        }
    }
});
