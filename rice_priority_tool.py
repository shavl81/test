#!/usr/bin/env python3
"""
RICE + Value/Complexity Priority Tool
Desktop application for project prioritization using RICE scoring and Value/Complexity matrix.
"""

import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QPushButton,
    QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QScrollArea, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Database setup
DB_NAME = "priority_projects.db"

def init_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reach REAL NOT NULL,
            impact REAL NOT NULL,
            confidence REAL NOT NULL,
            effort REAL NOT NULL,
            rice_score REAL NOT NULL,
            value REAL NOT NULL,
            complexity REAL NOT NULL,
            quadrant TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_project(name, reach, impact, confidence, effort, rice_score, 
                 value, complexity, quadrant):
    """Save a project to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO projects 
        (name, reach, impact, confidence, effort, rice_score, 
         value, complexity, quadrant, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, reach, impact, confidence, effort, rice_score,
          value, complexity, quadrant, now, now))
    
    conn.commit()
    conn.close()

def update_project(project_id, name, reach, impact, confidence, effort, 
                   rice_score, value, complexity, quadrant):
    """Update an existing project in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        UPDATE projects SET
            name = ?, reach = ?, impact = ?, confidence = ?, effort = ?,
            rice_score = ?, value = ?, complexity = ?, quadrant = ?,
            updated_at = ?
        WHERE id = ?
    ''', (name, reach, impact, confidence, effort, rice_score,
          value, complexity, quadrant, now, project_id))
    
    conn.commit()
    conn.close()

def get_all_projects():
    """Retrieve all projects from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = cursor.fetchall()
    
    conn.close()
    return projects

def delete_project(project_id):
    """Delete a project from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    
    conn.commit()
    conn.close()


class RICEInputWidget(QWidget):
    """Widget for collecting RICE scoring inputs."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        
        # Reach
        group_reach = QGroupBox("Охват (Reach)")
        group_reach.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_reach = QFormLayout()
        form_reach.setSpacing(2)
        self.reach_input = QDoubleSpinBox()
        self.reach_input.setFont(QFont("Arial", 9))
        self.reach_input.setRange(0.1, 1000000)
        self.reach_input.setValue(100)
        self.reach_input.setDecimals(2)
        lbl_reach = QLabel("Сколько пользователей/клиентов затронет проект?")
        lbl_reach.setWordWrap(True)
        lbl_reach.setFont(QFont("Arial", 8))
        form_reach.addRow(lbl_reach, self.reach_input)
        group_reach.setLayout(form_reach)
        
        # Impact
        group_impact = QGroupBox("Влияние (Impact)")
        group_impact.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_impact = QFormLayout()
        form_impact.setSpacing(2)
        self.impact_input = QDoubleSpinBox()
        self.impact_input.setFont(QFont("Arial", 9))
        self.impact_input.setRange(0.1, 5.0)
        self.impact_input.setValue(1.0)
        self.impact_input.setSingleStep(0.25)
        self.impact_input.setDecimals(2)
        lbl_impact = QLabel("Насколько сильно это повлияет на каждого пользователя?\n(0.25 - минимальное, 0.5 - низкое, 1 - среднее, 2 - высокое, 3 - очень высокое)")
        lbl_impact.setWordWrap(True)
        lbl_impact.setFont(QFont("Arial", 8))
        form_impact.addRow(lbl_impact, self.impact_input)
        group_impact.setLayout(form_impact)
        
        # Confidence
        group_confidence = QGroupBox("Уверенность (Confidence)")
        group_confidence.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_confidence = QFormLayout()
        form_confidence.setSpacing(2)
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setFont(QFont("Arial", 9))
        self.confidence_input.setRange(0.01, 1.0)
        self.confidence_input.setValue(0.8)
        self.confidence_input.setSingleStep(0.1)
        self.confidence_input.setDecimals(2)
        lbl_confidence = QLabel("Насколько вы уверены в оценках?\n(1.0 - 100% уверенность, 0.8 - 80%, 0.5 - 50%)")
        lbl_confidence.setWordWrap(True)
        lbl_confidence.setFont(QFont("Arial", 8))
        form_confidence.addRow(lbl_confidence, self.confidence_input)
        group_confidence.setLayout(form_confidence)
        
        # Effort
        group_effort = QGroupBox("Усилия (Effort)")
        group_effort.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_effort = QFormLayout()
        form_effort.setSpacing(2)
        self.effort_input = QDoubleSpinBox()
        self.effort_input.setFont(QFont("Arial", 9))
        self.effort_input.setRange(0.1, 10000)
        self.effort_input.setValue(10)
        self.effort_input.setDecimals(2)
        lbl_effort = QLabel("Сколько человеко-месяцев потребуется?\n(или другая единица измерения усилий)")
        lbl_effort.setWordWrap(True)
        lbl_effort.setFont(QFont("Arial", 8))
        form_effort.addRow(lbl_effort, self.effort_input)
        group_effort.setLayout(form_effort)
        
        layout.addWidget(group_reach)
        layout.addWidget(group_impact)
        layout.addWidget(group_confidence)
        layout.addWidget(group_effort)
        
        self.setLayout(layout)
    
    def calculate_rice(self):
        """Calculate RICE score: (Reach × Impact × Confidence) / Effort"""
        reach = self.reach_input.value()
        impact = self.impact_input.value()
        confidence = self.confidence_input.value()
        effort = self.effort_input.value()
        
        if effort == 0:
            return 0
        
        rice_score = (reach * impact * confidence) / effort
        return rice_score
    
    def get_values(self):
        """Return all RICE values."""
        return {
            'reach': self.reach_input.value(),
            'impact': self.impact_input.value(),
            'confidence': self.confidence_input.value(),
            'effort': self.effort_input.value(),
            'rice_score': self.calculate_rice()
        }


class ValueComplexityWidget(QWidget):
    """Widget for collecting Value/Complexity inputs."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        
        # Value
        group_value = QGroupBox("Ценность (Value)")
        group_value.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_value = QFormLayout()
        form_value.setSpacing(2)
        self.value_input = QDoubleSpinBox()
        self.value_input.setFont(QFont("Arial", 9))
        self.value_input.setRange(1, 10)
        self.value_input.setValue(5)
        self.value_input.setDecimals(1)
        lbl_value = QLabel("Какова ценность проекта для бизнеса?\n(1 - минимальная, 10 - максимальная)")
        lbl_value.setWordWrap(True)
        lbl_value.setFont(QFont("Arial", 8))
        form_value.addRow(lbl_value, self.value_input)
        group_value.setLayout(form_value)
        
        # Complexity
        group_complexity = QGroupBox("Сложность (Complexity)")
        group_complexity.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        form_complexity = QFormLayout()
        form_complexity.setSpacing(2)
        self.complexity_input = QDoubleSpinBox()
        self.complexity_input.setFont(QFont("Arial", 9))
        self.complexity_input.setRange(1, 10)
        self.complexity_input.setValue(5)
        self.complexity_input.setDecimals(1)
        lbl_complexity = QLabel("Какова сложность реализации?\n(1 - очень просто, 10 - очень сложно)")
        lbl_complexity.setWordWrap(True)
        lbl_complexity.setFont(QFont("Arial", 8))
        form_complexity.addRow(lbl_complexity, self.complexity_input)
        group_complexity.setLayout(form_complexity)
        
        # Quadrant info
        self.quadrant_label = QLabel("Квадрант: Быстрая победа")
        self.quadrant_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.quadrant_label.setStyleSheet("color: #2ecc71; padding: 5px;")
        self.quadrant_label.setWordWrap(True)
        
        layout.addWidget(group_value)
        layout.addWidget(group_complexity)
        layout.addWidget(self.quadrant_label)
        
        self.setLayout(layout)
        
        # Connect signals
        self.value_input.valueChanged.connect(self.update_quadrant)
        self.complexity_input.valueChanged.connect(self.update_quadrant)
        
        self.update_quadrant()
    
    def update_quadrant(self):
        """Determine quadrant based on value and complexity."""
        value = self.value_input.value()
        complexity = self.complexity_input.value()
        
        mid_value = 5
        mid_complexity = 5
        
        if value >= mid_value and complexity < mid_complexity:
            quadrant = "Быстрая победа"
            color = "#2ecc71"  # Green
        elif value >= mid_value and complexity >= mid_complexity:
            quadrant = "Стратегическая инициатива"
            color = "#3498db"  # Blue
        elif value < mid_value and complexity < mid_complexity:
            quadrant = "Заполнитель"
            color = "#f39c12"  # Orange
        else:
            quadrant = "Избегать"
            color = "#e74c3c"  # Red
        
        self.quadrant_label.setText(f"Квадрант: {quadrant}")
        self.quadrant_label.setStyleSheet(f"color: {color}; padding: 10px; font-weight: bold;")
    
    def get_values(self):
        """Return value, complexity and quadrant."""
        value = self.value_input.value()
        complexity = self.complexity_input.value()
        
        mid_value = 5
        mid_complexity = 5
        
        if value >= mid_value and complexity < mid_complexity:
            quadrant = "Быстрая победа"
        elif value >= mid_value and complexity >= mid_complexity:
            quadrant = "Стратегическая инициатива"
        elif value < mid_value and complexity < mid_complexity:
            quadrant = "Заполнитель"
        else:
            quadrant = "Избегать"
        
        return {
            'value': value,
            'complexity': complexity,
            'quadrant': quadrant
        }


class DashboardWidget(QWidget):
    """Widget for displaying dashboard with charts and tables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tab widget for different views
        tabs = QTabWidget()
        tabs.setDocumentMode(True)  # More compact tab style
        
        # Summary tab - with scroll area for small screens
        summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(5, 5, 5, 5)
        summary_layout.setSpacing(5)
        
        # RICE Score Bar Chart - smaller default size
        self.rice_figure = Figure(figsize=(6, 4), dpi=100)
        self.rice_canvas = FigureCanvas(self.rice_figure)
        self.rice_canvas.setMinimumHeight(200)
        rice_label = QLabel("RICE Scores")
        rice_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        summary_layout.addWidget(rice_label)
        summary_layout.addWidget(self.rice_canvas)
        
        # Value/Complexity Scatter Plot - smaller default size
        self.vc_figure = Figure(figsize=(6, 4), dpi=100)
        self.vc_canvas = FigureCanvas(self.vc_figure)
        self.vc_canvas.setMinimumHeight(200)
        vc_label = QLabel("Value vs Complexity Matrix")
        vc_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        summary_layout.addWidget(vc_label)
        summary_layout.addWidget(self.vc_canvas)
        
        # Add stretch to allow scrolling
        summary_layout.addStretch()
        
        # Wrap in scroll area for small screens
        summary_content = QWidget()
        summary_content.setLayout(summary_layout)
        summary_scroll = QScrollArea()
        summary_scroll.setWidget(summary_content)
        summary_scroll.setWidgetResizable(True)
        summary_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        summary_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        tabs.addTab(summary_scroll, "Графики")
        
        # Table tab - with scroll area
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Охват", "Влияние", "Уверенность",
            "Усилия", "RICE", "Ценность", "Сложность", "Квадрант"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(28)  # Smaller row height
        self.table.setFont(QFont("Arial", 9))  # Smaller font
        table_layout.addWidget(self.table)
        
        table_widget.setLayout(table_layout)
        tabs.addTab(table_widget, "Таблица")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def load_data(self):
        """Load and display project data."""
        self.projects = get_all_projects()
        self.update_table()
        self.update_charts()
    
    def update_table(self):
        """Update the table with project data."""
        self.table.setRowCount(len(self.projects))
        
        for row, project in enumerate(self.projects):
            proj_id, name, reach, impact, confidence, effort, rice_score, \
                value, complexity, quadrant, created_at, updated_at = project
            
            self.table.setItem(row, 0, QTableWidgetItem(str(proj_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{reach:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{impact:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{confidence:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{effort:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{rice_score:.2f}"))
            self.table.setItem(row, 7, QTableWidgetItem(f"{value:.2f}"))
            self.table.setItem(row, 8, QTableWidgetItem(f"{complexity:.2f}"))
            self.table.setItem(row, 9, QTableWidgetItem(quadrant))
    
    def update_charts(self):
        """Update charts with project data."""
        # RICE Bar Chart - always draw, even if empty
        self.rice_figure.clear()
        ax1 = self.rice_figure.add_subplot(111)
        
        if self.projects:
            names = [p[1] for p in self.projects]
            rice_scores = [p[6] for p in self.projects]
            
            colors = plt_colors_for_quadrants([p[9] for p in self.projects])
            
            ax1.bar(range(len(names)), rice_scores, color=colors)
            ax1.set_xticks(range(len(names)))
            # Adjust rotation based on number of projects
            rotation = 45 if len(names) <= 5 else 60
            ax1.set_xticklabels(names, rotation=rotation, ha='right', fontsize=8)
            ax1.set_ylabel('RICE Score', fontsize=9)
            ax1.set_title('RICE Scores', fontsize=10, pad=5)
            ax1.grid(axis='y', alpha=0.3)
            ax1.tick_params(axis='both', which='major', labelsize=8)
        else:
            ax1.text(0.5, 0.5, 'Нет данных для отображения\nДобавьте первый проект', 
                    ha='center', va='center', fontsize=10, transform=ax1.transAxes)
            ax1.set_ylabel('RICE Score', fontsize=9)
            ax1.set_title('RICE Scores', fontsize=10, pad=5)
            ax1.set_xticks([])
            ax1.set_yticks([])
        
        self.rice_figure.tight_layout(pad=1.0)
        self.rice_canvas.draw()
        
        # Value/Complexity Scatter Plot - always draw, even if empty
        self.vc_figure.clear()
        ax2 = self.vc_figure.add_subplot(111)
        
        if self.projects:
            values = [p[7] for p in self.projects]
            complexities = [p[8] for p in self.projects]
            quadrants = [p[9] for p in self.projects]
            names = [p[1] for p in self.projects]
            
            quadrant_colors = {
                "Быстрая победа": "#2ecc71",
                "Стратегическая инициатива": "#3498db",
                "Заполнитель": "#f39c12",
                "Избегать": "#e74c3c"
            }
            
            for quadrant in quadrant_colors.keys():
                x_vals = [complexities[i] for i, q in enumerate(quadrants) if q == quadrant]
                y_vals = [values[i] for i, q in enumerate(quadrants) if q == quadrant]
                labels = [names[i] for i, q in enumerate(quadrants) if q == quadrant]
                
                if x_vals:
                    ax2.scatter(x_vals, y_vals, c=[quadrant_colors[quadrant]], 
                               label=quadrant, s=80, edgecolors='black', linewidth=0.5)
                    
                    # Add labels with smaller font
                    for i, txt in enumerate(labels):
                        ax2.annotate(txt, (x_vals[i], y_vals[i]), fontsize=7, 
                                    xytext=(3, 3), textcoords='offset points')
        else:
            ax2.text(0.5, 0.5, 'Нет данных для отображения\nДобавьте первый проект', 
                    ha='center', va='center', fontsize=10, transform=ax2.transAxes)
            ax2.set_xticks([])
            ax2.set_yticks([])
        
        # Add quadrant lines (always show)
        ax2.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
        ax2.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('Complexity', fontsize=9)
        ax2.set_ylabel('Value', fontsize=9)
        ax2.set_title('Value vs Complexity', fontsize=10, pad=5)
        ax2.set_xlim(0, 11)
        ax2.set_ylim(0, 11)
        
        if self.projects:
            ax2.legend(fontsize=8, loc='best')
        
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='both', which='major', labelsize=8)
        self.vc_figure.tight_layout(pad=1.0)
        self.vc_canvas.draw()


def plt_colors_for_quadrants(quadrants):
    """Map quadrants to colors for matplotlib."""
    quadrant_colors = {
        "Быстрая победа": "#2ecc71",
        "Стратегическая инициатива": "#3498db",
        "Заполнитель": "#f39c12",
        "Избегать": "#e74c3c"
    }
    return [quadrant_colors.get(q, "#95a5a6") for q in quadrants]


class EditProjectDialog(QDialog):
    """Dialog for editing project data."""
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setWindowTitle("Редактировать проект")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Project name
        form_name = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setText(self.project_data[1])
        form_name.addRow("Название проекта:", self.name_input)
        layout.addLayout(form_name)
        
        # RICE inputs
        self.rice_widget = RICEInputWidget()
        self.rice_widget.reach_input.setValue(self.project_data[2])
        self.rice_widget.impact_input.setValue(self.project_data[3])
        self.rice_widget.confidence_input.setValue(self.project_data[4])
        self.rice_widget.effort_input.setValue(self.project_data[5])
        layout.addWidget(self.rice_widget)
        
        # Value/Complexity inputs
        self.vc_widget = ValueComplexityWidget()
        self.vc_widget.value_input.setValue(self.project_data[7])
        self.vc_widget.complexity_input.setValue(self.project_data[8])
        layout.addWidget(self.vc_widget)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_updated_data(self):
        """Return updated project data."""
        rice_data = self.rice_widget.get_values()
        vc_data = self.vc_widget.get_values()
        
        return {
            'id': self.project_data[0],
            'name': self.name_input.text(),
            'reach': rice_data['reach'],
            'impact': rice_data['impact'],
            'confidence': rice_data['confidence'],
            'effort': rice_data['effort'],
            'rice_score': rice_data['rice_score'],
            'value': vc_data['value'],
            'complexity': vc_data['complexity'],
            'quadrant': vc_data['quadrant']
        }


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RICE + Value/Complexity Priority Tool")
        # Set smaller minimum size for small screens
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)  # Default size that works on most screens
        self.init_ui()
        self.dashboard.load_data()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create vertical splitter to separate input/charts from table
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: horizontal splitter for input (left) and charts (right)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Input form
        input_group = QGroupBox("Добавить новый проект")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(5)
        
        # Project name
        name_form = QFormLayout()
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Введите название проекта")
        self.project_name_input.setFont(QFont("Arial", 9))
        name_form.addRow("Название проекта:", self.project_name_input)
        input_layout.addLayout(name_form)
        
        # RICE inputs
        self.rice_widget = RICEInputWidget()
        input_layout.addWidget(self.rice_widget)
        
        # Value/Complexity inputs
        self.vc_widget = ValueComplexityWidget()
        input_layout.addWidget(self.vc_widget)
        
        # Save button - smaller
        self.save_button = QPushButton("Сохранить проект")
        self.save_button.clicked.connect(self.save_project)
        self.save_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        input_layout.addWidget(self.save_button)
        
        input_group.setLayout(input_layout)
        
        # Wrap input in scroll area for very small screens
        input_scroll = QScrollArea()
        input_scroll.setWidget(input_group)
        input_scroll.setWidgetResizable(True)
        input_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        input_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        input_scroll.setMinimumWidth(300)
        
        # Right side: Charts (graphs only, no table)
        charts_widget = QWidget()
        charts_layout = QVBoxLayout()
        charts_layout.setContentsMargins(5, 5, 5, 5)
        charts_layout.setSpacing(5)
        
        # RICE Score Bar Chart
        self.charts_rice_figure = Figure(figsize=(5, 3), dpi=100)
        self.charts_rice_canvas = FigureCanvas(self.charts_rice_figure)
        self.charts_rice_canvas.setMinimumHeight(150)
        rice_label = QLabel("RICE Scores")
        rice_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        charts_layout.addWidget(rice_label)
        charts_layout.addWidget(self.charts_rice_canvas)
        
        # Value/Complexity Scatter Plot
        self.charts_vc_figure = Figure(figsize=(5, 3), dpi=100)
        self.charts_vc_canvas = FigureCanvas(self.charts_vc_figure)
        self.charts_vc_canvas.setMinimumHeight(150)
        vc_label = QLabel("Value vs Complexity Matrix")
        vc_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        charts_layout.addWidget(vc_label)
        charts_layout.addWidget(self.charts_vc_canvas)
        
        charts_layout.addStretch()
        charts_widget.setLayout(charts_layout)
        
        # Wrap charts in scroll area
        charts_scroll = QScrollArea()
        charts_scroll.setWidget(charts_widget)
        charts_scroll.setWidgetResizable(True)
        charts_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        charts_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        charts_scroll.setMinimumWidth(300)
        
        # Add widgets to top splitter
        top_splitter.addWidget(input_scroll)
        top_splitter.addWidget(charts_scroll)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        # Set initial split position (40% input, 60% charts)
        top_splitter.setSizes([400, 600])
        
        # Bottom section: Table
        table_group = QGroupBox("Все проекты")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        self.dashboard = DashboardWidget()
        # Hide the tabs since we're showing charts separately
        # Just show the table directly
        table_widget = self.dashboard.table
        table_layout.addWidget(table_widget)
        table_group.setLayout(table_layout)
        
        # Add sections to main splitter
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(table_group)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        # Set initial split position (65% top, 35% table)
        main_splitter.setSizes([500, 250])
        
        main_layout.addWidget(main_splitter)
        
        central_widget.setLayout(main_layout)
        
        # Menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Файл")
        
        refresh_action = file_menu.addAction("Обновить данные")
        refresh_action.triggered.connect(lambda: self.dashboard.load_data())
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        
        # Actions menu
        actions_menu = menubar.addMenu("Действия")
        
        edit_action = actions_menu.addAction("Редактировать выбранный")
        edit_action.triggered.connect(self.edit_selected_project)
        
        delete_action = actions_menu.addAction("Удалить выбранный")
        delete_action.triggered.connect(self.delete_selected_project)
    
    def save_project(self):
        """Save a new project to the database."""
        name = self.project_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название проекта!")
            return
        
        rice_data = self.rice_widget.get_values()
        vc_data = self.vc_widget.get_values()
        
        save_project(
            name=name,
            reach=rice_data['reach'],
            impact=rice_data['impact'],
            confidence=rice_data['confidence'],
            effort=rice_data['effort'],
            rice_score=rice_data['rice_score'],
            value=vc_data['value'],
            complexity=vc_data['complexity'],
            quadrant=vc_data['quadrant']
        )
        
        QMessageBox.information(self, "Успех", f"Проект '{name}' успешно сохранен!")
        
        # Clear inputs
        self.project_name_input.clear()
        self.rice_widget.reach_input.setValue(100)
        self.rice_widget.impact_input.setValue(1.0)
        self.rice_widget.confidence_input.setValue(0.8)
        self.rice_widget.effort_input.setValue(10)
        self.vc_widget.value_input.setValue(5)
        self.vc_widget.complexity_input.setValue(5)
        
        # Refresh dashboard
        self.dashboard.load_data()
        self.update_charts()
    
    def update_charts(self):
        """Update the charts in the main window."""
        projects = get_all_projects()
        
        if not projects:
            return
        
        # Update RICE chart
        self.charts_rice_figure.clear()
        ax1 = self.charts_rice_figure.add_subplot(111)
        ax1.clear()
        
        names = [p[1][:15] + '...' if len(p[1]) > 15 else p[1] for p in projects]
        rice_scores = [p[6] for p in projects]
        
        colors = ['#3498db'] * len(names)
        ax1.bar(range(len(names)), rice_scores, color=colors)
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
        ax1.set_ylabel('RICE Score', fontsize=8)
        ax1.set_title('RICE Scores by Project', fontsize=9)
        ax1.tick_params(axis='y', labelsize=7)
        ax1.grid(axis='y', alpha=0.3)
        self.charts_rice_figure.tight_layout(pad=1.0)
        self.charts_rice_canvas.draw()
        
        # Update Value/Complexity chart
        self.charts_vc_figure.clear()
        ax2 = self.charts_vc_figure.add_subplot(111)
        ax2.clear()
        
        values = [p[7] for p in projects]
        complexities = [p[8] for p in projects]
        quadrants = [p[9] for p in projects]
        scatter_colors = plt_colors_for_quadrants(quadrants)
        
        for i, (val, comp, name) in enumerate(zip(values, complexities, names)):
            ax2.scatter(comp, val, c=[scatter_colors[i]], s=100, alpha=0.7, 
                       edgecolors='black', linewidth=0.5)
            ax2.annotate(name, (comp, val), fontsize=6, ha='center', va='bottom')
        
        ax2.axhline(y=5, color='gray', linestyle='--', linewidth=0.5)
        ax2.axvline(x=5, color='gray', linestyle='--', linewidth=0.5)
        ax2.set_xlabel('Complexity', fontsize=8)
        ax2.set_ylabel('Value', fontsize=8)
        ax2.set_title('Value vs Complexity Matrix', fontsize=9)
        ax2.set_xlim(0, 11)
        ax2.set_ylim(0, 11)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='both', which='major', labelsize=7)
        self.charts_vc_figure.tight_layout(pad=1.0)
        self.charts_vc_canvas.draw()
    
    def edit_selected_project(self):
        """Edit the selected project from the table."""
        current_row = self.dashboard.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для редактирования!")
            return
        
        project_data = self.dashboard.projects[current_row]
        
        dialog = EditProjectDialog(project_data, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_updated_data()
            
            update_project(
                project_id=updated_data['id'],
                name=updated_data['name'],
                reach=updated_data['reach'],
                impact=updated_data['impact'],
                confidence=updated_data['confidence'],
                effort=updated_data['effort'],
                rice_score=updated_data['rice_score'],
                value=updated_data['value'],
                complexity=updated_data['complexity'],
                quadrant=updated_data['quadrant']
            )
            
            QMessageBox.information(self, "Успех", "Проект успешно обновлен!")
            self.dashboard.load_data()
            self.update_charts()
    
    def delete_selected_project(self):
        """Delete the selected project from the table."""
        current_row = self.dashboard.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для удаления!")
            return
        
        project_data = self.dashboard.projects[current_row]
        project_name = project_data[1]
        project_id = project_data[0]
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить проект '{project_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            delete_project(project_id)
            QMessageBox.information(self, "Успех", "Проект успешно удален!")
            self.dashboard.load_data()
            self.update_charts()


def main():
    # Initialize database
    init_database()
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
