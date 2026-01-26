// src/components/ThemeToggle.jsx
import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeWithToast } from '../context/ThemeContext';

const ThemeToggle = ({ className = '' }) => {
    const { theme, toggleTheme } = useThemeWithToast();
    const isDark = theme === 'dark';

    return (
        <button
            onClick={toggleTheme}
            className={`relative p-2 rounded-xl transition-all duration-300 
                ${isDark
                    ? 'bg-slate-700 hover:bg-slate-600 text-yellow-400'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                }
                hover:scale-105 active:scale-95
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-800
                ${className}`}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
            <div className="relative w-5 h-5">
                <Sun
                    className={`w-5 h-5 absolute inset-0 transition-all duration-300
                        ${isDark ? 'opacity-0 rotate-90 scale-0' : 'opacity-100 rotate-0 scale-100'}`}
                    aria-hidden="true"
                />
                <Moon
                    className={`w-5 h-5 absolute inset-0 transition-all duration-300
                        ${isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'}`}
                    aria-hidden="true"
                />
            </div>
        </button>
    );
};

export default ThemeToggle;
