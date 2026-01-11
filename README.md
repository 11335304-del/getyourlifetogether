# 🚀 Antigravity Planner

Welcome to your AI-powered Smart Scheduler! This project helps you organize your tasks, detects conflicts, and suggests breaks.

## 📂 Project Structure
- `app.py`: The main server for the Web App.
- `scheduler.py`: The core logic (parsing, conflict detection).
- `all_in_one_schedule.py`: A standalone script for the Terminal (CLI).
- `templates/`: Contains the HTML for the website.
- `static/`: Contains the CSS (styling) and JS (interactivity).

## 🛠️ How to Run in VS Code

### Option 1: The Web App (Recommended)
This gives you the beautiful "Glassmorphism" UI.

1.  **Open the Terminal** in VS Code (View > Terminal, or press `Ctrl+` `).
2.  **Install Flask** (if you haven't already):
    ```bash
    pip install flask
    ```
3.  **Run the App**:
    ```bash
    python app.py
    ```
4.  **Open in Browser**:
    You will see a message like `Running on http://127.0.0.1:5000`.
    Hold `Cmd` (Mac) or `Ctrl` (Windows) and click that link, or type it into Chrome/Safari.

### Option 2: The Interactive CLI
This runs directly in the text terminal.

1.  **Run the Script**:
    ```bash
    python all_in_one_schedule.py
    ```
2.  **Type your tasks**:
    e.g., `Tomorrow 10am Math Quiz`
3.  **Type `report`** to see your schedule.

## ❓ Troubleshooting
- **"Module not found: flask"**: Run `pip install flask` again.
- **"Address already in use"**: Another program is using port 5000. Try stopping other python processes or restart VS Code.
# getyourlifetogether
