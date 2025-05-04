/**
 * Admin JavaScript for Insight Sphere BD
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize TinyMCE for rich text editing if available
  if (typeof tinymce !== 'undefined') {
    initTinyMCE();
  }
  
  // Set up participant status toggles
  setupParticipantStatusToggles();
  
  // Set up certificate generation
  setupCertificateGeneration();
  
  // Set up sortable lists if SortableJS is available
  if (typeof Sortable !== 'undefined') {
    setupSortableLists();
  }
});

/**
 * Initialize TinyMCE editors
 */
function initTinyMCE() {
  tinymce.init({
    selector: 'textarea.editor',
    height: 400,
    menubar: false,
    plugins: [
      'advlist autolink lists link image charmap print preview anchor',
      'searchreplace visualblocks code fullscreen',
      'insertdatetime media table paste code help wordcount'
    ],
    toolbar: 'undo redo | formatselect | ' +
      'bold italic backcolor | alignleft aligncenter ' +
      'alignright alignjustify | bullist numlist outdent indent | ' +
      'removeformat | help',
    content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
  });
}

/**
 * Set up participant status toggles
 */
function setupParticipantStatusToggles() {
  const statusToggles = document.querySelectorAll('.participant-status-toggle');
  
  statusToggles.forEach(toggle => {
    toggle.addEventListener('change', function() {
      const userId = this.dataset.userId;
      const courseId = this.dataset.courseId;
      const completionStatus = this.checked;
      
      // Update participant status via AJAX
      fetch('/admin/participants/update-status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken()
        },
        body: `user_id=${userId}&course_id=${courseId}&completion_status=${completionStatus}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showNotification(data.message, 'success');
          
          // Enable certificate generation if applicable
          if (data.canGenerateCertificate) {
            const certButton = document.querySelector(`.generate-certificate[data-user-id="${userId}"][data-course-id="${courseId}"]`);
            if (certButton) {
              certButton.disabled = false;
            }
          }
        } else {
          showNotification(data.message, 'error');
        }
      })
      .catch(error => {
        console.error('Error updating status:', error);
        showNotification('Failed to update status.', 'error');
      });
    });
  });
}

/**
 * Set up certificate generation
 */
function setupCertificateGeneration() {
  const certButtons = document.querySelectorAll('.generate-certificate');
  
  certButtons.forEach(button => {
    button.addEventListener('click', function() {
      const userId = this.dataset.userId;
      const courseId = this.dataset.courseId;
      const templateId = document.querySelector('#certificate-template-select')?.value || '';
      
      // Generate certificate via AJAX
      fetch('/admin/certificate/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCsrfToken()
        },
        body: `user_id=${userId}&course_id=${courseId}&template_id=${templateId}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showNotification(data.message, 'success');
          
          // Update button state
          this.disabled = true;
          this.textContent = 'Certificate Sent';
          
          // Add link to certificate
          if (data.certificate_url) {
            const link = document.createElement('a');
            link.href = data.certificate_url;
            link.target = '_blank';
            link.className = 'btn btn-sm btn-secondary ml-2';
            link.textContent = 'View Certificate';
            this.parentNode.appendChild(link);
          }
        } else {
          showNotification(data.message, 'error');
        }
      })
      .catch(error => {
        console.error('Error generating certificate:', error);
        showNotification('Failed to generate certificate.', 'error');
      });
    });
  });
}

/**
 * Set up sortable lists for reordering content
 */
function setupSortableLists() {
  const sortableLists = document.querySelectorAll('.sortable-list');
  
  sortableLists.forEach(list => {
    Sortable.create(list, {
      handle: '.sort-handle',
      animation: 150,
      onEnd: function(evt) {
        const items = list.querySelectorAll('[data-item-id]');
        const orderData = [];
        
        items.forEach((item, index) => {
          orderData.push({
            id: item.dataset.itemId,
            order: index
          });
        });
        
        // Save new order via AJAX
        fetch(list.dataset.orderUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ items: orderData })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showNotification('Order updated successfully', 'success');
          }
        })
        .catch(error => {
          console.error('Error updating order:', error);
          showNotification('Failed to update order', 'error');
        });
      }
    });
  });
}

/**
 * Helper function to get CSRF token
 */
function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

/**
 * Display notification
 */
function showNotification(message, type = 'info') {
  // Use toastify or other notification library if available
  if (typeof Toastify !== 'undefined') {
    Toastify({
      text: message,
      duration: 3000,
      close: true,
      gravity: 'top',
      position: 'right',
      backgroundColor: type === 'success' ? '#4caf50' : 
                       type === 'error' ? '#f44336' : 
                       type === 'warning' ? '#ff9800' : '#2196f3'
    }).showToast();
    return;
  }
  
  // Fallback to alert for simplicity
  alert(message);
}
