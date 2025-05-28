import { useEmail } from '../contexts/EmailContext';

export const useFilters = () => {
  const { state, dispatch } = useEmail();

  const toggleFilterOption = (option) => {
    dispatch({
      type: 'SET_FILTER_OPTIONS',
      payload: { [option]: !state.filterOptions[option] },
    });
  };

  const toggleFilterByLabel = (labelName) => {
    const newByLabel = state.filterOptions.byLabel === labelName ? null : labelName;
    dispatch({
      type: 'SET_FILTER_OPTIONS',
      payload: { byLabel: newByLabel },
    });
  };

  const setSort = (sortOption) => {
    dispatch({
      type: 'SET_FILTER_OPTIONS',
      payload: { sortBy: sortOption },
    });
  };

  return {
    toggleFilterOption,
    toggleFilterByLabel,
    setSort,
  };
};
