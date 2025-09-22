'use client';
import React from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface PaginationProps {
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  totalPages,
  currentPage,
  onPageChange,
}) => {
  // Don't render pagination if there's only one page
  if (totalPages <= 1) {
    return null;
  }

  // Generate array of visible page numbers
  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxVisiblePages = 5; // Max number of page buttons to show
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if less than max visible
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // Logic for showing pages with ellipsis
      if (currentPage <= 3) {
        // Near start: show first 4 pages + ellipsis + last page
        for (let i = 1; i <= 4; i++) {
          pageNumbers.push(i);
        }
        pageNumbers.push(-1); // Ellipsis indicator
        pageNumbers.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        // Near end: show first page + ellipsis + last 4 pages
        pageNumbers.push(1);
        pageNumbers.push(-1); // Ellipsis indicator
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pageNumbers.push(i);
        }
      } else {
        // Middle: show first page + ellipsis + current-1, current, current+1 + ellipsis + last page
        pageNumbers.push(1);
        pageNumbers.push(-1); // Ellipsis indicator
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pageNumbers.push(i);
        }
        pageNumbers.push(-1); // Ellipsis indicator
        pageNumbers.push(totalPages);
      }
    }
    
    return pageNumbers;
  };

  const pageNumbers = getPageNumbers();

  return (
    <nav className="flex items-center justify-center" aria-label="Pagination">
      <div className="flex items-center space-x-1 md:space-x-2">
        {/* Previous page button */}
        <button
          onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={`
            relative inline-flex items-center justify-center p-2 rounded-md text-sm font-medium
            ${currentPage === 1
              ? 'text-gray-400 bg-gray-100 dark:bg-zinc-800 dark:text-gray-600 cursor-not-allowed'
              : 'text-mint-11 dark:text-mint-9 bg-white dark:bg-zinc-800 border border-mint-6 dark:border-mint-8 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors'}
          `}
          aria-label="Previous page"
        >
          <ChevronLeftIcon className="h-4 w-4" aria-hidden="true" />
        </button>

        {/* Page number buttons */}
        {pageNumbers.map((pageNumber, index) => (
          pageNumber === -1 ? (
            // Ellipsis indicator
            <span key={`ellipsis-${index}`} className="px-2 py-2 text-gray-500 dark:text-gray-400">
              ...
            </span>
          ) : (
            <button
              key={`page-${pageNumber}`}
              onClick={() => onPageChange(pageNumber)}
              className={`
                relative inline-flex items-center justify-center h-8 w-8 rounded-md text-sm font-medium
                ${pageNumber === currentPage
                  ? 'bg-mint-6 dark:bg-mint-8 text-white cursor-default'
                  : 'text-mint-11 dark:text-mint-9 bg-white dark:bg-zinc-800 border border-mint-6 dark:border-mint-8 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors'}
              `}
              aria-current={pageNumber === currentPage ? 'page' : undefined}
              aria-label={`Page ${pageNumber}`}
            >
              {pageNumber}
            </button>
          )
        ))}

        {/* Next page button */}
        <button
          onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`
            relative inline-flex items-center justify-center p-2 rounded-md text-sm font-medium
            ${currentPage === totalPages
              ? 'text-gray-400 bg-gray-100 dark:bg-zinc-800 dark:text-gray-600 cursor-not-allowed'
              : 'text-mint-11 dark:text-mint-9 bg-white dark:bg-zinc-800 border border-mint-6 dark:border-mint-8 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors'}
          `}
          aria-label="Next page"
        >
          <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </nav>
  );
};

export default Pagination;