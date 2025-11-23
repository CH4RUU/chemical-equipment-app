import React, { useState } from 'react';
import { uploadCSV, getHistory, downloadPDF } from './api';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';


ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function Dashboard({ onLogout }) {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a CSV file');
      return;
    }

    setLoading(true);
    try {
      const result = await uploadCSV(file);
      setData(result);
      alert('CSV uploaded successfully!');
    } catch (err) {
      alert('Error uploading file: ' + err.message);
    }
    setLoading(false);
  };

  const handleGetHistory = async () => {
    setLoading(true);
    try {
      const result = await getHistory();
      setHistory(result);
    } catch (err) {
      alert('Error fetching history: ' + err.message);
    }
    setLoading(false);
  };

  const handleDownloadPDF = async (datasetId) => {
    try {
      const blob = await downloadPDF(datasetId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${datasetId}.pdf`;
      a.click();
    } catch (err) {
      alert('Error downloading PDF: ' + err.message);
    }
  };


  const chartData = data ? {
    labels: Object.keys(data.type_distribution),
    datasets: [
      {
        label: 'Equipment Count by Type',
        data: Object.values(data.type_distribution),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  } : null;

  return (
    <div className="dashboard">
      <div className="header">
        <h2>Equipment Parameter Visualizer</h2>
        <div>
          <span>Welcome, {localStorage.getItem('username')}</span>
          <button onClick={onLogout}>Logout</button>
        </div>
      </div>

      <div className="upload-section">
        <h3>Upload CSV File</h3>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      {data && (
        <div className="results">
          <h3>Analysis Results</h3>
          <div className="stats">
            <p><strong>Total Equipment:</strong> {data.total_count}</p>
            <p><strong>Average Flowrate:</strong> {data.averages.flowrate.toFixed(2)}</p>
            <p><strong>Average Pressure:</strong> {data.averages.pressure.toFixed(2)}</p>
            <p><strong>Average Temperature:</strong> {data.averages.temperature.toFixed(2)}</p>
          </div>

          {/* NEW: Equipment Type Distribution */}
          {data.type_distribution && (
            <div className="type-distribution">
              <h3>Equipment Type Distribution:</h3>
              <ul>
                {Object.entries(data.type_distribution).map(([type, count]) => (
                  <li key={type}>
                    <strong>{type}:</strong> {count}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {chartData && (
            <div className="chart">
              <Bar data={chartData} options={{ responsive: true }} />
            </div>
          )}

          <div className="data-table">
            <h4>Equipment Data</h4>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Flowrate</th>
                  <th>Pressure</th>
                  <th>Temperature</th>
                </tr>
              </thead>
              <tbody>
                {data.data.map((item, index) => (
                  <tr key={index}>
                    <td>{item['Equipment Name']}</td>
                    <td>{item.Type}</td>
                    <td>{item.Flowrate}</td>
                    <td>{item.Pressure}</td>
                    <td>{item.Temperature}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button onClick={() => handleDownloadPDF(data.id)}>
            Download PDF Report
          </button>
        </div>
      )}

      <div className="history-section">
        <h3>Upload History</h3>
        <button onClick={handleGetHistory} disabled={loading}>
          Load History
        </button>
        {history.length > 0 && (
          <ul>
            {history.map((item) => (
              <li key={item.id}>
                {item.filename} - {new Date(item.upload_date).toLocaleString()}
                <button onClick={() => handleDownloadPDF(item.id)}>
                  Download PDF
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
