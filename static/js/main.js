/**
 * Main JavaScript for Insight Sphere BD
 */

document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const menuToggle = document.querySelector('.btn-menu');
  const mainNav = document.querySelector('.main-nav');
  
  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', function() {
      mainNav.classList.toggle('active');
      this.setAttribute('aria-expanded', mainNav.classList.contains('active'));
    });
  }
  
  // Alert dismissal
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        alert.classList.add('fade-out');
        setTimeout(() => {
          alert.remove();
        }, 300);
      });
    }
  });
  
  // Handle video embeds
  setupVideoPlayers();
  
  // Initialize tooltips if Bootstrap is available
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  }
});

/**
 * Setup video players for YouTube and Vimeo
 */
function setupVideoPlayers() {
  const videoContainers = document.querySelectorAll('.video-container');
  
  videoContainers.forEach(container => {
    const videoType = container.dataset.videoType;
    const videoId = container.dataset.videoId;
    
    if (!videoType || !videoId) return;
    
    let embedHtml = '';
    
    if (videoType === 'youtube') {
      embedHtml = `<iframe src="https://www.youtube.com/embed/${videoId}" allowfullscreen></iframe>`;
    } else if (videoType === 'vimeo') {
      embedHtml = `<iframe src="https://player.vimeo.com/video/${videoId}" allowfullscreen></iframe>`;
    }
    
    if (embedHtml) {
      container.innerHTML = embedHtml;
    }
  });
}

/**
 * Format date string to readable format
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', options);
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: 'BDT')
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = 'BDT') {
  if (amount === 0) return 'Free';
  
  return new Intl.NumberFormat('en-BD', {
    style: 'currency',
    currency: currency
  }).format(amount);
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Whether email is valid
 */
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
}

/**
 * Validate form inputs
 * @param {HTMLFormElement} form - Form to validate
 * @returns {boolean} Whether form is valid
 */
function validateForm(form) {
  let isValid = true;
  
  // Reset previous validation
  form.querySelectorAll('.form-control').forEach(input => {
    input.classList.remove('is-invalid');
  });
  
  // Check required fields
  form.querySelectorAll('[required]').forEach(field => {
    if (!field.value.trim()) {
      field.classList.add('is-invalid');
      isValid = false;
    }
  });
  
  // Check email fields
  form.querySelectorAll('input[type="email"]').forEach(field => {
    if (field.value && !isValidEmail(field.value)) {
      field.classList.add('is-invalid');
      isValid = false;
    }
  });
  
  return isValid;
}
