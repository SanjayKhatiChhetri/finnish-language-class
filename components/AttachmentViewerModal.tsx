
import React, { useMemo } from 'react';
import { Attachment, AttachmentType } from '../types';

interface AttachmentViewerModalProps {
  attachment: Attachment;
  onClose: () => void;
}

interface EmbedInfo {
  type: 'iframe' | 'image' | 'audio' | 'unsupported';
  url: string;
}

const getEmbedInfo = (attachment: Attachment): EmbedInfo => {
    const { url, title, type } = attachment;

    // 1. Handle YouTube URLs
    const youtubeRegex = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const youtubeMatch = url.match(youtubeRegex);
    if (youtubeMatch && youtubeMatch[2].length === 11) {
        return { type: 'iframe', url: `https://www.youtube.com/embed/${youtubeMatch[2]}` };
    }
    
    // 2. Handle Google Drive URLs (covers file, open, and docs/sheets/slides inside drive)
    const driveRegex = /drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)/;
    const driveMatch = url.match(driveRegex);
    if (driveMatch && driveMatch[1]) {
        // All drive files can be previewed. This handles videos, images, pdfs, etc hosted on drive.
        return { type: 'iframe', url: `https://drive.google.com/file/d/${driveMatch[1]}/preview` };
    }
    
    // 3. Handle standalone Google Docs/Sheets/etc URLs
    const gdocsRegex = /docs\.google\.com\/(?:document|presentation|spreadsheets)\/d\/([a-zA-Z0-9_-]+)/;
    if (url.match(gdocsRegex)) {
        // Add /preview to embed it
        return { type: 'iframe', url: url.replace('/edit', '').replace(/\?.*$/, '') + '/preview' };
    }
    
    // 4. Handle direct media links by extension in URL or title
    const isImage = /\.(png|jpg|jpeg|gif|webp|svg)$/i.test(url) || /\.(png|jpg|jpeg|gif|webp|svg)$/i.test(title);
    if (isImage || (type === AttachmentType.IMAGE && !driveMatch)) {
        return { type: 'image', url: url };
    }
    
    const isAudio = /\.mp3$/i.test(url) || /\.mp3$/i.test(title);
    if (isAudio) {
        return { type: 'audio', url: url };
    }
    
    // 5. Fallback for other known embeddable types like generic video links
    if (type === AttachmentType.VIDEO) {
      // It might be a direct video link that can be iframed. Risky but worth a try.
      return { type: 'iframe', url: url };
    }

    // Default to unsupported
    return { type: 'unsupported', url };
};


const AttachmentViewerModal: React.FC<AttachmentViewerModalProps> = ({ attachment, onClose }) => {
  const embedInfo = useMemo(() => getEmbedInfo(attachment), [attachment]);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="attachment-title"
      className="fixed inset-0 bg-gray-900 bg-opacity-80 flex items-center justify-center p-4 z-50 transition-opacity"
      onClick={onClose}
    >
      <div
        className="bg-brand-surface rounded-xl shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 flex justify-between items-center border-b border-brand-border flex-shrink-0">
          <h2 id="attachment-title" className="text-lg font-semibold text-brand-text-main truncate pr-4">
            {attachment.title}
          </h2>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-700 transition-colors rounded-full p-1 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary"
            aria-label="Close attachment viewer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-grow bg-gray-200 flex items-center justify-center">
           {embedInfo.type === 'iframe' && (
            <iframe
                src={embedInfo.url}
                className="w-full h-full border-0 bg-white"
                title={attachment.title}
                allow="autoplay; encrypted-media; picture-in-picture"
                allowFullScreen
                sandbox="allow-scripts allow-same-origin allow-presentation"
            />
          )}
          {embedInfo.type === 'image' && (
            <div className="w-full h-full flex items-center justify-center overflow-auto p-4">
                <img
                    src={embedInfo.url}
                    alt={attachment.title}
                    className="max-w-full max-h-full object-contain block"
                />
            </div>
          )}
          {embedInfo.type === 'audio' && (
             <div className="p-4 w-full flex justify-center">
                <audio controls src={embedInfo.url} className="w-full max-w-lg">
                    Your browser does not support the audio element.
                </audio>
            </div>
          )}
           {embedInfo.type === 'unsupported' && (
              <div className="text-center p-8 bg-white rounded-lg shadow-inner">
                <h3 className="text-lg font-semibold text-brand-text-main mb-2">Preview not available</h3>
                <p className="text-brand-text-secondary mb-4">This content can't be shown here, but you can open it in a new tab.</p>
                <a 
                  href={embedInfo.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-primary hover:bg-brand-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Open in New Tab
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>
              </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default AttachmentViewerModal;
