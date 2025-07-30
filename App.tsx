
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Header from './components/Header';
import LeftSidebar from './components/LeftSidebar';
import MainContent from './components/MainContent';
import RightSidebar from './components/RightSidebar';
import AttachmentViewerModal from './components/AttachmentViewerModal';
import { classroom_data as streamData } from './services/parser';
import { generateStreamSummary, learnMoreAbout } from './services/geminiService';
import { StreamItem, AiContent, Attachment, CardViewMode } from './types';

type LayoutMode = 'desktop' | 'mobile';

const App: React.FC = () => {
  const [streamItemsByWeek, setStreamItemsByWeek] = useState<Record<string, StreamItem[]>>({});
  const [weeks, setWeeks] = useState<string[]>([]);
  const [weekDisplayNames, setWeekDisplayNames] = useState<Record<string, string>>({});
  const [selectedWeek, setSelectedWeek] = useState<string | null>(null);
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  
  const [aiContent, setAiContent] = useState<AiContent | null>(null);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const [notes, setNotes] = useState<string>(() => localStorage.getItem('classroom-ai-notes') || '');
  const [viewingAttachment, setViewingAttachment] = useState<Attachment | null>(null);

  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(false);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);
  const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(false);
  const [isRightSidebarCollapsed, setIsRightSidebarCollapsed] = useState(false);
  
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(320);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(384);
  
  const [isResizing, setIsResizing] = useState<'left' | 'right' | null>(null);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('desktop');
  const [cardViewMode, setCardViewMode] = useState<CardViewMode>('grid');

  const courseInfo = {
      title: "FinnClass",
      description: "Finnish Language Class"
  };

  useEffect(() => {
    const savedLayout = localStorage.getItem('app-layout-mode') as LayoutMode;
    if (savedLayout) {
        setLayoutMode(savedLayout);
    }
    const savedCardView = localStorage.getItem('app-card-view-mode') as CardViewMode;
    if (savedCardView) {
        setCardViewMode(savedCardView);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('app-layout-mode', layoutMode);
  }, [layoutMode]);
  
  useEffect(() => {
    localStorage.setItem('app-card-view-mode', cardViewMode);
  }, [cardViewMode]);

  const handleToggleLayoutMode = useCallback(() => {
    setLayoutMode(prev => {
        const newMode = prev === 'desktop' ? 'mobile' : 'desktop';
        if (newMode === 'mobile') {
            setIsLeftSidebarCollapsed(false);
            setIsRightSidebarCollapsed(false);
        }
        return newMode;
    });
  }, []);

  const handleToggleCardViewMode = useCallback(() => {
    setCardViewMode(prev => (prev === 'grid' ? 'list' : 'grid'));
  }, []);


  const handleResizeStart = useCallback((side: 'left' | 'right', e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(side);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
        if (isResizing === 'left') {
            const newWidth = Math.max(50, Math.min(e.clientX, 500));
            setLeftSidebarWidth(newWidth);
        } else if (isResizing === 'right') {
            const newWidth = Math.max(50, Math.min(window.innerWidth - e.clientX, 640));
            setRightSidebarWidth(newWidth);
        }
    };

    const handleMouseUp = () => {
        const leftCollapseThreshold = 150;
        const rightCollapseThreshold = 200;

        setLeftSidebarWidth(currentWidth => {
            if (isResizing === 'left' && currentWidth < leftCollapseThreshold) {
                setIsLeftSidebarCollapsed(true);
            }
            return currentWidth;
        });

        setRightSidebarWidth(currentWidth => {
            if (isResizing === 'right' && currentWidth < rightCollapseThreshold) {
                setIsRightSidebarCollapsed(true);
            }
            return currentWidth;
        });
        
        setIsResizing(null);
    };

    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
    };
  }, [isResizing]);


  useEffect(() => {
    const mediaQuery = window.matchMedia('(min-width: 1024px)');
    const handleResize = () => {
        if (mediaQuery.matches && layoutMode === 'desktop') {
            setIsLeftSidebarOpen(false);
            setIsRightSidebarOpen(false);
        }
    };
    mediaQuery.addEventListener('change', handleResize);
    handleResize();
    return () => mediaQuery.removeEventListener('change', handleResize);
  }, [layoutMode]);

  const closeMobileSidebars = useCallback(() => {
    setIsLeftSidebarOpen(false);
    setIsRightSidebarOpen(false);
  }, []);

  useEffect(() => {
    const weekKeys = Object.keys(streamData).sort();
    
    const displayNames = Object.fromEntries(
        weekKeys.map(key => [key, streamData[key].display_name])
    );
    
    const itemsByWeek = Object.fromEntries(
        weekKeys.map(key => {
            const sortedItems = [...streamData[key].items].sort((a, b) => {
                const dateA = new Date(a.date);
                const dateB = new Date(b.date);
                return dateA.getTime() - dateB.getTime();
            });
            return [key, sortedItems];
        })
    );

    setWeekDisplayNames(displayNames);
    setStreamItemsByWeek(itemsByWeek);
    setWeeks(weekKeys);

    if (weekKeys.length > 0) {
        setSelectedWeek(weekKeys[0]);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('classroom-ai-notes', notes);
  }, [notes]);

  const handleSelectWeek = useCallback((week: string) => {
    setSelectedWeek(week);
    setActiveItemId(null); 
  }, []);
  
  const handleViewAttachment = useCallback((attachment: Attachment) => {
    setViewingAttachment(attachment);
  }, []);

  const handleCloseModal = useCallback(() => {
    setViewingAttachment(null);
  }, []);

  const handleSummarize = useCallback(async () => {
    if (!selectedWeek || !streamItemsByWeek[selectedWeek]) return;
    
    setAiContent(null);
    setAiError(null);
    setIsAiLoading(true);
    setActiveItemId(null);

    try {
      const weekItems = streamItemsByWeek[selectedWeek];
      const weekTitle = weekDisplayNames[selectedWeek] || `Week of ${selectedWeek}`;
      const result = await generateStreamSummary(weekItems, weekTitle);
      setAiContent({ type: 'summary', data: result });
    } catch (e) {
      console.error(e);
      setAiError('Failed to generate summary. Please try again.');
    } finally {
      setIsAiLoading(false);
    }
  }, [selectedWeek, streamItemsByWeek, weekDisplayNames]);

  const handleLearnMore = useCallback(async (topic: string) => {
    if (!topic.trim()) return;
    if (!selectedWeek || !streamItemsByWeek[selectedWeek]) return;

    setAiContent(null);
    setAiError(null);
    setIsAiLoading(true);
    setActiveItemId(null);

    try {
      const contextItems = streamItemsByWeek[selectedWeek];
      const result = await learnMoreAbout(topic, contextItems);
      setAiContent({ type: 'learnMore', data: result });
    } catch (e) {
      console.error(e);
      setAiError(`Failed to get details for "${topic}". Please try again.`);
    } finally {
      setIsAiLoading(false);
    }
  }, [selectedWeek, streamItemsByWeek]);
  
  const currentWeekItems = useMemo(() => {
    return selectedWeek ? streamItemsByWeek[selectedWeek] : [];
  }, [selectedWeek, streamItemsByWeek]);
  
  return (
    <div className="relative flex h-screen bg-brand-bg font-sans flex-col">
        {(isLeftSidebarOpen || isRightSidebarOpen) && (
            <div 
                onClick={closeMobileSidebars}
                className={`fixed inset-0 bg-black bg-opacity-50 z-30 ${layoutMode === 'desktop' ? 'lg:hidden' : ''}`}
                aria-hidden="true"
            />
        )}
        
        <Header
            title={courseInfo.title}
            description={courseInfo.description}
            onToggleLeftSidebar={() => setIsLeftSidebarOpen(prev => !prev)}
            onToggleRightSidebar={() => setIsRightSidebarOpen(prev => !prev)}
            layoutMode={layoutMode}
            onToggleLayoutMode={handleToggleLayoutMode}
        />
        <div className={`flex-1 overflow-hidden ${layoutMode === 'desktop' ? 'flex' : ''}`}>
            {isLeftSidebarCollapsed && layoutMode === 'desktop' && (
                <button
                    onClick={() => setIsLeftSidebarCollapsed(false)}
                    className="hidden lg:flex fixed top-1/2 -translate-y-1/2 left-0 z-20 bg-brand-surface hover:bg-brand-primary text-brand-text-secondary hover:text-white p-2 rounded-r-md shadow-lg transition-all items-center justify-center"
                    aria-label="Expand navigation"
                    title="Expand navigation"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                </button>
            )}

            <LeftSidebar 
                weeks={weeks}
                weekDisplayNames={weekDisplayNames}
                selectedWeek={selectedWeek}
                onSelectWeek={handleSelectWeek}
                streamItemsByWeek={streamItemsByWeek}
                activeItemId={activeItemId}
                onSelectItem={setActiveItemId}
                isOpen={isLeftSidebarOpen}
                isCollapsed={isLeftSidebarCollapsed}
                onToggleCollapse={() => setIsLeftSidebarCollapsed(prev => !prev)}
                width={leftSidebarWidth}
                isResizing={isResizing === 'left'}
                onResizeStart={(e) => handleResizeStart('left', e)}
                layoutMode={layoutMode}
            />
            <MainContent
                weekDisplayName={selectedWeek ? weekDisplayNames[selectedWeek] : 'Loading...'}
                items={currentWeekItems}
                activeItemId={activeItemId}
                onViewAttachment={handleViewAttachment}
                cardViewMode={cardViewMode}
                onToggleCardViewMode={handleToggleCardViewMode}
            />
            <RightSidebar
                content={aiContent}
                isLoading={isAiLoading}
                error={aiError}
                onSummarize={handleSummarize}
                onLearnMore={handleLearnMore}
                notes={notes}
                onNotesChange={setNotes}
                isOpen={isRightSidebarOpen}
                onClose={closeMobileSidebars}
                width={rightSidebarWidth}
                isCollapsed={isRightSidebarCollapsed}
                onToggleCollapse={() => setIsRightSidebarCollapsed(prev => !prev)}
                isResizing={isResizing === 'right'}
                onResizeStart={(e) => handleResizeStart('right', e)}
                layoutMode={layoutMode}
            />
        </div>
        
        {viewingAttachment && (
            <AttachmentViewerModal 
                attachment={viewingAttachment} 
                onClose={handleCloseModal} 
            />
        )}
        
        {isRightSidebarCollapsed && layoutMode === 'desktop' && (
             <button
                onClick={() => setIsRightSidebarCollapsed(false)}
                className="hidden lg:flex fixed top-1/2 -translate-y-1/2 right-0 z-20 bg-brand-surface hover:bg-brand-primary text-brand-text-secondary hover:text-white p-2 rounded-l-md shadow-lg transition-all items-center justify-center"
                aria-label="Expand study tools"
                title="Expand study tools"
            >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
            </button>
        )}
    </div>
  );
};

export default App;