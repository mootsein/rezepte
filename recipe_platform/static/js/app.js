document.addEventListener('DOMContentLoaded', () => {
    let token = localStorage.getItem('authToken');
    let currentUser = null;
    let searchTimeout;

    // --- DOM Elements ---
    const guestNav = document.getElementById('guest-nav');
    const userNav = document.getElementById('user-nav');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    const recipeGrid = document.getElementById('recipe-grid');
    const resultsTitle = document.getElementById('results-title');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorContainer = document.getElementById('error-container');
    const logoLink = document.getElementById('logo-link');

    // Filter elements
    const searchInput = document.getElementById('search-input');
    const kategorieSelect = document.getElementById('kategorie');
    const ernaehrungSelect = document.getElementById('ernahrung');
    const kucheSelect = document.getElementById('kuche');
    const maxZeitInput = document.getElementById('max_zeit');
    const portionenInput = document.getElementById('portionen');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    
    // Modals
    const modalBackdrop = document.getElementById('modal-backdrop');
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    const recipeModal = document.getElementById('recipe-modal');
    const addRecipeModal = document.getElementById('add-recipe-modal');
    const addRecipeBtn = document.getElementById('add-recipe-btn');
    const addRecipeForm = document.getElementById('add-recipe-form');

    // Dark Mode
    const darkModeCheckbox = document.getElementById('dark-mode-toggle');
    const htmlElement = document.documentElement;

    // --- API Call Helper ---
    const apiCall = async (endpoint, method = 'GET', body = null) => {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`/api/v1${endpoint}`, options);
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                let message = `HTTP Error ${response.status}`;
                
                // Bessere Fehlerbehandlung nach Status-Code
                if (response.status === 401) {
                    message = 'Nicht authentifiziert. Bitte melden Sie sich an.';
                    logout();
                } else if (response.status === 403) {
                    message = 'Zugriff verweigert.';
                } else if (response.status === 404) {
                    message = 'Ressource nicht gefunden.';
                } else if (response.status === 429) {
                    message = 'Zu viele Anfragen. Bitte warten Sie einen Moment.';
                } else if (response.status >= 500) {
                    message = 'Serverfehler. Bitte versuchen Sie es später erneut.';
                } else if (data.detail) {
                    if (Array.isArray(data.detail)) {
                        message = data.detail.map((item) => item.msg || JSON.stringify(item)).join(' ');
                    } else if (typeof data.detail === 'string') {
                        message = data.detail;
                    } else if (data.detail.msg) {
                        message = data.detail.msg;
                    }
                }
                throw new Error(message);
            }
            return response.status === 204 ? null : await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                showError('Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.');
            } else {
                showError(error.message);
            }
            throw error;
        }
    };

    // --- UI Updates ---
    const showLoading = (show) => loadingIndicator.classList.toggle('hidden', !show);
    const showToast = (message, type = 'error') => {
        const icon = type === 'success' ? '✅' : '⚠️';
        errorContainer.textContent = `${icon} ${message}`;
        errorContainer.classList.remove('hidden');
        errorContainer.classList.toggle('toast-success', type === 'success');
        setTimeout(() => errorContainer.classList.add('hidden'), 5000);
    };
    const showError = (message) => showToast(message, 'error');
    const showSuccess = (message) => showToast(message, 'success');

    const updateNav = () => {
        if (currentUser) {
            guestNav.classList.add('hidden');
            userNav.classList.remove('hidden');
            document.getElementById('user-name').textContent = currentUser.first_name || currentUser.username;
            document.getElementById('user-avatar').textContent = (currentUser.first_name || currentUser.username).charAt(0).toUpperCase();
        } else {
            guestNav.classList.remove('hidden');
            userNav.classList.add('hidden');
        }
    };

    // --- Modals ---
    const openModal = (modal) => {
        modalBackdrop.classList.remove('hidden');
        modal.classList.remove('hidden');
    };

    const closeModal = (modal) => {
        if (modal) {
            modalBackdrop.classList.add('hidden');
            modal.classList.add('hidden');
        }
    };

    // --- Authentication ---
    const handleLogin = async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');
        try {
            errorEl.classList.add('hidden');
            const data = await apiCall('/auth/login', 'POST', { username, password });
            token = data.access_token;
            localStorage.setItem('authToken', token);
            currentUser = data.user;
            updateNav();
            closeModal(loginModal);
            loadRecipes();
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.classList.remove('hidden');
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById('register-error');
        const userData = {
            username: document.getElementById('reg-username').value,
            email: document.getElementById('reg-email').value,
            first_name: document.getElementById('reg-firstname').value,
            last_name: document.getElementById('reg-lastname').value,
            password: document.getElementById('reg-password').value,
        };
        try {
            errorEl.classList.add('hidden');
            await apiCall('/auth/register', 'POST', userData);
            const loginData = await apiCall('/auth/login', 'POST', { username: userData.username, password: userData.password });
            token = loginData.access_token;
            localStorage.setItem('authToken', token);
            currentUser = loginData.user;
            updateNav();
            closeModal(registerModal);
            loadRecipes();
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.classList.remove('hidden');
        }
    };

    const logout = () => {
        token = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        updateNav();
        loadRecipes();
    };

    const checkCurrentUser = async () => {
        if (token) {
            try {
                currentUser = await apiCall('/auth/me');
            } catch (error) {
                logout();
            }
        }
        updateNav();
    };

    // --- Filters & Search ---
    const getFilterParams = () => {
        const params = new URLSearchParams();
        if (searchInput.value) params.append('query', searchInput.value);
        if (kategorieSelect.value) params.append('kategorie', kategorieSelect.value);
        if (ernaehrungSelect.value) params.append('ernahrung', ernaehrungSelect.value);
        if (kucheSelect.value) params.append('kuche', kucheSelect.value);
        if (maxZeitInput.value) params.append('max_zeit', maxZeitInput.value);
        if (portionenInput.value) params.append('min_portionen', portionenInput.value);
        return params;
    };
    
    const updateURL = (params) => {
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState({ path: newUrl }, '', newUrl);
    };

    const loadFilterOptions = async () => {
        try {
            const data = await apiCall('/recipes/filters');
            const populateSelect = (selectElement, options, selectedValue) => {
                selectElement.innerHTML = '<option value="">Alle</option>';
                (options || []).forEach(option => {
                    const selected = option === selectedValue ? 'selected' : '';
                    selectElement.innerHTML += `<option value="${option}" ${selected}>${option}</option>`;
                });
            };
            const urlParams = new URLSearchParams(window.location.search);
            populateSelect(kategorieSelect, data.kategorien, urlParams.get('kategorie'));
            populateSelect(ernaehrungSelect, data.ernaehrungen, urlParams.get('ernahrung'));
            populateSelect(kucheSelect, data.kuchen, urlParams.get('kuche'));
        } catch (e) {
            console.error('Filter options error:', e);
        }
    };

    const loadRecipes = async () => {
        showLoading(true);
        recipeGrid.innerHTML = '';
        const params = getFilterParams();
        updateURL(params);
        
        try {
            const data = await apiCall(`/recipes/search?${params.toString()}`);
            displayRecipes(data);
        } catch (error) {
            // Error is already shown by apiCall
        } finally {
            showLoading(false);
        }
    };

    const displayRecipes = (data) => {
        resultsTitle.textContent = `${data.total} Rezepte gefunden`;
        if (data.recipes.length === 0) {
            recipeGrid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <p>Keine Rezepte gefunden. Passe deine Filter an oder lasse dich überraschen.</p>
                    <div class="empty-state-actions">
                        <button id="reset-filters-no-results" class="btn btn-secondary">Filter zurücksetzen</button>
                        <button id="random-no-results" class="btn btn-primary">Überrasch mich!</button>
                    </div>
                </div>
            `;
            document.getElementById('reset-filters-no-results').addEventListener('click', resetFilters);
            document.getElementById('random-no-results').addEventListener('click', getRandomRecipe);
            return;
        }
        recipeGrid.innerHTML = data.recipes.map(recipe => `
            <div class="recipe-card" data-id="${recipe.id}">
                <div class="recipe-card-content">
                    <h3 class="recipe-card-title">${recipe.titel}</h3>
                    <p class="recipe-card-description">${recipe.beschreibung ? recipe.beschreibung.slice(0, 110) + (recipe.beschreibung.length > 110 ? '…' : '') : 'Keine Beschreibung verfügbar.'}</p>
                    <div class="recipe-card-meta">
                        <span><i class="fas fa-clock"></i> ${recipe.gesamtzeit_min || '?'} Min</span>
                        <span><i class="fas fa-users"></i> ${recipe.portionen || '?'}</span>
                        <span><i class="fas fa-star"></i> ${Number(recipe.avg_rating ?? 0).toFixed(1)}</span>
                    </div>
                </div>
                ${currentUser ? `<div class="recipe-card-actions"><button class="fav-btn ${recipe.is_favorite ? 'favorited' : ''}" data-id="${recipe.id}"><i class="fas fa-heart"></i></button></div>` : ''}
            </div>
        `).join('');
    };
    
    const showRecipeDetail = async (id) => {
        try {
            const recipe = await apiCall(`/recipes/${id}`);
            const detailContent = document.getElementById('recipe-detail-content');
            
            const zutaten = recipe.zutaten_json ? JSON.parse(recipe.zutaten_json) : [];
            const schritte = recipe.schritte_json ? JSON.parse(recipe.schritte_json) : [];

            detailContent.innerHTML = `
                <div class="recipe-detail-header">
                    <h2>${recipe.titel}</h2>
                    <button id="pdf-export-btn" class="btn btn-secondary"><i class="fas fa-file-pdf"></i> Export</button>
                </div>
                <p><strong>Kategorie:</strong> ${recipe.kategorie || '-'} | <strong>Küche:</strong> ${recipe.kuche || '-'}</p>
                <div class="recipe-card-meta" style="margin: 1rem 0;">
                    <span><i class="fas fa-clock"></i> ${recipe.gesamtzeit_min || '?'} Min</span>
                    <span><i class="fas fa-users"></i> ${recipe.portionen || '?'}</span>
                    <span><i class="fas fa-star"></i> ${Number(recipe.avg_rating ?? 0).toFixed(1)} (${recipe.ratings_count || 0})</span>
                </div>
                <h3>Zutaten</h3>
                <ul>${zutaten.map(z => `<li>${z}</li>`).join('')}</ul>
                <h3>Zubereitung</h3>
                <ol>${schritte.map(s => `<li>${s}</li>`).join('')}</ol>
                ${currentUser ? `
                    <h3>Bewerte dieses Rezept</h3>
                    <div class="rating-stars" data-recipe-id="${recipe.id}">
                        ${[1,2,3,4,5].map(star => `<i class="far fa-star" data-value="${star}"></i>`).join('')}
                    </div>
                ` : '<p>Bitte <a href="#" id="login-from-modal">anmelden</a>, um zu bewerten.</p>'}
            `;
            openModal(recipeModal);

            document.getElementById('pdf-export-btn').addEventListener('click', () => handlePdfExport(recipe.id));

            if (currentUser) {
                const stars = detailContent.querySelectorAll('.rating-stars i');
                stars.forEach(star => {
                    star.addEventListener('click', () => rateRecipe(id, star.dataset.value));
                });
            } else {
                document.getElementById('login-from-modal').addEventListener('click', (e) => {
                    e.preventDefault();
                    closeModal(recipeModal);
                    openModal(loginModal);
                });
            }
        } catch (error) {
            showError("Rezept konnte nicht geladen werden.");
        }
    };

    const handlePdfExport = (recipeId) => {
        window.open(`/api/v1/recipes/${recipeId}/pdf`, '_blank');
    };

    const rateRecipe = async (recipeId, stars) => {
        try {
            await apiCall(`/recipes/${recipeId}/rate`, 'POST', { stars: parseInt(stars, 10) });
            showSuccess("Bewertung gespeichert!");
            closeModal(recipeModal);
            loadRecipes();
        } catch (error) {
            showError("Fehler beim Bewerten.");
        }
    };

    const toggleFavorite = async (id) => {
        if (!currentUser) {
            openModal(loginModal);
            return;
        }
        try {
            const response = await apiCall(`/recipes/${id}/favorite`, 'POST');
            const favBtn = document.querySelector(`.fav-btn[data-id='${id}']`);
            if (favBtn) {
                favBtn.classList.toggle('favorited', response.is_favorite);
            }
        } catch (error) {
            showError("Favorit konnte nicht geändert werden.");
        }
    };

    const showFavorites = async () => {
        if (!currentUser) {
            openModal(loginModal);
            return;
        }
        resultsTitle.textContent = "Meine Favoriten";
        const data = await apiCall(`/recipes/favorites/me`);
        displayRecipes(data);
    };

    const getRandomRecipe = async () => {
        try {
            const recipe = await apiCall('/recipes/random');
            showRecipeDetail(recipe.id);
        } catch (error) {
            showError("Zufallsrezept konnte nicht geladen werden.");
        }
    };

    const resetFilters = () => {
        searchInput.value = '';
        kategorieSelect.value = '';
        ernaehrungSelect.value = '';
        kucheSelect.value = '';
        maxZeitInput.value = '';
        portionenInput.value = '';
        loadRecipes();
    };

    const openAddRecipeModal = () => {
        if (!currentUser) {
            openModal(loginModal);
            return;
        }
        addRecipeForm.reset();
        document.getElementById('add-recipe-error').classList.add('hidden');
        openModal(addRecipeModal);
    };

    const handleAddRecipe = async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById('add-recipe-error');
        const splitLines = (text) => text.split('\n').map(line => line.trim()).filter(Boolean);
        const payload = {
            titel: document.getElementById('recipe-title').value,
            beschreibung: document.getElementById('recipe-description').value,
            kategorie: document.getElementById('recipe-category').value,
            kuche: document.getElementById('recipe-kitchen').value,
            ernahrung: document.getElementById('recipe-diet').value,
            portionen: parseInt(document.getElementById('recipe-portions').value, 10),
            gesamtzeit_min: parseInt(document.getElementById('recipe-time').value, 10),
            zutaten: splitLines(document.getElementById('recipe-ingredients').value),
            schritte: splitLines(document.getElementById('recipe-steps').value)
        };
        try {
            errorEl.classList.add('hidden');
            await apiCall('/recipes', 'POST', payload);
            showSuccess('Rezept gespeichert!');
            closeModal(addRecipeModal);
            loadRecipes();
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.classList.remove('hidden');
        }
    };
    
    const setupEventListeners = () => {
        if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', () => mainNav.classList.toggle('active'));
        if (logoLink) logoLink.addEventListener('click', (e) => {
            e.preventDefault();
            resetFilters();
        });
        
        const loginBtn = document.getElementById('login-btn');
        const registerBtn = document.getElementById('register-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const favoritesBtn = document.getElementById('favorites-btn');
        const randomBtn = document.getElementById('random-btn');
        
        if (loginBtn) loginBtn.addEventListener('click', () => openModal(loginModal));
        if (registerBtn) registerBtn.addEventListener('click', () => openModal(registerModal));
        if (logoutBtn) logoutBtn.addEventListener('click', logout);
        if (favoritesBtn) favoritesBtn.addEventListener('click', showFavorites);
        if (randomBtn) randomBtn.addEventListener('click', getRandomRecipe);
        if (addRecipeBtn) addRecipeBtn.addEventListener('click', openAddRecipeModal);

        modalBackdrop.addEventListener('click', () => {
            closeModal(loginModal);
            closeModal(registerModal);
            closeModal(recipeModal);
            closeModal(addRecipeModal);
        });
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => closeModal(btn.closest('.modal')));
        });

        document.getElementById('login-form').addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);
        addRecipeForm.addEventListener('submit', handleAddRecipe);

        searchInput.addEventListener('keyup', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => loadRecipes(), 300);
        });

        [kategorieSelect, ernaehrungSelect, kucheSelect, maxZeitInput, portionenInput].forEach(el => {
            el.addEventListener('change', () => loadRecipes());
        });

        resetFiltersBtn.addEventListener('click', resetFilters);

        recipeGrid.addEventListener('click', (e) => {
            const card = e.target.closest('.recipe-card');
            const favBtn = e.target.closest('.fav-btn');

            if (favBtn) {
                e.stopPropagation();
                toggleFavorite(favBtn.dataset.id);
            } else if (card) {
                showRecipeDetail(card.dataset.id);
            }
        });

        // Dish of the Day
        const dishCard = document.querySelector('.dish-card');
        if (dishCard) {
            dishCard.addEventListener('click', () => {
                const recipeId = dishCard.dataset.recipeId;
                if (recipeId) showRecipeDetail(recipeId);
            });
        }

        // Dark Mode
        if (darkModeCheckbox) {
            darkModeCheckbox.addEventListener('change', (e) => {
                const theme = e.target.checked ? 'dark' : 'light';
                htmlElement.setAttribute('data-theme', theme);
                localStorage.setItem('theme', theme);
            });
        }
    };

    // --- Initial Load ---
    const init = async () => {
        // Set theme on initial load
        if (localStorage.getItem('theme') === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            if (darkModeCheckbox) darkModeCheckbox.checked = true;
        }

        // Parse URL for filters
        const urlParams = new URLSearchParams(window.location.search);
        searchInput.value = urlParams.get('query') || '';
        ernaehrungSelect.value = urlParams.get('ernahrung') || '';
        maxZeitInput.value = urlParams.get('max_zeit') || '';
        portionenInput.value = urlParams.get('min_portionen') || '';

        setupEventListeners();
        await checkCurrentUser();
        await loadFilterOptions(); // This will also set select values from URL
        await loadRecipes();
    };

    init();
});
