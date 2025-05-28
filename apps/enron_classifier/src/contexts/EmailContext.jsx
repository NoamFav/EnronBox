import React, { createContext, useContext, useReducer } from 'react';

const EmailContext = createContext();

const initialState = {
  currentUser: null,
  folders: [],
  emails: [],
  selectedEmail: null,
  activeFolder: 'inbox',
  loading: true,
  searchQuery: '',
  labels: [],
  filterOptions: {
    unreadOnly: false,
    hasAttachments: false,
    sortBy: 'date',
    byLabel: null,
    byStar: false,
    byFlag: false,
  },
  emailSummary: '',
  summarizing: false,
};

function emailReducer(state, action) {
  switch (action.type) {
    case 'SET_CURRENT_USER':
      return { ...state, currentUser: action.payload, selectedEmail: null };
    case 'SET_FOLDERS':
      return { ...state, folders: action.payload };
    case 'SET_EMAILS':
      return { ...state, emails: action.payload };
    case 'SET_SELECTED_EMAIL':
      return { ...state, selectedEmail: action.payload, emailSummary: '' };
    case 'SET_ACTIVE_FOLDER':
      return { ...state, activeFolder: action.payload, selectedEmail: null };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_SEARCH_QUERY':
      return { ...state, searchQuery: action.payload };
    case 'SET_LABELS':
      return { ...state, labels: action.payload };
    case 'SET_FILTER_OPTIONS':
      return { ...state, filterOptions: { ...state.filterOptions, ...action.payload } };
    case 'UPDATE_EMAIL':
      return {
        ...state,
        emails: state.emails.map((email) =>
          email.id === action.payload.id ? { ...email, ...action.payload.updates } : email
        ),
      };
    case 'DELETE_EMAIL':
      return {
        ...state,
        emails: state.emails.filter((email) => email.id !== action.payload),
        selectedEmail: state.selectedEmail?.id === action.payload ? null : state.selectedEmail,
      };
    case 'SET_EMAIL_SUMMARY':
      return { ...state, emailSummary: action.payload };
    case 'SET_SUMMARIZING':
      return { ...state, summarizing: action.payload };
    default:
      return state;
  }
}

export const EmailProvider = ({ children }) => {
  const [state, dispatch] = useReducer(emailReducer, initialState);

  return <EmailContext.Provider value={{ state, dispatch }}>{children}</EmailContext.Provider>;
};

export const useEmail = () => {
  const context = useContext(EmailContext);
  if (!context) {
    throw new Error('useEmail must be used within an EmailProvider');
  }
  return context;
};
