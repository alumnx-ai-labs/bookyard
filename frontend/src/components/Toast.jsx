// src/components/Toast.jsx
import React from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useToast, TOAST_TYPES } from '../context/ToastContext';

/**
 * Toast component - Renders all active toast notifications
 */
const Toast = () => {
    const { toasts, removeToast } = useToast();

    const getToastStyles = (type) => {
        switch (type) {
            case TOAST_TYPES.SUCCESS:
                return {
                    bg: 'bg-green-50 dark:bg-green-900/30',
                    border: 'border-green-200 dark:border-green-800',
                    text: 'text-green-800 dark:text-green-200',
                    icon: <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" aria-hidden="true" />
                };
            case TOAST_TYPES.ERROR:
                return {
                    bg: 'bg-red-50 dark:bg-red-900/30',
                    border: 'border-red-200 dark:border-red-800',
                    text: 'text-red-800 dark:text-red-200',
                    icon: <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400" aria-hidden="true" />
                };
            case TOAST_TYPES.WARNING:
                return {
                    bg: 'bg-amber-50 dark:bg-amber-900/30',
                    border: 'border-amber-200 dark:border-amber-800',
                    text: 'text-amber-800 dark:text-amber-200',
                    icon: <AlertTriangle className="w-5 h-5 text-amber-500 dark:text-amber-400" aria-hidden="true" />
                };
            case TOAST_TYPES.INFO:
            default:
                return {
                    bg: 'bg-blue-50 dark:bg-blue-900/30',
                    border: 'border-blue-200 dark:border-blue-800',
                    text: 'text-blue-800 dark:text-blue-200',
                    icon: <Info className="w-5 h-5 text-blue-500 dark:text-blue-400" aria-hidden="true" />
                };
        }
    };

    if (toasts.length === 0) return null;

    return (
        <div
            className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm"
            role="region"
            aria-label="Notifications"
            aria-live="polite"
            aria-atomic="false"
        >
            {toasts.map((toast) => {
                const styles = getToastStyles(toast.type);
                return (
                    <div
                        key={toast.id}
                        className={`
              ${styles.bg} ${styles.border} ${styles.text}
              border rounded-xl px-4 py-3 shadow-lg
              flex items-center gap-3
              animate-slide-in
              backdrop-blur-sm
            `}
                        role="alert"
                        aria-live="assertive"
                    >
                        {styles.icon}
                        <p className="flex-1 text-sm font-medium">{toast.message}</p>
                        <button
                            onClick={() => removeToast(toast.id)}
                            className={`
                p-1 rounded-lg transition-colors
                hover:bg-black/10 dark:hover:bg-white/10
                focus:outline-none focus:ring-2 focus:ring-current
              `}
                            aria-label="Dismiss notification"
                        >
                            <X className="w-4 h-4" aria-hidden="true" />
                        </button>
                    </div>
                );
            })}
        </div>
    );
};

export default Toast;
