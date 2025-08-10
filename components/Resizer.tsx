
import React from 'react';

interface ResizerProps {
  onResizeStart: (event: React.MouseEvent<HTMLDivElement>) => void;
  className?: string;
}

export const Resizer: React.FC<ResizerProps> = ({ onResizeStart, className = '' }) => {
  return (
    <div
      onMouseDown={onResizeStart}
      className={`absolute top-0 bottom-0 w-2 cursor-col-resize group ${className}`}
      // Prevent event bubbling to avoid closing modals/sidebars when starting a resize
      onClick={(e) => e.stopPropagation()}
    >
      <div className="w-0.5 h-full bg-transparent group-hover:bg-brand-primary transition-colors duration-200 mx-auto" />
    </div>
  );
};
