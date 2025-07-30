
import React from 'react';
import { StreamItem, StreamItemType } from '../types';
import { Icon } from './Icon';
import { Resizer } from './Resizer';

interface LeftSidebarProps {
  weeks: string[];
  weekDisplayNames: Record<string, string>;
  selectedWeek: string | null;
  onSelectWeek: (week: string) => void;
  streamItemsByWeek: Record<string, StreamItem[]>;
  activeItemId: string | null;
  onSelectItem: (itemId: string) => void;
  isOpen: boolean;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  width: number;
  isResizing: boolean;
  onResizeStart: (e: React.MouseEvent) => void;
  layoutMode: 'desktop' | 'mobile';
}

const getItemTitle = (item: StreamItem) => {
    if (item.type === StreamItemType.ASSIGNMENT) {
        return item.content; // It's already a short title like 'Assignment: "..."'
    }
    // For announcements, find the first bolded text as a title
    const boldMatch = item.content.match(/\*\*(.*?)\*\*/);
    if (boldMatch && boldMatch[1]) {
        return boldMatch[1].replace(/\n/g, ' ').trim(); // Clean up newlines within title
    }
    // Fallback for announcements without bold text
    const plainText = item.content
        .replace(/\*\*|\*/g, '')
        .replace(/\n/g, ' ')
        .trim();
    return plainText.substring(0, 45) + (plainText.length > 45 ? '...' : '');
};


const LeftSidebar: React.FC<LeftSidebarProps> = ({
  weeks,
  weekDisplayNames,
  selectedWeek,
  onSelectWeek,
  streamItemsByWeek,
  activeItemId,
  onSelectItem,
  isOpen,
  isCollapsed,
  onToggleCollapse,
  width,
  isResizing,
  onResizeStart,
  layoutMode
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  };

   const sidebarClasses = `
    bg-brand-surface border-r border-brand-border flex flex-col
    fixed inset-y-0 left-0 z-40 w-80 transform transition-transform duration-300 ease-in-out
    ${isOpen ? 'translate-x-0' : '-translate-x-full'}
    ${layoutMode === 'desktop' ? `
        lg:relative lg:translate-x-0 lg:inset-auto lg:z-auto lg:shrink-0
        ${isResizing ? 'lg:transition-none' : 'lg:transition-all'}
    ` : ''}
  `;
  
  const dynamicStyle = layoutMode === 'desktop' ? { flexBasis: isCollapsed ? '80px' : `${width}px` } : {};

  return (
    <aside className={sidebarClasses} style={dynamicStyle}>
      <div className={`p-4 border-b border-brand-border flex items-center h-[73px] transition-all ${isCollapsed && layoutMode === 'desktop' ? 'justify-center' : 'justify-between'}`}>
          <h2 className={`text-lg font-semibold text-brand-text-main transition-opacity ${isCollapsed && layoutMode === 'desktop' ? 'opacity-0 lg:hidden' : 'opacity-100'}`}>Course Weeks</h2>
      </div>

      <div className={`flex flex-col flex-1 overflow-hidden`}>
        <nav className={`flex-1 overflow-y-auto p-2 space-y-1 ${isCollapsed && layoutMode === 'desktop' ? 'overflow-x-hidden' : ''}`}>
          {weeks.map((week) => {
              const isSelected = selectedWeek === week;
              const weekItems = streamItemsByWeek[week] || [];
              const weekNumberMatch = weekDisplayNames[week]?.match(/\d+/);
              const weekNumber = weekNumberMatch ? weekNumberMatch[0] : '';
              
              return (
              <div key={week}>
                <button
                  onClick={() => onSelectWeek(week)}
                  title={isCollapsed && layoutMode === 'desktop' ? (weekDisplayNames[week] || `Week of ${formatDate(week)}`) : ''}
                  className={`w-full text-left px-3 py-2 rounded-md transition-all duration-200 flex items-center ${isCollapsed && layoutMode === 'desktop' ? 'justify-center' : 'justify-between'} ${
                    isSelected
                      ? 'bg-brand-primary text-white shadow-sm'
                      : 'text-brand-text-secondary hover:bg-gray-100'
                  }`}
                >
                  <div className={`transition-opacity ${isCollapsed && layoutMode === 'desktop' ? 'opacity-0 lg:hidden' : 'opacity-100'}`}>
                      <span className={`font-semibold ${isSelected ? 'text-white' : 'text-brand-text-main'}`}>
                          {weekDisplayNames[week] || `Week of ${formatDate(week)}`}
                      </span>
                      <span className={`block text-xs ${isSelected ? 'text-indigo-200' : 'text-gray-500'}`}>
                          {formatDate(week)}
                      </span>
                  </div>
                  <div className={`hidden ${isCollapsed && layoutMode === 'desktop' ? 'lg:flex' : ''} flex-col items-center`}>
                      <span className="font-bold text-lg">{weekNumber}</span>
                      <span className="text-xs -mt-1">Wk</span>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 transition-all duration-300 ${isCollapsed && layoutMode === 'desktop' ? 'opacity-0 lg:hidden' : ''} ${isSelected ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                {(isSelected && (!isCollapsed || layoutMode === 'mobile')) && (
                  <ul className="pl-4 mt-2 mb-1 border-l-2 border-indigo-100 space-y-1">
                      {weekItems.map(item => {
                          const isItemActive = item.id === activeItemId;
                          return (
                              <li key={item.id}>
                                  <a
                                      href={`#${item.id}`}
                                      onClick={(e) => { e.preventDefault(); onSelectItem(item.id); }}
                                      className={`w-full text-left px-3 py-2 text-xs rounded-r-md transition-colors flex items-center gap-3 ${
                                          isItemActive
                                          ? 'bg-indigo-100 text-brand-primary font-semibold'
                                          : 'text-brand-text-secondary hover:bg-gray-100 hover:text-brand-text-main'
                                      }`}
                                  >
                                  <div className="w-4 h-4 flex-shrink-0">
                                      <Icon type={item.type === StreamItemType.ASSIGNMENT ? 'assignment' : 'announcement'} />
                                  </div>
                                  <span className="flex-1 truncate">{getItemTitle(item)}</span>
                                  </a>
                              </li>
                          )
                      })}
                  </ul>
                )}
              </div>
            )
          })}
        </nav>
      </div>
      {layoutMode === 'desktop' && (
        <>
            <div className="p-2 border-t border-brand-border hidden lg:block">
                <button
                    onClick={onToggleCollapse}
                    className="w-full flex items-center justify-center p-2 rounded-md text-brand-text-secondary hover:bg-gray-100 hover:text-brand-primary transition-colors"
                    aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className={`h-6 w-6 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                    <span className={`ml-2 font-medium transition-opacity ${isCollapsed ? 'opacity-0 lg:hidden' : 'opacity-100'}`}>Collapse</span>
                </button>
            </div>
            {!isCollapsed && (
                <Resizer onResizeStart={onResizeStart} className="right-0 hidden lg:block" />
            )}
        </>
      )}
    </aside>
  );
};

export default LeftSidebar;
