// Global variable to hold the selected book ID
let selectedBookId = null;

// Called directly by the HTML onclick
function openBook(id, title, author) {
    selectedBookId = id;
    
    document.getElementById('rv-title').innerText = title;
    document.getElementById('rv-author').innerText = "by " + author;
    document.getElementById('rv-external-link').href = `https://openlibrary.org/search?q=${encodeURIComponent(title)}`;
    
    document.getElementById('book-grid-container').classList.add('hidden');
    document.getElementById('reading-view').classList.remove('hidden');
    
    document.getElementById('pasted-summary').value = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Called directly by the Back button onclick
function backToLibrary() {
    document.getElementById('reading-view').classList.add('hidden');
    document.getElementById('book-grid-container').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Called directly by the Submit button onclick
function submitSummary() {
    const summaryTextarea = document.getElementById('pasted-summary');
    const submitBtn = document.getElementById('submit-summary-btn');
    const pastedText = summaryTextarea.value.trim();

    if (pastedText.length < 100) {
        alert(`Please paste a proper summary! You need at least 100 characters. (You have ${pastedText.length})`);
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing...";

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/submit-reading/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            pages_read: 15, 
            book_id: selectedBookId || 1,
            summary_text: pastedText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/'; 
        } else {
            alert("Error: " + data.error);
            submitBtn.disabled = false;
            submitBtn.innerText = "Submit & Claim Reward";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred. Please try again.");
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit & Claim Reward";
    });
}