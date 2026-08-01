import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box, Typography, Paper, Button, Card, CardContent, CardHeader, Grid,
  LinearProgress, Chip, Divider, IconButton, Tooltip, Alert, Dialog,
  DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  Image as ImageIcon,
  PictureAsPdf as PictureAsPdfIcon,
  CameraAlt as CameraAltIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import ocrApi from '../services/ocrApi';
import { handleApiError } from '../services/api';

function OCRPage({ apiUrl }) {
  const { t } = useTranslation();
  const [engines, setEngines] = useState([]);
  const [selectedEngine, setSelectedEngine] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const fileInputRef = useRef(null);
  const pdfInputRef = useRef(null);

  useEffect(() => {
    fetchEngines();
    fetchDocuments();
  }, [apiUrl]);

  const fetchEngines = async () => {
    try {
      setLoading(true);
      const response = await ocrApi.getEngines();
      setEngines(response.data || []);
      if (response.data && response.data.length > 0) {
        setSelectedEngine(response.data[0].name);
      }
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await ocrApi.listDocuments({ limit: 20 });
      setDocuments(response.data || []);
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file, type) => {
    try {
      setLoading(true);
      setError(null);
      let response;
      if (type === 'image') {
        response = await ocrApi.processImage(file, { engine: selectedEngine });
      } else if (type === 'pdf') {
        response = await ocrApi.processPDF(file, { engine: selectedEngine });
      }
      if (response.data) {
        fetchDocuments();
        setSelectedDocument(response.data);
        setPreviewOpen(true);
      }
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = (type) => {
    if (type === 'image') fileInputRef.current.click();
    else if (type === 'pdf') pdfInputRef.current.click();
    else if (type === 'screenshot') screenshotInputRef.current.click();
  };

  const handleFileChange = (event, type) => {
    const file = event.target.files[0];
    if (file) handleFileUpload(file, type);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('ocr_title')}
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchDocuments} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {loading && <LinearProgress />}
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title={t('ocr_upload')} />
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" onClick={() => handleUploadClick('image')} startIcon={<ImageIcon />}>
                {t('ocr_upload_image')}
              </Button>
              <input type="file" ref={fileInputRef} onChange={(e) => handleFileChange(e, 'image')} accept="image/*" style={{ display: 'none' }} />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" onClick={() => handleUploadClick('pdf')} startIcon={<PictureAsPdfIcon />}>
                {t('ocr_upload_pdf')}
              </Button>
              <input type="file" ref={pdfInputRef} onChange={(e) => handleFileChange(e, 'pdf')} accept=".pdf" style={{ display: 'none' }} />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" onClick={() => handleUploadClick('screenshot')} startIcon={<CameraAltIcon />}>
                {t('ocr_upload_screenshot')}
              </Button>
              <input type="file" ref={screenshotInputRef} onChange={(e) => handleFileChange(e, 'image')} accept="image/*" capture="environment" style={{ display: 'none' }} />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="contained" color="primary" onClick={() => setSettingsOpen(true)} startIcon={<SettingsIcon />}>
                {t('ocr_settings')}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card elevation={2}>
        <CardHeader title={t('ocr_documents')} />
        <CardContent>
          {documents.length === 0 ? (
            <Typography variant="body2" color="text.secondary" textAlign="center" p={3}>
              {t('ocr_no_documents')}
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {documents.map((doc) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={doc.document_id}>
                  <Card elevation={1}>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom noWrap>
                        {doc.file_name || doc.document_id}
                      </Typography>
                      <Chip label={doc.engine || 'unknown'} size="small" color="primary" sx={{ mr: 1, mb: 1 }} />
                      <Chip label={doc.language || 'en'} size="small" color="secondary" sx={{ mr: 1, mb: 1 }} />
                      <Typography variant="caption" color="text.secondary" display="block">
                        {formatDate(doc.created_at)}
                      </Typography>
                      <Divider sx={{ my: 1 }} />
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Tooltip title="View">
                          <IconButton size="small" onClick={() => { setSelectedDocument(doc); setPreviewOpen(true); }} color="primary">
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>

      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>OCR Result Preview</DialogTitle>
        <DialogContent dividers>
          {selectedDocument && (
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                {selectedDocument.file_name || selectedDocument.document_id}
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, maxHeight: '400px', overflow: 'auto', whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                {selectedDocument.text || 'No text extracted'}
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)} color="primary">Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>OCR Settings</DialogTitle>
        <DialogContent dividers>
          <Typography>OCR Engine Settings</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)} color="primary">Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default OCRPage;

// Urdu: NFM-X OCR Page
// یہ NFM-X کے لیے OCR پیج ہے