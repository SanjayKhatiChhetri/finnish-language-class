
import React from 'react';
import { AttachmentType } from '../types';

interface IconProps {
  type: AttachmentType | 'assignment' | 'announcement';
  url?: string;
  title?: string;
  className?: string;
}

const getIconKey = (type: AttachmentType, url?: string, title?: string): string => {
  if (url?.includes('youtube.com') || url?.includes('youtu.be')) {
    return 'YOUTUBE';
  }
  if (url?.includes('zoom.us')) {
    return 'ZOOM';
  }
  // This handles the case where an mp3 was mis-typed as IMAGE by the parser
  if (title?.toLowerCase().endsWith('.mp3')) {
    return 'MP3';
  }
  return type;
};


export const Icon: React.FC<IconProps> = ({ type, url, title, className = "w-full h-full" }) => {

  const iconKey = (type !== 'assignment' && type !== 'announcement') 
    ? getIconKey(type as AttachmentType, url, title) 
    : type;

  const icons: Record<string, React.ReactNode> = {
    'assignment': (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    'announcement': (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-2.236 9.168-5.514C18.358 1.84 19.642 1 21 1v12c-1.358 0-2.642.84-3.832 1.514C15.625 17.236 12.1 19.474 8 19.474a4.001 4.001 0 01-2.564-1.026" />
      </svg>
    ),
    'YOUTUBE': (
        <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#FF0000">
            <path d="M21.582,6.186c-0.23-0.854-0.908-1.532-1.762-1.762C18.265,4,12,4,12,4S5.735,4,4.18,4.424c-0.854,0.23-1.532,0.908-1.762,1.762C2,7.735,2,12,2,12s0,4.265,0.418,5.814c0.23,0.854,0.908,1.532,1.762,1.762C5.735,20,12,20,12,20s6.265,0,7.818-0.424c0.854-0.23,1.532-0.908,1.762-1.762C22,16.265,22,12,22,12S22,7.735,21.582,6.186zM10,15.464V8.536L16,12L10,15.464z"/>
        </svg>
    ),
    'ZOOM': (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="4.8" fill="#2D8CFF"/>
        <path d="M8.75 11.2332C8.75 10.4691 9.38583 9.83325 10.1499 9.83325H12.9833L16.0833 7.41659V15.5833L12.9833 13.1666H10.1499C9.38583 13.1666 8.75 12.5308 8.75 11.7666V11.2332Z" fill="white"/>
      </svg>
    ),
    'MP3': (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#8E44AD">
          <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55c-2.21 0-4 1.79-4 4s1.79 4 4 4s4-1.79 4-4V7h4V3h-6z"/>
      </svg>
    ),
    DOCS: (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#4285F4">
        <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/>
      </svg>
    ),
    VIDEO: (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#DB4437">
        <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
      </svg>
    ),
    PDF: (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#DB4437">
        <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3.5h-2.5v4H21V11c0-.83-.67-1.5-1.5-1.5zM9 8.5H7.5v1H9c.28 0 .5-.22.5-.5s-.22-.5-.5-.5zm5.5 0h-2.5v1h2.5c.28 0 .5-.22.5-.5s-.22-.5-.5-.5z"/>
      </svg>
    ),
    LINK: (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#1a73e8">
        <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
      </svg>
    ),
    IMAGE: (
       <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#34A853">
        <path d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2l-.01-12zM17 14l-3-4-2 2.72-2-1.72-3 4V6h14v8z"/>
       </svg>
    ),
    DRIVE: (
      <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="#FFC107">
        <path d="M7.71 3.25L1.15 14.26l3.54 6.13l6.56-11.01L7.71 3.25zM22.85 14.26L16.29 3.25L12.75 9.38l6.56 11.01l3.54-6.13zM12 10.13L9.17 15.25h5.66L12 10.13z"/>
      </svg>
    ),
  };
  
  // Return the specific icon, or a fallback from the original type, or null
  return icons[iconKey] || icons[type] || null;
};
