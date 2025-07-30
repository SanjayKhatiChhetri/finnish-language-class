import React from 'react';
import { StreamItem, StreamItemType, Attachment, AttachmentType, CardViewMode } from '../types';
import { Icon } from './Icon';

interface StreamItemCardProps {
  item: StreamItem;
  activeItemId: string | null;
  onViewAttachment: (attachment: Attachment) => void;
  cardViewMode: CardViewMode;
}

const isEmbeddable = (type: AttachmentType) => {
    // The mis-typed mp3 is an IMAGE type, so it is correctly handled here.
    return [AttachmentType.PDF, AttachmentType.DOCS, AttachmentType.VIDEO, AttachmentType.IMAGE].includes(type);
};

const markdownToHtml = (text: string): string => {
  if (!text) return '';

  const emojiMap: Record<string, string> = {
    ':D': '😀',
    ':)': '🙂',
    ':-)': '🙂',
    ':(': '🙁',
    ':-(': '🙁',
    ';)': '😉',
    ';-)': '😉',
    ':o': '😮',
    ':O': '😮',
    ':p': '😛',
    ':P': '😛',
    '<3': '❤️',
    ':/': '😕',
    ':\\': '😕', // For markdown compatibility
    'xD': '😆',
    'XD': '😆',
    '=db=)': '👍', // Custom emoji as requested
  };
  
  let html = text;

  // Function to escape special regex characters
  const escapeRegex = (str: string) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // Replace emoticons first to avoid conflicts with markdown
  for (const emoticon in emojiMap) {
    // We use a global replace for each emoticon
    const regex = new RegExp(escapeRegex(emoticon), 'g');
    html = html.replace(regex, emojiMap[emoticon]);
  }
  
  // BOLD: Use the 's' (dotAll) flag to make `.` match newlines.
  // This will correctly format text like **\nTitle\n**
  html = html.replace(/\*\*(.*?)\*\*/gs, '<strong>$1</strong>');

  // LISTS: Find lines starting with * or - and wrap them in list tags.
  // The 'm' (multiline) flag is essential for ^ to match the start of each line.
  const listRegex = /^(?:\s*([*-])\s.*(?:\r?\n|$))+/gm;
  html = html.replace(listRegex, (match) => {
    const items = match.trim().split(/\r?\n/).map(item => {
      // Remove the markdown list character (* or -) and extra spaces
      const content = item.trim().replace(/^[*-]\s/, '');
      return `<li>${content}</li>`;
    }).join('');
    return `<ul class="list-disc list-inside space-y-1 my-2">${items}</ul>`;
  });

  // PARAGRAPHS: Wrap remaining text blocks in <p> tags.
  // We avoid wrapping our new <ul> blocks.
  const blocks = html.split(/(<ul.*<\/ul>)/gs);
  const result = blocks.map(block => {
    if (!block) return '';
    if (block.startsWith('<ul')) {
      return block; // It's a list, leave it as is.
    }
    // For other text, replace newlines with <br> and wrap in a <p> tag
    // if it's not just whitespace.
    if (block.trim() === '') {
      return '';
    }
    return `<p>${block.trim().replace(/\n/g, '<br />')}</p>`;
  }).join('');

  return result;
};


const AttachmentChip: React.FC<{ attachment: Attachment, onViewAttachment: (attachment: Attachment) => void }> = ({ attachment, onViewAttachment }) => {
    if (isEmbeddable(attachment.type)) {
        return (
            <button
                onClick={() => onViewAttachment(attachment)}
                className="inline-flex items-center gap-2 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full p-2 pr-4 text-sm text-gray-700 font-medium text-left"
            >
                <div className="w-6 h-6 flex-shrink-0">
                    <Icon type={attachment.type} url={attachment.url} title={attachment.title} />
                </div>
                <span className="truncate min-w-0">{attachment.title}</span>
            </button>
        );
    }

    return (
        <a
            href={attachment.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full p-2 pr-4 text-sm text-gray-700 font-medium"
        >
            <div className="w-6 h-6 flex-shrink-0">
                <Icon type={attachment.type} url={attachment.url} title={attachment.title} />
            </div>
            <span className="truncate min-w-0">{attachment.title}</span>
        </a>
    );
};

const StreamItemCard: React.FC<StreamItemCardProps> = ({ item, activeItemId, onViewAttachment, cardViewMode }) => {
  const isAssignment = item.type === StreamItemType.ASSIGNMENT;
  const isActive = item.id === activeItemId;

  const cardClasses = `bg-brand-surface rounded-lg shadow-md overflow-hidden transition-all flex flex-col ${
    cardViewMode === 'grid' ? 'grow shrink basis-80' : ''
  } ${
    item.deleted ? 'opacity-60 hover:opacity-100' : 'hover:opacity-100'
  } ${isActive ? 'ring-2 ring-offset-2 ring-brand-primary' : ''}`;

  return (
    <div id={item.id} className={cardClasses}>
      <div className="p-6 flex flex-col gap-4 flex-grow">
        {/* Author + Icon Header */}
        <div className="flex gap-4 items-center">
          <div
            className={`h-10 w-10 flex-shrink-0 flex items-center justify-center rounded-full ${
              isAssignment ? 'bg-indigo-100 text-indigo-600' : 'bg-green-100 text-green-600'
            }`}
          >
            <Icon type={isAssignment ? 'assignment' : 'announcement'} />
          </div>
          <div className="flex flex-col flex-1 min-w-0">
            <p className="text-sm font-semibold text-brand-text-main truncate">{item.author}</p>
            <p className="text-xs text-brand-text-secondary truncate">
              {item.date}
              {item.deleted && (
                <span className="ml-2 text-red-600 font-semibold">(Deleted)</span>
              )}
            </p>
          </div>
        </div>

        {/* Content Section */}
        <div
          className="text-brand-text-secondary prose prose-sm space-y-2 max-w-none flex-grow-initial"
          dangerouslySetInnerHTML={{ __html: markdownToHtml(item.content) }}
        />

        {/* Attachments */}
        {item.attachments.length > 0 && (
          <div className="border-t border-brand-border pt-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-3">Attachments</h4>
            <div className="flex flex-wrap gap-3">
              {item.attachments.map((att, index) => (
                <AttachmentChip key={index} attachment={att} onViewAttachment={onViewAttachment} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamItemCard;