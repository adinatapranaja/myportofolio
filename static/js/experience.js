const experienceGrid = document.getElementById('experience-grid');
const searchForm = document.getElementById('experience-search-form');
const searchInput = document.getElementById('experience-title-search');
const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;
let experienceAbortController;

function displayExperiencesState(state) {
    for (const name of ['loading', 'error', 'empty', 'grid']) {
        document.getElementById(`experience-${name}`).classList.toggle('hide', name !== state);
    }
    experienceGrid.setAttribute('aria-busy', String(state === 'loading'));
}

function buildExperienceCardElement(item) {
    const card = document.getElementById('experience-card-template').content.firstElementChild.cloneNode(true);
    const experience = item.fields;
    // Only the UUID is substituted in trusted template attributes; data stays text.
    if (!/^[0-9a-f-]{36}$/i.test(item.pk)) throw new Error('Invalid experience ID');
    for (const element of card.querySelectorAll('*')) {
        for (const attribute of [...element.attributes]) {
            if (attribute.value.includes('00000000-0000-0000-0000-000000000000')) {
                element.setAttribute(attribute.name, attribute.value.replaceAll('00000000-0000-0000-0000-000000000000', item.pk));
            }
        }
    }
    for (const field of ['title', 'description', 'category_display']) {
        card.querySelector(`[data-field="${field}"]`).textContent = experience[field];
    }
    card.querySelector('.experience-status').textContent = experience.is_ongoing ? 'Sedang berlangsung' : 'Selesai';
    const starButton = card.querySelector('.button-star');
    starButton.classList.toggle('is-starred', experience.is_starred);
    starButton.title = experience.star_count ? `Starred by ${experience.starred_by_names}` : 'Be the first to star';
    card.querySelector('[data-field="star-label"]').textContent = experience.is_starred ? 'Unstar' : 'Star';
    card.querySelector('.star-count').textContent = experience.star_count;
    const deleteModal = card.querySelector('.project-delete-modal');
    if (deleteModal) {
        deleteModal.querySelector('strong').textContent = experience.title;
        card.querySelector('button[popovertarget]').setAttribute('aria-label', `Delete ${experience.title}`);
    }
    return card;
}

async function fetchExperiences(searchQuery = '') {
    experienceAbortController?.abort();
    const controller = new AbortController();
    experienceAbortController = controller;
    displayExperiencesState('loading');
    try {
        const url = new URL(experienceGrid.dataset.endpoint, window.location.origin);
        if (searchQuery) url.searchParams.set('title', searchQuery);
        const response = await fetch(url, {
            headers: {Accept: 'application/json'},
            signal: controller.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const experiences = await response.json();
        if (controller.signal.aborted) return;
        experienceGrid.replaceChildren(...experiences.map(buildExperienceCardElement));
        document.getElementById('experience-empty').textContent = searchQuery
            ? 'No experiences match that title.' : 'Belum ada pengalaman yang ditambahkan.';
        displayExperiencesState(experiences.length ? 'grid' : 'empty');
    } catch (error) {
        if (controller.signal.aborted) return;
        console.error('Error loading experience:', error);
        displayExperiencesState('error');
    }
}

function searchExperiences() {
    fetchExperiences(searchInput.value.trim());
}

searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    experienceAbortController?.abort();
    searchDebounceTimer = setTimeout(searchExperiences, SEARCH_DEBOUNCE_DELAY);
});

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    searchExperiences();
});

fetchExperiences(searchInput.value.trim());
