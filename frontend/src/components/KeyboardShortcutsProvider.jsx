// src/components/KeyboardShortcutsProvider.jsx
import React, { useState, useEffect } from 'react';
import { X, Keyboard } from 'lucide-react';
import useKeyboardShortcuts from '../hooks/useKeyboardShortcuts';

/**
 * Keyboard shortcuts data
 */
const SHORTCUTS = [
    { keys: ['G', 'L'], description: 'Go to Library' },
    { keys: ['G', 'D'], description: 'Go to Dashboard' },
    { keys: ['A'], description: 'Add new book' },
    { keys: ['/'], description: 'Focus search (on Library page)' },
    { keys: ['?'], description: 'Show keyboard shortcuts' },
    { keys: ['Esc'], description: 'Close modals/dropdowns' },
];

/**
 * Keyboard key badge component
 */
const KeyBadge = ({ children }) => (
    <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-2 text-xs font-semibold text-gray-700 dark:text-slate-200 bg-gray-100 dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded shadow-sm">
        {children}
    </kbd>
);

/**
 * Keyboard shortcuts help modal
 */
const ShortcutsHelpModal = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-gray-900/60 dark:bg-black/70 backdrop-blur-sm"
                onClick={onClose}
                aria-hidden="true"
            />
            <div
                className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
                role="dialog"
                aria-modal="true"
                aria-labelledby="shortcuts-title"
            >
                <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-slate-700">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                            <Keyboard className="w-5 h-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
                        </div>
                        <h2 id="shortcuts-title" className="text-lg font-bold text-gray-900 dark:text-white">
                            Keyboard Shortcuts
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Close shortcuts help"
                    >
                        <X className="w-5 h-5" aria-hidden="true" />
                    </button>
                </div>

                <div className="p-4 space-y-3 max-h-[60vh] overflow-y-auto">
                    {SHORTCUTS.map((shortcut, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors"
                        >
                            <span className="text-sm text-gray-700 dark:text-slate-300">
                                {shortcut.description}
                            </span>
                            <div className="flex items-center gap-1">
                                {shortcut.keys.map((key, i) => (
                                    <React.Fragment key={i}>
                                        <KeyBadge>{key}</KeyBadge>
                                        {i < shortcut.keys.length - 1 && (
                                            <span className="text-xs text-gray-400 dark:text-slate-500 mx-1">then</span>
                                        )}
                                    </React.Fragment>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="p-4 bg-gray-50 dark:bg-slate-700/50 border-t border-gray-100 dark:border-slate-700">
                    <p className="text-xs text-gray-500 dark:text-slate-400 text-center">
                        Press <KeyBadge>?</KeyBadge> to toggle this help
                    </p>
                </div>
            </div>
        </div>
    );
};

/**
 * Keyboard shortcuts tooltip button
 */
const ShortcutsHelpButton = ({ onClick }) => (
    <button
        onClick={onClick}
        className="fixed bottom-4 left-4 z-50 flex items-center gap-2 px-3 py-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-full shadow-lg hover:shadow-xl transition-all text-sm font-medium text-gray-600 dark:text-slate-300 hover:text-gray-900 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
        aria-label="Show keyboard shortcuts"
        title="Keyboard shortcuts (?)"
    >
        <Keyboard className="w-4 h-4" aria-hidden="true" />
        <span className="hidden sm:inline">Shortcuts</span>
        <kbd className="hidden sm:inline-flex items-center justify-center w-5 h-5 text-[10px] font-bold bg-gray-100 dark:bg-slate-700 rounded">?</kbd>
    </button>
);

/**
 * Provider component that enables keyboard shortcuts and shows help modal
 */
const KeyboardShortcutsProvider = ({ children }) => {
    const [isHelpOpen, setIsHelpOpen] = useState(false);

    // Initialize keyboard shortcuts
    useKeyboardShortcuts();

    // Listen for custom event to toggle help modal
    useEffect(() => {
        const handleToggle = () => setIsHelpOpen(prev => !prev);
        window.addEventListener('toggle-shortcuts-help', handleToggle);
        return () => window.removeEventListener('toggle-shortcuts-help', handleToggle);
    }, []);

    // Close on Escape
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && isHelpOpen) {
                setIsHelpOpen(false);
            }
        };
        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [isHelpOpen]);

    return (
        <>
            {children}
            <ShortcutsHelpButton onClick={() => setIsHelpOpen(true)} />
            <ShortcutsHelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
        </>
    );
};

export default KeyboardShortcutsProvider;
