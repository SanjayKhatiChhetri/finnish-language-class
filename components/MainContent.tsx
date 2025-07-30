import React, { useEffect } from 'react';
import StreamItemCard from './StreamItemCard';
import { StreamItem, Attachment, CardViewMode } from '../types';

interface MainContentProps {
  weekDisplayName: string;
  items: StreamItem[];
  activeItemId: string | null;
  onViewAttachment: (attachment: Attachment) => void;
  cardViewMode: CardViewMode;
  onToggleCardViewMode: () => void;
}

const GridIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
);

const ListIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5h11M9 12h11M9 19h11M5 5h.01M5 12h.01M5 19h.01" />
    </svg>
);

const MainContent: React.FC<MainContentProps> = ({ weekDisplayName, items, activeItemId, onViewAttachment, cardViewMode, onToggleCardViewMode }) => {

  useEffect(() => {
    if (activeItemId) {
      const element = document.getElementById(activeItemId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [activeItemId, items]);
  
  const layoutClasses = cardViewMode === 'grid'
    ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6'
    : 'flex flex-col gap-6 max-w-4xl mx-auto';

  return (
    <div className="flex-1 overflow-y-auto">
        <main className="max-w-full mx-auto p-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-brand-text-main">{weekDisplayName}</h2>
                <div className="hidden md:flex items-center">
                    <button
                        onClick={onToggleCardViewMode}
                        className="p-2 rounded-full text-brand-text-secondary hover:bg-gray-100 hover:text-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary"
                        aria-label={`Switch to ${cardViewMode === 'grid' ? 'list' : 'grid'} view`}
                        title={`Switch to ${cardViewMode === 'grid' ? 'list' : 'grid'} view`}
                    >
                        {cardViewMode === 'grid' ? <ListIcon /> : <GridIcon />}
                    </button>
                </div>
            </div>

            {items.length > 0 ? (
              <div className={layoutClasses}>
                {items.map((item) => (
                  <StreamItemCard 
                    key={item.id} 
                    item={item} 
                    activeItemId={activeItemId} 
                    onViewAttachment={onViewAttachment} 
                    cardViewMode={cardViewMode}
                  />
                ))}
              </div>
            ) : (
                <div className="text-center py-16 bg-brand-surface rounded-lg">
                    <p className="text-brand-text-secondary">No items to display for this week.</p>
                </div>
            )}
        </main>
    </div>
  );
};

export default MainContent;