

# **Chemical Equipment Parameter Visualizer 🧪**

A full-stack web and desktop application for analyzing chemical equipment parameters with data visualization, PDF reporting, and historical data management.

***

## **📋 Table of Contents**

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Guide](#usage-guide)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

***

## **🎯 Overview**

The Chemical Equipment Parameter Visualizer is a comprehensive solution for analyzing equipment data from CSV files. It provides statistical analysis, interactive charts, and professional PDF reports for chemical engineering applications.

**Project Components:**
- **Django Backend API** - RESTful API for data processing and storage
- **React Web Frontend** - Modern web interface
- **PyQt5 Desktop App** - Standalone desktop application

***

## **✨ Features**

- ✅ **CSV Upload & Analysis** - Upload equipment data and get instant analysis
- ✅ **Statistical Summaries** - Total count, averages, type distribution
- ✅ **Data Visualization** - Interactive bar charts with Chart.js
- ✅ **PDF Report Generation** - Professional reports with ReportLab
- ✅ **History Management** - Store and retrieve last 5 uploads
- ✅ **User Authentication** - Token-based secure authentication
- ✅ **Desktop & Web Access** - Multiple platform support
- ✅ **Responsive Design** - Works on desktop and mobile

***

## **🛠 Tech Stack**

### **Backend (Django)**
- Python 3.8+
- Django 4.x
- Django REST Framework
- ReportLab (PDF generation)
- Pandas (data processing)
- SQLite/PostgreSQL

### **Frontend (React)**
- React 18
- Chart.js & react-chartjs-2
- Axios
- CSS3

### **Desktop (PyQt5)**
- Python 3.8+
- PyQt5
- Matplotlib
- Requests

***

## **📁 Project Structure**

```
chemical-equipment-app/
├── backend/                  # Django backend
│   ├── api/                 # API app
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API views
│   │   ├── serializers.py   # DRF serializers
│   │   └── urls.py          # API routes
│   ├── backend/             # Django settings
│   ├── manage.py
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js           # Main app component
│   │   ├── api.js           # API client
│   │   └── App.css          # Styles
│   ├── public/
│   └── package.json         # Node dependencies
│
├── frontend-desktop/        # PyQt5 desktop app
│   └── main.py              # Desktop application
│
├── sample_equipment_data.csv # Sample data
└── README.md                # This file
```

***

## **⚙️ Prerequisites**

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **pip** (comes with Python)
- **npm** (comes with Node.js)

***

## **🚀 Installation & Setup**

### **1. Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/chemical-equipment-app.git
cd chemical-equipment-app
```

### **2. Backend Setup (Django)**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create username/password

# Start Django server
python manage.py runserver
```

**Backend will run on:** `http://localhost:8000`

### **3. Frontend Setup (React)**

Open a **new terminal window:**

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start React development server
npm start
```

**Frontend will run on:** `http://localhost:3000`

### **4. Desktop App Setup (PyQt5)**

Open a **new terminal window:**

```bash
# Navigate to desktop app directory
cd frontend-desktop

# Install PyQt5 dependencies
pip install PyQt5 matplotlib pandas requests

# Run desktop application
python main.py
```

***

## **▶️ Running the Application**

### **Start All Services:**

1. **Terminal 1 - Django Backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Terminal 2 - React Frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Terminal 3 - Desktop App (Optional):**
   ```bash
   cd frontend-desktop
   python main.py
   ```

***

## **📡 API Endpoints**

### **Authentication**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login/` | POST | User login, returns token |

### **Data Management**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/` | POST | Upload CSV file for analysis |
| `/api/history/` | GET | Get last 5 uploads with summaries |
| `/api/report/<id>/` | GET | Download PDF report for dataset |

### **Example API Request:**

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Response:
{
  "token": "abc123xyz...",
  "username": "admin"
}

# Upload CSV
curl -X POST http://localhost:8000/api/upload/ \
  -H "Authorization: Token abc123xyz..." \
  -F "file=@sample_equipment_data.csv"
```

***

## **📖 Usage Guide**

### **Web Application:**

1. **Login** - Use your superuser credentials
2. **Upload CSV** - Select a CSV file with columns: `Equipment Name`, `Type`, `Flowrate`, `Pressure`, `Temperature`
3. **View Analysis** - See statistics, charts, and data table
4. **Download PDF** - Generate professional report
5. **Check History** - View past uploads

### **Desktop Application:**

1. **Login** - Same credentials as web
2. **Upload & Analyze Tab** - Upload CSV and view results
3. **History Tab** - View and download past reports
4. **Pinch Zoom** - Use trackpad gestures to zoom charts
5. **Resizable Sections** - Drag blue bars to resize sections

***

## **📊 Sample CSV Format**

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Valve-1,Valve,95,8.4,95
Compressor-1,Compressor,150,12.5,140
```

***

## **🖼️ Screenshots**

*(Add screenshots of your application here)*

***

## **🤝 Contributing**

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

***

## **📝 License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

## **👨‍💻 Author**

**Your Name**
- GitHub: [@your_username](https://github.com/your_username)
- Email: your.email@example.com

***

## **🙏 Acknowledgments**

- FOSSEE for project inspiration
- Django REST Framework documentation
- React community
- PyQt5 contributors

***

## **⚠️ Troubleshooting**

### Common Issues:

**1. Port already in use:**
```bash
# Change Django port
python manage.py runserver 8001

# Change React port
PORT=3001 npm start
```

**2. Migration errors:**
```bash
python manage.py migrate --run-syncdb
```

**3. Module not found:**
```bash
pip install -r requirements.txt --force-reinstall
```

***

**Happy Coding! 🚀**
