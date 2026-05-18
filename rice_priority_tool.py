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
        
        # Reach
        group_reach = QGroupBox("Охват (Reach)")
        form_reach = QFormLayout()
        self.reach_input = QDoubleSpinBox()
        self.reach_input.setRange(0.1, 1000000)
        self.reach_input.setValue(100)
        self.reach_input.setDecimals(2)
        lbl_reach = QLabel("Сколько пользователей/клиентов затронет проект?")
        lbl_reach.setWordWrap(True)
        form_reach.addRow(lbl_reach, self.reach_input)
        group_reach.setLayout(form_reach)
        
        # Impact
        group_impact = QGroupBox("Влияние (Impact)")
        form_impact = QFormLayout()
        self.impact_input = QDoubleSpinBox()
        self.impact_input.setRange(0.1, 5.0)
        self.impact_input.setValue(1.0)
        self.impact_input.setSingleStep(0.25)
        self.impact_input.setDecimals(2)
        lbl_impact = QLabel("Насколько сильно это повлияет на каждого пользователя?\n(0.25 - минимальное, 0.5 - низкое, 1 - среднее, 2 - высокое, 3 - очень высокое)")
        lbl_impact.setWordWrap(True)
        form_impact.addRow(lbl_impact, self.impact_input)
        group_impact.setLayout(form_impact)
        
        # Confidence
        group_confidence = QGroupBox("Уверенность (Confidence)")
        form_confidence = QFormLayout()
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setRange(0.01, 1.0)
        self.confidence_input.setValue(0.8)
        self.confidence_input.setSingleStep(0.1)
        self.confidence_input.setDecimals(2)
        lbl_confidence = QLabel("Насколько вы уверены в оценках?\n(1.0 - 100% уверенность, 0.8 - 80%, 0.5 - 50%)")
        lbl_confidence.setWordWrap(True)
        form_confidence.addRow(lbl_confidence, self.confidence_input)
        group_confidence.setLayout(form_confidence)
        
        # Effort
        group_effort = QGroupBox("Усилия (Effort)")
        form_effort = QFormLayout()
        self.effort_input = QDoubleSpinBox()
        self.effort_input.setRange(0.1, 10000)
        self.effort_input.setValue(10)
        self.effort_input.setDecimals(2)
        lbl_effort = QLabel("Сколько человеко-месяцев потребуется?\n(или другая единица измерения усилий)")
        lbl_effort.setWordWrap(True)
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
        
        # Value
        group_value = QGroupBox("Ценность (Value)")
        form_value = QFormLayout()
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(1, 10)
        self.value_input.setValue(5)
        self.value_input.setDecimals(1)
        lbl_value = QLabel("Какова ценность проекта для бизнеса?\n(1 - минимальная, 10 - максимальная)")
        lbl_value.setWordWrap(True)
        form_value.addRow(lbl_value, self.value_input)
        group_value.setLayout(form_value)
        
        # Complexity
        group_complexity = QGroupBox("Сложность (Complexity)")
        form_complexity = QFormLayout()
        self.complexity_input = QDoubleSpinBox()
        self.complexity_input.setRange(1, 10)
        self.complexity_input.setValue(5)
        self.complexity_input.setDecimals(1)
        lbl_complexity = QLabel("Какова сложность реализации?\n(1 - очень просто, 10 - очень сложно)")
        lbl_complexity.setWordWrap(True)
        form_complexity.addRow(lbl_complexity, self.complexity_input)
        group_complexity.setLayout(form_complexity)
        
        # Quadrant info
        self.quadrant_label = QLabel("Квадрант: Быстрая победа")
        self.quadrant_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.quadrant_label.setStyleSheet("color: #2ecc71; padding: 10px;")
        
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
        
        # Create tab widget for different views
        tabs = QTabWidget()
        
        # Summary tab
        summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        
        # RICE Score Bar Chart
        self.rice_figure = Figure(figsize=(10, 6))
        self.rice_canvas = FigureCanvas(self.rice_figure)
        summary_layout.addWidget(QLabel("RICE Scores"))
        summary_layout.addWidget(self.rice_canvas)
        
        # Value/Complexity Scatter Plot
        self.vc_figure = Figure(figsize=(10, 6))
        self.vc_canvas = FigureCanvas(self.vc_figure)
        summary_layout.addWidget(QLabel("Value vs Complexity Matrix"))
        summary_layout.addWidget(self.vc_canvas)
        
        summary_widget.setLayout(summary_layout)
        tabs.addTab(summary_widget, "Графики")
        
        # Table tab
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Охват", "Влияние", "Уверенность",
            "Усилия", "RICE", "Ценность", "Сложность", "Квадрант"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        if not self.projects:
            return
        
        # RICE Bar Chart
        self.rice_figure.clear()
        ax1 = self.rice_figure.add_subplot(111)
        
        names = [p[1] for p in self.projects]
        rice_scores = [p[6] for p in self.projects]
        
        colors = plt_colors_for_quadrants([p[9] for p in self.projects])
        
        ax1.bar(range(len(names)), rice_scores, color=colors)
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.set_ylabel('RICE Score')
        ax1.set_title('RICE Scores by Project')
        ax1.grid(axis='y', alpha=0.3)
        self.rice_figure.tight_layout()
        self.rice_canvas.draw()
        
        # Value/Complexity Scatter Plot
        self.vc_figure.clear()
        ax2 = self.vc_figure.add_subplot(111)
        
        values = [p[7] for p in self.projects]
        complexities = [p[8] for p in self.projects]
        quadrants = [p[9] for p in self.projects]
        
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
                           label=quadrant, s=100, edgecolors='black', linewidth=0.5)
                
                # Add labels
                for i, txt in enumerate(labels):
                    ax2.annotate(txt, (x_vals[i], y_vals[i]), fontsize=8, 
                                xytext=(5, 5), textcoords='offset points')
        
        # Add quadrant lines
        ax2.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
        ax2.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('Complexity')
        ax2.set_ylabel('Value')
        ax2.set_title('Value vs Complexity Matrix')
        ax2.set_xlim(0, 11)
        ax2.set_ylim(0, 11)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self.vc_figure.tight_layout()
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
        self.setMinimumSize(1200, 800)
        self.init_ui()
        self.dashboard.load_data()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Input section
        input_group = QGroupBox("Добавить новый проект")
        input_layout = QVBoxLayout()
        
        # Project name
        name_form = QFormLayout()
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Введите название проекта")
        name_form.addRow("Название проекта:", self.project_name_input)
        input_layout.addLayout(name_form)
        
        # RICE and Value/Complexity inputs side by side
        inputs_layout = QHBoxLayout()
        
        self.rice_widget = RICEInputWidget()
        inputs_layout.addWidget(self.rice_widget)
        
        self.vc_widget = ValueComplexityWidget()
        inputs_layout.addWidget(self.vc_widget)
        
        input_layout.addLayout(inputs_layout)
        
        # Save button
        self.save_button = QPushButton("Сохранить проект")
        self.save_button.clicked.connect(self.save_project)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        input_layout.addWidget(self.save_button)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Dashboard section
        self.dashboard = DashboardWidget()
        main_layout.addWidget(self.dashboard)
        
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
