const experienceGrid = document.getElementById('experience-grid');
const searchForm = document.getElementById('experience-search-form');
const searchInput = document.getElementById('experience-title-search');
const SEARCH_DEBOUNCE_DELAY = 300;
const PLACEHOLDER_ID = '00000000-0000-0000-0000-000000000000';
let searchDebounceTimer;
let experienceAbortController;

function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie.split(';').map(value => value.trim())
        .find(value => value.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function experienceEndpoint(pattern, id) {
    return pattern.replace(PLACEHOLDER_ID, id);
}

function displayExperiencesState(state) {
    for (const name of ['loading', 'error', 'empty', 'grid']) {
        document.getElementById(`experience-${name}`).classList.toggle('hide', name !== state);
    }
    experienceGrid.setAttribute('aria-busy', String(state === 'loading'));
}

function buildExperienceCardElement(experience) {
    const card = document.getElementById('experience-card-template').content.firstElementChild.cloneNode(true);
    // Only the UUID is substituted in trusted template attributes; data stays text.
    if (!/^[0-9a-f-]{36}$/i.test(experience.id)) throw new Error('Invalid experience ID');
    for (const element of card.querySelectorAll('*')) {
        for (const attribute of [...element.attributes]) {
            if (attribute.value.includes(PLACEHOLDER_ID)) {
                element.setAttribute(attribute.name, attribute.value.replaceAll(PLACEHOLDER_ID, experience.id));
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
    const starLabel = card.querySelector('[data-field="star-label"]');
    if (starLabel) starLabel.textContent = experience.is_starred ? 'Unstar' : 'Star';
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

function apiErrorMessage(data, status) {
    const messages = Object.values(data).flat().filter(value => typeof value === 'string');
    return messages.join(' ') || `Terjadi kesalahan (status ${status}).`;
}

async function writeExperience(url, method, payload) {
    const response = await fetch(url, {
        method,
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
    return data;
}

function searchExperiences() {
    fetchExperiences(searchInput.value.trim());
}

function refreshExperiences() {
    clearTimeout(searchDebounceTimer);
    return fetchExperiences(searchInput.value.trim());
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

function closeExperienceModal() {
    document.getElementById('add-experience-modal')?.hidePopover();
}

const experienceForm = document.getElementById('experience-form');

async function addExperience(event) {
    event.preventDefault();
    const submitButton = experienceForm.querySelector('button[type="submit"]');
    if (submitButton.disabled) return;
    submitButton.disabled = true;
    try {
        const fields = new FormData(experienceForm);
        const payload = Object.fromEntries(
            ['title', 'description', 'category', 'thumbnail'].map(name => [name, fields.get(name)]),
        );
        await writeExperience(experienceForm.dataset.ajaxUrl, 'POST', payload);
        experienceForm.reset();
        closeExperienceModal();
        showToast('Berhasil', 'Pengalaman baru berhasil ditambahkan!', 'success');
        await refreshExperiences();
    } catch (error) {
        console.error('Error adding experience:', error);
        showToast('Gagal menambahkan pengalaman', error.message, 'error');
    } finally {
        submitButton.disabled = false;
    }
}

experienceForm?.addEventListener('submit', addExperience);

experienceGrid.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;
    const action = button.dataset.action;
    const isStar = action === 'star';
    button.disabled = true;
    try {
        const pattern = isStar ? experienceGrid.dataset.starEndpoint : experienceGrid.dataset.detailEndpoint;
        await writeExperience(experienceEndpoint(pattern, button.dataset.id), isStar ? 'POST' : 'DELETE');
        button.closest('[popover]')?.hidePopover();
        showToast('Berhasil', isStar ? 'Star diperbarui.' : 'Pengalaman berhasil dihapus.', 'success');
        await refreshExperiences();
    } catch (error) {
        console.error(`Error on experience ${action}:`, error);
        showToast(isStar ? 'Gagal memperbarui star' : 'Gagal menghapus pengalaman', error.message, 'error');
    } finally {
        button.disabled = false;
    }
});

fetchExperiences(searchInput.value.trim());
