document.addEventListener('DOMContentLoaded', () => {
  const audio = new Audio();
  let activeButton = null;

  function setIdle(button) {
    button.textContent = 'Play';
    button.setAttribute('aria-pressed', 'false');
  }

  function stopPlayback() {
    audio.pause();
    audio.currentTime = 0;
    if (activeButton) {
      setIdle(activeButton);
      activeButton = null;
    }
  }

  document.querySelectorAll('.preview-toggle').forEach((button) => {
    button.addEventListener('click', () => {
      const wasActive = activeButton === button;
      stopPlayback();
      if (wasActive) {
        return;
      }

      audio.src = button.dataset.src;
      const cuePoint = Number(button.dataset.cuePoint || 0);
      audio.addEventListener('loadedmetadata', () => {
        audio.currentTime = cuePoint;
        audio.play();
      }, { once: true });
      activeButton = button;
      button.textContent = 'Stop';
      button.setAttribute('aria-pressed', 'true');
    });
  });

  audio.addEventListener('ended', stopPlayback);

  document.querySelectorAll('.track-delete').forEach((button) => {
    button.addEventListener('click', async () => {
      if (!confirm(`Delete "${button.dataset.name}"? This cannot be undone.`)) {
        return;
      }

      const row = button.closest('tr');
      const editRow = row.nextElementSibling;
      if (activeButton && row.contains(activeButton)) {
        stopPlayback();
      }

      try {
        const response = await fetch(button.dataset.deleteUrl, { method: 'DELETE' });
        if (response.status === 204) {
          row.remove();
          if (editRow && editRow.classList.contains('edit-row')) {
            editRow.remove();
          }
          return;
        }
        alert(`Could not delete track (${response.status}).`);
      } catch (err) {
        alert('Could not reach the server. Please check your connection and try again.');
      }
    });
  });

  function formatCuePoint(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  }

  let openEditRow = null;

  function closeEditRow(editRow) {
    editRow.classList.add('hidden');
    editRow.querySelector('.edit-audio').pause();
    editRow.querySelector('.edit-error').classList.add('hidden');
    editRow.previousElementSibling.classList.remove('hidden');
    if (openEditRow === editRow) {
      openEditRow = null;
    }
  }

  document.querySelectorAll('.track-edit').forEach((button) => {
    const row = button.closest('tr');
    const editRow = row.nextElementSibling;
    const nameInput = editRow.querySelector('.edit-name');
    const cuePointInput = editRow.querySelector('.edit-cue-point');
    const cueDisplay = editRow.querySelector('.edit-cue-display');
    const audio = editRow.querySelector('.edit-audio');
    const errorBox = editRow.querySelector('.edit-error');

    button.addEventListener('click', () => {
      if (openEditRow === editRow) {
        closeEditRow(editRow);
        return;
      }

      if (openEditRow) {
        closeEditRow(openEditRow);
      }

      stopPlayback();
      row.classList.add('hidden');
      editRow.classList.remove('hidden');
      openEditRow = editRow;

      const cuePoint = Number(cuePointInput.value || 0);
      audio.addEventListener('loadedmetadata', () => {
        audio.currentTime = cuePoint;
      }, { once: true });
      audio.load();
    });

    editRow.querySelector('.edit-mark-cue').addEventListener('click', () => {
      cuePointInput.value = Math.round(audio.currentTime);
      cueDisplay.textContent = formatCuePoint(Number(cuePointInput.value));
    });

    cuePointInput.addEventListener('input', () => {
      const value = cuePointInput.value;
      cueDisplay.textContent = value === '' ? 'not set' : formatCuePoint(Number(value));
    });

    editRow.querySelector('.edit-cancel').addEventListener('click', () => {
      nameInput.value = nameInput.defaultValue;
      cuePointInput.value = cuePointInput.defaultValue;
      cueDisplay.textContent = formatCuePoint(Number(cuePointInput.defaultValue));
      errorBox.classList.add('hidden');
      closeEditRow(editRow);
    });

    editRow.querySelector('.edit-save').addEventListener('click', async () => {
      errorBox.classList.add('hidden');

      try {
        const response = await fetch(button.dataset.updateUrl, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: nameInput.value,
            cue_point: Number(cuePointInput.value),
            path: editRow.dataset.path,
          }),
        });

        if (response.status === 204) {
          row.children[0].textContent = nameInput.value;
          row.children[1].textContent = formatCuePoint(Number(cuePointInput.value));
          row.querySelector('.preview-toggle').dataset.cuePoint = cuePointInput.value;
          nameInput.defaultValue = nameInput.value;
          cuePointInput.defaultValue = cuePointInput.value;
          closeEditRow(editRow);
          return;
        }

        const body = await response.json().catch(() => null);
        errorBox.textContent = body?.error ?? `Could not save track (${response.status}).`;
        errorBox.classList.remove('hidden');
      } catch (err) {
        errorBox.textContent = 'Could not reach the server. Please check your connection and try again.';
        errorBox.classList.remove('hidden');
      }
    });
  });
});
