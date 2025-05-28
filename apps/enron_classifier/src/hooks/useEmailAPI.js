import { useEmail } from '../contexts/EmailContext';
import { useUI } from '../contexts/UIContext';
import {
  formatDate,
  processEmails,
  processClassificationResults,
  applyFilters,
} from '../utils/emailUtils';

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
    summarizeEmail,
  };
};
