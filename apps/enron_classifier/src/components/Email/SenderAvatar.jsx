import React from 'react';

const SenderAvatar = ({ sender, darkMode }) => {
  return (
    <div
      className={`w-10 h-10 ${darkMode ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-600'} rounded-full flex items-center justify-center font-semibold transition-colors duration-300`}
    >
      {(sender || 'U')[0].toUpperCase()}
    </div>
  );
};

export default SenderAvatar;
