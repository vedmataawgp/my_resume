document.addEventListener('DOMContentLoaded', function() {
    // Only run this script if the video resources section exists
    const videoSection = document.getElementById('video-resources');
    if (!videoSection) return;
    
    // Focus on search input when page loads
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.focus();
    }
    
    // Common elements
    const youtubeIframe = document.getElementById('youtube-iframe');
    const playerSection = document.getElementById('player-section');
    
    // Function to play video by ID
    function playVideo(videoId) {
        if (videoId) {
            // Set iframe source to YouTube embed URL
            youtubeIframe.src = `https://www.youtube.com/embed/${videoId}`;
            // Show player section
            playerSection.style.display = 'block';
            // Scroll to player
            playerSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Handle form submission
    const youtubeForm = document.getElementById('youtube-form');
    const youtubeUrl = document.getElementById('youtube-url');
    
    if (youtubeForm) {
        youtubeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = youtubeUrl.value.trim();
            if (!url) return;
            
            // Extract video ID from URL
            let videoId = null;
            
            // Match pattern: youtube.com/watch?v=VIDEO_ID
            const regExp1 = /(?:youtube\.com\/watch\?v=)([^&]+)/;
            // Match pattern: youtu.be/VIDEO_ID
            const regExp2 = /(?:youtu\.be\/)([^?]+)/;
            // Match pattern: youtube.com/embed/VIDEO_ID
            const regExp3 = /(?:youtube\.com\/embed\/)([^?]+)/;
            
            const match1 = url.match(regExp1);
            const match2 = url.match(regExp2);
            const match3 = url.match(regExp3);
            
            if (match1) {
                videoId = match1[1];
            } else if (match2) {
                videoId = match2[1];
            } else if (match3) {
                videoId = match3[1];
            }
            
            if (videoId) {
                playVideo(videoId);
            } else {
                alert('Please enter a valid YouTube URL');
            }
        });
    }
    
    // Handle sample video buttons
    const sampleButtons = document.querySelectorAll('.sample-video-btn');
    sampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const videoId = this.getAttribute('data-video-id');
            playVideo(videoId);
        });
    });
});