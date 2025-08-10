
import React, { useState, useRef, useEffect } from 'react';
import { AiContent, Summary, LearnMore } from '../types';
import { Loader } from './Loader';
import { Resizer } from './Resizer';

interface RightSidebarProps {
  content: AiContent | null;
  isLoading: boolean;
  error: string | null;
  onSummarize: () => void;
  onLearnMore: (topic: string) => void;
  notes: string;
  onNotesChange: (notes: string) => void;
  isOpen: boolean;
  onClose: () => void;
  width: number;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isResizing: boolean;
  onResizeStart: (e: React.MouseEvent) => void;
  layoutMode: 'desktop' | 'mobile';
}

const basicMarkdownToHtml = (text: string) => {
    if(!text) return '';
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-gray-200 text-red-600 font-mono text-sm px-1 py-0.5 rounded">$1</code>');
    
    const listRegex = /((\r\n|\n)?((  )*?|(\t*?))(\*|\-|\+) ([^\r\n|\n]*))+/g;
    html = html.replace(listRegex, (match) => {
        const listItems = match.trim().split('\n').map(item => `<li>${item.substring(2)}</li>`).join('');
        return `<ul class="list-disc list-inside space-y-1">${listItems}</ul>`;
    });
    
    return html.split('\n').map(p => p.trim() ? `<p>${p}</p>` : '<br/>').join('');
}


const SummaryView: React.FC<{ summary: Summary }> = ({ summary }) => (
    <div className="space-y-6">
        <div>
            <h3 className="text-xl font-bold text-brand-text-main mb-3">{summary.title}</h3>
        </div>
        <div>
            <h4 className="text-lg font-semibold text-brand-text-main mb-3 border-b pb-2">Key Points</h4>
            <ul className="list-disc list-inside space-y-2 text-brand-text-secondary">
            {summary.keyPoints.map((point, index) => (
                <li key={index}>{point}</li>
            ))}
            </ul>
        </div>
        {summary.upcomingAssignments && summary.upcomingAssignments.length > 0 && (
            <div>
            <h4 className="text-lg font-semibold text-brand-text-main mb-3 border-b pb-2">Upcoming Assignments</h4>
            <div className="space-y-3">
                {summary.upcomingAssignments.map((assignment, index) => (
                <div key={index} className="bg-gray-50 p-3 rounded-lg flex justify-between items-center">
                    <p className="font-medium text-brand-text-main">{assignment.title}</p>
                    <span className="text-sm text-red-600 font-semibold bg-red-100 px-2 py-1 rounded-full whitespace-nowrap">{assignment.dueDate}</span>
                </div>
                ))}
            </div>
            </div>
        )}
    </div>
);

const LearnMoreView: React.FC<{ content: LearnMore }> = ({ content }) => (
    <div className="space-y-4">
        <h3 className="text-xl font-bold text-brand-text-main mb-3">{content.title}</h3>
        <div 
            className="prose prose-sm max-w-none text-brand-text-secondary"
            dangerouslySetInnerHTML={{ __html: basicMarkdownToHtml(content.explanation) }} 
        />
    </div>
);


