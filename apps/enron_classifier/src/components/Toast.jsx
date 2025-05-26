import React from 'react';
import { X } from 'lucide-react';

const ToastNotification = ({ show, message, onClose }) => {
  if (!show) return null;

  return (
    <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center z-50 animate-pulse">
      <p>{message}</p>
      <button className="ml-2" onClick={onClose}>
        <X size={14} />
      </button>
    </div>
  );
};

export default ToastNotification;
