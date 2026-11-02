const projectGrid = document.getElementById('projects-grid');
const searchForm = document.getElementById('project-search-form');
const searchInput = document.getElementById('project-title-search');
const SEARCH_DEBOUNCE_DELAY = 300;
const PLACEHOLDER_ID = '00000000-0000-0000-0000-000000000000';
let searchDebounceTimer;
let projectsAbortController;

function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie.split(';').map(value => value.trim())
        .find(value => value.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function projectEndpoint(pattern, id) {
    return pattern.replace(PLACEHOLDER_ID, id);
}

function displayProjectsState(state) {
    for (const name of ['loading', 'error', 'empty', 'grid']) {
        document.getElementById(`projects-${name}`).classList.toggle('hide', name !== state);
    }
    projectGrid.setAttribute('aria-busy', String(state === 'loading'));
}

function buildProjectCardElement(project) {
    const card = document.getElementById('project-card-template').content.firstElementChild.cloneNode(true);
    // Only the UUID is substituted in trusted template attributes; data stays text.
    if (!/^[0-9a-f-]{36}$/i.test(project.id)) throw new Error('Invalid project ID');
    for (const element of card.querySelectorAll('*')) {
        for (const attribute of [...element.attributes]) {
            if (attribute.value.includes(PLACEHOLDER_ID)) {
                element.setAttribute(attribute.name, attribute.value.replaceAll(PLACEHOLDER_ID, project.id));
            }
        }
    }
    for (const field of ['title', 'description', 'technologies']) {
        card.querySelector(`[data-field="${field}"]`).textContent = project[field];
    }
    for (const field of ['project_url', 'repository_url']) {
        const link = card.querySelector(`[data-field="${field}"]`);
        try {
            const url = new URL(project[field]);
            if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Invalid URL');
            link.href = url.href;
        } catch {
            link.remove();
        }
    }
    const starButton = card.querySelector('.button-star');
    starButton.classList.toggle('is-starred', project.is_starred);
    starButton.title = project.star_count ? `Starred by ${project.starred_by_names}` : 'Be the first to star';
    const starLabel = card.querySelector('[data-field="star-label"]');
    if (starLabel) starLabel.textContent = project.is_starred ? 'Unstar' : 'Star';
    card.querySelector('.star-count').textContent = project.star_count;
    const deleteModal = card.querySelector('.project-delete-modal');
    if (deleteModal) {
        deleteModal.querySelector('strong').textContent = project.title;
        card.querySelector('button[popovertarget]').setAttribute('aria-label', `Delete ${project.title}`);
    }
    return card;
}

async function fetchProjects(searchQuery = '') {
    projectsAbortController?.abort();
    const controller = new AbortController();
    projectsAbortController = controller;
    displayProjectsState('loading');
    try {
        const url = new URL(projectGrid.dataset.endpoint, window.location.origin);
        if (searchQuery) url.searchParams.set('title', searchQuery);
        const response = await fetch(url, {
            headers: {Accept: 'application/json'},
            signal: controller.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const projects = await response.json();
        if (controller.signal.aborted) return;
        projectGrid.replaceChildren(...projects.map(buildProjectCardElement));
        document.getElementById('projects-empty').textContent = searchQuery
            ? 'No projects match that title.' : 'Belum ada proyek yang ditambahkan.';
        displayProjectsState(projects.length ? 'grid' : 'empty');
    } catch (error) {
        if (controller.signal.aborted) return;
        console.error('Error loading projects:', error);
        displayProjectsState('error');
    }
}

function apiErrorMessage(data, status) {
    const messages = Object.values(data).flat().filter(value => typeof value === 'string');
    return messages.join(' ') || `Terjadi kesalahan (status ${status}).`;
}

async function writeProject(url, method, payload) {
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

function searchProjects() {
    fetchProjects(searchInput.value.trim());
}

function closeProjectModal() {
    document.getElementById('add-project-modal')?.hidePopover();
}

searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    projectsAbortController?.abort();
    searchDebounceTimer = setTimeout(searchProjects, SEARCH_DEBOUNCE_DELAY);
});

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    searchProjects();
});

const projectForm = document.getElementById('project-form');

async function addProject(event) {
    event.preventDefault();
    const submitButton = projectForm.querySelector('button[type="submit"]');
    if (submitButton.disabled) return;
    submitButton.disabled = true;
    try {
        const fields = new FormData(projectForm);
        const payload = Object.fromEntries([
            'title', 'description', 'technologies', 'project_url', 'repository_url',
        ].map(name => [name, fields.get(name)]));
        await writeProject(projectForm.dataset.ajaxUrl, 'POST', payload);
        projectForm.reset();
        closeProjectModal();
        showToast('Berhasil', 'Proyek baru berhasil ditambahkan!', 'success');
        clearTimeout(searchDebounceTimer);
        await fetchProjects(searchInput.value.trim());
    } catch (error) {
        console.error('Error adding project:', error);
        showToast('Gagal menambahkan proyek', error.message, 'error');
    } finally {
        submitButton.disabled = false;
    }
}

projectForm?.addEventListener('submit', addProject);

projectGrid.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;
    const action = button.dataset.action;
    const isStar = action === 'star';
    button.disabled = true;
    try {
        const pattern = isStar ? projectGrid.dataset.starEndpoint : projectGrid.dataset.detailEndpoint;
        await writeProject(projectEndpoint(pattern, button.dataset.id), isStar ? 'POST' : 'DELETE');
        button.closest('[popover]')?.hidePopover();
        showToast('Berhasil', isStar ? 'Star diperbarui.' : 'Proyek berhasil dihapus.', 'success');
        clearTimeout(searchDebounceTimer);
        await fetchProjects(searchInput.value.trim());
    } catch (error) {
        console.error(`Error on project ${action}:`, error);
        showToast(isStar ? 'Gagal memperbarui star' : 'Gagal menghapus proyek', error.message, 'error');
    } finally {
        button.disabled = false;
    }
});

fetchProjects(searchInput.value.trim());
