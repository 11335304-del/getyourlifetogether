document.addEventListener('DOMContentLoaded', () => {
    const taskNameInput = document.getElementById('task-name');
    const taskDurationInput = document.getElementById('task-duration');
    const planBtn = document.getElementById('plan-btn');
    const clearBtn = document.getElementById('clear-btn');
    const wellnessList = document.getElementById('wellness-list');
    const currentDate = document.getElementById('current-date');
    const calendarEl = document.getElementById('calendar');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Modal Elements
    const taskModal = document.getElementById('task-modal');
    const modalTaskName = document.getElementById('modal-task-name');
    const modalTaskTime = document.getElementById('modal-task-time');
    const startFocusBtn = document.getElementById('start-focus-btn');
    const deleteTaskBtn = document.getElementById('delete-task-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');

    // Timer Elements
    const focusOverlay = document.getElementById('focus-overlay');
    const timerDisplay = document.getElementById('timer-display');
    const focusTaskName = document.getElementById('focus-task-name');
    const pauseTimerBtn = document.getElementById('pause-timer-btn');
    const stopTimerBtn = document.getElementById('stop-timer-btn');

    let currentEventId = null;
    let timerInterval = null;
    let timeLeft = 25 * 60; // 25 minutes in seconds
    let isPaused = false;

    // Set Date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    currentDate.textContent = new Date().toLocaleDateString('en-US', options);

    // Initialize FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay'
        },
        height: 'auto',
        editable: true,
        selectable: true,
        slotMinTime: '08:00:00',
        slotMaxTime: '22:00:00',
        allDaySlot: false,
        events: async function (info, successCallback, failureCallback) {
            try {
                const response = await fetch('/api/schedule');
                const data = await response.json();

                renderWellness(data.breaks, data.conflicts);

                const events = data.tasks.map(task => ({
                    id: task.id,
                    title: task.name,
                    start: task.start_time,
                    end: task.end_time,
                    backgroundColor: '#C1DBE8', // Pastel Blue
                    borderColor: '#C1DBE8',
                    textColor: '#43302E' // Old Burgundy for contrast
                }));
                successCallback(events);
            } catch (error) {
                failureCallback(error);
            }
        },
        eventDrop: function (info) { updateTask(info.event); },
        eventResize: function (info) { updateTask(info.event); },
        eventClick: function (info) {
            openTaskModal(info.event);
        }
    });

    calendar.render();

    // --- Modal Logic ---
    function openTaskModal(event) {
        currentEventId = event.id;
        modalTaskName.textContent = event.title;

        const start = event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const end = event.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        modalTaskTime.textContent = `${start} - ${end}`;

        taskModal.classList.remove('hidden');
    }

    closeModalBtn.addEventListener('click', () => {
        taskModal.classList.add('hidden');
    });

    deleteTaskBtn.addEventListener('click', () => {
        if (currentEventId) {
            if (confirm("Delete this task?")) {
                deleteTask(currentEventId);
                taskModal.classList.add('hidden');
            }
        }
    });

    startFocusBtn.addEventListener('click', () => {
        taskModal.classList.add('hidden');
        startFocusSession(modalTaskName.textContent);
    });

    // --- Timer Logic ---
    function startFocusSession(taskName) {
        focusOverlay.classList.remove('hidden');
        focusTaskName.textContent = `Focusing on: ${taskName}`;
        timeLeft = 25 * 60;
        isPaused = false;
        updateTimerDisplay();

        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(tick, 1000);
        pauseTimerBtn.textContent = '⏸️';
    }

    function tick() {
        if (!isPaused) {
            timeLeft--;
            updateTimerDisplay();
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                alert("Focus session complete! Take a break. ☕");
                focusOverlay.classList.add('hidden');
            }
        }
    }

    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    pauseTimerBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        pauseTimerBtn.textContent = isPaused ? '▶️' : '⏸️';
    });

    stopTimerBtn.addEventListener('click', () => {
        if (confirm("Stop focus session?")) {
            clearInterval(timerInterval);
            focusOverlay.classList.add('hidden');
        }
    });

    // --- Core App Logic ---
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
                calendar.refetchEvents();
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
            calendar.refetchEvents();
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        analyzeBtn.textContent = "Thinking... 🧠";
        analyzeBtn.disabled = true;

        try {
            // Fetch current tasks first
            const scheduleResponse = await fetch('/api/schedule');
            const scheduleData = await scheduleResponse.json();

            const response = await fetch('/api/analyze_wellness', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tasks: scheduleData.tasks })
            });
            const data = await response.json();

            if (data.status === 'success' || data.status === 'mock') {
                wellnessList.innerHTML = `<div class="ai-response">${data.message}</div>`;
            } else {
                alert("Error: " + data.message);
            }
        } catch (error) {
            console.error("Error analyzing wellness:", error);
            alert("Failed to analyze.");
        } finally {
            analyzeBtn.textContent = "🤖 Analyze Day";
            analyzeBtn.disabled = false;
        }
    });

    // --- Posture Guard Logic ---
    const toggleCameraBtn = document.getElementById('toggle-camera-btn');
    const cameraContainer = document.getElementById('camera-container');
    const videoFeed = document.getElementById('video-feed');
    let isCameraOn = false;

    toggleCameraBtn.addEventListener('click', () => {
        isCameraOn = !isCameraOn;

        if (isCameraOn) {
            videoFeed.src = "/video_feed";
            cameraContainer.classList.remove('hidden');
            toggleCameraBtn.textContent = "Disable Camera";
            toggleCameraBtn.classList.replace('primary-btn', 'secondary-btn');
        } else {
            videoFeed.src = "";
            cameraContainer.classList.add('hidden');
            toggleCameraBtn.textContent = "Enable Camera";
            toggleCameraBtn.classList.replace('secondary-btn', 'primary-btn');
        }
    });

    async function updateTask(event) {
        try {
            await fetch(`/api/tasks/${event.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: event.title,
                    start_time: event.start.toISOString(),
                    end_time: event.end.toISOString()
                })
            });
        } catch (error) {
            console.error("Error updating task:", error);
            alert("Failed to update task.");
            info.revert();
        }
    }

    async function deleteTask(id) {
        try {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            calendar.refetchEvents();
        } catch (error) {
            console.error("Error deleting task:", error);
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
