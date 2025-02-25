// utils/markdownParser.jsx
import React from 'react';
import Typography from '@mui/material/Typography';

export const parseMarkdown = (text) => {
  if (!text || typeof text !== 'string') return null;

  // Split the text into parts based on Markdown patterns
  const parts = text.split(/(\*\*.*?\*\*|###.*?$|\[.*?\]\(.*?\)|\n)/);

  return parts.map((part, index) => {
    if (part.startsWith('###')) {
      // Handle headers
      return (
        <Typography key={index} variant="h6" component="div" sx={{ fontWeight: 'bold', my: 1 }}>
          {part.replace('###', '').trim()}
        </Typography>
      );
    } else if (part.startsWith('**') && part.endsWith('**')) {
      // Handle bold text
      return (
        <Typography key={index} component="span" sx={{ fontWeight: 'bold' }}>
          {part.replace(/\*\*/g, '')}
        </Typography>
      );
    } else if (/\[.*?\]\(.*?\)/.test(part)) {
      // Handle links
      const [_, text, url] = part.match(/\[(.*?)\]\((.*?)\)/);
      return (
        <Typography
          key={index}
          component="a"
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          sx={{ color: 'blue', textDecoration: 'underline', cursor: 'pointer', display: 'inline-block', mx: 0.5 }}
        >
          {text}
        </Typography>
      );
    } else if (part === '\n') {
      // Handle line breaks
      return <br key={index} />;
    } else {
      // Plain text
      return part.trim() ? (
        <Typography key={index} component="span" sx={{ mx: 0.5 }}>
          {part}
        </Typography>
      ) : null;
    }
  });
};