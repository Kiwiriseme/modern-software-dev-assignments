async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

let notesPage = 1;
let actionsPage = 1;

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const body = await fetchJSON(`/notes/?page=${notesPage}&page_size=5`);
  for (const n of body.items) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
  document.getElementById('notes-info').textContent =
    `Page ${body.page} of ${Math.ceil(body.total / body.page_size)} (${body.total} total)`;
  document.getElementById('notes-prev').disabled = notesPage <= 1;
  document.getElementById('notes-next').disabled = notesPage * body.page_size >= body.total;
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const body = await fetchJSON(`/action-items/?page=${actionsPage}&page_size=5`);
  for (const a of body.items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
  document.getElementById('actions-info').textContent =
    `Page ${body.page} of ${Math.ceil(body.total / body.page_size)} (${body.total} total)`;
  document.getElementById('actions-prev').disabled = actionsPage <= 1;
  document.getElementById('actions-next').disabled = actionsPage * body.page_size >= body.total;
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    notesPage = 1;
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    actionsPage = 1;
    loadActions();
  });

  document.getElementById('notes-prev').addEventListener('click', () => {
    if (notesPage > 1) { notesPage--; loadNotes(); }
  });
  document.getElementById('notes-next').addEventListener('click', () => {
    notesPage++; loadNotes();
  });
  document.getElementById('actions-prev').addEventListener('click', () => {
    if (actionsPage > 1) { actionsPage--; loadActions(); }
  });
  document.getElementById('actions-next').addEventListener('click', () => {
    actionsPage++; loadActions();
  });

  loadNotes();
  loadActions();
});
