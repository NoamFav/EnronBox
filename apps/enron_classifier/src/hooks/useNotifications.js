import { useState } from 'react';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([
    { id: 1, text: 'New settings update available', read: false },
    { id: 2, text: 'Storage limit reached 80%', read: false },
    { id: 3, text: '2 new email drafts saved', read: true },
  ]);

  const unreadNotifications = notifications.filter((n) => !n.read).length;

  const markAllNotificationsRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
  };

  const markNotificationRead = (id) => {
    setNotifications(notifications.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  return {
    notifications,
    setNotifications,
    unreadNotifications,
    markAllNotificationsRead,
    markNotificationRead,
  };
};
