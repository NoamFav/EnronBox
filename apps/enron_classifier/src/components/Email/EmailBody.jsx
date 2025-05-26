import React from 'react';
import EmailSummary from './EmailSummary';
import EmailAttachments from './EmailAttachments';

const EmailBody = ({ selectedEmail, darkMode, emailSummary }) => {
  return (
    <div className="flex-1 overflow-y-auto p-6 animate-fadeIn" style={{ animationDelay: '150ms' }}>
      <EmailSummary emailSummary={emailSummary} darkMode={darkMode} />

      {/* Email body */}
      <div className="py-4 whitespace-pre-line mb-4">
        <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>{selectedEmail.content}</p>
        <p className={`mt-6 ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>Best regards,</p>
        <p className={darkMode ? 'text-gray-300' : 'text-gray-800'}>
          {selectedEmail.sender || 'Unknown'}
        </p>
      </div>

      <EmailAttachments attachments={selectedEmail.attachments} darkMode={darkMode} />
    </div>
  );
};

export default EmailBody;
