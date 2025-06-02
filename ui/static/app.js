async function performSearch() {
    const collection = document.getElementById('collection').value;
    const query = document.getElementById('query').value;
    const negative = document.getElementById('negative').value;
    const distinct = document.getElementById('distinct').checked;

    if (!query) {
        alert('Введите запрос');
        return;
    }

    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
    resultsContainer.style.display = 'block';

    try {
        const formData = new FormData();
        formData.append('collection', collection);
        formData.append('query', query);
        if (negative.length > 0){
            formData.append('negative', negative);
        }
        formData.append('distinct', distinct.toString()); // Преобразуем boolean в строку

        const response = await fetch('/search', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            resultsContainer.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        if (data.points.length > 0) {
            resultsContainer.innerHTML = data.points.map(points => `
                <div class="result-item">
                    <h3>${points.payload.name || 'Unnamed Result'}</h3>
                    
                    ${points.payload.link ? `<a href="${points.payload.link}" target="_blank">View Source</a>` : ''}
                </div>
            `).join('');
        } else {
            resultsContainer.innerHTML = '<div class="no-results">No results found</div>';
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        console.error('Search error:', error);
    }
}