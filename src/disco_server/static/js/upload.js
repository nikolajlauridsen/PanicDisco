document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('upload-form');
  const dropZone = document.getElementById('drop-zone');
  const dropZoneText = document.getElementById('drop-zone-text');
  const fileInput = document.getElementById('file-input');
  const previewPlayer = document.getElementById('preview-player');
  const markCueBtn = document.getElementById('mark-cue-btn');
  const cueDisplay = document.getElementById('cue-display');
  const cuePointInput = document.getElementById('cue-point-input');
  const submitBtn = document.getElementById('submit-btn');
  const errorBox = document.getElementById('upload-error');

  const ACCEPTED_EXTENSIONS = ['mp3', 'wav', 'flac'];
  let selectedFile = null;

  function formatCuePoint(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
  }

  function clearError() {
    errorBox.textContent = '';
    errorBox.classList.add('hidden');
  }

  function updateCueDisplay() {
    const value = cuePointInput.value;
    if (value === '' || Number(value) < 0) {
      cueDisplay.textContent = 'not set';
      submitBtn.disabled = true;
      return;
    }
    cueDisplay.textContent = formatCuePoint(Number(value));
    submitBtn.disabled = false;
  }

  function resetCuePoint() {
    cuePointInput.value = '';
    updateCueDisplay();
  }

  function handleFileSelected(file) {
    if (!file) {
      return;
    }

    const extension = file.name.split('.').pop().toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      showError('Unsupported file type — please choose an mp3, wav, or flac file.');
      return;
    }

    clearError();
    selectedFile = file;
    dropZoneText.textContent = file.name;
    previewPlayer.src = URL.createObjectURL(file);
    previewPlayer.classList.remove('hidden');
    markCueBtn.disabled = false;
    resetCuePoint();
  }

  dropZone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => handleFileSelected(e.target.files[0]));

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-indigo-600', 'bg-indigo-50');
  });

  dropZone.addEventListener('dragleave', (e) => {
    if (dropZone.contains(e.relatedTarget)) {
      return;
    }
    dropZone.classList.remove('border-indigo-600', 'bg-indigo-50');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-indigo-600', 'bg-indigo-50');
    handleFileSelected(e.dataTransfer.files[0]);
  });

  window.addEventListener('dragover', (e) => e.preventDefault());
  window.addEventListener('drop', (e) => e.preventDefault());

  markCueBtn.addEventListener('click', () => {
    cuePointInput.value = Math.round(previewPlayer.currentTime);
    updateCueDisplay();
  });

  cuePointInput.addEventListener('input', updateCueDisplay);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();

    if (!selectedFile) {
      showError('Please choose a file first.');
      return;
    }

    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('name', document.getElementById('name-input').value);
    formData.append('cue_point', cuePointInput.value);

    try {
      const response = await fetch(form.dataset.uploadUrl, { method: 'POST', body: formData });

      if (response.status === 201) {
        window.location.href = '/';
        return;
      }

      const body = await response.json().catch(() => null);
      showError(body?.error ?? `Upload failed (${response.status}).`);
      submitBtn.disabled = false;
    } catch (err) {
      showError('Could not reach the server. Please check your connection and try again.');
      submitBtn.disabled = false;
    }
  });
});
