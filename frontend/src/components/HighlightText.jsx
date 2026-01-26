// src/components/HighlightText.jsx
import React from 'react';

/**
 * Component that highlights matching text within a string.
 * @param {string} text - The full text to display
 * @param {string} highlight - The search term to highlight
 * @returns {JSX.Element} - Text with highlighted matches
 */
const HighlightText = ({ text, highlight }) => {
    if (!highlight || !highlight.trim() || !text) {
        return <>{text}</>;
    }

    // Escape special regex characters
    const escapedHighlight = highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    // Split text on the search term (case-insensitive)
    const parts = text.split(new RegExp(`(${escapedHighlight})`, 'gi'));

    return (
        <>
            {parts.map((part, index) => {
                const isMatch = part.toLowerCase() === highlight.toLowerCase();
                return isMatch ? (
                    <mark
                        key={index}
                        className="search-highlight bg-amber-200/50 dark:bg-amber-500/30 text-inherit rounded-sm px-0.5"
                    >
                        {part}
                    </mark>
                ) : (
                    <span key={index}>{part}</span>
                );
            })}
        </>
    );
};

export default HighlightText;
