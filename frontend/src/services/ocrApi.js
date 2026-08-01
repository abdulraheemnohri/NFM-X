import axios from 'axios';
import { apiClient, configureApi, handleApiError } from './api';

const ocrApi = {
  processDocument: (data, config = {}) => apiClient.post('/api/ocr/document', data, config).catch(handleApiError),
  processImage: (imageFile, options = {}) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    if (options.engine) formData.append('engine', options.engine);
    if (options.language) formData.append('language', options.language);
    return apiClient.post('/api/ocr/image', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).catch(handleApiError);
  },
  processPDF: (pdfFile, options = {}) => {
    const formData = new FormData();
    formData.append('pdf', pdfFile);
    if (options.engine) formData.append('engine', options.engine);
    return apiClient.post('/api/ocr/pdf', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).catch(handleApiError);
  },
  getEngines: () => apiClient.get('/api/ocr/engines').catch(handleApiError),
  getLanguages: (engineName) => apiClient.get(/api/ocr/engines/ + engineName + /languages/).catch(handleApiError),
  getResult: (documentId) => apiClient.get(/api/ocr/results/ + documentId).catch(handleApiError),
  listDocuments: (params = {}) => apiClient.get('/api/ocr/documents', { params }).catch(handleApiError),
  deleteDocument: (documentId) => apiClient.delete(/api/ocr/documents/ + documentId).catch(handleApiError),
  processScreenshot: (imageFile, options = {}) => ocrApi.processImage(imageFile, { ...options, preprocess: true })
};

export default ocrApi;

// Urdu: NFM-X OCR API Service