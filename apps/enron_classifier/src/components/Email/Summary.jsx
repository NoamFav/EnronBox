import React from 'react';
import { FileText } from 'lucide-react';

const Summary = ({ emailSummary, darkMode }) => {
  if (!emailSummary) return null;

  return (
    <div
      className={`mb-4 p-4 rounded-lg ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-blue-50 text-gray-800'}`}
    >
      <div className="flex items-center mb-2">
        <FileText size={16} className={`mr-2 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
        <h3 className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Summary
        </h3>
      </div>
      <p className="text-sm">{emailSummary}</p>
    </div>
  );
};

export default Summary;
