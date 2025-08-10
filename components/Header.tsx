
import React from 'react';

interface HeaderProps {
  title: string;
  description: string;
  onToggleLeftSidebar: () => void;
  onToggleRightSidebar: () => void;
  layoutMode: 'desktop' | 'mobile';
  onToggleLayoutMode: () => void;
}

const Header: React.FC<HeaderProps> = ({ title, description, onToggleLeftSidebar, onToggleRightSidebar, layoutMode, onToggleLayoutMode }) => {
  return (
    <header className="bg-brand-surface shadow-sm flex-shrink-0 z-10">
      <div className="max-w-full mx-auto py-3 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <div className="flex items-center">
            <button
                onClick={onToggleLeftSidebar}
                className={`${layoutMode === 'desktop' ? 'lg:hidden' : ''} text-brand-text-secondary hover:text-brand-text-main mr-4 p-1 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-primary`}
                aria-label="Toggle navigation"
            >
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
            <div>
                <h1 className="text-xl font-bold leading-tight text-brand-text-main">{title}</h1>
                <p className="mt-1 text-sm text-brand-text-secondary truncate">{description}</p>
            </div>
        </div>
        <div className="flex items-center gap-2">
             <button
                onClick={onToggleLayoutMode}
                className="hidden lg:flex items-center gap-2 text-brand-text-secondary hover:text-brand-text-main px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-primary transition-colors"
                aria-label={`Switch to ${layoutMode === 'desktop' ? 'mobile' : 'desktop'} view`}
                title={`Switch to ${layoutMode === 'desktop' ? 'mobile' : 'desktop'} view`}
            >
                {layoutMode === 'desktop' ? (
                    <>
                        <span className="text-sm font-medium">Focus</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z" />
                        </svg>
                    </>
                ) : (
                    <>
                        <span className="text-sm font-medium">Desktop</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                        </svg>
                    </>
                )}
            </button>
            <button
                onClick={onToggleRightSidebar}
                className={`${layoutMode === 'desktop' ? 'lg:hidden' : ''} text-brand-text-secondary hover:text-brand-text-main p-1 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-primary`}
                aria-label="Toggle study tools"
            >
                 <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" />
                </svg>
            </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
