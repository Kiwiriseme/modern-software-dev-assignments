async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes(q) {
  const list = document.getElementById("notes");
  list.innerHTML = "";
  const url = q ? `/notes/search/?q=${encodeURIComponent(q)}` : "/notes/";
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement("li");

    const span = document.createElement("span");
    span.textContent = `${n.title}: ${n.content}`;
    li.appendChild(span);

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.onclick = () => editNote(n);
    li.appendChild(editBtn);

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.onclick = async () => {
      await fetchJSON(`/notes/${n.id}`, { method: "DELETE" });
      loadNotes();
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

async function editNote(note) {
  const title = prompt("New title:", note.title);
  const content = prompt("New content:", note.content);
  if (title !== null && content !== null) {
    await fetchJSON(`/notes/${note.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
    loadNotes();
  }
}
//从服务器获取笔记列表，然后在网页上显示出来
async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
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
}
//当用户填写表单并提交时，把数据发送给服务器，然后刷新显示
window.addEventListener('DOMContentLoaded', () => {
  const noteForm = document.getElementById('note-form');
  const noteTitle = document.getElementById('note-title');
  const noteContent = document.getElementById('note-content');
  const actionForm = document.getElementById('action-form');
  const actionDesc = document.getElementById('action-desc');
  const noteSearch = document.getElementById('note-search');

  if (noteForm) {
    noteForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = noteTitle.value;
      const content = noteContent.value;
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      e.target.reset();
      loadNotes();
    });
  }

  if (actionForm) {
    actionForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const description = actionDesc.value;
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      e.target.reset();
      loadActions();
    });
  }

  if (noteSearch) {
    noteSearch.addEventListener('input', (e) => {
      loadNotes(e.target.value);
    });
  }

  loadNotes();
  loadActions();
});
