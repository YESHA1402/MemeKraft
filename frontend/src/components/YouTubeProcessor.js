import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const YouTubeProcessor = ({ onProcessSuccess }) => {
  const [url, setUrl] = useState('');
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState('');

  const handleProcess = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setProcessing(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('youtube_url', url);

      const response = await axios.post(`${API}/youtube/process`, formData);
      setMessage(`✅ ${response.data.message}`);
      if (onProcessSuccess) onProcessSuccess(response.data);
      setUrl('');
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="youtube-processor">
      <form onSubmit={handleProcess}>
        <div className="input-group">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter YouTube video or playlist URL"
            disabled={processing}
            className="youtube-input"
          />
          <button
            type="submit"
            disabled={processing || !url.trim()}
            className="process-btn"
            data-testid="youtube-process-btn"
          >
            {processing ? '⏳ Processing...' : '🎬 Process YouTube'}
          </button>
        </div>
      </form>
      {message && <div className="process-message">{message}</div>}
    </div>
  );
};

export default YouTubeProcessor;
