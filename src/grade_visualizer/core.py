from platformdirs import user_data_dir
from pathlib import Path
import json
import os
from typing import Dict, List


class GradeEntry:
    def __init__(self, description: str, earned_points: float, total_points: float, weight: float):
        self.description = description
        self.earned_points = earned_points
        self.total_points = total_points
        self.weight = weight

    @property
    def percentage(self) -> float:
        if self.total_points == 0:
            return 0
        return (self.earned_points / self.total_points) * 100

    def to_dict(self) -> Dict:
        return {
            "description": self.description,
            "earned_points": self.earned_points,
            "total_points": self.total_points,
            "weight": self.weight
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            data["description"],
            data["earned_points"],
            data["total_points"],
            data["weight"]
        )

class Course:
    def __init__(self, name: str):
        self.name = name
        self.entries: List[GradeEntry] = []

    def add_entry(self, entry: GradeEntry):
        self.entries.append(entry)

    def remove_entry(self, index: int) -> bool:
        if 0 <= index < len(self.entries):
            self.entries.pop(index)
            return True
        return False

    @property
    def total_weight(self) -> float:
        return sum(entry.weight for entry in self.entries)

    @property
    def current_grade(self) -> float:
        if not self.entries:
            return 0
        total_weighted_points = sum(
            (entry.earned_points / entry.total_points) * entry.weight
            for entry in self.entries
            if entry.total_points > 0
        )
        if self.total_weight == 0:
            return 0
        return (total_weighted_points / self.total_weight) * 100

    @property
    def earned_percentage(self) -> float:
        """Percentage of total grade earned so far (sum of weighted scores)"""
        if not self.entries:
            return 0
        earned_weighted_points = sum(
            (entry.earned_points / entry.total_points) * entry.weight
            for entry in self.entries
            if entry.total_points > 0
        )
        return earned_weighted_points

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "entries": [entry.to_dict() for entry in self.entries]
        }

    @classmethod
    def from_dict(cls, data: Dict):
        course = cls(data["name"])
        course.entries = [GradeEntry.from_dict(entry_data) for entry_data in data["entries"]]
        return course

class GradeManager:
    def __init__(self, filename: str = "grades.json"):
        self.data_dir = Path(user_data_dir("grade-visualizer"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filename = self.data_dir / filename
        self.courses: Dict[str, Course] = {}
        self.load_data()

    def add_course(self, course_name: str) -> bool:
        if course_name in self.courses:
            return False
        self.courses[course_name] = Course(course_name)
        return True

    def remove_course(self, course_name: str) -> bool:
        if course_name in self.courses:
            del self.courses[course_name]
            return True
        return False

    def get_course(self, course_name: str) -> Course:
        return self.courses.get(course_name)

    def save_data(self):
        data = {name: course.to_dict() for name, course in self.courses.items()}
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            self.courses = {
                name: Course.from_dict(course_data)
                for name, course_data in data.items()
            }
        except (json.JSONDecodeError, KeyError):
            print("Error loading data. Starting with empty gradebook.")
