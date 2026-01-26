// src/components/SearchSuggestions.jsx
import React from 'react';
import { Book, User, Hash } from 'lucide-react';
import HighlightText from './HighlightText';

/**
 * Dropdown component for search suggestions grouped by Title, Author, and ISBN.
 * @param {Object} props
 * @param {Object} props.suggestions - Grouped suggestions { titles: [], authors: [], isbns: [] }
 * @param {string} props.searchQuery - Current search query for highlighting
 * @param {Function} props.onSelect - Callback when a suggestion is clicked
 * @param {boolean} props.isVisible - Whether to show the dropdown
 */
const SearchSuggestions = ({ suggestions, searchQuery, onSelect, isVisible }) => {
    if (!isVisible || !searchQuery.trim()) {
        return null;
    }

    const { titles = [], authors = [], isbns = [] } = suggestions;
    const hasAny = titles.length > 0 || authors.length > 0 || isbns.length > 0;

    if (!hasAny) {
        return (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-gray-200 dark:border-slate-700 p-4 z-50">
                <p className="text-sm text-gray-500 dark:text-slate-400 text-center">
                    No suggestions found
                </p>
            </div>
        );
    }

    const renderSection = (title, items, icon, field) => {
        if (items.length === 0) return null;

        const Icon = icon;
        return (
            <div className="mb-3 last:mb-0">
                <div className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                    <Icon className="w-3.5 h-3.5" />
                    {title}
                </div>
                <div className="space-y-1">
                    {items.slice(0, 5).map((book) => (
                        <button
                            key={`${field}-${book.id}`}
                            onClick={() => onSelect(book[field])}
                            className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors group"
                        >
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                <HighlightText text={book[field]} highlight={searchQuery} />
                            </p>
                            <p className="text-xs text-gray-500 dark:text-slate-400 truncate mt-0.5">
                                {field === 'title' ? book.author : book.title}
                            </p>
                        </button>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-gray-200 dark:border-slate-700 p-2 z-50 max-h-80 overflow-y-auto">
            {renderSection('Title', titles, Book, 'title')}
            {titles.length > 0 && (authors.length > 0 || isbns.length > 0) && (
                <hr className="border-gray-100 dark:border-slate-700 my-2" />
            )}
            {renderSection('Author', authors, User, 'author')}
            {authors.length > 0 && isbns.length > 0 && (
                <hr className="border-gray-100 dark:border-slate-700 my-2" />
            )}
            {renderSection('ISBN', isbns, Hash, 'isbn')}
        </div>
    );
};

export default SearchSuggestions;
