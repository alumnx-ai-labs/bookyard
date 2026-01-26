// src/hooks/useKeyboardShortcuts.js
import { useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';

/**
 * Check if the event target is an input element
 */
const isInputElement = (target) => {
    const tagName = target.tagName.toUpperCase();
    return (
        tagName === 'INPUT' ||
        tagName === 'TEXTAREA' ||
        tagName === 'SELECT' ||
        target.isContentEditable
    );
};

/**
 * Custom hook for global keyboard shortcuts with sequential key detection
 */
const useKeyboardShortcuts = () => {
    const navigate = useNavigate();
    const toast = useToast();

    // Track the last key pressed for sequential shortcuts
    const lastKeyRef = useRef(null);
    const timeoutRef = useRef(null);
    const SEQUENCE_TIMEOUT = 1000; // 1 second timeout for key sequences

    const clearSequence = useCallback(() => {
        lastKeyRef.current = null;
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }
    }, []);

    const handleKeyDown = useCallback((event) => {
        // Don't trigger shortcuts when typing in input fields
        if (isInputElement(event.target)) {
            return;
        }

        // Don't trigger on modifier keys alone or with modifiers (except shift)
        if (event.ctrlKey || event.altKey || event.metaKey) {
            return;
        }

        const key = event.key.toLowerCase();

        // Handle sequential shortcuts (G → L, G → D)
        if (lastKeyRef.current === 'g') {
            clearSequence();

            if (key === 'l') {
                event.preventDefault();
                navigate('/books');
                toast.info('Navigated to Library');
                return;
            }

            if (key === 'd') {
                event.preventDefault();
                navigate('/dashboard');
                toast.info('Navigated to Dashboard');
                return;
            }
        }

        // Handle single key shortcuts
        if (key === 'g') {
            // Start sequence - wait for next key
            lastKeyRef.current = 'g';
            timeoutRef.current = setTimeout(clearSequence, SEQUENCE_TIMEOUT);
            return;
        }

        if (key === 'a') {
            event.preventDefault();
            navigate('/books/create');
            toast.info('Opening Add New Book');
            return;
        }

        // Handle ? for help modal (shift + /)
        if (key === '?' || (event.shiftKey && key === '/')) {
            event.preventDefault();
            // Dispatch custom event for help modal
            window.dispatchEvent(new CustomEvent('toggle-shortcuts-help'));
            return;
        }

    }, [navigate, toast, clearSequence]);

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [handleKeyDown]);
};

export default useKeyboardShortcuts;
