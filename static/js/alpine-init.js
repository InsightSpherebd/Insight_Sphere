/**
 * Alpine.js initialization for Insight Sphere BD
 */

document.addEventListener('alpine:init', () => {
  // Admin dashboard data
  Alpine.data('adminDashboard', () => ({
    activeTab: 'overview',
    
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    
    isActiveTab(tab) {
      return this.activeTab === tab;
    }
  }));
  
  // CMS editor component
  Alpine.data('contentEditor', () => ({
    sections: ['hero', 'about', 'mission_vision', 'footer'],
    activeSection: 'hero',
    
    setActiveSection(section) {
      this.activeSection = section;
    },
    
    isActiveSection(section) {
      return this.activeSection === section;
    }
  }));
  
  // Certificate builder component
  Alpine.data('certificateBuilder', () => ({
    template: {
      name: '',
      background_url: '',
      html_template: ''
    },
    previewMode: false,
    
    previewCertificate() {
      this.previewMode = true;
      
      // Use setTimeout to give the DOM time to update
      setTimeout(() => {
        const previewFrame = document.getElementById('certificate-preview-frame');
        if (previewFrame) {
          const frameDoc = previewFrame.contentDocument || previewFrame.contentWindow.document;
          frameDoc.open();
          frameDoc.write(this.template.html_template);
          frameDoc.close();
        }
      }, 50);
    },
    
    editTemplate() {
      this.previewMode = false;
    },
    
    updateTemplate(template) {
      this.template = {...template};
    }
  }));
  
  // Course registration component
  Alpine.data('courseRegistration', () => ({
    course: null,
    registrationStep: 1,
    formData: {
      full_name: '',
      email: '',
      phone: ''
    },
    
    init() {
      // Get course data from data attribute
      const courseDataElement = document.getElementById('course-data');
      if (courseDataElement) {
        this.course = JSON.parse(courseDataElement.dataset.course);
      }
    },
    
    nextStep() {
      // Simple client-side validation
      if (this.registrationStep === 1) {
        if (!this.formData.full_name || !this.formData.email || !this.formData.phone) {
          alert('Please fill in all required fields');
          return;
        }
        
        if (!isValidEmail(this.formData.email)) {
          alert('Please enter a valid email address');
          return;
        }
      }
      
      this.registrationStep++;
    },
    
    prevStep() {
      this.registrationStep--;
    },
    
    submitRegistration() {
      // Form submission is handled by the HTML form
      // This is just for any additional client-side logic
      console.log('Registration submitted', this.formData);
    }
  }));
  
  // User dashboard component
  Alpine.data('userDashboard', () => ({
    activeTab: 'courses',
    
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    
    isActiveTab(tab) {
      return this.activeTab === tab;
    }
  }));
  
  // Video player component
  Alpine.data('videoPlayer', () => ({
    videoType: null,
    videoId: null,
    
    init() {
      this.videoType = this.$el.dataset.videoType;
      this.videoId = this.$el.dataset.videoId;
      this.setupPlayer();
    },
    
    setupPlayer() {
      if (!this.videoType || !this.videoId) return;
      
      let embedHtml = '';
      
      if (this.videoType === 'youtube') {
        embedHtml = `<iframe src="https://www.youtube.com/embed/${this.videoId}" allowfullscreen></iframe>`;
      } else if (this.videoType === 'vimeo') {
        embedHtml = `<iframe src="https://player.vimeo.com/video/${this.videoId}" allowfullscreen></iframe>`;
      }
      
      if (embedHtml) {
        this.$el.innerHTML = embedHtml;
      }
    }
  }));
});
