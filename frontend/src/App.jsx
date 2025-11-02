import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, MessageSquare, Download, CheckCircle, AlertCircle } from 'lucide-react';

const LegalDocumentApp = () => {
  const [file, setFile] = useState(null);
  const [placeholders, setPlaceholders] = useState([]);
  const [currentStep, setCurrentStep] = useState('upload');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [completedDoc, setCompletedDoc] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);

  const API_BASE = 'http://localhost:8000';

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.docx')) {
      setError('Please upload a .docx file');
      return;
    }

    setFile(uploadedFile);
    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setPlaceholders(data.placeholders);
      setCurrentStep('conversation');
      
      const initialMessage = data.placeholders.length > 0
        ? `I've analyzed your document and found ${data.placeholders.length} placeholders to fill. Let's complete them one by one.\n\n${data.placeholders[0].question}`
        : "I've analyzed your document but couldn't find any placeholders to fill.";
      
      setConversationHistory([
        {
          role: 'assistant',
          message: initialMessage
        }
      ]);
    } catch (err) {
      setError('Failed to process document. Make sure the backend is running at http://localhost:8000');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    const newHistory = [
      ...conversationHistory,
      { role: 'user', message: userInput }
    ];
    setConversationHistory(newHistory);
    setUserInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userInput,
          conversation_history: newHistory
        }),
      });

      if (!response.ok) throw new Error('Chat failed');

      const data = await response.json();
      
      setConversationHistory([
        ...newHistory,
        { role: 'assistant', message: data.response }
      ]);

      if (data.all_filled) {
        setTimeout(() => {
          setCurrentStep('review');
          generateDocument(newHistory);
        }, 1000);
      }
    } catch (err) {
      setError('Failed to send message. Check console for details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateDocument = async (history = conversationHistory) => {
    try {
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_history: history
        }),
      });

      if (!response.ok) throw new Error('Generation failed');

      const blob = await response.blob();
      setCompletedDoc(URL.createObjectURL(blob));
    } catch (err) {
      setError('Failed to generate document');
      console.error(err);
    }
  };

  const handleDownload = () => {
    if (completedDoc) {
      const a = document.createElement('a');
      a.href = completedDoc;
      a.download = 'completed_document.docx';
      a.click();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="w-full max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
            <div className="flex items-center gap-3">
              <FileText size={32} />
              <div>
                <h1 className="text-2xl font-bold">Legal Document Assistant</h1>
                <p className="text-blue-100 text-sm">Upload, Complete, Download</p>
              </div>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="bg-gray-50 px-6 py-4 border-b">
            <div className="flex items-center justify-between max-w-2xl mx-auto">
              <div className={`flex items-center gap-2 ${currentStep === 'upload' ? 'text-blue-600 font-semibold' : 'text-gray-400'}`}>
                <Upload size={20} />
                <span className="text-sm">Upload</span>
              </div>
              <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
              <div className={`flex items-center gap-2 ${currentStep === 'conversation' ? 'text-blue-600 font-semibold' : 'text-gray-400'}`}>
                <MessageSquare size={20} />
                <span className="text-sm">Complete</span>
              </div>
              <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
              <div className={`flex items-center gap-2 ${currentStep === 'review' ? 'text-blue-600 font-semibold' : 'text-gray-400'}`}>
                <CheckCircle size={20} />
                <span className="text-sm">Download</span>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
              <AlertCircle size={20} />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Content Area */}
          <div className="p-6">
            {currentStep === 'upload' && (
              <div className="text-center py-12 max-w-2xl mx-auto">
                <div className="mb-6">
                  <FileText size={64} className="mx-auto text-gray-400" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Upload Your Legal Document</h2>
                <p className="text-gray-600 mb-6">
                  Upload a .docx file with placeholders like [Company Name], [Date], etc.
                </p>
                <label className="inline-block">
                  <input
                    type="file"
                    accept=".docx"
                    onChange={handleFileUpload}
                    className="hidden"
                    disabled={loading}
                  />
                  <div className="px-6 py-3 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition">
                    {loading ? 'Processing...' : 'Choose File'}
                  </div>
                </label>
                {file && <p className="mt-4 text-sm text-gray-600">Selected: {file.name}</p>}
              </div>
            )}

            {currentStep === 'conversation' && (
              <div className="space-y-4 max-w-4xl mx-auto">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <strong>Document:</strong> {file?.name}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    {placeholders.length} placeholders found
                  </p>
                </div>

                <div className="border rounded-lg h-96 overflow-y-auto p-4 bg-gray-50">
                  {conversationHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-400">
                      <p>Loading conversation...</p>
                    </div>
                  ) : (
                    conversationHistory.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-md px-4 py-3 rounded-lg whitespace-pre-wrap ${
                            msg.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-white border border-gray-200 text-gray-800'
                          }`}
                        >
                          {msg.message}
                        </div>
                      </div>
                    ))
                  )}
                  {loading && (
                    <div className="flex justify-start mb-4">
                      <div className="bg-white border border-gray-200 px-4 py-3 rounded-lg">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your answer..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={loading || !userInput.trim()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition font-medium"
                  >
                    Send
                  </button>
                </div>
              </div>
            )}

            {currentStep === 'review' && (
              <div className="text-center py-12 max-w-2xl mx-auto">
                <div className="mb-6">
                  <CheckCircle size={64} className="mx-auto text-green-500" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Document Complete!</h2>
                <p className="text-gray-600 mb-6">
                  Your document has been filled with all the provided information.
                </p>
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                >
                  <Download size={20} />
                  Download Document
                </button>
                <div className="mt-4">
                  <button
                    onClick={() => {
                      setCurrentStep('upload');
                      setFile(null);
                      setPlaceholders([]);
                      setConversationHistory([]);
                      setCompletedDoc(null);
                      setError('');
                    }}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Start Over
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Info Card */}
        <div className="mt-6 bg-white rounded-lg shadow p-6 text-sm text-gray-600">
          <p className="font-semibold mb-3 text-gray-800">How it works:</p>
          <ol className="list-decimal list-inside space-y-2">
            <li>Upload your legal document template (.docx format)</li>
            <li>The system identifies placeholders like [Company Name], [Date], etc.</li>
            <li>Have a conversation to fill in each placeholder</li>
            <li>Download your completed document</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default LegalDocumentApp;