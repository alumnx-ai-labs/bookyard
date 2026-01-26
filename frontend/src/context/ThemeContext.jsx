// src/context/ThemeContext.jsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useToast } from './ToastContext';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(() => {
        // Check localStorage first
        if (typeof window !== 'undefined') {
            const savedTheme = localStorage.getItem('bookyard-theme');
            if (savedTheme) return savedTheme;

            // Check system preference
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return 'dark';
            }
        }
        return 'light';
    });

    // Track if this is the initial mount (don't show toast on first load)
    const [isInitialMount, setIsInitialMount] = useState(true);

    useEffect(() => {
        const root = window.document.documentElement;

        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }

        localStorage.setItem('bookyard-theme', theme);
    }, [theme]);

    // Mark initial mount as complete after first render
    useEffect(() => {
        setIsInitialMount(false);
    }, []);

    const toggleTheme = useCallback(() => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    }, []);

    return (
        <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, isInitialMount }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

/**
 * Hook to show toast on theme changes
 * Use this in components that handle theme toggle
 */
export const useThemeWithToast = () => {
    const { theme, setTheme, toggleTheme, isInitialMount } = useTheme();
    const toast = useToast();

    const toggleThemeWithToast = useCallback(() => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        toggleTheme();

        // Only show toast if not initial mount
        if (!isInitialMount) {
            toast.info(`Theme changed to ${newTheme === 'dark' ? 'Dark' : 'Light'} mode`);
        }
    }, [theme, toggleTheme, toast, isInitialMount]);

    return { theme, setTheme, toggleTheme: toggleThemeWithToast };
};
