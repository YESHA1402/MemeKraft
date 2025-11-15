import React, { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import FileUploader from "@/components/FileUploader";
import YouTubeProcessor from "@/components/YouTubeProcessor";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [languages, setLanguages] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [generationMode, setGenerationMode] = useState('full');
  const [useUploadedContent, setUseUploadedContent] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [generating, setGenerating] = useState(false);
  const [bookId, setBookId] = useState(null);
  const [message, setMessage] = useState('');
  const [chapterNumber, setChapterNumber] = useState(1);
  const [chapterTitle, setChapterTitle] = useState('');
  const [chapterContent, setChapterContent] = useState('');

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API}/languages`);
      setLanguages(response.data.languages);
    } catch (error) {
      console.error('Error fetching languages:', error);
    }
  };

  const handleGenerateBook = async () => {
    setGenerating(true);
    setMessage('🎬 Generating your Bollywood-style book... This may take a few minutes!');
    setBookId(null);

    try {
      const response = await axios.post(`${API}/generate/book`, {
        language: selectedLanguage,
        generation_mode: generationMode,
        use_uploaded_content: useUploadedContent,
        youtube_url: youtubeUrl || null
      });

      setBookId(response.data.book_id);
      setMessage('✅ Book generated successfully! Download below.');
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateChapter = async () => {
    if (!chapterTitle.trim()) {
      setMessage('❌ Please enter a chapter title');
      return;
    }

    setGenerating(true);
    setMessage('🎬 Generating chapter...');
    setChapterContent('');

    try {
      const response = await axios.post(`${API}/generate/chapter`, {
        language: selectedLanguage,
        chapter_number: chapterNumber,
        chapter_title: chapterTitle,
        use_uploaded_content: useUploadedContent
      });

      setChapterContent(response.data.content);
      setMessage('✅ Chapter generated successfully!');
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (format) => {
    if (!bookId) return;
    window.open(`${API}/download/${format}/${bookId}`, '_blank');
  };

  return (
    <div className="App">
      <header className="app-header" data-testid="app-header">
        <h1 className="title">🎬 Bollywood Cloud Computing Book Generator</h1>
        <p className="subtitle">Generate fun, meme-rich Cloud Computing books in 10+ languages!</p>
      </header>

      <main className="main-content">
        {/* Upload Section */}
        <section className="section upload-section" data-testid="upload-section">
          <h2>📚 Step 1: Upload Your Materials (Optional)</h2>
          <div className="upload-grid">
            <FileUploader 
              type="slides" 
              onUploadSuccess={(data) => console.log('Slides uploaded:', data)} 
            />
            <FileUploader 
              type="notes" 
              onUploadSuccess={(data) => console.log('Notes uploaded:', data)} 
            />
          </div>
          <div className="youtube-section">
            <h3>🎥 Or Add YouTube Content</h3>
            <YouTubeProcessor 
              onProcessSuccess={(data) => setYoutubeUrl(data.url)} 
            />
          </div>
        </section>

        {/* Generation Settings */}
        <section className="section settings-section" data-testid="settings-section">
          <h2>⚙️ Step 2: Configure Your Book</h2>
          
          <div className="setting-group">
            <label htmlFor="language-select">🌐 Language:</label>
            <select 
              id="language-select"
              value={selectedLanguage} 
              onChange={(e) => setSelectedLanguage(e.target.value)}
              disabled={generating}
              data-testid="language-select"
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="mode-select">📖 Generation Mode:</label>
            <select 
              id="mode-select"
              value={generationMode} 
              onChange={(e) => setGenerationMode(e.target.value)}
              disabled={generating}
              data-testid="mode-select"
            >
              <option value="full">Full 60-Page Book</option>
              <option value="chapter">Chapter by Chapter</option>
            </select>
          </div>

          <div className="setting-group checkbox-group">
            <label>
              <input 
                type="checkbox" 
                checked={useUploadedContent}
                onChange={(e) => setUseUploadedContent(e.target.checked)}
                disabled={generating}
                data-testid="use-content-checkbox"
              />
              Use my uploaded slides/notes/YouTube content
            </label>
          </div>
        </section>

        {/* Generation Controls */}
        <section className="section generation-section" data-testid="generation-section">
          <h2>🎯 Step 3: Generate Your Book</h2>
          
          {generationMode === 'full' ? (
            <div className="full-book-generation">
              <button 
                onClick={handleGenerateBook}
                disabled={generating}
                className="generate-btn primary-btn"
                data-testid="generate-book-btn"
              >
                {generating ? '⏳ Generating...' : '🎬 Generate Full Book (60 pages)'}
              </button>
              <p className="info-text">⚠️ Full book generation takes 3-5 minutes</p>
            </div>
          ) : (
            <div className="chapter-generation">
              <div className="chapter-inputs">
                <input 
                  type="number" 
                  min="1" 
                  value={chapterNumber}
                  onChange={(e) => setChapterNumber(parseInt(e.target.value))}
                  placeholder="Chapter #"
                  disabled={generating}
                  className="chapter-number-input"
                  data-testid="chapter-number-input"
                />
                <input 
                  type="text" 
                  value={chapterTitle}
                  onChange={(e) => setChapterTitle(e.target.value)}
                  placeholder="Enter chapter title"
                  disabled={generating}
                  className="chapter-title-input"
                  data-testid="chapter-title-input"
                />
                <button 
                  onClick={handleGenerateChapter}
                  disabled={generating || !chapterTitle.trim()}
                  className="generate-btn primary-btn"
                  data-testid="generate-chapter-btn"
                >
                  {generating ? '⏳ Generating...' : '📝 Generate Chapter'}
                </button>
              </div>
            </div>
          )}

          {message && (
            <div className={`message ${message.includes('❌') ? 'error' : 'success'}`} data-testid="status-message">
              {message}
            </div>
          )}
        </section>

        {/* Chapter Preview */}
        {chapterContent && (
          <section className="section preview-section" data-testid="chapter-preview">
            <h2>📄 Chapter Preview</h2>
            <div className="chapter-preview">
              <pre>{chapterContent}</pre>
            </div>
          </section>
        )}

        {/* Download Section */}
        {bookId && (
          <section className="section download-section" data-testid="download-section">
            <h2>⬇️ Download Your Book</h2>
            <div className="download-buttons">
              <button 
                onClick={() => handleDownload('pdf')}
                className="download-btn pdf-btn"
                data-testid="download-pdf-btn"
              >
                📕 Download PDF
              </button>
              <button 
                onClick={() => handleDownload('docx')}
                className="download-btn docx-btn"
                data-testid="download-docx-btn"
              >
                📘 Download DOCX
              </button>
              <button 
                onClick={() => handleDownload('md')}
                className="download-btn md-btn"
                data-testid="download-md-btn"
              >
                📗 Download Markdown
              </button>
            </div>
          </section>
        )}

        {/* Features Section */}
        <section className="section features-section">
          <h2>✨ Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">🎭</span>
              <h3>Bollywood Style</h3>
              <p>Memes, dialogues & filmy references</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">📚</span>
              <h3>Academically Accurate</h3>
              <p>100% correct Cloud Computing concepts</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🌍</span>
              <h3>10 Languages</h3>
              <p>Hindi, Tamil, Telugu, Gujarati & more</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🎬</span>
              <h3>Comic Format</h3>
              <p>Visual descriptions & funny dialogues</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <p>Made with ❤️ for B.Tech CSE Students | Powered by AI</p>
      </footer>
    </div>
  );
}

export default App;
