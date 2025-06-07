import React from 'react';
import { Mail } from 'lucide-react';
import Header from './Header';
import Body from './Body';
import Actions from './Actions';
import ReplyPopup from './ReplyPopup';
import Entities from './Entities';


const Content = ({
  selectedEmail,
  darkMode,
  activeFolder,
  emailSummary,
  summarizing,

  emailEntities,
  entityExtracting,

  getLabelById,
  lightBadgeClassMap,
  darkBadgeClassMap,
  toggleStarred,
  toggleFlag,

  replyToEmail,
  forwardEmail,
  deleteEmail,
  summarizeEmail,
  extractEntitiesEmail,
  printEmail,
  showReplyPopup,
  closeReplyPopup
}) => {
  return (
    <div
      className={`flex-1 ${darkMode ? 'bg-gray-800' : 'bg-white'} flex flex-col transition-colors duration-300`}
    >
      {selectedEmail ? (
        <>
          <Header
            selectedEmail={selectedEmail}
            darkMode={darkMode}
            getLabelById={getLabelById}
            lightBadgeClassMap={lightBadgeClassMap}
            darkBadgeClassMap={darkBadgeClassMap}
            toggleStarred={toggleStarred}
            toggleFlag={toggleFlag}
          />

          <Body selectedEmail={selectedEmail} darkMode={darkMode} emailSummary={emailSummary} />

          {entityExtracting && (
            <div className="p-4 text-sm italic text-gray-500 animate-pulse">
              Extracting entities…
            </div>
          )}
          {emailEntities && !entityExtracting && (
            <Entities entities={emailEntities} darkMode={darkMode} />
          )}

          <Actions
            selectedEmail={selectedEmail}
            darkMode={darkMode}
            summarizing={summarizing}
            entityExtracting={entityExtracting}
            replyToEmail={replyToEmail}
            forwardEmail={forwardEmail}
            deleteEmail={deleteEmail}
            summarizeEmail={summarizeEmail}
            extractEntitiesEmail={extractEntitiesEmail}
            printEmail={printEmail}
          />
          
          {showReplyPopup && selectedEmail && (
            <ReplyPopup 
              email={selectedEmail} 
              onClose={closeReplyPopup} 
              darkMode={darkMode} 
            />
          )}
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

export default Content;
