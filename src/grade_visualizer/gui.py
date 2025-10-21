from .core import GradeManager, GradeEntry
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox

class GradeVisualizer:
    def __init__(self, manager: GradeManager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Student Grade Visualization")
        self.root.geometry("1000x700")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.update_course_list()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Course selection
        course_frame = ttk.LabelFrame(main_frame, text="Courses", padding="5")
        course_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(course_frame, text="Add Course", command=self.add_course).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(course_frame, text="Remove Course", command=self.remove_course).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(course_frame, text="Save Data", command=self.save_data).pack(side=tk.LEFT)
        
        # Course list
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        ttk.Label(list_frame, text="Select Course:").pack(anchor=tk.W)
        
        self.course_listbox = tk.Listbox(list_frame)
        self.course_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.course_listbox.bind('<<ListboxSelect>>', self.on_course_select)
        
        # Entry management
        entry_frame = ttk.LabelFrame(main_frame, text="Grade Entries", padding="5")
        entry_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.rowconfigure(1, weight=1)
        
        # Add entry form
        form_frame = ttk.Frame(entry_frame)
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.desc_var).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(form_frame, text="Earned:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.earned_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.earned_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(form_frame, text="Total:").grid(row=1, column=1, sticky=tk.W, padx=(80, 5), pady=(5, 0))
        self.total_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.total_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(130, 0), pady=(5, 0))
        
        ttk.Label(form_frame, text="Weight:").grid(row=1, column=1, sticky=tk.W, padx=(210, 5), pady=(5, 0))
        self.weight_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.weight_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(270, 0), pady=(5, 0))
        
        ttk.Button(form_frame, text="Add Entry", command=self.add_entry).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Entries list
        ttk.Label(entry_frame, text="Course Entries:").grid(row=1, column=0, sticky=tk.W)
        
        self.entries_tree = ttk.Treeview(entry_frame, columns=("Description", "Score", "Weight"), show="headings", height=6)
        self.entries_tree.heading("Description", text="Description")
        self.entries_tree.heading("Score", text="Score")
        self.entries_tree.heading("Weight", text="Weight (%)")
        self.entries_tree.column("Description", width=200)
        self.entries_tree.column("Score", width=100)
        self.entries_tree.column("Weight", width=80)
        self.entries_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Remove entry button
        ttk.Button(entry_frame, text="Remove Selected Entry", command=self.remove_entry).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Visualization area
        viz_frame = ttk.LabelFrame(main_frame, text="Grade Visualization", padding="5")
        viz_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.current_course = None

    def update_course_list(self):
        self.course_listbox.delete(0, tk.END)
        for course_name in self.manager.courses:
            self.course_listbox.insert(tk.END, course_name)

    def on_course_select(self, event=None):
        selection = self.course_listbox.curselection()
        if selection:
            course_name = self.course_listbox.get(selection[0])
            self.current_course = self.manager.get_course(course_name)
            self.update_entries_list()
            self.update_visualization()
            self.status_var.set(f"Selected: {course_name} | Weighted Grade: {self.current_course.current_grade:.2f}% | Earned: {self.current_course.earned_percentage:.2f}%")

    def update_entries_list(self):
        # Clear existing items
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        if not self.current_course:
            return
            
        for entry in self.current_course.entries:
            score_text = f"{entry.earned_points}/{entry.total_points} ({entry.percentage:.1f}%)"
            self.entries_tree.insert("", tk.END, values=(entry.description, score_text, f"{entry.weight}%"))

    def update_visualization(self):
        self.ax.clear()
        
        if not self.current_course or not self.current_course.entries:
            self.ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', transform=self.ax.transAxes)
            self.ax.set_title('Grade Visualization')
            self.canvas.draw()
            return
        
        # Prepare data for visualization
        entries = self.current_course.entries
        descriptions = [entry.description[:15] + "..." if len(entry.description) > 15 else entry.description for entry in entries]
        percentages = [entry.percentage for entry in entries]
        weights = [entry.weight for entry in entries]
        current_grade = self.current_course.current_grade
        earned_percentage = self.current_course.earned_percentage
        
        # Scale bar heights according to weights
        scaled_heights = []
        for pct, weight in zip(percentages, weights):
            # Scale height based on weight (0-100% weight maps to 0-1 height multiplier)
            weight_factor = weight / 100 if self.current_course.total_weight > 0 else 0
            scaled_heights.append(pct * weight_factor)
        
        # Create bar chart with scaled heights
        bars = self.ax.bar(range(len(entries)), scaled_heights, color='skyblue', edgecolor='navy', linewidth=0.5)
        
        # Add value labels on bars
        for i, (bar, pct, weight) in enumerate(zip(bars, percentages, weights)):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + max(scaled_heights) * 0.02,
                        f'{pct:.1f}%\n({weight}%)',
                        ha='center', va='bottom', fontsize=9)
        
        # Add weighted average line (Average Performance)
        weighted_line = self.ax.axhline(y=current_grade * max(weights) / 100 if weights else 0, 
                                       color='red', linestyle='--', linewidth=2, 
                                       label=f'Average Performance: {current_grade:.2f}%')
        
        # Add earned percentage line (Pure Grade)
        earned_line = self.ax.axhline(y=earned_percentage * max(weights) / 100 if weights else 0, 
                                     color='green', linestyle='-.', linewidth=2, 
                                     label=f'Pure Grade: {earned_percentage:.2f}%')
        
        # Add legend
        self.ax.legend([weighted_line, earned_line], 
                      [f'Average Performance: {current_grade:.2f}%', f'Pure Grade: {earned_percentage:.2f}%'],
                      loc='upper right')
        
        # Customize chart
        self.ax.set_xlabel('Grade Entries')
        self.ax.set_ylabel('Scaled Percentage')
        self.ax.set_title(f'Grade Visualization - {self.current_course.name}')
        self.ax.set_xticks(range(len(entries)))
        self.ax.set_xticklabels(descriptions, rotation=45, ha='right')
        
        # Set y-axis limit based on maximum scaled value
        max_y = max(max(scaled_heights) * 1.3 if scaled_heights else 0, 
                   current_grade * max(weights) / 100 * 1.1 if weights else 0,
                   earned_percentage * max(weights) / 100 * 1.1 if weights else 0,
                   10)
        self.ax.set_ylim(0, max_y)
        
        self.ax.grid(axis='y', alpha=0.3)
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
        self.canvas.draw()

    def add_course(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Course")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Course Name:").pack(pady=(10, 0))
        name_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def confirm():
            name = name_var.get().strip()
            if name and self.manager.add_course(name):
                self.update_course_list()
                dialog.destroy()
            elif not name:
                messagebox.showerror("Error", "Please enter a course name")
            else:
                messagebox.showerror("Error", "Course already exists")
        
        entry.bind('<Return>', lambda e: confirm())
        ttk.Button(dialog, text="Add", command=confirm).pack(pady=5)

    def remove_course(self):
        selection = self.course_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a course to remove")
            return
            
        course_name = self.course_listbox.get(selection[0])
        if messagebox.askyesno("Confirm", f"Remove course '{course_name}' and all its entries?"):
            self.manager.remove_course(course_name)
            self.update_course_list()
            self.current_course = None
            self.update_entries_list()
            self.update_visualization()
            self.status_var.set("")

    def add_entry(self):
        if not self.current_course:
            messagebox.showwarning("Warning", "Please select a course first")
            return
            
        try:
            description = self.desc_var.get().strip()
            earned = float(self.earned_var.get())
            total = float(self.total_var.get())
            weight = float(self.weight_var.get())
            
            if not description:
                messagebox.showerror("Error", "Please enter a description")
                return
                
            if total <= 0:
                messagebox.showerror("Error", "Total points must be greater than 0")
                return
                
            if weight < 0:
                messagebox.showerror("Error", "Weight cannot be negative")
                return
            
            entry = GradeEntry(description, earned, total, weight)
            self.current_course.add_entry(entry)
            
            # Clear form
            self.desc_var.set("")
            self.earned_var.set("")
            self.total_var.set("")
            self.weight_var.set("")
            
            self.update_entries_list()
            self.update_visualization()
            self.status_var.set(f"Selected: {self.current_course.name} | Weighted Grade: {self.current_course.current_grade:.2f}% | Earned: {self.current_course.earned_percentage:.2f}%")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for earned points, total points, and weight")

    def remove_entry(self):
        if not self.current_course:
            messagebox.showwarning("Warning", "Please select a course first")
            return
            
        selected = self.entries_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry to remove")
            return
            
        item = self.entries_tree.item(selected[0])
        index = self.entries_tree.index(selected[0])
        
        if messagebox.askyesno("Confirm", f"Remove entry '{item['values'][0]}'?"):
            self.current_course.remove_entry(index)
            self.update_entries_list()
            self.update_visualization()
            self.status_var.set(f"Selected: {self.current_course.name} | Weighted Grade: {self.current_course.current_grade:.2f}% | Earned: {self.current_course.earned_percentage:.2f}%")

    def save_data(self):
        self.manager.save_data()
        messagebox.showinfo("Success", "Data saved successfully!")

    def on_closing(self):
        """Handle window closing event"""
        self.manager.save_data()
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    manager = GradeManager()
    app = GradeVisualizer(manager)
    app.run()


if __name__ == "__main__":
    main()
