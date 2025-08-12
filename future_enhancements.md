# 🌟 Finnish Language Class — Full Enhancement Roadmap
This roadmap outlines the next-level improvements for the app, transforming it from a great learning tool into a personalized, immersive, and scalable Finnish language platform.

## 🔮 AI Features & Smart Learning Tools

### 🧑‍🏫 AI Summarize Reimagined

Redesign the Study Tools layout:
- Move AI Summarize to the top section
- Make it conversational like a chat experience
- Persist chat history per week (e.g., Week 1, Week 33)

### ✍️ Personalized Quizzes
- Add a "Quiz Me" button per week
- Gemini generates MCQs using weekly data
- Output structured as JSON for easy rendering

### 🔊 Pronunciation Practice
- Let users record Finnish phrases
- Gemini analyzes and gives feedback on pronunciation quality

### 🖼️ Image-Based Vocabulary Builder
- Users upload images
- Gemini identifies objects and returns Finnish names

## 📝 Notes System Upgrade

### 📚 Contextual Notes
- Allow saving notes within specific week contexts
- e.g., “Save to Week 2,” “Save to Week 34”

### ✒️ Rich Text Editor
- Add formatting features:
- Bold / Italics / Underline
- Lists
- Emojis and hyperlinks
- Keyboard shortcuts like Ctrl+B

### 💾 Auto-Save Feedback
- Implement visible save indicator when writing notes

## 🎮 User Experience & Layout Enhancements

### 🧩 Sidebar & Layout Control
- Live Resizable Sidebars (Left & Right) with drag handles
- Auto-collapse when dragged below threshold
- Reopen Icons when sidebar is collapsed

### Toggle Layout Modes:
- Option 1: Mobile-style layout even on desktop
- Option 2: Classic multi-column view

### 🗂️ Week View Layout Toggle
Users can choose between:
- Grid layout
- Single-column list view
- Persist preferences in local storage

### 📦 Card UI Fixes
- Switch from hamburger menu to list view icon
- Cards auto-resize to fit their content in list view

## 🔔 Engagement Features

### 🏆 Gamification
- Daily streaks, points, badges
- Weekly challenges
- Leaderboard for tracking progress
- Personalized dashboard for tracking progress

### 🧠 Advanced Search
- Global search across all weeks for grammar rules, posts, vocabulary

### 📳 Push Notifications (PWA)
-  Remind users of tasks, quizzes, and study time
- Sync notes, preferences, summaries across devices
-  Users can opt in/out of push notifications

## 🛠️ Backend & Infrastructure

### 🗃️ State Management
- Refactor state logic using Zustand or Redux Toolkit
- Better organization and scalability

### ☁️ Database Integration
- Replace localStorage with Firebase or Supabase
- Sync notes, preferences, summaries across devices

###  🧪 Automated Testing
- Set up Vitest + React Testing Library
- Add unit tests for services & UI behavior

compiled into a Notion page, a GitHub project board, or a formatted pitch deck slide 🚀
