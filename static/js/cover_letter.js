document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('generateCoverLetterBtn');
    if (!btn) {
      return;
    }
    btn.addEventListener('click', function() {
        const desc = document.getElementById('jobDescriptionRaw').textContent || '';
        const output = document.getElementById('coverLetterOutput');
        output.innerHTML = '<div class="text-info">Generating cover letter...</div>';
        fetch('/cover-letter/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ job_description: desc })
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.cover_letter) {
                output.innerHTML = `<pre class="bg-light p-3 border rounded">${data.cover_letter}</pre>`;
            } else {
                output.innerHTML = `<div class="text-danger">${data.error || 'Failed to generate cover letter.'}</div>`;
            }
        })
        .catch(() => {
            output.innerHTML = '<div class="text-danger">Error contacting server.</div>';
        });
    });
});