const RightSidebar: React.FC<RightSidebarProps> = ({ 
    content, 
    isLoading, 
    error, 
    onSummarize, 
    onLearnMore, 
    notes, 
    onNotesChange, 
    isOpen, 
    onClose,
    width,
    isCollapsed,
    onToggleCollapse,
    isResizing,
    onResizeStart,
    layoutMode
}) => {
  const [learnMoreTopic, setLearnMoreTopic] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [wasSaved, setWasSaved] = useState(false);
  const typingTimeoutRef = useRef<number | null>(null);
  const savedTimeoutRef = useRef<number | null>(null);

  const handleLearnMoreSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLearnMore(learnMoreTopic);
  };

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onNotesChange(e.target.value);

    setIsTyping(true);
    setWasSaved(false);

    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    if (savedTimeoutRef.current) clearTimeout(savedTimeoutRef.current);

    typingTimeoutRef.current = window.setTimeout(() => {
        setIsTyping(false);
        setWasSaved(true);
        savedTimeoutRef.current = window.setTimeout(() => {
            setWasSaved(false);
        }, 2000);
    }, 1000);
  };

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
      if (savedTimeoutRef.current) clearTimeout(savedTimeoutRef.current);
    };
  }, []);


  const sidebarClasses = `
    bg-brand-surface border-l border-brand-border flex flex-col
    fixed inset-y-0 right-0 z-40 w-full max-w-md transform transition-transform duration-300 ease-in-out
    ${isOpen ? 'translate-x-0' : 'translate-x-full'}
    ${layoutMode === 'desktop' ? `
        lg:relative lg:translate-x-0 lg:inset-auto lg:z-auto lg:shrink-0 lg:max-w-none
        ${isResizing ? 'lg:transition-none' : 'lg:transition-all'}
    ` : ''}
  `;
  
  const dynamicStyle = layoutMode === 'desktop' ? { flexBasis: isCollapsed ? '80px' : `${width}px` } : {};

  return (
    <aside className={sidebarClasses} style={dynamicStyle}>
      {layoutMode === 'desktop' && !isCollapsed && (
        <Resizer onResizeStart={onResizeStart} className="left-0 hidden lg:block" />
      )}
      <div className="p-4 border-b border-brand-border flex items-center justify-between h-[73px]">
          <h2 className={`text-lg font-semibold text-brand-text-main transition-opacity ${isCollapsed && layoutMode === 'desktop' ? 'opacity-0 lg:hidden' : 'opacity-100'}`}>Study Tools</h2>
          <div className={`hidden ${isCollapsed && layoutMode === 'desktop' ? 'lg:flex' : ''} items-center justify-center w-full h-full`}>
              <h2 className="transform -rotate-90 whitespace-nowrap font-semibold text-brand-text-secondary">Study Tools</h2>
          </div>
          <button
            onClick={onClose}
            className={`${layoutMode === 'desktop' ? 'lg:hidden' : ''} text-gray-400 hover:text-gray-700 transition-colors rounded-full p-1 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary`}
            aria-label="Close study tools"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
      </div>
      <div className={`flex-1 flex flex-col overflow-y-hidden ${isCollapsed && layoutMode === 'desktop' ? 'lg:hidden' : ''}`}>
        <div className="p-4 space-y-4">
            {/* AI Actions */}
            <div className="bg-gray-50 p-3 rounded-lg">
                <button
                    onClick={onSummarize}
                    disabled={isLoading}
                    className="w-full mb-3 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-primary hover:bg-brand-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300 disabled:cursor-not-allowed"
                >
                    {isLoading && content?.type !== 'summary' ? <Loader size="sm" /> : <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path d="M5 2a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1V3a1 1 0 00-1-1H5zM5 8a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1V9a1 1 0 00-1-1H5zM5 14a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1v-1a1 1 0 00-1-1H5zM15 2a1 1 0 00-1-1h-5a1 1 0 000 2h5a1 1 0 001-1zM9 9a1 1 0 000-2H8a1 1 0 100 2h1zm6 0a1 1 0 00-1-1h-2a1 1 0 100 2h2a1 1 0 001-1zM9 15a1 1 0 000-2H8a1 1 0 100 2h1zm6 0a1 1 0 00-1-1h-2a1 1 0 100 2h2a1 1 0 001-1z" /></svg>}
                    <span className="truncate">Summarize Week</span>
                </button>
                <form onSubmit={handleLearnMoreSubmit}>
                    <input
                        type="text"
                        value={learnMoreTopic}
                        onChange={(e) => setLearnMoreTopic(e.target.value)}
                        placeholder="Learn about a topic..."
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                        disabled={isLoading}
                    />
                </form>
            </div>
            {/* Notes */}
            <div>
                <div className="flex justify-between items-center mb-1">
                    <label htmlFor="notes" className="block text-sm font-medium text-brand-text-secondary">My Notes</label>
                    <span className={`text-xs text-brand-text-secondary transition-opacity duration-500 ${isTyping || wasSaved ? 'opacity-100' : 'opacity-0'}`}>
                        {isTyping ? 'Saving...' : 'Saved!'}
                    </span>
                </div>
                <textarea
                id="notes"
                value={notes}
                onChange={handleNotesChange}
                rows={6}
                className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="Jot down your notes here..."
                />
            </div>
        </div>
        
        <div className="px-4"><hr className="border-brand-border" /></div>

        <div className="p-4 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-brand-text-main flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-brand-primary" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.707-10.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 001.414 1.414L9 9.414V12a1 1 0 102 0V9.414l.293.293a1 1 0 001.414-1.414l-3-3z" clipRule="evenodd" />
                </svg>
                AI Output
            </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-6 pt-0">
                {isLoading && (
                    <div className="flex flex-col items-center justify-center h-full">
                    <Loader size="md" />
                    <p className="mt-4 text-brand-text-secondary">AI is thinking...</p>
                    </div>
                )}
                {error && <div className="text-red-600 bg-red-100 p-4 rounded-md text-sm">{error}</div>}
                {content && !isLoading && !error && (
                    <>
                        {content.type === 'summary' && <SummaryView summary={content.data} />}
                        {content.type === 'learnMore' && <LearnMoreView content={content.data} />}
                    </>
                )}
                {!isLoading && !error && !content && (
                    <div className="flex flex-col items-center justify-center h-full text-center text-brand-text-secondary">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <p className="mt-4 text-sm">AI results will appear here.</p>
                    </div>
                )}
            </div>
      </div>
       {layoutMode === 'desktop' && (
        <div className={`p-2 border-t border-brand-border hidden lg:block ${isCollapsed ? 'mt-auto' : ''}`}>
          <button
            onClick={onToggleCollapse}
            className="w-full flex items-center justify-center p-2 rounded-md text-brand-text-secondary hover:bg-gray-100 hover:text-brand-primary transition-colors"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className={`h-6 w-6 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
            <span className={`ml-2 font-medium transition-opacity ${isCollapsed ? 'opacity-0 lg:hidden' : 'opacity-100'}`}>Collapse</span>
          </button>
      </div>
      )}
    </aside>
  );
};

export default RightSidebar;
