import { useState } from 'react';
import { useEmail } from '../contexts/EmailContext';
import { useUI } from '../contexts/UIContext';
import { useEmailAPI } from './useEmailAPI';

export const useEmailActions = () => {
  const { state, dispatch } = useEmail();
  const { displayToast } = useUI();
  const { fetchEmails } = useEmailAPI();
  const [showReplyPopup, setShowReplyPopup] = useState(false);

  const handleEmailClick = (email) => {
    dispatch({ type: 'SET_SELECTED_EMAIL', payload: email });
    dispatch({
      type: 'UPDATE_EMAIL',
      payload: { id: email.id, updates: { read: true } },
    });
    // Sync with backend
    fetch(`http://localhost:5050/api/emails/${email.id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ read: true }),
    });
  };

  const toggleStarred = async (id, e) => {
    e?.stopPropagation();
    const email = state.emails.find((e) => e.id === id);
    const isStarred = !email.starred;

    try {
      const response = await fetch(`http://localhost:5050/api/emails/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ starred: isStarred ? 1 : 0 }),
      });

      if (!response.ok) {
        throw new Error('Failed to update star status');
      }

      // update local state
      dispatch({
        type: 'UPDATE_EMAIL',
        payload: { id, updates: { starred: isStarred } },
      });

      displayToast(`Email ${isStarred ? 'starred' : 'unstarred'}`);
    } catch (err) {
      console.error('Error updating star status:', err);
      displayToast('Failed to update star status', 'error');
    }
  };

  const toggleFlag = async (id, e) => {
    e?.stopPropagation();
    const email = state.emails.find((e) => e.id === id);
    const isFlagged = !email.flagged;

    try {
      const response = await fetch(`http://localhost:5050/api/emails/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flagged: isFlagged ? 1 : 0 }),
      });

      if (!response.ok) {
        throw new Error('Failed to update flag status');
      }

      // update local state
      dispatch({
        type: 'UPDATE_EMAIL',
        payload: { id, updates: { flagged: isFlagged } },
      });

      displayToast(`Email ${isFlagged ? 'flagged' : 'unflagged'}`);
    } catch (err) {
      console.error('Error updating flag status:', err);
      displayToast('Failed to update flag status', 'error');
    }
  };

  const markAsUnread = async (id, e) => {
    e?.stopPropagation();
    try {
      const response = await fetch(`http://localhost:5050/api/emails/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ read: false }),
      });
      if (!response.ok) {
        throw new Error('Failed to mark as unread');
      }
      dispatch({
        type: 'UPDATE_EMAIL',
        payload: { id, updates: { read: false } },
      });
      displayToast('Email marked as unread');
      refreshEmails();
    } catch (err) {
      displayToast('Failed to mark as unread', 'error');
    }
  };

  const deleteEmail = async (id, e) => {
    e?.stopPropagation();
    try {
      const response = await fetch(`http://localhost:5050/api/emails/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deleted: true }),
      });
      if (!response.ok) {
        throw new Error('Failed to delete email');
      }
      dispatch({
        type: 'UPDATE_EMAIL',
        payload: { id, updates: { deleted: true } },
      });
      displayToast('Email moved to trash');
      refreshEmails();
    } catch (err) {
      displayToast('Failed to delete email', 'error');
    }
  };

  const archiveEmail = async (id, e) => {
    e?.stopPropagation();
    try {
      const response = await fetch(`http://localhost:5050/api/emails/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ archived: true }),
      });
      if (!response.ok) {
        throw new Error('Failed to archive email');
      }
      dispatch({
        type: 'UPDATE_EMAIL',
        payload: { id, updates: { archived: true } },
      });
      displayToast('Email archived');
      refreshEmails();
    } catch (err) {
      displayToast('Failed to archive email', 'error');
    }
  };

  const refreshEmails = () => {
    if (state.currentUser && state.activeFolder) {
      fetchEmails(state.currentUser.username, state.activeFolder);
      displayToast('Refreshing emails');
    }
  };

  const replyToEmail = () => {
    setShowReplyPopup(true);
    displayToast('Generating auto-reply...');
  };

  const closeReplyPopup = () => {
    setShowReplyPopup(false);
  };

  const forwardEmail = () => {
    displayToast('Forward window opened');
  };

  const printEmail = () => {
    displayToast('Preparing to print');
  };

  const composeNewEmail = () => {
    displayToast('New email composition window opened');
  };

  return {
    handleEmailClick,
    toggleStarred,
    toggleFlag,
    markAsUnread,
    deleteEmail,
    archiveEmail,
    refreshEmails,
    replyToEmail,
    forwardEmail,
    printEmail,
    composeNewEmail,
    showReplyPopup,
    closeReplyPopup,
  };
};
