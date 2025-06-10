import React, { createContext, useContext, useState, useEffect } from 'react';

const UIContext = createContext();

export const UIProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('darkMode');
      return savedMode === 'true' || false;
    }
    return false;
  });

  const [showLabels, setShowLabels] = useState(true);
  const [showFolders, setShowFolders] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [entityExtracting, setEntityExtracting] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      document.documentElement.classList.toggle('dark', darkMode);
      localStorage.setItem('darkMode', darkMode);
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    displayToast(darkMode ? 'Light mode enabled' : 'Dark mode enabled');
  };

  const displayToast = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 3000);
  };

  return (
    <UIContext.Provider
      value={{
        darkMode,
        setDarkMode,
        toggleDarkMode,
        showLabels,
        showFolders,
        setShowLabels,
        setShowFolders,
        showNotifications,
        setShowNotifications,
        showToast,
        setShowToast,
        toastMessage,
        setToastMessage,
        displayToast,
        entityExtracting,
        setEntityExtracting,
      }}
    >
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};
