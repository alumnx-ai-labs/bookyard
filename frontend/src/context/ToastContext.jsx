// src/context/ToastContext.jsx
import React, { createContext, useContext, useState, useCallback, useRef } from 'react';

const ToastContext = createContext(null);

/**
 * Toast types for different notification styles
 */
export const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    INFO: 'info',
    WARNING: 'warning'
};

/**
 * ToastProvider - Manages toast notifications across the app
 */
export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);
    const toastIdRef = useRef(0);
    const recentToastsRef = useRef(new Map()); // Prevent duplicate toasts

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    const addToast = useCallback((message, type = TOAST_TYPES.INFO, duration = 3000) => {
        // Prevent duplicate toasts within 2 seconds
        const now = Date.now();
        const toastKey = `${message}-${type}`;
        const lastShown = recentToastsRef.current.get(toastKey);

        if (lastShown && now - lastShown < 2000) {
            return; // Skip duplicate
        }

        recentToastsRef.current.set(toastKey, now);

        // Clean up old entries
        if (recentToastsRef.current.size > 20) {
            const entries = Array.from(recentToastsRef.current.entries());
            entries.slice(0, 10).forEach(([key]) => recentToastsRef.current.delete(key));
        }

        const id = ++toastIdRef.current;
        const newToast = { id, message, type, duration };

        setToasts(prev => [...prev, newToast]);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }

        return id;
    }, [removeToast]);

    // Convenience methods
    const success = useCallback((message, duration) => addToast(message, TOAST_TYPES.SUCCESS, duration), [addToast]);
    const error = useCallback((message, duration) => addToast(message, TOAST_TYPES.ERROR, duration), [addToast]);
    const info = useCallback((message, duration) => addToast(message, TOAST_TYPES.INFO, duration), [addToast]);
    const warning = useCallback((message, duration) => addToast(message, TOAST_TYPES.WARNING, duration), [addToast]);

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, info, warning }}>
            {children}
        </ToastContext.Provider>
    );
};

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};
