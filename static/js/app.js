document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const gridContainer = document.getElementById('book-grid-container');
    const readingView = document.getElementById('reading-view');
    const backBtn = document.getElementById('back-to-grid-btn');
    const submitBtn = document.getElementById('submit-summary-btn');
    const summaryTextarea = document.getElementById('pasted-summary');
    
    const rvTitle = document.getElementById('rv-title');
    const rvAuthor = document.getElementById('rv-author');
    const rvLink = document.getElementById('rv-external-link');

    let selectedBookId = null;

    // 1. BOOK SELECTION (Show Research View)
    const bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach(card => {
        card.addEventListener('click', () => {
            selectedBookId = card.getAttribute('data-book-id');
            const title = card.getAttribute('data-title');
            const author = card.getAttribute('data-author');
            
            // Populate the Research View
            rvTitle.innerText = title;
            rvAuthor.innerText = "by " + author;
            
            // Create the Open Library link
            rvLink.href = `https://openlibrary.org/search?q=${encodeURIComponent(title)}`;
            
            // Switch views
            gridContainer.classList.add('hidden');
            readingView.classList.add('active');
            
            // Clear textarea for the new book
            summaryTextarea.value = '';
        });
    });

    // 2. BACK TO GRID
    backBtn.addEventListener('click', () => {
        readingView.classList.remove('active');
        gridContainer.classList.remove('hidden');
    });

    // 3. SUBMIT SUMMARY & CLAIM REWARD
    submitBtn.addEventListener('click', () => {
        const pastedText = summaryTextarea.value.trim();

        // Anti-Cheat: Ensure they actually pasted something substantial (at least 100 chars)
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
                summary_text: pastedText // Send the pasted text to Django!
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to dashboard to see the wallet update!
                window.location.href = '/'; 
            } else {
                alert("Error: " + data.error);
                submitBtn.disabled = false;
                submitBtn.innerText = "Submit Summary & Claim Reward";
            }
        });
    });
});