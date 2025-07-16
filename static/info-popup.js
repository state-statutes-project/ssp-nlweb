// Handle info popup
document.addEventListener('DOMContentLoaded', function() {
  const infoPopupOverlay = document.getElementById('infoPopupOverlay');
  const infoPopupClose = document.getElementById('infoPopupClose');
  
  // Check if popup has been shown before
  const hasSeenInfo = localStorage.getItem('nlweb-has-seen-info');
  
  // If user hasn't seen the info, show it
  if (!hasSeenInfo) {
    // Popup is already visible by default
  } else {
    // Hide popup if user has seen it before
    infoPopupOverlay.classList.add('hidden');
  }
  
  // Close popup when X is clicked
  if (infoPopupClose) {
    infoPopupClose.addEventListener('click', function() {
      infoPopupOverlay.classList.add('hidden');
      // Remember that user has seen the info
      localStorage.setItem('nlweb-has-seen-info', 'true');
    });
  }
  
  // Close popup when clicking outside
  infoPopupOverlay.addEventListener('click', function(e) {
    if (e.target === infoPopupOverlay) {
      infoPopupOverlay.classList.add('hidden');
      localStorage.setItem('nlweb-has-seen-info', 'true');
    }
  });
  
  // Close popup with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !infoPopupOverlay.classList.contains('hidden')) {
      infoPopupOverlay.classList.add('hidden');
      localStorage.setItem('nlweb-has-seen-info', 'true');
    }
  });
});