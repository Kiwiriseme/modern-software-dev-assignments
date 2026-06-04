<template>
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #4f6ef7;
  --bg-main: #f5f7fa;
  --bg-white: #ffffff;
  --text-heading: #1a1a1a;
  --text-body: #666666;
  --text-aux: #999999;
  --cat-work: #3b82f6;
  --cat-study: #22c55e;
  --cat-life: #a855f7;
  --cat-idea: #f59e0b;
  --radius-sm: 8px;
  --radius-lg: 12px;
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-modal: 0 4px 16px rgba(0, 0, 0, 0.1);
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  font-family: var(--font-family);
  background: var(--bg-main);
  color: var(--text-body);
}

button {
  font-family: inherit;
}

input, textarea {
  font-family: inherit;
}
</style>
