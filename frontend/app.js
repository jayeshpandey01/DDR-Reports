document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const sampleInput = document.getElementById('sampleReport');
    const thermalInput = document.getElementById('thermalReport');
    const sampleName = document.getElementById('sampleName');
    const thermalName = document.getElementById('thermalName');
    const sampleDropZone = document.getElementById('sampleDropZone');
    const thermalDropZone = document.getElementById('thermalDropZone');
    
    const generateBtn = document.getElementById('generateBtn');
    const btnLoader = document.getElementById('btnLoader');
    const btnText = generateBtn.querySelector('span');
    
    const statusArea = document.getElementById('statusArea');
    const resultArea = document.getElementById('resultArea');
    const errorArea = document.getElementById('errorArea');
    
    // File Input Handlers
    sampleInput.addEventListener('change', (e) => updateFileName(e.target, sampleName, sampleDropZone));
    thermalInput.addEventListener('change', (e) => updateFileName(e.target, thermalName, thermalDropZone));

    // Drag and Drop Handlers
    setupDropZone(sampleDropZone, sampleInput);
    setupDropZone(thermalDropZone, thermalInput);

    function updateFileName(input, nameElement, dropZone) {
        if (input.files.length > 0) {
            nameElement.textContent = input.files[0].name;
            dropZone.classList.add('has-file');
        } else {
            nameElement.textContent = 'No file selected';
            dropZone.classList.remove('has-file');
        }
    }

    function setupDropZone(dropZone, inputElement) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                inputElement.files = files;
                const event = new Event('change');
                inputElement.dispatchEvent(event);
            } else {
                alert('Please upload a valid PDF file.');
            }
        });
    }

    // Form Submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!sampleInput.files.length || !thermalInput.files.length) {
            alert('Please select both the Sample Report and Thermal Images.');
            return;
        }

        // UI State Update
        generateBtn.disabled = true;
        btnText.textContent = 'Analyzing...';
        btnLoader.classList.remove('hidden');
        statusArea.classList.remove('hidden');
        resultArea.classList.add('hidden');
        errorArea.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('sample_report', sampleInput.files[0]);
            formData.append('thermal_images', thermalInput.files[0]);

            // Assuming typical local dev port or relative path
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                // Show Success
                statusArea.classList.add('hidden');
                resultArea.classList.remove('hidden');
                
                document.getElementById('downloadPdf').href = data.results.pdf_url;
                document.getElementById('downloadJson').href = data.results.json_url;
            } else {
                throw new Error(data.detail || 'Failed to generate report.');
            }
        } catch (error) {
            // Show Error
            statusArea.classList.add('hidden');
            errorArea.classList.remove('hidden');
            document.getElementById('errorText').textContent = error.message;
        } finally {
            // Reset Button
            generateBtn.disabled = false;
            btnText.textContent = 'Generate Report';
            btnLoader.classList.add('hidden');
        }
    });

    // Reset Handlers
    document.getElementById('resetBtn').addEventListener('click', resetForm);
    document.getElementById('retryBtn').addEventListener('click', resetForm);

    function resetForm() {
        uploadForm.reset();
        sampleName.textContent = 'No file selected';
        thermalName.textContent = 'No file selected';
        sampleDropZone.classList.remove('has-file');
        thermalDropZone.classList.remove('has-file');
        
        resultArea.classList.add('hidden');
        errorArea.classList.add('hidden');
        statusArea.classList.add('hidden');
    }
});
