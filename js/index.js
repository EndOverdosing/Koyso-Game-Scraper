document.addEventListener("DOMContentLoaded", () => {
    const addInteractiveBorderListeners = (element) => {
        if (!element) return;
        let leaveTimeout;
        const handleMove = (clientX, clientY) => {
            clearTimeout(leaveTimeout);
            const rect = element.getBoundingClientRect();
            const x = clientX - rect.left;
            const y = clientY - rect.top;
            element.style.setProperty("--x", `${x}px`);
            element.style.setProperty("--y", `${y}px`);
            element.style.setProperty("--opacity", "1");
        };
        const handleLeave = () => {
            element.style.setProperty("--opacity", "0");
        };
        element.addEventListener("mousemove", (e) => handleMove(e.clientX, e.clientY));
        element.addEventListener("mouseleave", handleLeave);
        element.addEventListener("touchstart", (e) => handleMove(e.touches[0].clientX, e.touches[0].clientY), { passive: true });
        element.addEventListener("touchmove", (e) => handleMove(e.touches[0].clientX, e.touches[0].clientY), { passive: true });
        element.addEventListener("touchend", () => { leaveTimeout = setTimeout(handleLeave, 500); });
    };

    const applyInteractiveBorders = () => {
        document.querySelectorAll(".js-interactive-border").forEach((element) => {
            if (element.dataset.interactiveBorderInit) return;
            addInteractiveBorderListeners(element);
            element.dataset.interactiveBorderInit = "true";
        });
    };
    applyInteractiveBorders();

    let allGames = [];
    const gameContainer = document.getElementById("gameContainer");
    const searchInput = document.getElementById("navSearchInput");
    const gameCountEl = document.getElementById("gameCount");
    const themeToggle = document.getElementById("theme-toggle-button");
    const proxyToggle = document.getElementById("proxy-toggle-button");
    const gamePlayerOverlay = document.getElementById("game-player-overlay");
    const closeGamePlayerBtn = document.getElementById("closeGamePlayer");
    const gamePlayerTitle = document.getElementById("gamePlayerTitle");
    const gameFrame = document.getElementById("gameFrame");
    const fullscreenBtn = document.getElementById("fullscreenBtn");
    const aboutBlankBtn = document.getElementById("aboutBlankBtn");
    const downloadBtn = document.getElementById("downloadBtn");

    const renderSkeletonGrid = (container, count = 24) => {
        if (!container) return;
        container.innerHTML = "";
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement("div");
            skeleton.className = "skeleton-card";
            container.appendChild(skeleton);
        }
    };

    const createGameCard = (game) => {
        const card = document.createElement("div");
        card.className = "content-card interactive-border";
        const posterUrl = game.image || 'images/default-game-poster.png';
        const truncatedDescription = game.description.length > 100 ? game.description.substring(0, 100) + '...' : game.description;

        card.innerHTML = `
            <div class="card-image">
                <img src="${posterUrl}" alt="${game.title}" loading="lazy" onerror="this.onerror=null;this.src='images/default-game-poster.png';">
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h2 class="card-title">${game.title}</h2>
                </div>
                <p class="card-description">${truncatedDescription}</p> 
            </div>`;

        card.addEventListener("click", () => openGamePlayer(game));
        return card;
    };

    const addCardListeners = (element) => {
        element.addEventListener('mousemove', e => {
            const rect = element.getBoundingClientRect();
            element.style.setProperty('--x', `${e.clientX - rect.left}px`);
            element.style.setProperty('--y', `${e.clientY - rect.top}px`);
            element.style.setProperty('--opacity', '1');
        });

        element.addEventListener('mouseleave', () => {
            element.style.setProperty('--opacity', '0');
        });
    };

    const renderGames = (games) => {
        gameContainer.innerHTML = "";
        if (games.length === 0) {
            gameContainer.innerHTML = `<p style="grid-column: 1 / -1; text-align: center;">No games found.</p>`;
        } else {
            games.forEach((game) => {
                const card = createGameCard(game);
                gameContainer.appendChild(card);
            });
            document.querySelectorAll('#gameContainer .interactive-border').forEach(addCardListeners);
        }
    };

    const openGamePlayer = (game) => {
        gamePlayerTitle.textContent = game.title;
        gameFrame.src = "about:blank";

        const gameUrl = new URL(game.url, window.location.origin).href;
        const displayUrl = isProxyEnabled ? `${PROXY_URL}${gameUrl}` : gameUrl;

        setTimeout(() => {
            gameFrame.src = displayUrl;
        }, 100);

        gamePlayerOverlay.classList.add("active");
        document.body.style.overflow = "hidden";

        const openInNewWindow = (url) => {
            const newWindow = window.open("about:blank", "_blank");
            if (newWindow) {
                newWindow.document.title = game.title;
                newWindow.document.body.style.margin = "0";
                newWindow.document.body.style.overflow = "hidden";
                const iframe = newWindow.document.createElement("iframe");
                iframe.style.cssText = "border: none; width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden;";
                iframe.src = url;
                newWindow.document.body.appendChild(iframe);
            }
        };

        fullscreenBtn.onclick = () => {
            if (gameFrame.requestFullscreen) {
                gameFrame.requestFullscreen().catch(err => {
                    console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
                });
            }
        };
        aboutBlankBtn.onclick = () => openInNewWindow(displayUrl);
        downloadBtn.style.display = game.downloadUrl ? 'inline-flex' : 'none';
        if (game.downloadUrl) {
            downloadBtn.onclick = () => window.open(game.downloadUrl, '_blank');
        }
    };

    const closeGamePlayer = () => {
        gameFrame.src = "about:blank";
        gamePlayerOverlay.classList.remove("active");
        document.body.style.overflow = "";
    };

    const handleSearch = () => {
        const query = searchInput.value.toLowerCase();
        const filteredGames = allGames.filter((game) =>
            game.title.toLowerCase().includes(query)
        );
        renderGames(filteredGames);
    };

    const populateBackgroundScroller = (games) => {
        const scroller = document.getElementById('background-scroller');
        if (!scroller) return;
        scroller.innerHTML = '';

        let gameImages = games.map(g => g.image).filter(Boolean);
        if (gameImages.length === 0) return;

        for (let i = gameImages.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [gameImages[i], gameImages[j]] = [gameImages[j], gameImages[i]];
        }

        const numRows = 8;
        const imagesPerRow = 25;

        for (let i = 1; i <= numRows; i++) {
            const row = document.createElement('div');
            row.className = `scroller-row scroller-row-${i}`;
            const fragment = document.createDocumentFragment();
            for (let j = 0; j < imagesPerRow; j++) {
                const imgPath = gameImages[(i * imagesPerRow + j) % gameImages.length];
                const img = document.createElement('img');
                img.src = imgPath;
                img.loading = 'lazy';
                img.alt = '';
                img.setAttribute('aria-hidden', 'true');
                fragment.appendChild(img);
            }
            const originalImages = Array.from(fragment.children);
            row.appendChild(fragment);
            originalImages.forEach(img => row.appendChild(img.cloneNode(true)));
            scroller.appendChild(row);
        }
        requestAnimationFrame(() => {
            scroller.classList.add('animations-active');
        });
    };

    const initialize = async () => {
        renderSkeletonGrid(gameContainer);
        try {
            const response = await fetch("/games.json");
            if (!response.ok) throw new Error("Network response was not ok");
            const games = await response.json();
            allGames = games;
            gameCountEl.textContent = `Games: ${games.length}`;
            renderGames(games);
            populateBackgroundScroller(games);
        } catch (error) {
            gameContainer.innerHTML = `<p style="grid-column: 1 / -1; text-align: center;">Could not load games. Please try again later.</p>`;
        }
    };

    searchInput.addEventListener("input", handleSearch);
    closeGamePlayerBtn.addEventListener("click", closeGamePlayer);
    gamePlayerOverlay.addEventListener("click", (e) => {
        if (e.target.classList.contains('details-overlay-backdrop')) closeGamePlayer();
    });

    const THEME_KEY = 'vyla_theme';
    const applyTheme = (theme) => {
        const icon = themeToggle.querySelector('i');
        if (theme === 'light') {
            document.documentElement.classList.add('color-revert-active');
            icon.className = 'fas fa-moon';
        } else {
            document.documentElement.classList.remove('color-revert-active');
            icon.className = 'fas fa-sun';
        }
        localStorage.setItem(THEME_KEY, theme);
    };

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.classList.contains('color-revert-active') ? 'light' : 'dark';
        applyTheme(currentTheme === 'light' ? 'dark' : 'light');
    });

    const savedTheme = localStorage.getItem(THEME_KEY) || 'dark';
    applyTheme(savedTheme);

    const PROXY_URL = 'https://ovala.vercel.app/proxy/';
    const PROXY_KEY = 'vyla_proxy_enabled';
    let isProxyEnabled = false;

    const applyProxyMode = (enabled) => {
        if (!proxyToggle) return;
        isProxyEnabled = enabled;
        if (enabled) {
            proxyToggle.classList.add('active');
        } else {
            proxyToggle.classList.remove('active');
        }
        localStorage.setItem(PROXY_KEY, enabled);
    };

    if (proxyToggle) {
        proxyToggle.addEventListener('click', () => {
            applyProxyMode(!isProxyEnabled);
        });

        const savedProxy = localStorage.getItem(PROXY_KEY) === 'true';
        applyProxyMode(savedProxy);
    }

    initialize();
});