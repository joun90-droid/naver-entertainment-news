/* =========================================================
   전영재 전용 네이버 연예뉴스 핫토픽 JavaScript App Engine
   100% Fully Automated Real-time Live Engine (Zero-Click Sync)
   ========================================================= */

const CATEGORIES = {
  "실시간 랭킹": "https://api-gw.entertain.naver.com/news/ranking",
  "연예가 핫토픽": "https://api-gw.entertain.naver.com/news/articles?sid=221&pageSize=30",
  "방송·TV": "https://api-gw.entertain.naver.com/news/articles?sid=224&pageSize=30",
  "영화": "https://api-gw.entertain.naver.com/news/articles?sid=222&pageSize=30",
  "드라마": "https://api-gw.entertain.naver.com/news/articles?sid=225&pageSize=30",
  "뮤직": "https://api-gw.entertain.naver.com/news/articles?sid=7a5&pageSize=30",
  "해외연예": "https://api-gw.entertain.naver.com/news/articles?sid=309&pageSize=30"
};

class NaverEntertainWebApp {
  constructor() {
    this.currentCategory = "실시간 랭킹";
    this.currentItems = [];
    this.filteredItems = [];
    this.selectedItem = null;
    this.bookmarks = this.loadBookmarks();

    // Auto Refresh Timer states
    this.autoRefreshIntervalSec = 15;
    this.countdownRemainingSec = 15;
    this.timerId = null;

    this.initElements();
    this.bindEvents();

    // Initial Load
    this.loadCategory(this.currentCategory, false);

    // Start 100% Zero-Click Auto Sync Engine
    this.startAutoSyncEngine();
  }

  initElements() {
    this.newsFeed = document.getElementById("newsFeed");
    this.searchInput = document.getElementById("searchInput");
    this.chipContainer = document.getElementById("chipContainer");
    this.inspectorContent = document.getElementById("inspectorContent");
    
    // Live Indicators
    this.liveStatusBadge = document.getElementById("liveStatusBadge");
    this.countdownText = document.getElementById("countdownText");
    this.syncProgressBar = document.getElementById("syncProgressBar");
    this.refreshIntervalSelect = document.getElementById("refreshIntervalSelect");
    this.toastNotify = document.getElementById("toastNotify");
    this.toastMsg = document.getElementById("toastMsg");

    // Modal elements
    this.modalOverlay = document.getElementById("modalOverlay");
    this.bottomSheet = document.getElementById("bottomSheet");
    this.sheetBody = document.getElementById("sheetBody");
  }

