const projectGrid = document.getElementById('projects-grid');
const searchForm = document.getElementById('project-search-form');
const searchInput = document.getElementById('project-title-search');
const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;
let projectsAbortController;

function displayProjectsState(state) {
    for (const name of ['loading', 'error', 'empty', 'grid']) {
        document.getElementById(`projects-${name}`).classList.toggle('hide', name !== state);
    }
    projectGrid.setAttribute('aria-busy', String(state === 'loading'));
}

function buildProjectCardElement(item) {
    const card = document.getElementById('project-card-template').content.firstElementChild.cloneNode(true);
    const project = item.fields;
    // Only the UUID is substituted in trusted template attributes; data stays text.
    if (!/^[0-9a-f-]{36}$/i.test(item.pk)) throw new Error('Invalid project ID');
    for (const element of card.querySelectorAll('*')) {
        for (const attribute of [...element.attributes]) {
            if (attribute.value.includes('00000000-0000-0000-0000-000000000000')) {
                element.setAttribute(attribute.name, attribute.value.replaceAll('00000000-0000-0000-0000-000000000000', item.pk));
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
    card.querySelector('[data-field="star-label"]').textContent = project.is_starred ? 'Unstar' : 'Star';
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

function searchProjects() {
    fetchProjects(searchInput.value.trim());
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

fetchProjects(searchInput.value.trim());
