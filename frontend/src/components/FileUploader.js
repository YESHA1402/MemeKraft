import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FileUploader = ({ type, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = type === 'slides' ? '/upload/slides' : '/upload/notes';
      const response = await axios.post(`${API}${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMessage(`✅ ${response.data.message}`);
      if (onUploadSuccess) onUploadSuccess(response.data);
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-uploader">
      <label className="file-label" htmlFor={`file-${type}`}>
        <div className="upload-box">
          {uploading ? (
            <div className="spinner">⏳ Uploading...</div>
          ) : (
            <>
              <span className="upload-icon">📁</span>
              <span>Click to upload {type === 'slides' ? 'Slides' : 'Notes'}</span>
              <span className="file-types">
                {type === 'slides' ? 'PDF, PPT, DOCX' : 'TXT, PDF, DOCX'}
              </span>
            </>
          )}
        </div>
      </label>
      <input
        id={`file-${type}`}
        type="file"
        accept={type === 'slides' ? '.pdf,.pptx,.docx' : '.txt,.pdf,.docx'}
        onChange={handleFileUpload}
        disabled={uploading}
        style={{ display: 'none' }}
      />
      {message && <div className="upload-message">{message}</div>}
    </div>
  );
};

export default FileUploader;
