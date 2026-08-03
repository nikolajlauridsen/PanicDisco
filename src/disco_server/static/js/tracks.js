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
      if (activeButton && row.contains(activeButton)) {
        stopPlayback();
      }

      try {
        const response = await fetch(button.dataset.deleteUrl, { method: 'DELETE' });
        if (response.status === 204) {
          row.remove();
          return;
        }
        alert(`Could not delete track (${response.status}).`);
      } catch (err) {
        alert('Could not reach the server. Please check your connection and try again.');
      }
    });
  });
});
