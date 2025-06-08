import axios from 'axios';
import { useEmail } from '../contexts/EmailContext';
import { useUI } from '../contexts/UIContext';
import { processEmails, processClassificationResults, applyFilters } from '../utils/emailUtils';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:5050/api',
  timeout: 2400000, // 60 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

export const useEmailAPI = () => {
  const { state, dispatch } = useEmail();
  const { displayToast } = useUI();

  const fetchFolders = async (username) => {
    try {
      console.log('Fetching folders for:', username);
      const response = await api.get(`/users/${username}/folders`);

      console.log('Folders received:', response.data);
      dispatch({ type: 'SET_FOLDERS', payload: response.data });

      // Set first folder as active if current active folder doesn't exist
      if (response.data.length > 0 && !response.data.includes(state.activeFolder)) {
        dispatch({ type: 'SET_ACTIVE_FOLDER', payload: response.data[0] });
      }
    } catch (error) {
      console.error('Error fetching folders:', error.response?.data || error.message);
      displayToast('Failed to load folders', 'error');
    }
  };

  const fetchEmails = async (username, folder) => {
    if (!username || !folder) {
      console.log('Missing username or folder:', { username, folder });
      return;
    }

    // If there's a search query, use IR search instead
    if (state.searchQuery && state.searchQuery.trim()) {
      console.log('Search query detected, using IR search:', state.searchQuery);
      await fetchEmailsIR(username, folder);
      return;
    }

    console.log('Fetching emails for:', username, folder);
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // Fetch emails
      const emailResponse = await api.get(`/users/${username}/folders/${folder}/emails`);
      const rawEmails = emailResponse.data;

      console.log('Raw emails received:', rawEmails.length);

      if (!Array.isArray(rawEmails)) {
        throw new Error('Expected array of emails');
      }

      const processedEmails = processEmails(rawEmails);
      console.log('Processed emails:', processedEmails.length);

      // Try to classify emails
      let finalEmails = processedEmails;
      let labels = [];

      try {
        const classificationPayload = processedEmails.map((e) => ({
          id: e.id,
          subject: e.subject,
          body: e.content,
          sender: e.sender,
          has_attachment: e.hasAttachments,
          num_recipients: 1,
          time_sent: e.rawTime,
        }));

        const classifyResponse = await api.post('/classify/batch', classificationPayload);
        const classificationResults = classifyResponse.data;

        console.log('Classification results:', classificationResults);

        const { emails: classifiedEmails, labels: extractedLabels } = processClassificationResults(
          processedEmails,
          classificationResults
        );

        finalEmails = classifiedEmails;
        labels = extractedLabels;

        dispatch({ type: 'SET_LABELS', payload: labels });
      } catch (classifyError) {
        console.warn(
          'Classification error (non-fatal):',
          classifyError.response?.data || classifyError.message
        );
      }

      // Apply filters
      const filteredEmails = applyFilters(finalEmails, state.filterOptions, labels);
      console.log('Final filtered emails:', filteredEmails.length);

      dispatch({ type: 'SET_EMAILS', payload: filteredEmails });
      displayToast(`Loaded ${filteredEmails.length} emails`);
    } catch (error) {
      console.error('Error fetching emails:', error.response?.data || error.message);
      displayToast(
        `Failed to load emails: ${error.response?.data?.message || error.message}`,
        'error'
      );

      // Set empty array to stop loading state
      dispatch({ type: 'SET_EMAILS', payload: [] });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const fetchEmailsIR = async (username, folder) => {
    if (!username || !folder || !state.searchQuery?.trim()) {
      console.log('Missing required parameters for IR search:', {
        username,
        folder,
        searchQuery: state.searchQuery,
      });
      return;
    }

    console.log('Performing IR search for:', state.searchQuery, 'in folder:', folder);
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // Perform IR search using the search query
      const searchResponse = await api.post('/search', {
        query: state.searchQuery.trim(),
        username: username,
        folder: folder,
        search_fields: ['subject', 'body'], // Search both title and body
        max_results: 100,
      });

      const searchResults = searchResponse.data;
      console.log('IR search results:', searchResults);

      // Check if we got results in the expected format
      if (!searchResults.results || !Array.isArray(searchResults.results)) {
        console.warn('Unexpected search results format, falling back to client-side search');
        // Fallback to client-side search if IR endpoint doesn't work as expected
        await performClientSideSearch(username, folder);
        return;
      }

      // Process the search results
      const processedEmails = processEmails(searchResults.results);
      console.log('Processed IR search emails:', processedEmails.length);

      // Order results by relevance: title matches first, then body matches
      const searchQuery = state.searchQuery.toLowerCase().trim();
      processedEmails.sort((a, b) => {
        const aSubjectMatch = a.subject.toLowerCase().includes(searchQuery);
        const bSubjectMatch = b.subject.toLowerCase().includes(searchQuery);
        const aBodyMatch = a.content.toLowerCase().includes(searchQuery);
        const bBodyMatch = b.content.toLowerCase().includes(searchQuery);

        // Both have subject matches - maintain original order
        if (aSubjectMatch && bSubjectMatch) return 0;

        // Only a has subject match - a comes first
        if (aSubjectMatch && !bSubjectMatch) return -1;

        // Only b has subject match - b comes first
        if (!aSubjectMatch && bSubjectMatch) return 1;

        // Neither has subject match, both have body matches - maintain original order
        if (aBodyMatch && bBodyMatch) return 0;

        // Should not happen as these came from search results, but handle anyway
        return 0;
      });

      // Try to classify the search results
      let finalEmails = processedEmails;
      let labels = [];

      if (processedEmails.length > 0) {
        try {
          const classificationPayload = processedEmails.map((e) => ({
            id: e.id,
            subject: e.subject,
            body: e.content,
            sender: e.sender,
            has_attachment: e.hasAttachments,
            num_recipients: 1,
            time_sent: e.rawTime,
          }));

          const classifyResponse = await api.post('/classify/batch', classificationPayload);
          const classificationResults = classifyResponse.data;

          const { emails: classifiedEmails, labels: extractedLabels } =
            processClassificationResults(processedEmails, classificationResults);

          finalEmails = classifiedEmails;
          labels = extractedLabels;

          dispatch({ type: 'SET_LABELS', payload: labels });
        } catch (classifyError) {
          console.warn(
            'Classification error for search results (non-fatal):',
            classifyError.response?.data || classifyError.message
          );
        }
      }

      // Apply filters to search results
      const filteredEmails = applyFilters(finalEmails, state.filterOptions, labels);
      console.log('Final filtered search results:', filteredEmails.length);

      dispatch({ type: 'SET_EMAILS', payload: filteredEmails });
      displayToast(`Found ${filteredEmails.length} emails matching "${state.searchQuery}"`);
    } catch (error) {
      console.error('Error performing IR search:', error.response?.data || error.message);
      displayToast(`Search failed: ${error.response?.data?.message || error.message}`, 'error');

      // Fallback to client-side search if IR fails
      console.log('Falling back to client-side search');
      await performClientSideSearch(username, folder);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Fallback client-side search function
  const performClientSideSearch = async (username, folder) => {
    try {
      // First fetch all emails
      const emailResponse = await api.get(`/users/${username}/folders/${folder}/emails`);
      const rawEmails = emailResponse.data;
      const processedEmails = processEmails(rawEmails);

      // Perform client-side search
      const searchQuery = state.searchQuery.toLowerCase().trim();
      const searchResults = processedEmails.filter((email) => {
        const subjectMatch = email.subject.toLowerCase().includes(searchQuery);
        const bodyMatch = email.content.toLowerCase().includes(searchQuery);
        return subjectMatch || bodyMatch;
      });

      // Order results by relevance: title matches first, then body matches
      searchResults.sort((a, b) => {
        const aSubjectMatch = a.subject.toLowerCase().includes(searchQuery);
        const bSubjectMatch = b.subject.toLowerCase().includes(searchQuery);

        // Both have subject matches - maintain original order
        if (aSubjectMatch && bSubjectMatch) return 0;

        // Only a has subject match - a comes first
        if (aSubjectMatch && !bSubjectMatch) return -1;

        // Only b has subject match - b comes first
        if (!aSubjectMatch && bSubjectMatch) return 1;

        // Neither has subject match (both must have body matches) - maintain original order
        return 0;
      });

      console.log(`Client-side search found ${searchResults.length} results`);

      // Apply filters
      const filteredEmails = applyFilters(searchResults, state.filterOptions, []);

      dispatch({ type: 'SET_EMAILS', payload: filteredEmails });
      displayToast(
        `Found ${filteredEmails.length} emails matching "${state.searchQuery}" (client-side search)`
      );
    } catch (error) {
      console.error('Client-side search also failed:', error.response?.data || error.message);
      displayToast('Search failed completely', 'error');
      dispatch({ type: 'SET_EMAILS', payload: [] });
    }
  };

  const summarizeEmail = async () => {
    if (!state.selectedEmail?.content) {
      displayToast('No content to summarize', 'error');
      return;
    }

    dispatch({ type: 'SET_SUMMARIZING', payload: true });
    dispatch({ type: 'SET_EMAIL_SUMMARY', payload: '' });

    try {
      const response = await api.post('/summarize', {
        email_text: state.selectedEmail.content,
        num_sentences: 3,
      });

      dispatch({ type: 'SET_EMAIL_SUMMARY', payload: response.data.summary });
      displayToast('Email summarized successfully');
    } catch (error) {
      console.error('Error summarizing email:', error.response?.data || error.message);
      displayToast('Failed to summarize email', 'error');
    } finally {
      dispatch({ type: 'SET_SUMMARIZING', payload: false });
    }
  };

  const extractEntities = async () => {
    if (!state.selectedEmail?.content) {
      displayToast('No content to extract entities from', 'error');
      return;
    }

    // turn on spinner + clear previous entities
    dispatch({ type: 'SET_ENTITY_EXTRACTING', payload: true });
    dispatch({ type: 'SET_EMAIL_ENTITIES', payload: null });

    try {
      const res = await api.post('/ner', {
        email_text: state.selectedEmail.content,
        email_id: state.selectedEmail.id, // optional for persistence
      });

      dispatch({ type: 'SET_EMAIL_ENTITIES', payload: res.data.entities });
      displayToast('Entities extracted successfully');
    } catch (err) {
      console.error('Error extracting entities:', err.response?.data || err.message);
      displayToast('Failed to extract entities', 'error');
    } finally {
      dispatch({ type: 'SET_ENTITY_EXTRACTING', payload: false });
    }
  };

  return {
    fetchFolders,
    fetchEmails,
    fetchEmailsIR,
    summarizeEmail,
    extractEntities,
  };
};
