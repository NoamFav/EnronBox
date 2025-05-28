import { useEmail } from '../contexts/EmailContext';
import { useUI } from '../contexts/UIContext';

export const useUserActions = () => {
  const { dispatch } = useEmail();
  const { displayToast } = useUI();

  const handleSelectUser = (user) => {
    dispatch({ type: 'SET_CURRENT_USER', payload: user });
  };

  const handleSelectFolder = (folder) => {
    dispatch({ type: 'SET_ACTIVE_FOLDER', payload: folder });
  };

  const setSearchQuery = (query) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
  };

  return {
    handleSelectUser,
    handleSelectFolder,
    setSearchQuery,
  };
};
