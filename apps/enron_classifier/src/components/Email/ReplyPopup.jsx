import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Loader2 } from 'lucide-react';
import axios from 'axios';
import { API_URL, API_TIMEOUT, DEFAULT_MODEL, DEFAULT_TEMPERATURE } from '../../config';

const ReplyPopup = ({ email, onClose, darkMode }) => {
  const [reply, setReply] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);
  
  useEffect(() => {
    // Focus the textarea when the component mounts
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    
    // Generate reply when component mounts
    generateReply();
  }, []);
  
  const generateReply = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Format the email content for the API
      const emailContent = `
Subject: ${email.subject}
From: ${email.sender}

${email.content}
      `.trim();
      
      // Call the API to generate a reply
      const response = await axios.post(`${API_URL}/respond`, {
        content: emailContent,
        subject: email.subject,
        sender: email.sender,
        model: DEFAULT_MODEL,
        temperature: DEFAULT_TEMPERATURE
      }, {
        timeout: API_TIMEOUT
      });
      
      if (response.data.success) {
        setReply(response.data.reply);
      } else {
        throw new Error(response.data.error || 'Failed to generate reply');
      }
    } catch (err) {
      console.error('Error generating reply:', err);
      setError(err.message || 'An error occurred while generating the reply');
      // Set a default reply in case of error
      setReply(`Hi,\n\nThank you for your email regarding "${email.subject}".\n\nI'll get back to you soon.\n\nBest regards,\n[Your Name]`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSend = () => {
    // In a real app, this would send the email
    // For now, just close the popup
    onClose();
  };
  
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50 animate-fadeIn">
      <div 
        className={`w-full max-w-2xl max-h-[80vh] rounded-lg shadow-xl overflow-hidden flex flex-col ${
          darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800'
        }`}
      >
        {/* Header */}
        <div className={`px-4 py-3 flex justify-between items-center border-b ${
          darkMode ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <h3 className="font-medium">Reply to: {email.subject}</h3>
          <button 
            onClick={onClose}
            className={`p-1 rounded-full hover:bg-opacity-10 ${
              darkMode ? 'hover:bg-gray-300' : 'hover:bg-gray-500'
            }`}
          >
            <X size={18} />
          </button>
        </div>
        
        {/* To field */}
        <div className={`px-4 py-2 flex items-center border-b ${
          darkMode ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <span className="w-12 text-sm text-gray-500">To:</span>
          <span className="ml-2">{email.sender}</span>
        </div>
        
        {/* Reply content */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-full">
              <Loader2 className="animate-spin" size={24} />
              <p className="mt-2 text-sm text-gray-500">Generating reply...</p>
            </div>
          ) : (
            <>
              {error && (
                <div className={`mb-4 p-3 rounded text-sm ${
                  darkMode ? 'bg-red-900 bg-opacity-20 text-red-300' : 'bg-red-100 text-red-700'
                }`}>
                  {error}
                </div>
              )}
              <textarea
                ref={textareaRef}
                value={reply}
                onChange={(e) => setReply(e.target.value)}
                className={`w-full h-full min-h-[200px] p-2 rounded border resize-none focus:outline-none focus:ring-2 ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 focus:ring-blue-600' 
                    : 'bg-white border-gray-300 focus:ring-blue-400'
                }`}
                placeholder="Your reply here..."
              />
            </>
          )}
        </div>
        
        {/* Footer */}
        <div className={`px-4 py-3 flex justify-between items-center border-t ${
          darkMode ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <div>
            {!loading && (
              <button
                onClick={generateReply}
                className={`px-3 py-1 text-sm rounded ${
                  darkMode 
                    ? 'bg-gray-700 hover:bg-gray-600' 
                    : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                Regenerate
              </button>
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={loading}
            className={`px-4 py-2 rounded-md flex items-center ${
              loading
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-opacity-90'
            } ${
              darkMode 
                ? 'bg-blue-600 text-white' 
                : 'bg-blue-500 text-white'
            }`}
          >
            <Send size={16} className="mr-2" />
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReplyPopup; 