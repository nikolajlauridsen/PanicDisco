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
      audio.play();
      activeButton = button;
      button.textContent = 'Stop';
      button.setAttribute('aria-pressed', 'true');
    });
  });

  audio.addEventListener('ended', stopPlayback);
});
