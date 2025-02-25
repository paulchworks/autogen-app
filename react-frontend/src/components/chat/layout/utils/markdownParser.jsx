// utils/markdownParser.jsx
import React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';

const parseInlineMarkdown = (text) => {
  // Split the text into parts based on bold (**...**) or italic (*...*) patterns
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/);

  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      // Handle bold text
      return (
        <Typography key={index} component="span" sx={{ fontWeight: 'bold' }}>
          {part.replace(/\*\*/g, '')}
        </Typography>
      );
    } else if (part.startsWith('*') && part.endsWith('*')) {
      // Handle italic text
      return (
        <Typography key={index} component="span" sx={{ fontStyle: 'italic' }}>
          {part.replace(/\*/g, '')}
        </Typography>
      );
    } else {
      // Plain text
      return part;
    }
  });
};

export const parseMarkdown = (text) => {
  if (!text || typeof text !== 'string') return null;

  // Split the text into blocks separated by two or more newlines
  const blocks = text.split(/\n{2,}/);

  return blocks.map((block, index) => {
    // Handle headers
    if (block.startsWith('#')) {
      const level = block.match(/^#+/)[0].length; // Count the number of '#' characters
      const headerText = block.replace(/^#+\s*/, '').trim();
      return (
        <Typography key={index} variant={`h${level}`} sx={{ fontWeight: 'bold', my: 2 }}>
          {headerText}
        </Typography>
      );
    }
    // Handle unordered lists
    else if (block.match(/^\s*-\s+/gm)) {
      const items = block.split(/\n\s*-\s+/).filter(Boolean); // Split by list items
      return (
        <Box key={index} sx={{ my: 2 }}>
          <List>
            {items.map((item, idx) => (
              <ListItem key={idx} sx={{ display: 'list-item', pl: 2 }}>
                <Typography>{parseInlineMarkdown(item.trim())}</Typography>
              </ListItem>
            ))}
          </List>
        </Box>
      );
    }
    // Handle ordered lists
    else if (block.match(/^\s*\d+\.\s+/gm)) {
      const items = block.split(/\n\s*\d+\.\s+/).filter(Boolean); // Split by list items
      return (
        <Box key={index} sx={{ my: 2 }}>
          <List>
            {items.map((item, idx) => (
              <ListItem key={idx} sx={{ display: 'list-item', pl: 2 }}>
                <Typography>{parseInlineMarkdown(item.trim())}</Typography>
              </ListItem>
            ))}
          </List>
        </Box>
      );
    }
    // Handle links
    else if (/\[.*?\]\(.*?\)/.test(block)) {
      const parts = block.split(/(\[.*?\]\(.*?\))/);
      return (
        <Typography key={index} paragraph sx={{ my: 1 }}>
          {parts.map((part, idx) => {
            if (/\[.*?\]\(.*?\)/.test(part)) {
              const [_, text, url] = part.match(/\[(.*?)\]\((.*?)\)/);
              return (
                <Typography
                  key={idx}
                  component="a"
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'primary.main',
                    textDecoration: 'underline',
                    cursor: 'pointer',
                    '&:hover': { textDecoration: 'none' },
                  }}
                >
                  {text}
                </Typography>
              );
            } else {
              return parseInlineMarkdown(part);
            }
          })}
        </Typography>
      );
    }
    // Default: Handle paragraphs
    else {
      return (
        <Typography key={index} paragraph sx={{ my: 1 }}>
          {parseInlineMarkdown(block.trim())}
        </Typography>
      );
    }
  });
};