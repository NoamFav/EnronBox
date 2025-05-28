export const formatDate = (dateStr) => {
  if (!dateStr) return 'Unknown';

  try {
    const date = new Date(dateStr);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);

    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  } catch (e) {
    return 'Invalid date';
  }
};

export const processEmails = (rawEmails) => {
  return rawEmails.map((e) => ({
    id: e.id,
    sender: e.from_address,
    subject: e.subject || '(No Subject)',
    content: e.body,
    read: Math.random() > 0.5,
    starred: Math.random() > 0.7,
    time: formatDate(e.date),
    rawTime: e.date,
    hasAttachments: Math.random() > 0.7,
    priority: Math.random() > 0.8 ? 'high' : Math.random() > 0.5 ? 'medium' : 'normal',
    flagged: Math.random() > 0.85,
    attachments:
      Math.random() > 0.7
        ? [
            { name: 'document.pdf', size: '2.4 MB', type: 'pdf' },
            { name: 'image.jpg', size: '1.1 MB', type: 'image' },
          ]
        : [],
    labels: [],
  }));
};

export const processClassificationResults = (emails, results) => {
  const byCategory = new Map(results.map((r) => [Number(r.email_id), r.classification.category]));

  const allCategories = [
    'Work',
    'Urgent',
    'Business',
    'Personal',
    'Meeting',
    'External',
    'Newsletter',
  ];

  const colorMap = {
    Work: 'blue',
    Urgent: 'red',
    Business: 'orange',
    Personal: 'green',
    Meeting: 'teal',
    External: 'gray',
    Newsletter: 'purple',
  };

  const usedNames = Array.from(
    new Set(Array.from(byCategory.values()).filter((c) => allCategories.includes(c)))
  );

  const labels = usedNames.map((name, i) => ({
    id: i + 1,
    name,
    color: colorMap[name] || 'gray',
  }));

  const nameToId = new Map(labels.map((l) => [l.name, l.id]));

  const classified = emails.map((e) => {
    const cat = byCategory.get(e.id);
    const lid = nameToId.get(cat);
    return { ...e, labels: lid ? [lid] : [] };
  });

  return { emails: classified, labels };
};

export const applyFilters = (emails, filterOptions, labels) => {
  let filtered = emails;

  if (filterOptions.unreadOnly) {
    filtered = filtered.filter((e) => !e.read);
  }

  if (filterOptions.hasAttachments) {
    filtered = filtered.filter((e) => e.hasAttachments);
  }

  if (filterOptions.byLabel) {
    filtered = filtered.filter((e) => {
      return e.labels.some((id) => {
        const label = labels.find((l) => l.id === id);
        return label?.name === filterOptions.byLabel;
      });
    });
  }

  // Sort emails
  switch (filterOptions.sortBy) {
    case 'sender':
      filtered.sort((a, b) => a.sender.localeCompare(b.sender));
      break;
    case 'subject':
      filtered.sort((a, b) => a.subject.localeCompare(b.subject));
      break;
    default:
      // Keep default date order
      break;
  }

  return filtered;
};
