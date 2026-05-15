import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({ baseURL: API_URL });

// Resume
export const uploadResume = (formData) =>
  api.post('/resume/upload-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// Analysis
export const analyzeResume = (data) =>
  api.post('/analysis/analyze-resume', data);

// Report download
export const downloadReport = async (analysisId) => {
  const response = await api.get(`/report/generate-report/${analysisId}`, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = `resume_analysis_${analysisId.slice(0, 8)}.pdf`;
  link.click();
  window.URL.revokeObjectURL(url);
};

export default api;
