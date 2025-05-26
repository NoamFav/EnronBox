import React from 'react';
import { Mail } from 'lucide-react';
import EmailHeader from './EmailHeader';
import EmailBody from './EmailBody';
import EmailActions from './EmailActions';

const EmailContent = ({
  selectedEmail,
  darkMode,
  activeFolder,
  emailSummary,
  summarizing,
  getLabelById,
  lightBadgeClassMap,
  darkBadgeClassMap,
  toggleStarred,
  toggleFlag,
  replyToEmail,
  forwardEmail,
  deleteEmail,
  summarizeEmail,
  printEmail,
}) => {
  return (
    <div
      className={`flex-1 ${darkMode ? 'bg-gray-800' : 'bg-white'} flex flex-col transition-colors duration-300`}
    >
      {selectedEmail ? (
        <>
          <EmailHeader
            selectedEmail={selectedEmail}
            darkMode={darkMode}
            getLabelById={getLabelById}
            lightBadgeClassMap={lightBadgeClassMap}
            darkBadgeClassMap={darkBadgeClassMap}
            toggleStarred={toggleStarred}
            toggleFlag={toggleFlag}
          />

          <EmailBody
            selectedEmail={selectedEmail}
            darkMode={darkMode}
            emailSummary={emailSummary}
          />

          <EmailActions
            selectedEmail={selectedEmail}
            darkMode={darkMode}
            summarizing={summarizing}
            replyToEmail={replyToEmail}
            forwardEmail={forwardEmail}
            deleteEmail={deleteEmail}
            summarizeEmail={summarizeEmail}
            printEmail={printEmail}
          />
        </>
      ) : (
        <div
          className={`flex flex-col items-center justify-center h-full ${darkMode ? 'text-gray-400' : 'text-gray-500'} animate-fadeIn`}
        >
          <Mail size={64} strokeWidth={1} className="animate-pulse transition-all duration-500" />
          <p
            className={`mt-4 text-lg ${darkMode ? 'text-gray-300' : ''} animate-slideUp`}
            style={{ animationDelay: '200ms' }}
          >
            Select an email to read
          </p>
          <p
            className={`text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'} mt-2 animate-slideUp`}
            style={{ animationDelay: '300ms' }}
          >
            {activeFolder === 'inbox'
              ? 'Your inbox is organized and ready for you'
              : `Viewing your ${activeFolder} folder`}
          </p>
        </div>
      )}
    </div>
  );
};

export default EmailContent;
