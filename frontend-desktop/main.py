"""
Chemical Equipment Parameter Visualizer - Desktop Application
This PyQt5 application connects to a Django backend API to upload CSV files,
analyze equipment data, and generate PDF reports.
"""

# ============================================================================
# IMPORTS - Import all necessary libraries
# ============================================================================

import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QListWidget,
    QScrollArea, QFrame, QSplitter, QListWidgetItem
)
from PyQt5.QtCore import Qt, QEvent
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

API_BASE_URL = 'http://localhost:8000/api'
TOKEN = None

# ============================================================================
# LOGIN WINDOW CLASS
# ============================================================================

class LoginWindow(QWidget):
    """Login Window Class"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Visualizer - Login')
        self.setGeometry(100, 100, 400, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel('Login to Equipment Visualizer')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 18px; font-weight: bold; margin: 20px;')
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def handle_login(self):
        global TOKEN
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            response = requests.post(
                f'{API_BASE_URL}/login/',
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                TOKEN = data['token']
                QMessageBox.information(self, 'Success', f'Welcome, {data["username"]}!')
                self.open_main_window()
            else:
                QMessageBox.warning(self, 'Error', 'Invalid credentials')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Login failed: {str(e)}')
    
    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# ============================================================================
# CHART WIDGET CLASS
# ============================================================================

class ChartCanvas(FigureCanvas):
    """Chart Canvas Widget"""
    
    def __init__(self, parent=None):
        fig = Figure(figsize=(8, 6), facecolor='#2F4F4F')
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
    
    def plot_bar_chart(self, labels, values, title):
        """Plot a Bar Chart"""
        self.axes.clear()
        self.axes.set_facecolor('#2F4F4F')
        self.axes.bar(labels, values, color='skyblue')
        self.axes.set_title(title, color='#FFFFFF', fontsize=14, pad=20)
        self.axes.set_xlabel('Equipment Type', color='#FFFFFF', fontsize=11)
        self.axes.set_ylabel('Count', color='#FFFFFF', fontsize=11)
        self.axes.tick_params(axis='x', colors='#FFFFFF', labelsize=10)
        self.axes.tick_params(axis='y', colors='#FFFFFF', labelsize=10)
        self.axes.spines['bottom'].set_color('#FFFFFF')
        self.axes.spines['left'].set_color('#FFFFFF')
        self.axes.spines['top'].set_color('#FFFFFF')
        self.axes.spines['right'].set_color('#FFFFFF')
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)
        self.figure.tight_layout(pad=3.0)
        self.figure.subplots_adjust(bottom=0.20)
        self.draw()

# ============================================================================
# MAIN WINDOW CLASS
# ============================================================================

class MainWindow(QMainWindow):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        self.current_data = None
        self.zoom_start_width = 800
        self.zoom_start_height = 600
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        header = QLabel('Equipment Parameter Visualizer - Desktop App')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            'font-size: 20px; font-weight: bold; padding: 10px; '
            'background-color: #007bff; color: white;'
        )
        main_layout.addWidget(header)
        
        tabs = QTabWidget()
        upload_tab = self.create_upload_tab()
        tabs.addTab(upload_tab, 'Upload & Analyze')
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, 'History')
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def create_upload_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        upload_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        upload_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton('Browse CSV File')
        browse_btn.clicked.connect(self.browse_file)
        upload_layout.addWidget(browse_btn)
        
        upload_btn = QPushButton('Upload & Analyze')
        upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(upload_btn)
        
        layout.addLayout(upload_layout)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet("""
            QSplitter::handle { background-color: #007bff; border: 1px solid #0056b3; }
            QSplitter::handle:hover { background-color: #0056b3; }
        """)
        
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel('Upload a CSV file to see statistics')
        self.stats_label.setStyleSheet(
            'padding: 20px; background-color: #2F4F4F; border-radius: 5px; color: white;'
        )
        stats_layout.addWidget(self.stats_label)
        stats_widget.setLayout(stats_layout)
        splitter.addWidget(stats_widget)
        
        chart_widget = QWidget()
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_frame = QFrame()
        chart_frame.setStyleSheet("QFrame { background-color: #2F4F4F; border-radius: 8px; }")
        chart_frame_layout = QVBoxLayout()
        chart_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chart_scroll = QScrollArea()
        self.chart_scroll.setWidgetResizable(False)
        self.chart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chart_scroll.setStyleSheet("QScrollArea { background-color: #2F4F4F; border: none; }")
        
        self.chart = ChartCanvas(self)
        self.chart_base_width = 800
        self.chart_base_height = 600
        self.chart.setMinimumSize(self.chart_base_width, self.chart_base_height)
        self.chart.grabGesture(Qt.PinchGesture)
        self.chart.installEventFilter(self)
        self.chart_scroll.setWidget(self.chart)
        
        chart_frame_layout.addWidget(self.chart_scroll)
        chart_frame.setLayout(chart_frame_layout)
        chart_layout.addWidget(chart_frame)
        chart_widget.setLayout(chart_layout)
        splitter.addWidget(chart_widget)
        
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("background-color: #2F4F4F; color: white;")
        table_layout.addWidget(self.data_table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)
        
        splitter.setSizes([150, 600, 250])
        layout.addWidget(splitter)
        
        self.pdf_btn = QPushButton('Download PDF Report')
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)
        layout.addWidget(self.pdf_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        refresh_btn = QPushButton('Load Upload History')
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.download_history_pdf)
        layout.addWidget(self.history_list)
        
        info_label = QLabel('Double-click on an item to download its PDF report')
        info_label.setStyleSheet('color: gray; font-style: italic;')
        layout.addWidget(info_label)
        
        widget.setLayout(layout)
        return widget
    
    def eventFilter(self, obj, event):
        if obj == self.chart and event.type() == QEvent.Gesture:
            gesture = event.gesture(Qt.PinchGesture)
            if gesture:
                if gesture.state() == Qt.GestureStarted:
                    self.zoom_start_width = self.chart.width()
                    self.zoom_start_height = self.chart.height()
                elif gesture.state() == Qt.GestureUpdated or gesture.state() == Qt.GestureFinished:
                    scale_factor = gesture.totalScaleFactor()
                    new_width = int(self.zoom_start_width * scale_factor)
                    new_height = int(self.zoom_start_height * scale_factor)
                    new_width = max(new_width, self.chart_base_width)
                    new_height = max(new_height, self.chart_base_height)
                    new_width = min(new_width, 3000)
                    new_height = min(new_height, 3000)
                    self.chart.resize(new_width, new_height)
                    self.chart.setMinimumSize(new_width, new_height)
                return True
        return super().eventFilter(obj, event)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '', 'CSV Files (*.csv);;All Files (*)'
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
    
    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, 'Error', 'Please select a CSV file first')
            return
        try:
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                headers = {'Authorization': f'Token {TOKEN}'}
                response = requests.post(f'{API_BASE_URL}/upload/', files=files, headers=headers)
            if response.status_code == 201:
                self.current_data = response.json()
                self.display_results()
                QMessageBox.information(self, 'Success', 'CSV uploaded and analyzed successfully!')
            else:
                QMessageBox.warning(self, 'Error', f'Upload failed: {response.text}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Upload error: {str(e)}')
    
    def display_results(self):
        data = self.current_data
        type_dist = data['type_distribution']
        type_dist_html = ""
        for equip_type, count in type_dist.items():
            type_dist_html += f"<li style='color: white;'>{equip_type}: {count}</li>"
        
        stats_text = f"""
        <h3 style='color: white;'>Analysis Results</h3>
        <p style='color: white;'><b>Total Equipment:</b> {data['total_count']}</p>
        <p style='color: white;'><b>Average Flowrate:</b> {data['averages']['flowrate']:.2f}</p>
        <p style='color: white;'><b>Average Pressure:</b> {data['averages']['pressure']:.2f}</p>
        <p style='color: white;'><b>Average Temperature:</b> {data['averages']['temperature']:.2f}</p>
        <p style='color: white; margin-top: 15px;'><b>Equipment Type Distribution:</b></p>
        <ul style='color: white; margin-left: 20px;'>{type_dist_html}</ul>
        """
        self.stats_label.setText(stats_text)
        
        self.chart.plot_bar_chart(
            list(type_dist.keys()),
            list(type_dist.values()),
            'Equipment Type Distribution'
        )
        
        equipment_data = data['data']
        self.data_table.setRowCount(len(equipment_data))
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(
            ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        )
        
        for i, item in enumerate(equipment_data):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(item['Equipment Name'])))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(item['Type'])))
            self.data_table.setItem(i, 2, QTableWidgetItem(str(item['Flowrate'])))
            self.data_table.setItem(i, 3, QTableWidgetItem(str(item['Pressure'])))
            self.data_table.setItem(i, 4, QTableWidgetItem(str(item['Temperature'])))
        
        self.data_table.resizeColumnsToContents()
        self.pdf_btn.setEnabled(True)
    
    def download_pdf(self):
        if not self.current_data:
            return
        try:
            dataset_id = self.current_data['id']
            headers = {'Authorization': f'Token {TOKEN}'}
            response = requests.get(f'{API_BASE_URL}/report/{dataset_id}/', headers=headers)
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF Report', f'report_{dataset_id}.pdf', 'PDF Files (*.pdf)'
                )
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', f'PDF saved to {file_path}')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'PDF download error: {str(e)}')
    
    def load_history(self):
        try:
            headers = {'Authorization': f'Token {TOKEN}'}
            response = requests.get(f'{API_BASE_URL}/history/', headers=headers)
            if response.status_code == 200:
                history = response.json()
                self.history_list.clear()
                self.history_data = history
                if not history:
                    self.history_list.addItem('No upload history yet')
                else:
                    for item in history:
                        summary = item['summary']
                        type_dist = summary['type_distribution']
                        type_dist_str = ', '.join([f"{k}: {v}" for k, v in type_dist.items()])
                        history_text = (
                            f"ID: {item['id']} | {item['filename']} | {item['upload_date'][:10]}\n"
                            f"   Total: {summary['total_count']} | "
                            f"Avg Flow: {summary['avg_flowrate']} | "
                            f"Avg Press: {summary['avg_pressure']} | "
                            f"Avg Temp: {summary['avg_temperature']}\n"
                            f"   Types: {type_dist_str}"
                        )
                        list_item = QListWidgetItem(history_text)
                        list_item.setData(Qt.UserRole, item['id'])
                        self.history_list.addItem(list_item)
            else:
                QMessageBox.warning(self, 'Error', 'Failed to load history')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'History error: {str(e)}')
    
    def download_history_pdf(self, item):
        try:
            dataset_id = item.data(Qt.UserRole)
            if dataset_id is None:
                return
            headers = {'Authorization': f'Token {TOKEN}'}
            response = requests.get(f'{API_BASE_URL}/report/{dataset_id}/', headers=headers)
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF Report', f'report_{dataset_id}.pdf', 'PDF Files (*.pdf)'
                )
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF downloaded successfully')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Download error: {str(e)}')

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
