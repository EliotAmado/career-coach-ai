import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [career, setCareer] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);

  const tips = [
    "Tip: Tailor your resume for each job application.",
    "Tip: Build projects to showcase your skills.",
    "Tip: Network with people in your target industry.",
    "Tip: Stay updated on industry trends.",
    "Tip: Practice interview questions regularly."
  ];

  useEffect(() => {
    if (loading) {
      const tipInterval = setInterval(() => {
        setTipIndex((prev) => (prev + 1) % tips.length);
      }, 3000); // Rotate tips every 3 seconds
      return () => clearInterval(tipInterval);
    }
  }, [loading, tips.length]);

  const handleSubmit = async () => {
    if (!career.trim()) return;
    setLoading(true);
    setProgress(0);

    let progressValue = 0;
    let interval = setInterval(() => {
      progressValue += Math.max(1, (100 - progressValue) * 0.08); 
      if (progressValue >= 95) {
        progressValue = 95;
        clearInterval(interval);
      }
      setProgress(progressValue);
    }, 500);

    try {
      const response = await axios.post('http://localhost:8000/chat', null, {
        params: { career },
      });
      setSummary(response.data.summary);
    } catch (err) {
      setSummary("⚠️ Something went wrong. Please try again.");
    } finally {
      clearInterval(interval);
      setProgress(100);
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
      }, 500);
    }
  };

  return (
    <div className="container">
      <h1>🎓 Career Coach AI</h1>
      <input
        type="text"
        placeholder="Enter a career (e.g. Data Analyst)"
        value={career}
        onChange={(e) => setCareer(e.target.value)}
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Fetching Insights...' : 'Get Career Insights'}
      </button>

      {loading && (
        <div>
          <div className="loading-container">
            <div className="loading-bar" style={{ width: `${progress}%` }}></div>
          </div>
          <p>Analyzing {career || 'career'}... {Math.round(progress)}%</p>
          <p className='loading-tip'>{tips[tipIndex]}</p>
        </div>
      )}

      <div className="markdown">
        <ReactMarkdown>{summary}</ReactMarkdown>
      </div>
    </div>
  );
}

export default App;
