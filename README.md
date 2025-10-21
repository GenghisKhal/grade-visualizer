# Student Grade Visualizer

A desktop application to track, manage, and visualize student grades with weighted categories.

## Features
- Add/remove courses
- Add grade entries with earned/total points and weights
- Real-time grade calculation
- Interactive bar chart visualization
- Automatic JSON data persistence

## Installation

### From Source
```bash
git clone https://github.com/GenghisKhal/grade-visualizer.git
cd grade-visualizer
pip install -e .
```

## Data Storage

Your grade data is automatically saved to your system's application data directory:

- **Windows**: `%APPDATA%\grade-visualizer\grades.json`
  - Full path: `C:\Users\[YourUsername]\AppData\Roaming\grade-visualizer\grades.json`
- **macOS**: `~/Library/Application Support/grade-visualizer/grades.json`
- **Linux**: `~/.local/share/grade-visualizer/grades.json`
