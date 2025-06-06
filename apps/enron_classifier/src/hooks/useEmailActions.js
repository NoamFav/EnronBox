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
  };

  const toggleStarred = (id, e) => {
    e?.stopPropagation();
    const email = state.emails.find((e) => e.id === id);
    const isStarred = !email.starred;

    dispatch({
      type: 'UPDATE_EMAIL',
      payload: { id, updates: { starred: isStarred } },
    });

    displayToast(`Email ${isStarred ? 'starred' : 'unstarred'}`);
  };

  const toggleFlag = (id, e) => {
    e?.stopPropagation();
    const email = state.emails.find((e) => e.id === id);
    const isFlagged = !email.flagged;

    dispatch({
      type: 'UPDATE_EMAIL',
      payload: { id, updates: { flagged: isFlagged } },
    });

    displayToast(`Email ${isFlagged ? 'flagged' : 'unflagged'}`);
  };

  const markAsUnread = (id, e) => {
    e?.stopPropagation();
    dispatch({
      type: 'UPDATE_EMAIL',
      payload: { id, updates: { read: false } },
    });
    displayToast('Email marked as unread');
  };

  const deleteEmail = (id, e) => {
    e?.stopPropagation();
    dispatch({ type: 'DELETE_EMAIL', payload: id });
    displayToast('Email moved to trash');
  };

  const archiveEmail = (id, e) => {
    e?.stopPropagation();
    dispatch({ type: 'DELETE_EMAIL', payload: id });
    displayToast('Email archived');
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
    closeReplyPopup
  };
};
