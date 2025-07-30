
export enum AttachmentType {
  DOCS = 'DOCS',
  VIDEO = 'VIDEO',
  PDF = 'PDF',
  LINK = 'LINK',
  IMAGE = 'IMAGE',
  DRIVE = 'DRIVE',
}

export interface Attachment {
  type: AttachmentType;
  title: string;
  url: string;
}

export enum StreamItemType {
  ANNOUNCEMENT = 'ANNOUNCEMENT',
  ASSIGNMENT = 'ASSIGNMENT',
}

export interface StreamItem {
  id: string;
  type: StreamItemType;
  author: string;
  date: string;
  deleted: boolean;
  content: string;
  attachments: Attachment[];
}

export interface WeeklyData {
    display_name: string;
    items: StreamItem[];
}

export interface StreamDataMap {
    [weekKey: string]: WeeklyData;
}

export interface Summary {
    title: string;
    keyPoints: string[];
    upcomingAssignments: {
        title: string;
        dueDate: string;
    }[];
}

export interface LearnMore {
    title: string;
    explanation: string; 
}

export type CardViewMode = 'grid' | 'list';

export type AiContent = 
    | { type: 'summary'; data: Summary }
    | { type: 'learnMore'; data: LearnMore };
