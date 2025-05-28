import { useEmail } from '../contexts/EmailContext';
import { useUI } from '../contexts/UIContext';
import { processEmails, processClassificationResults, applyFilters } from '../utils/emailUtils';

export const useEmailAPI = () => {
  const { state, dispatch } = useEmail();
  const { displayToast } = useUI();

  const fetchFolders = async (username) => {
    try {
      console.log('Fetching folders for:', username);
      const response = await fetch(`http://localhost:5050/api/users/${username}/folders`);

      if (response.ok) {
        const data = await response.json();
        console.log('Folders received:', data);
        dispatch({ type: 'SET_FOLDERS', payload: data });

        // Set first folder as active if current active folder doesn't exist
        if (data.length > 0 && !data.includes(state.activeFolder)) {
          dispatch({ type: 'SET_ACTIVE_FOLDER', payload: data[0] });
        }
      } else {
        console.error('Failed to fetch folders:', response.status, response.statusText);
        displayToast('Failed to load folders', 'error');
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
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
      const emailResponse = await fetch(
        `http://localhost:5050/api/users/${username}/folders/${folder}/emails`
      );

      if (!emailResponse.ok) {
        throw new Error(`Email fetch failed: ${emailResponse.status} ${emailResponse.statusText}`);
      }

      const rawEmails = await emailResponse.json();
      console.log('Raw emails received:', rawEmails.length);

      if (!Array.isArray(rawEmails)) {
        throw new Error('Expected array of emails');
      }

      const processedEmails = processEmails(rawEmails);
      console.log('Processed emails:', processedEmails.length);

      // Try to classify emails (optional - if this fails, just use processed emails)
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

        const classifyResponse = await fetch('http://localhost:5050/api/classify/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(classificationPayload),
        });

        if (classifyResponse.ok) {
          const classificationResults = await classifyResponse.json();
          console.log('Classification results:', classificationResults);

          const { emails: classifiedEmails, labels: extractedLabels } =
            processClassificationResults(processedEmails, classificationResults);

          finalEmails = classifiedEmails;
          labels = extractedLabels;

          dispatch({ type: 'SET_LABELS', payload: labels });
        } else {
          console.warn('Classification failed, using emails without labels');
        }
      } catch (classifyError) {
        console.warn('Classification error (non-fatal):', classifyError);
      }

      // Apply filters
      const filteredEmails = applyFilters(finalEmails, state.filterOptions, labels);
      console.log('Final filtered emails:', filteredEmails.length);

      dispatch({ type: 'SET_EMAILS', payload: filteredEmails });
      displayToast(`Loaded ${filteredEmails.length} emails`);
    } catch (error) {
      console.error('Error fetching emails:', error);
      displayToast(`Failed to load emails: ${error.message}`, 'error');

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
      const searchResponse = await fetch('http://localhost:5050/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: state.searchQuery.trim(),
          username: username,
          folder: folder,
          search_fields: ['subject', 'body'], // Search both title and body
          max_results: 100, // Adjust as needed
        }),
      });

      if (!searchResponse.ok) {
        throw new Error(`Search failed: ${searchResponse.status} ${searchResponse.statusText}`);
      }

      const searchResults = await searchResponse.json();
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

          const classifyResponse = await fetch('http://localhost:5050/api/classify/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(classificationPayload),
          });

          if (classifyResponse.ok) {
            const classificationResults = await classifyResponse.json();
            const { emails: classifiedEmails, labels: extractedLabels } =
              processClassificationResults(processedEmails, classificationResults);

            finalEmails = classifiedEmails;
            labels = extractedLabels;

            dispatch({ type: 'SET_LABELS', payload: labels });
          }
        } catch (classifyError) {
          console.warn('Classification error for search results (non-fatal):', classifyError);
        }
      }

      // Apply filters to search results
      const filteredEmails = applyFilters(finalEmails, state.filterOptions, labels);
      console.log('Final filtered search results:', filteredEmails.length);

      dispatch({ type: 'SET_EMAILS', payload: filteredEmails });
      displayToast(`Found ${filteredEmails.length} emails matching "${state.searchQuery}"`);
    } catch (error) {
      console.error('Error performing IR search:', error);
      displayToast(`Search failed: ${error.message}`, 'error');

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
      const emailResponse = await fetch(
        `http://localhost:5050/api/users/${username}/folders/${folder}/emails`
      );

      if (!emailResponse.ok) {
        throw new Error(`Email fetch failed: ${emailResponse.status} ${emailResponse.statusText}`);
      }

      const rawEmails = await emailResponse.json();
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
      console.error('Client-side search also failed:', error);
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
      const response = await fetch('http://localhost:5050/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_text: state.selectedEmail.content,
          num_sentences: 3,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        dispatch({ type: 'SET_EMAIL_SUMMARY', payload: data.summary });
        displayToast('Email summarized successfully');
      } else {
        displayToast('Failed to summarize email', 'error');
      }
    } catch (error) {
      console.error('Error summarizing email:', error);
      displayToast('Failed to summarize email', 'error');
    } finally {
      dispatch({ type: 'SET_SUMMARIZING', payload: false });
    }
  };

  return {
    fetchFolders,
    fetchEmails,
    fetchEmailsIR,
    summarizeEmail,
  };
};
