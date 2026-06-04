<template>
  <router-view />
</template>

<style>
/* ============================================
   Zen Editorial Design System
   Inspired by Japanese book design & washi paper
   ============================================ */

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* ── Surface colors ── */
  --bg-page: #faf7f2;
  --bg-surface: #fffdf9;
  --bg-sidebar: #f3efe8;
  --bg-hover: #ede7dd;
  --bg-active: #e5ddd0;

  /* ── Text colors ── */
  --text-primary: #2d2418;
  --text-secondary: #6b5d4f;
  --text-muted: #9b8d7e;
  --text-inverse: #faf7f2;

  /* ── Accent colors ── */
  --accent: #4a6741;
  --accent-hover: #3d5535;
  --accent-soft: #e8efe5;
  --accent-warm: #b8734a;
  --accent-warm-hover: #a05f3a;

  /* ── Border colors ── */
  --border: #e5ddd0;
  --border-light: #f0ebe2;
  --border-focus: #b8a890;

  /* ── Category tag colors (muted, harmonious) ── */
  --cat-work: #5b7f95;
  --cat-work-bg: #e8eff4;
  --cat-study: #5a8a6a;
  --cat-study-bg: #e6f0e9;
  --cat-life: #b08a7a;
  --cat-life-bg: #f5ede9;
  --cat-idea: #c4a05a;
  --cat-idea-bg: #f9f2e3;
  --cat-default: #8b7e6a;
  --cat-default-bg: #f0ede6;

  /* ── Semantic colors ── */
  --success: #5a8a6a;
  --success-bg: #e6f0e9;
  --success-border: #b8d4be;
  --error: #c45a4a;
  --error-bg: #f9ece9;
  --error-border: #e8c4bc;

  /* ── Typography ── */
  --font-display: 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', 'SimSun', serif;
  --font-body: 'DM Sans', 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;

  /* ── Spacing scale ── */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-2xl: 32px;
  --space-3xl: 48px;

  /* ── Radii ── */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;

  /* ── Shadows (warm-toned) ── */
  --shadow-xs: 0 1px 2px rgba(45, 36, 24, 0.04);
  --shadow-sm: 0 2px 8px rgba(45, 36, 24, 0.05);
  --shadow-md: 0 4px 16px rgba(45, 36, 24, 0.07);
  --shadow-lg: 0 8px 32px rgba(45, 36, 24, 0.09);
  --shadow-xl: 0 16px 48px rgba(45, 36, 24, 0.12);

  /* ── Transitions ── */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* ── Layout ── */
  --sidebar-width: 220px;
  --detail-width: 380px;
}

/* ── Global resets ── */
html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  font-family: var(--font-body);
  background: var(--bg-page);
  color: var(--text-secondary);
  line-height: 1.6;
  letter-spacing: 0.01em;
  /* Subtle paper texture via CSS gradient noise */
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(180, 160, 140, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(160, 140, 120, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(200, 180, 150, 0.05) 0%, transparent 50%);
  transition: background-color var(--duration-slow) var(--ease-in-out),
              color var(--duration-slow) var(--ease-in-out);
}

/* ============================================
   Dark Theme — Midnight Study
   Deep navy-charcoal, calm and scholarly
   ============================================ */

[data-theme="dark"] {
  /* ── Surface colors ── */
  --bg-page: #1a1d23;
  --bg-surface: #21242b;
  --bg-sidebar: #1e2128;
  --bg-hover: #282c34;
  --bg-active: #2d313a;

  /* ── Text colors ── */
  --text-primary: #e4e8f0;
  --text-secondary: #8b909c;
  --text-muted: #5c6170;
  --text-inverse: #1a1d23;

  /* ── Accent colors ── */
  --accent: #8aabcf;
  --accent-hover: #9dbde0;
  --accent-soft: rgba(138, 171, 207, 0.12);
  --accent-warm: #c9a96e;
  --accent-warm-hover: #d4b87a;

  /* ── Border colors ── */
  --border: #2d313a;
  --border-light: #262a32;
  --border-focus: #4a5568;

  /* ── Category tag colors ── */
  --cat-work: #7b9fba;
  --cat-work-bg: rgba(123, 159, 186, 0.12);
  --cat-study: #7aaa8a;
  --cat-study-bg: rgba(122, 170, 138, 0.12);
  --cat-life: #c4a07e;
  --cat-life-bg: rgba(196, 160, 126, 0.12);
  --cat-idea: #d4b86a;
  --cat-idea-bg: rgba(212, 184, 106, 0.12);
  --cat-default: #8b909c;
  --cat-default-bg: rgba(139, 144, 156, 0.1);

  /* ── Semantic colors ── */
  --success: #7aaa8a;
  --success-bg: rgba(122, 170, 138, 0.1);
  --success-border: #4a6a5a;
  --error: #d48574;
  --error-bg: rgba(212, 133, 116, 0.1);
  --error-border: #8a554a;

  /* ── Shadows (cool-toned) ── */
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.35);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.4);
}

[data-theme="dark"] body {
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(100, 130, 160, 0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(80, 100, 130, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(120, 140, 160, 0.03) 0%, transparent 50%);
}

[data-theme="dark"] ::-webkit-scrollbar-thumb {
  background: var(--border);
}

[data-theme="dark"] ::-webkit-scrollbar-thumb:hover {
  background: var(--border-focus);
}

[data-theme="dark"] ::selection {
  background: rgba(138, 171, 207, 0.22);
  color: var(--text-primary);
}

/* ── Theme transition helpers ── */
.sidebar,
button,
input,
textarea,
select,
.nav-item,
.toast-container,
.detail-panel,
.content-area,
.note-card {
  transition: background-color var(--duration-slow) var(--ease-in-out),
              border-color var(--duration-slow) var(--ease-in-out),
              color var(--duration-slow) var(--ease-in-out),
              box-shadow var(--duration-slow) var(--ease-in-out);
}

/* ── Scrollbar styling ── */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--border-focus);
}

/* ── Selection styling ── */
::selection {
  background: rgba(74, 103, 65, 0.18);
  color: var(--text-primary);
}

/* ── Focus ring ── */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* ── Button base ── */
button {
  font-family: var(--font-body);
  cursor: pointer;
  border: none;
  background: none;
  font-size: inherit;
  color: inherit;
  transition: all var(--duration-fast) var(--ease-out);
}

/* ── Input base ── */
input, textarea, select {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  outline: none;
  transition: border-color var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}

input:focus, textarea:focus, select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

input::placeholder, textarea::placeholder {
  color: var(--text-muted);
}

/* ── Typography utility classes (used via :deep() in components) ── */
.display-text {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.body-text {
  font-family: var(--font-body);
  color: var(--text-secondary);
}

/* ── Animation: fade in up ── */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Animation: fade in ── */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ── Animation: slide in from right ── */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(16px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ── Animation: subtle pulse ── */
@keyframes subtlePulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
