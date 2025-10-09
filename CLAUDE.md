# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NCE-Flow is a New Concept English (新概念英语) online reading application - a pure static web application for language learning with sentence-level audio playback and bilingual support.

## Development Commands

### Local Development
```bash
# Start local development server (recommended)
python3 -m http.server 8080

# Alternative with Node.js
npx http-server -p 8080

# Open in browser
# http://localhost:8080
```

### Build/Deploy
No build process required - the project is ready for deployment to any static hosting platform (GitHub Pages, Vercel, Cloudflare Pages, etc.).

## Architecture Overview

### Core Technologies
- **Pure Static**: HTML5/CSS3/ES6+ JavaScript with zero dependencies
- **Web Audio API**: For precise audio playback control
- **LocalStorage**: User preferences persistence
- **LRC Format**: Audio synchronization with lyrics/timing data

### Key Files and Structure

#### Entry Points
- `index.html` - Main navigation (book + lesson listing)
- `lesson.html` - Individual lesson player with audio controls
- `book.html` - Legacy redirect for backward compatibility

#### Core JavaScript Modules
- `assets/app.js` - Language switching, UI controls, preferences
- `assets/lesson.js` - Audio playback, LRC parsing, sentence highlighting

#### Data Organization
- `static/data.json` - Metadata for all 4 books (348 total lessons)
- `NCE1/` to `NCE4/` - Audio and LRC files organized by book

### Audio Synchronization System

The app supports two LRC formats:
1. **Inline bilingual**: `[00:12.34]English | Chinese`
2. **Stacked format**: Alternating English/Chinese lines

Key components in `lesson.js`:
- `parseLRC()` - Parses LRC files into time-coded segments
- `updateSentenceHighlight()` - Highlights current sentence during playback
- `setupSentenceClickHandlers()` - Enables click-to-play from any sentence

### Language Display System

Three display modes managed in `app.js`:
- **EN**: English only
- **EN+CN**: Both languages visible
- **CN**: Chinese only

Uses segmented controls with LocalStorage persistence for user preferences.

## Development Patterns

### Adding New Lessons
1. Add lesson metadata to `static/data.json`
2. Place audio file in corresponding book folder (NCE1-NCE4)
3. Create corresponding LRC file with proper timing
4. Follow naming convention: `lesson-XX.mp3` and `lesson-XX.lrc`

### Audio Synchronization
- Precision timing is critical - ensure LRC timestamps match audio exactly
- Test playback at different speeds (0.75x - 2.5x)
- Verify sentence highlighting matches audio playback

### UI/UX Considerations
- Apple-inspired design with smooth transitions
- Mobile-first responsive layout
- Dark/light theme support based on system preferences
- Accessibility: semantic HTML, ARIA labels, keyboard navigation

## File Naming Conventions

- **Audio files**: `lesson-01.mp3`, `lesson-02.mp3`, etc.
- **LRC files**: `lesson-01.lrc`, `lesson-02.lrc`, etc.
- **Images**: Descriptive names with hyphens
- **JavaScript**: `app.js` (global), `lesson.js` (lesson-specific)

## Browser Support

- Modern browsers with Web Audio API support
- Progressive enhancement for older browsers
- Mobile-friendly touch interactions
- Works offline once loaded (service worker not implemented)

## Performance Considerations

- Zero external dependencies for fast loading
- Optimized for static hosting with minimal assets
- Efficient audio preloading and caching
- Minimal DOM manipulation for smooth playback