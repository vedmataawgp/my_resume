document.addEventListener('DOMContentLoaded', function() {
    // Ad simulation
    const adOverlay = document.getElementById('ad-overlay');
    const adTimer = document.getElementById('ad-timer');
    const skipAdBtn = document.getElementById('skip-ad-btn');
    const videoContainer = document.getElementById('video-container');
    const videoIframe = document.getElementById('video-iframe');
    
    if (adOverlay && videoContainer && videoIframe) {
        let adDuration = 5; // Default ad duration in seconds
        let adInterval;
        
        // Function to update ad timer
        function updateAdTimer() {
            adTimer.textContent = `Ad: ${adDuration}s`;
            
            if (adDuration <= 0) {
                clearInterval(adInterval);
                adOverlay.style.display = 'none';
                videoContainer.classList.remove('blurred');
                
                // Load YouTube video if iframe is empty
                const videoId = videoIframe.getAttribute('data-video-id');
                if (videoIframe.src === "" && videoId) {
                    videoIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
                }
            } else {
                adDuration--;
            }
        }
        
        // Start ad timer
        if (adOverlay.style.display !== 'none') {
            updateAdTimer();
            adInterval = setInterval(updateAdTimer, 1000);
            
            // Skip ad button
            if (skipAdBtn) {
                // Initially hide skip button
                skipAdBtn.style.display = 'none';
                
                // Show skip button after 3 seconds
                setTimeout(() => {
                    skipAdBtn.style.display = 'block';
                    
                    skipAdBtn.addEventListener('click', function() {
                        clearInterval(adInterval);
                        adOverlay.style.display = 'none';
                        videoContainer.classList.remove('blurred');
                        
                        // Load YouTube video if iframe is empty
                        const videoId = videoIframe.getAttribute('data-video-id');
                        if (videoIframe.src === "" && videoId) {
                            videoIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
                        }
                    });
                }, 3000);
            }
        }
    }
    
    // Video modal
    const videoCards = document.querySelectorAll('.video-card');
    const videoModal = document.getElementById('video-modal');
    const modalVideoContainer = document.getElementById('modal-video-container');
    const closeModalBtn = document.querySelector('.close-modal');
    
    if (videoCards.length > 0 && videoModal && modalVideoContainer) {
        videoCards.forEach(card => {
            const playButton = card.querySelector('.play-btn');
            
            if (playButton) {
                playButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const videoId = this.getAttribute('data-video-id');
                    const videoTitle = card.querySelector('.video-title').textContent;
                    
                    // Set modal content
                    document.getElementById('modal-video-title').textContent = videoTitle;
                    
                    // Show modal
                    videoModal.style.display = 'flex';
                    document.body.style.overflow = 'hidden';
                    
                    // Start ad then load video
                    const modalAdOverlay = document.getElementById('modal-ad-overlay');
                    const modalAdTimer = document.getElementById('modal-ad-timer');
                    let adDuration = 5;
                    let adInterval;
                    
                    // Function to update ad timer
                    function updateModalAdTimer() {
                        modalAdTimer.textContent = `Ad: ${adDuration}s`;
                        
                        if (adDuration <= 0) {
                            clearInterval(adInterval);
                            modalAdOverlay.style.display = 'none';
                            
                            // Load YouTube video
                            const modalIframe = document.getElementById('modal-video-iframe');
                            modalIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
                        } else {
                            adDuration--;
                        }
                    }
                    
                    // Start ad timer
                    updateModalAdTimer();
                    adInterval = setInterval(updateModalAdTimer, 1000);
                });
            }
        });
        
        // Close modal
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', function() {
                videoModal.style.display = 'none';
                document.body.style.overflow = 'auto';
                
                // Stop video
                const modalIframe = document.getElementById('modal-video-iframe');
                modalIframe.src = '';
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === videoModal) {
                videoModal.style.display = 'none';
                document.body.style.overflow = 'auto';
                
                // Stop video
                const modalIframe = document.getElementById('modal-video-iframe');
                modalIframe.src = '';
            }
        });
    }
    
    // Download button (admin only)
    const downloadBtn = document.getElementById('download-video-btn');
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const videoId = this.getAttribute('data-video-id');
            
            // Show loading state
            const originalText = this.textContent;
            this.textContent = 'Downloading...';
            this.disabled = true;
            
            // Send AJAX request to download video
            fetch(`/ysearchplay/download/${videoId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('Video downloaded successfully!', 'success');
                    } else {
                        showNotification('Error downloading video: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showNotification('Error downloading video: ' + error, 'error');
                })
                .finally(() => {
                    // Reset button
                    this.textContent = originalText;
                    this.disabled = false;
                });
        });
    }
});
