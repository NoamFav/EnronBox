import React from 'react';
import Summary from './Summary';
import Attachments from './Attachments';
import Entities from './Entities';

const Body = ({ selectedEmail, darkMode, emailSummary, emailEntities, entityExtracting }) => {
  return (
    <div className="flex-1 overflow-y-auto p-6 animate-fadeIn" style={{ animationDelay: '150ms' }}>
      <Summary emailSummary={emailSummary} darkMode={darkMode} />

      {entityExtracting && (
        <div className="p-4 text-sm italic text-gray-500 animate-pulse">Extracting entities…</div>
      )}
      {emailEntities && !entityExtracting && (
        <Entities entities={emailEntities} darkMode={darkMode} />
      )}

      {/* Email body */}
      <div className="py-4 whitespace-pre-line mb-4">
        <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>{selectedEmail.content}</p>
        <p className={`mt-6 ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>Best regards,</p>
        <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>
          {selectedEmail.sender || 'Unknown'}
        </p>
      </div>

      <Attachments attachments={selectedEmail.attachments} darkMode={darkMode} />
    </div>
  );
};

export default Body;