  bindEvents() {
    // Category chips click
    this.chipContainer.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip-btn");
      if (!chip) return;
      
      document.querySelectorAll(".chip-btn").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      
      const cat = chip.dataset.category;
      this.currentCategory = cat;
      this.updateNavState(cat);
      
      if (cat === "⭐ 즐겨찾기") {
        this.renderBookmarks();
      } else {
        this.loadCategory(cat, false);
      }
      this.resetCountdown();
    });

    // Mobile bottom nav click
    document.querySelectorAll(".mobile-bottom-nav .nav-item").forEach(nav => {
      nav.addEventListener("click", (e) => {
        e.preventDefault();
        const cat = nav.dataset.category;
        if (!cat) return;

        document.querySelectorAll(".mobile-bottom-nav .nav-item").forEach(n => n.classList.remove("active"));
        nav.classList.add("active");

        // Sync chip button
        document.querySelectorAll(".chip-btn").forEach(c => {
          c.classList.toggle("active", c.dataset.category === cat);
        });

        this.currentCategory = cat;
        if (cat === "⭐ 즐겨찾기") {
          this.renderBookmarks();
        } else {
          this.loadCategory(cat, false);
        }
        this.resetCountdown();
      });
    });

    // Search input real-time filtering
    this.searchInput.addEventListener("input", () => this.filterNews());

    // Modal overlay close
    this.modalOverlay.addEventListener("click", () => this.closeModal());
    document.getElementById("btnCloseSheet")?.addEventListener("click", () => this.closeModal());
    
    // Header manual refresh button
    document.getElementById("btnRefresh")?.addEventListener("click", () => {
      if (this.currentCategory === "⭐ 즐겨찾기") {
        this.renderBookmarks();
      } else {
        this.loadCategory(this.currentCategory, false);
      }
      this.resetCountdown();
    });

    // Interval selector change
    this.refreshIntervalSelect?.addEventListener("change", (e) => {
      this.autoRefreshIntervalSec = parseInt(e.target.value, 10);
      this.resetCountdown();
    });
  }

  startAutoSyncEngine() {
    if (this.timerId) clearInterval(this.timerId);

    this.timerId = setInterval(() => {
      if (this.autoRefreshIntervalSec <= 0) {
        if (this.countdownText) this.countdownText.textContent = "(자동 갱신 꺼짐)";
        if (this.syncProgressBar) this.syncProgressBar.style.width = "0%";
        return;
      }

      this.countdownRemainingSec -= 1;

      if (this.countdownRemainingSec <= 0) {
        // Trigger silent automatic background sync
        if (this.currentCategory !== "⭐ 즐겨찾기") {
          this.loadCategory(this.currentCategory, true);
        }
        this.resetCountdown();
      } else {
        // Update countdown text & progress bar
        if (this.countdownText) {
          this.countdownText.textContent = `(${this.countdownRemainingSec}초 후 자동 갱신)`;
        }
        if (this.syncProgressBar) {
          const pct = (this.countdownRemainingSec / this.autoRefreshIntervalSec) * 100;
          this.syncProgressBar.style.width = `${pct}%`;
        }
      }
    }, 1000);
  }

  resetCountdown() {
    this.countdownRemainingSec = this.autoRefreshIntervalSec;
    if (this.countdownText) {
      if (this.autoRefreshIntervalSec > 0) {
        this.countdownText.textContent = `(${this.countdownRemainingSec}초 후 자동 갱신)`;
      } else {
        this.countdownText.textContent = "(자동 갱신 꺼짐)";
      }
    }
    if (this.syncProgressBar) {
      this.syncProgressBar.style.width = this.autoRefreshIntervalSec > 0 ? "100%" : "0%";
    }
  }

  showToast(message) {
    if (!this.toastNotify || !this.toastMsg) return;
    this.toastMsg.textContent = message;
    this.toastNotify.classList.add("show");
    setTimeout(() => {
      this.toastNotify.classList.remove("show");
    }, 3000);
  }

  updateNavState(cat) {
    document.querySelectorAll(".mobile-bottom-nav .nav-item").forEach(n => {
      n.classList.toggle("active", n.dataset.category === cat);
    });
  }

  async fetchNaverData(targetUrl) {
    const timeBuster = new Date().getTime();
    const urlWithBuster = targetUrl + (targetUrl.includes('?') ? '&' : '?') + `_t=${timeBuster}`;

    // Determine proxy endpoints depending on origin
    const localProxyUrl = window.location.protocol === "file:" 
      ? `http://localhost:8080/api/news?url=${encodeURIComponent(urlWithBuster)}`
      : `/api/news?url=${encodeURIComponent(urlWithBuster)}`;

    // Attempt 1: Local server proxy with no-store
    try {
      const localRes = await fetch(localProxyUrl, { cache: 'no-store' });
      if (localRes.ok) {
        const json = await localRes.json();
        if (json && json.result) return json;
      }
    } catch (e) {
      console.warn("Local proxy fetch failed, trying direct...", e);
    }

    // Attempt 2: Direct API fetch with no-store
    try {
      const directRes = await fetch(urlWithBuster, { cache: 'no-store' });
      if (directRes.ok) {
        const json = await directRes.json();
        if (json && json.result) return json;
      }
    } catch (e) {
      console.warn("Direct fetch failed...", e);
    }

    return null;
  }

  async loadCategory(catName, isSilentAutoSync = false) {
    // Only show loading spinner if it's NOT a silent background auto-sync
    if (!isSilentAutoSync) {
      this.newsFeed.innerHTML = `
        <div class="state-center">
          <div class="spinner"></div>
          <p>🔴 <strong>[${catName}]</strong> 네이버 실시간 소식을 불러오는 중...</p>
        </div>
      `;
    }

    const targetUrl = CATEGORIES[catName];
    let parsedItems = [];
    let isLive = false;

    try {
      const data = await this.fetchNaverData(targetUrl);

      if (data && data.result) {
        const rawItems = data.result.articles || data.result.newsList || [];
        parsedItems = rawItems.map((item, idx) => {
          const office = item.officeName || "연예뉴스";
          const title = item.title || "제목 없음";
          const summary = item.subContent || title;
          const url = item.url || "#";
          let thumb = item.thumbnail || (item.image ? item.image.url : "");
          const id = item.officeId && item.articleId ? `${item.officeId}_${item.articleId}` : url;

          return {
            rank: idx + 1,
            id,
            office,
            title,
            summary,
            url,
            thumbnail: thumb,
            category: catName
          };
        });
        isLive = true;
      }
    } catch (error) {
      console.warn("Live fetch error:", error);
    }

    // Fallback if live fetch failed
    if (!parsedItems || parsedItems.length === 0) {
      if (window.INITIAL_NEWS_CACHE && window.INITIAL_NEWS_CACHE[catName]) {
        parsedItems = window.INITIAL_NEWS_CACHE[catName];
        isLive = false;
      }
    }

    if (parsedItems && parsedItems.length > 0) {
      // Check if data actually changed during auto sync
      const firstOldTitle = this.currentItems[0] ? this.currentItems[0].title : "";
      const firstNewTitle = parsedItems[0] ? parsedItems[0].title : "";

      this.currentItems = parsedItems;
      this.filteredItems = parsedItems;
      this.renderFeed();

      // Keep selection or auto select first
      if (!this.selectedItem || !parsedItems.some(it => it.id === this.selectedItem.id)) {
        this.selectArticle(parsedItems[0], false);
      }

      if (isSilentAutoSync) {
        const nowTimeStr = new Date().toLocaleTimeString("ko-KR", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.showToast(`✨ 네이버 연예뉴스가 실시간 연동되었습니다 (${nowTimeStr})`);
      }
    } else if (!isSilentAutoSync) {
      this.newsFeed.innerHTML = `
        <div class="state-center" style="color: #f87171;">
          <p style="font-size:1.1rem; font-weight:700; margin-bottom:6px;">⚠️ [${catName}] 실시간 연동 중</p>
          <p style="font-size:0.85rem; color:#94a3b8; margin-bottom:14px;">네트워크 연결 상태를 확인해주시기 바랍니다.</p>
          <button class="btn-primary" style="width:auto; padding:8px 20px; display:inline-block;" onclick="app.loadCategory('${catName}', false)">🔄 다시 시도</button>
        </div>
      `;
    }
  }

  renderFeed() {
    if (!this.filteredItems || this.filteredItems.length === 0) {
      this.newsFeed.innerHTML = `
        <div class="state-center">
          <p>표시할 뉴스 기사가 없습니다.</p>
        </div>
      `;
      return;
    }

    this.newsFeed.innerHTML = this.filteredItems.map(item => `
      <div class="news-card" onclick="app.selectArticleByUrl('${item.url}')">
        <div class="rank-badge ${item.rank <= 3 ? 'top3' : ''}">${item.rank}</div>
        <div class="news-thumb-wrapper">
          ${item.thumbnail 
            ? `<img src="${item.thumbnail}" alt="thumb" loading="lazy" onerror="this.src='https://ssl.pstatic.net/static/entertain/2025/m/09/18/favicon_enter_192.png'">` 
            : `<span style="font-size:1.5rem;">🖼️</span>`}
        </div>
        <div class="news-content">
          <div class="news-office-row">
            <span>[${item.office}]</span>
            ${this.isBookmarked(item.id) ? '<span style="color:#facc15;">⭐</span>' : ''}
          </div>
          <h3 class="news-title">${item.title}</h3>
          <p class="news-summary">${item.summary}</p>
        </div>
      </div>
    `).join("");
  }

  selectArticleByUrl(url) {
    const found = this.currentItems.find(it => it.url === url) || this.bookmarks[url];
    if (found) {
      this.selectArticle(found, true);
    }
  }

  selectArticle(item, openMobileModal = true) {
    this.selectedItem = item;
    const isBm = this.isBookmarked(item.id);

    const htmlContent = `
      ${item.thumbnail ? `<img src="${item.thumbnail}" class="article-detail-img" alt="preview">` : ''}
      <div style="display:flex; gap:6px; margin-bottom:8px;">
        <span style="background:#2e1065; color:#c084fc; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">[${item.office}]</span>
        <span style="background:#831843; color:#f472b6; font-size:0.75rem; padding:2px 8px; border-radius:12px;">${item.category || this.currentCategory}</span>
      </div>
      <h2 class="article-detail-title">${item.title}</h2>
      <div class="article-detail-body">${item.summary}\n\n🔗 URL: ${item.url}</div>
      <div class="action-buttons">
        <a href="${item.url}" target="_blank" class="btn-primary">🌐 네이버 원본 기사 읽기</a>
        <div style="display:flex; gap:8px;">
          <button class="btn-secondary" style="flex:1;" onclick="app.toggleBookmarkCurrent()">${isBm ? '★ 즐겨찾기 해제' : '⭐ 즐겨찾기'}</button>
          <button class="btn-secondary" style="flex:1;" onclick="app.shareNative()">📤 공유하기</button>
        </div>
      </div>
    `;

    // Render to Desktop inspector
    if (this.inspectorContent) {
      this.inspectorContent.innerHTML = htmlContent;
    }

    // Open Mobile Bottom Sheet Modal on phones
    if (openMobileModal && window.innerWidth <= 768) {
      this.sheetBody.innerHTML = htmlContent;
      this.modalOverlay.classList.add("active");
      this.bottomSheet.classList.add("active");
    }
  }

  closeModal() {
    this.modalOverlay.classList.remove("active");
    this.bottomSheet.classList.remove("active");
  }

  filterNews() {
    const q = this.searchInput.value.trim().toLowerCase();
    if (!q) {
      this.filteredItems = this.currentItems;
    } else {
      this.filteredItems = this.currentItems.filter(it => 
        it.title.toLowerCase().includes(q) || 
        it.office.toLowerCase().includes(q) || 
        it.summary.toLowerCase().includes(q)
      );
    }
    this.renderFeed();
  }

  // Bookmark Management
  loadBookmarks() {
    try {
      return JSON.parse(localStorage.getItem("jyj_bookmarks") || "{}");
    } catch (e) {
      return {};
    }
  }

  saveBookmarks() {
    localStorage.setItem("jyj_bookmarks", JSON.stringify(this.bookmarks));
  }

  isBookmarked(id) {
    return !!this.bookmarks[id];
  }

  toggleBookmarkCurrent() {
    if (!this.selectedItem) return;
    const item = this.selectedItem;
    
    if (this.bookmarks[item.id]) {
      delete this.bookmarks[item.id];
    } else {
      this.bookmarks[item.id] = item;
    }
    this.saveBookmarks();
    this.selectArticle(item, false);
    
    if (this.currentCategory === "⭐ 즐겨찾기") {
      this.renderBookmarks();
    } else {
      this.renderFeed();
    }
  }

  renderBookmarks() {
    const items = Object.values(this.bookmarks);
    this.currentItems = items;
    this.filteredItems = items;
    this.renderFeed();
  }

  shareNative() {
    if (!this.selectedItem) return;
    if (navigator.share) {
      navigator.share({
        title: this.selectedItem.title,
        text: `[전영재의 연예뉴스 핫토픽] ${this.selectedItem.title}`,
        url: this.selectedItem.url,
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(this.selectedItem.url);
      alert("📋 기사 링크가 클립보드에 복사되었습니다!");
    }
  }
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  window.app = new NaverEntertainWebApp();
});
