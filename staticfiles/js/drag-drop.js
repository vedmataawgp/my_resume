// drag-drop.js - Common drag and drop functionality for file uploads

document.addEventListener('DOMContentLoaded', function() {
    // Find all drop areas in the page
    const dropAreas = document.querySelectorAll('.drop-area');
    
    // Apply event listeners to each drop area
    dropAreas.forEach(dropArea => {
        const fileInput = dropArea.querySelector('input[type="file"]');
        if (!fileInput) return;
        
        // Prevent default behaviors for drag events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.classList.add('highlight');
        }
        
        function unhighlight() {
            dropArea.classList.remove('highlight');
        }
        
        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            // Check if fileInput accepts multiple files
            if (fileInput.multiple) {
                const dataTransfer = new DataTransfer();
                for (let i = 0; i < files.length; i++) {
                    dataTransfer.items.add(files[i]);
                }
                fileInput.files = dataTransfer.files;
            } else {
                // If multiple files are dropped but the input only accepts one,
                // take just the first file
                if (files.length > 0) {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(files[0]);
                    fileInput.files = dataTransfer.files;
                }
            }
            
            // Trigger change event
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
        
        // Make the entire drop area clickable to open file selector
        dropArea.addEventListener('click', function(e) {
            // Prevent click if the click was on a button or input inside the drop area
            if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
                fileInput.click();
            }
        });
    });
});

/**
 * Validate files before allowing them to be dropped
 * @param {FileList} files - The files to validate
 * @param {string} acceptType - The accepted file type(s)
 * @returns {boolean} - Whether all files are valid
 */
function validateFiles(files, acceptType) {
    if (!files || files.length === 0) return false;
    
    // If accept type is for PDFs
    if (acceptType.includes('.pdf') || acceptType.includes('application/pdf')) {
        for (let i = 0; i < files.length; i++) {
            if (!validatePdfFile(files[i])) {
                showError(`${files[i].name} is not a valid PDF file.`);
                return false;
            }
        }
    }
    
    return true;
}
