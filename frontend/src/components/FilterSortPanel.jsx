// src/components/FilterSortPanel.jsx
import React from 'react';
import { Filter, ArrowUpDown, X, ChevronDown } from 'lucide-react';

/**
 * Compact filter and sort panel for the Library page.
 * Includes proper ARIA labels for accessibility.
 */
const FilterSortPanel = ({
    authors,
    filters,
    sortBy,
    onFilterChange,
    onSortChange,
    onClear,
    hasActiveFilters
}) => {
    const selectClasses = `
    appearance-none bg-white dark:bg-slate-700 
    border border-gray-200 dark:border-slate-600 
    text-gray-700 dark:text-slate-200 
    text-sm font-medium
    pl-3 pr-8 py-2 rounded-lg
    hover:border-gray-300 dark:hover:border-slate-500
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-800 focus:border-transparent
    transition-colors cursor-pointer
  `;

    return (
        <div
            className="bg-white dark:bg-slate-800/50 border border-gray-100 dark:border-slate-700 rounded-xl p-3 mb-6"
            role="region"
            aria-label="Filter and sort options"
        >
            <div className="flex flex-wrap items-center gap-3">
                {/* Filter Label */}
                <div className="flex items-center gap-1.5 text-gray-500 dark:text-slate-400" id="filter-label">
                    <Filter className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-semibold uppercase tracking-wider">Filters</span>
                </div>

                {/* Author Filter */}
                <div className="relative">
                    <label htmlFor="author-filter" className="sr-only">Filter by author</label>
                    <select
                        id="author-filter"
                        value={filters.author}
                        onChange={(e) => onFilterChange('author', e.target.value)}
                        className={selectClasses}
                        aria-label="Filter by author"
                    >
                        <option value="">All Authors</option>
                        {authors.map((author) => (
                            <option key={author} value={author}>
                                {author}
                            </option>
                        ))}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-500 pointer-events-none" aria-hidden="true" />
                </div>

                {/* ISBN Filter */}
                <div className="relative">
                    <label htmlFor="isbn-filter" className="sr-only">Filter by ISBN</label>
                    <select
                        id="isbn-filter"
                        value={filters.isbn}
                        onChange={(e) => onFilterChange('isbn', e.target.value)}
                        className={selectClasses}
                        aria-label="Filter by ISBN availability"
                    >
                        <option value="all">All ISBNs</option>
                        <option value="has">Has ISBN</option>
                        <option value="none">No ISBN</option>
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-500 pointer-events-none" aria-hidden="true" />
                </div>

                {/* Divider */}
                <div className="h-6 w-px bg-gray-200 dark:bg-slate-600 hidden sm:block" role="separator" aria-hidden="true"></div>

                {/* Sort Label */}
                <div className="flex items-center gap-1.5 text-gray-500 dark:text-slate-400" id="sort-label">
                    <ArrowUpDown className="w-4 h-4" aria-hidden="true" />
                    <span className="text-xs font-semibold uppercase tracking-wider">Sort</span>
                </div>

                {/* Sort By */}
                <div className="relative">
                    <label htmlFor="sort-select" className="sr-only">Sort books by</label>
                    <select
                        id="sort-select"
                        value={sortBy}
                        onChange={(e) => onSortChange(e.target.value)}
                        className={selectClasses}
                        aria-label="Sort books by"
                    >
                        <option value="default">Recently Added</option>
                        <option value="title-asc">Title A–Z</option>
                        <option value="title-desc">Title Z–A</option>
                        <option value="author-asc">Author A–Z</option>
                        <option value="pages-asc">Pages: Low to High</option>
                        <option value="pages-desc">Pages: High to Low</option>
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-500 pointer-events-none" aria-hidden="true" />
                </div>

                {/* Clear Button */}
                {hasActiveFilters && (
                    <button
                        onClick={onClear}
                        className="flex items-center gap-1.5 text-sm font-medium text-red-500 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-2 rounded-lg transition-colors ml-auto focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-slate-800"
                        aria-label="Clear all filters and sorting"
                    >
                        <X className="w-4 h-4" aria-hidden="true" />
                        Clear
                    </button>
                )}
            </div>
        </div>
    );
};

export default FilterSortPanel;
