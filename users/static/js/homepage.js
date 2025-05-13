document.addEventListener('DOMContentLoaded', function() {
  const searchForm       = document.getElementById('search-form');
  const searchInput      = document.getElementById('search-input');
  const resultsContainer = document.getElementById('search-results');
  const carouselArea     = document.getElementById('carousel-area');

  function runSearch(keyword, pushState = true) {
    if (!keyword) {
      carouselArea.style.display = '';
      resultsContainer.innerHTML = '';
      if (pushState) window.history.pushState({}, '', searchForm.action);
      return;
    }

    const newUrl = `${searchForm.action}?q=${encodeURIComponent(keyword)}`;
    if (pushState) window.history.pushState({q: keyword}, '', newUrl);

    carouselArea.style.display = 'none';
    resultsContainer.innerHTML = '<p>Loading…</p>';

    fetch(newUrl, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => {
      if (!res.ok) throw new Error(`Status ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (Array.isArray(data.results) && data.results.length) {
        let html = '<div class="results-boxes">';
        data.results.forEach(item => {
          html += `
            <div class="result-box">
              <a href="/clothing/item/${item.id}/">
                ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}">` : ''}
                <div id="result-box-text-content">
                  <h3>${item.name}</h3>
                  <p><strong>Availability:</strong><br>
                    <span class="badge-status ${item.availability_code}">
                      ${item.availability}
                    </span>
                  </p>
                </div>
              </a>
            </div>`;
        });
        html += '</div>';
        resultsContainer.innerHTML = html;
      } else {
        resultsContainer.innerHTML = '<p>No results found.</p>';
      }
    })
    .catch(err => {
      console.error('Error fetching search results:', err);
      resultsContainer.innerHTML = '<p class="text-danger">Error fetching results.</p>';
    });
  }

  // 1) On load, check URL for ?q=
  const params = new URLSearchParams(window.location.search);
  const initialQ = params.get('q') || '';
  if (initialQ) {
    searchInput.value = initialQ;
    runSearch(initialQ, false);
  }

  // 2) Intercept form submits
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    runSearch(searchInput.value.trim(), true);
  });

  // 3) Handle back/forward navigation
  window.addEventListener('popstate', function(e) {
    const q = (e.state && e.state.q) || new URLSearchParams(window.location.search).get('q') || '';
    searchInput.value = q;
    runSearch(q, false);
  });

  // CAROUSEL HANDLER
  document.querySelectorAll('.carousel').forEach(carousel => {
    const container = carousel.querySelector('.carousel-container');
    const prevBtn   = carousel.querySelector('.carousel-prev');
    const nextBtn   = carousel.querySelector('.carousel-next');
    let position    = 0;
    const itemWidth = 230;
    const maxScroll = container.scrollWidth - carousel.offsetWidth;

    prevBtn.addEventListener('click', () => {
      position = Math.max(position - itemWidth, 0);
      container.style.transform = `translateX(-${position}px)`;
    });
    nextBtn.addEventListener('click', () => {
      position = Math.min(position + itemWidth, maxScroll);
      container.style.transform = `translateX(-${position}px)`;
    });
  });
});
