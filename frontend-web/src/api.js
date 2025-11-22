import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Get token from localStorage
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      'Authorization': `Token ${token}`
    }
  };
};

// Login API
export const login = async (username, password) => {
  const response = await axios.post(`${API_BASE_URL}/login/`, {
    username,
    password
  });
  return response.data;
};

// Upload CSV API
export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(
    `${API_BASE_URL}/upload/`,
    formData,
    getAuthHeaders()
  );
  return response.data;
};

// Get History API
export const getHistory = async () => {
  const response = await axios.get(
    `${API_BASE_URL}/history/`,
    getAuthHeaders()
  );
  return response.data;
};

// Download PDF API
export const downloadPDF = async (datasetId) => {
  const response = await axios.get(
    `${API_BASE_URL}/report/${datasetId}/`,
    {
      ...getAuthHeaders(),
      responseType: 'blob'
    }
  );
  return response.data;
};
