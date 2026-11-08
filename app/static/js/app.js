/*!
 * ITSA Platform — Core Application JavaScript
 * Command Center Layout — Sidebar logic removed
 * Exposes window.ITSA with toasts, command palette, optimistic UI, confetti & helpers
 */

(function () {
  'use strict';

  window.ITSA = window.ITSA || {};

  /* ==========================================================================
     1. TOAST NOTIFICATIONS
     ========================================================================== */
  const toast = {
    container: null,

    init() {
      if (!this.container) {
        let el = document.getElementById('toast-container');
        if (!el) {
          el = document.createElement('div');
          el.id = 'toast-container';
          el.setAttribute('role', 'region');
          el.setAttribute('aria-label', 'Notifications');
          document.body.appendChild(el);
        }
        this.container = el;
      }
    },

    show({ type = 'info', title = '', message = '', duration = 5000, action = null }) {
      this.init();

      const icons = {
        success: 'bi-check-circle-fill',
        error:   'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info:    'bi-info-circle-fill'
      };
      const colors = {
        success: 'var(--success-solid)',
        error:   'var(--danger-solid)',
        warning: 'var(--warning-solid)',
        info:    'var(--info-solid)'
      };

      const item = document.createElement('div');
      item.className = 'toast-item';

      let actionHtml = '';
      if (action && action.label) {
        actionHtml = `<button class="btn btn-brand btn-xs mt-2 toast-action-btn">${action.label}</button>`;
      }

      item.innerHTML = `
        <i class="bi ${icons[type] || icons.info} toast-item-icon" style="color: ${colors[type] || colors.info}"></i>
        <div class="toast-item-body">
          ${title ? `<div class="toast-title">${title}</div>` : ''}
          <div class="toast-msg">${message}</div>
          ${actionHtml}
        </div>
        <button class="toast-item-close" aria-label="Close">&times;</button>
        <div class="toast-item-progress"></div>
      `;

      this.container.appendChild(item);

      setTimeout(() => item.classList.add('toast-visible'), 10);

      const progressBar = item.querySelector('.toast-item-progress');
      if (progressBar) {
        progressBar.style.transition = `width ${duration}ms linear`;
        setTimeout(() => progressBar.style.width = '0%', 20);
      }

      const closeToast = () => {
        item.classList.remove('toast-visible');
        setTimeout(() => item.remove(), 250);
      };

      item.querySelector('.toast-item-close').addEventListener('click', closeToast);

      if (action && action.onClick) {
        const btn = item.querySelector('.toast-action-btn');
        if (btn) btn.addEventListener('click', (e) => {
          action.onClick(e);
          closeToast();
        });
      }

      if (duration > 0) {
        setTimeout(closeToast, duration);
      }
    },

    success(title, message, duration) { this.show({ type: 'success', title, message, duration }); },
    error(title, message, duration)   { this.show({ type: 'error', title, message, duration }); },
    warning(title, message, duration) { this.show({ type: 'warning', title, message, duration }); },
    info(title, message, duration)    { this.show({ type: 'info', title, message, duration }); }
  };

  /* ==========================================================================
     2. COMMAND PALETTE (Ctrl+K)
     ========================================================================== */
  const palette = {
    modal: null,
    input: null,
    results: null,
    activeIndex: 0,
    filteredItems: [],

    commands: [
      { label: 'Browse All Events', url: '/events', icon: 'bi-calendar-event', role: 'all' },
      { label: 'View Leaderboard', url: '/leaderboard', icon: 'bi-trophy', role: 'all' },
      { label: 'Verify a Certificate', url: '/certificates/verify', icon: 'bi-patch-check', role: 'all' },

      { label: 'Student Dashboard', url: '/student/dashboard', icon: 'bi-grid-1x2', role: 'STUDENT' },
      { label: 'My QR Tickets', url: '/student/tickets', icon: 'bi-ticket-perforated', role: 'STUDENT' },
      { label: 'My Attendance History', url: '/student/attendance', icon: 'bi-check2-circle', role: 'STUDENT' },
      { label: 'My Certificates', url: '/student/certificates', icon: 'bi-award', role: 'STUDENT' },
      { label: 'AI Assistant Chatbot', url: '/chatbot', icon: 'bi-robot', role: 'STUDENT' },
      { label: 'Community Feed', url: '/feed', icon: 'bi-people', role: 'all' },

      { label: 'Coordinator Dashboard', url: '/coordinator/dashboard', icon: 'bi-grid-1x2', role: 'COORDINATOR' },
      { label: 'QR Attendance Scanner', url: '/coordinator/scanner', icon: 'bi-qr-code-scan', role: 'COORDINATOR' },

      { label: 'Admin Control Center', url: '/admin/dashboard', icon: 'bi-speedometer2', role: 'ADMIN' },
      { label: 'User Directory', url: '/admin/users', icon: 'bi-people', role: 'ADMIN' },
      { label: 'Event Lifecycle Management', url: '/admin/events', icon: 'bi-calendar-week', role: 'ADMIN' },
      { label: 'Registration Roster', url: '/admin/registrations', icon: 'bi-ticket-detailed', role: 'ADMIN' },
      { label: 'Attendance Records', url: '/admin/attendance', icon: 'bi-qr-code', role: 'ADMIN' },
      { label: 'Certificate Management', url: '/admin/certificates', icon: 'bi-award', role: 'ADMIN' },
      { label: 'Community Moderation', url: '/admin/community', icon: 'bi-chat-dots', role: 'ADMIN' },
      { label: 'Broadcast Notifications', url: '/admin/notifications', icon: 'bi-megaphone', role: 'ADMIN' },
      { label: 'AI Operations Center', url: '/admin/ai-center', icon: 'bi-cpu', role: 'ADMIN' },
      { label: 'Deep Analytics', url: '/admin/analytics', icon: 'bi-bar-chart-line', role: 'ADMIN' },
      { label: 'System Audit Logs', url: '/admin/audit-logs', icon: 'bi-shield-check', role: 'ADMIN' }
    ],

    init() {
      if (document.getElementById('cmd-palette-backdrop')) return;

      const backdrop = document.createElement('div');
      backdrop.id = 'cmd-palette-backdrop';
      backdrop.className = 'cmd-palette-backdrop';
      backdrop.innerHTML = `
        <div class="cmd-palette-modal">
          <div class="cmd-palette-search">
            <i class="bi bi-search text-muted"></i>
            <input type="text" id="cmd-palette-input" placeholder="Type a command or jump to..." autocomplete="off">
            <kbd class="badge bg-secondary-subtle text-secondary-emphasis">ESC</kbd>
          </div>
          <div class="cmd-palette-results" id="cmd-palette-results"></div>
          <div class="cmd-palette-footer">
            <span><kbd>↑</kbd> <kbd>↓</kbd> Navigate</span>
            <span><kbd>↵</kbd> Select</span>
            <span><kbd>ESC</kbd> Close</span>
          </div>
        </div>
      `;

      document.body.appendChild(backdrop);
      this.modal = backdrop;
      this.input = backdrop.querySelector('#cmd-palette-input');
      this.results = backdrop.querySelector('#cmd-palette-results');

      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) this.close();
      });

      this.input.addEventListener('input', () => {
        this.render(this.input.value.trim());
      });

      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          this.activeIndex = (this.activeIndex + 1) % this.filteredItems.length;
          this.highlight();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          this.activeIndex = (this.activeIndex - 1 + this.filteredItems.length) % this.filteredItems.length;
          this.highlight();
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (this.filteredItems[this.activeIndex]) {
            window.location.href = this.filteredItems[this.activeIndex].url;
          }
        } else if (e.key === 'Escape') {
          this.close();
        }
      });

      window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          this.open();
        }
      });
    },

    open() {
      this.init();
      this.modal.classList.add('open');
      this.input.value = '';
      this.render('');
      setTimeout(() => this.input.focus(), 50);
    },

    close() {
      if (this.modal) {
        this.modal.classList.remove('open');
      }
    },

    render(query) {
      const userRole = document.body.dataset.userRole || 'GUEST';
      const q = query.toLowerCase();

      this.filteredItems = this.commands.filter(cmd => {
        const matchesRole = cmd.role === 'all' || cmd.role === userRole;
        const matchesQuery = !q || cmd.label.toLowerCase().includes(q) || cmd.url.toLowerCase().includes(q);
        return matchesRole && matchesQuery;
      });

      this.activeIndex = 0;

      if (this.filteredItems.length === 0) {
        this.results.innerHTML = `<div class="p-4 text-center text-muted small">No matching commands found.</div>`;
        return;
      }

      this.results.innerHTML = this.filteredItems.map((cmd, idx) => `
        <a href="${cmd.url}" class="cmd-result-item ${idx === 0 ? 'active' : ''}" data-index="${idx}">
          <div class="cmd-result-icon"><i class="bi ${cmd.icon}"></i></div>
          <span class="cmd-result-label">${cmd.label}</span>
          <i class="bi bi-arrow-right ms-auto text-muted small"></i>
        </a>
      `).join('');
    },

    highlight() {
      const items = this.results.querySelectorAll('.cmd-result-item');
      items.forEach((item, idx) => {
        item.classList.toggle('active', idx === this.activeIndex);
        if (idx === this.activeIndex) {
          item.scrollIntoView({ block: 'nearest' });
        }
      });
    }
  };

  /* ==========================================================================
     3. OPTIMISTIC UI & DELIGHT HELPERS
     ========================================================================== */
  const optimistic = {
    reaction(btnEl, delta = 1) {
      if (!btnEl) return;
      const countEl = btnEl.querySelector('.reaction-count');
      if (countEl) {
        const count = parseInt(countEl.textContent, 10) || 0;
        countEl.textContent = count + delta;
      }
      btnEl.style.transform = 'scale(1.25)';
      setTimeout(() => btnEl.style.transform = '', 200);
    }
  };

  const copy = (text, successMsg = 'Copied to clipboard!') => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        toast.success('Copied', successMsg);
      });
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
      toast.success('Copied', successMsg);
    }
  };

  const confetti = {
    burst(x = window.innerWidth / 2, y = window.innerHeight / 2, count = 40) {
      const colors = ['#0f2744', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'];
      for (let i = 0; i < count; i++) {
        const el = document.createElement('div');
        el.style.position = 'fixed';
        el.style.left = `${x}px`;
        el.style.top = `${y}px`;
        el.style.width = '8px';
        el.style.height = '8px';
        el.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        el.style.borderRadius = '2px';
        el.style.pointerEvents = 'none';
        el.style.zIndex = '99999';

        const angle = Math.random() * Math.PI * 2;
        const velocity = 50 + Math.random() * 150;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity + 100;

        el.style.transition = 'transform 1s cubic-bezier(0.1, 0.8, 0.3, 1), opacity 1s';
        document.body.appendChild(el);

        setTimeout(() => {
          el.style.transform = `translate(${tx}px, ${ty}px) rotate(${Math.random() * 720}deg)`;
          el.style.opacity = '0';
        }, 10);

        setTimeout(() => el.remove(), 1100);
      }
    }
  };

  /* ==========================================================================
     4. NOTIFICATIONS — Mark all read with fallbacks
     ========================================================================== */
  const notifications = {
    markAllRead(btnEl) {
      // Disable the button to prevent double-clicks
      if (btnEl) {
        btnEl.disabled = true;
        btnEl.dataset.originalText = btnEl.innerHTML;
        btnEl.innerHTML = '<i class="bi bi-hourglass-split"></i> Marking...';
      }

      // Try the primary endpoint, then a fallback if 404
      const endpoints = [
        '/api/v1/notifications/read-all',
        '/api/v1/notifications/mark-all-read'
      ];

      const tryEndpoint = (index) => {
        if (index >= endpoints.length) {
          // All failed — still update UI optimistically
          this.updateUI();
          toast.info('Updated', 'Notifications cleared locally.');
          if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = btnEl.dataset.originalText || 'Mark all read';
          }
          return;
        }

        fetch(endpoints[index], {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        .then(res => {
          if (res.status === 404 && index < endpoints.length - 1) {
            // Try next endpoint
            tryEndpoint(index + 1);
            return null;
          }
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        })
        .then(data => {
          if (data === null) return; // switched to fallback

          this.updateUI();
          toast.success('Done', 'All notifications marked as read.');

          if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = btnEl.dataset.originalText || 'Mark all read';
          }
        })
        .catch((err) => {
          console.error('markAllRead error:', err);
          // Try next endpoint
          tryEndpoint(index + 1);
        });
      };

      tryEndpoint(0);
    },

    updateUI() {
      // Hide every notification badge on the page
      document.querySelectorAll('.notification-badge').forEach(b => {
        b.style.display = 'none';
        b.textContent = '';
      });

      // Remove unread styling
      document.querySelectorAll('.notif-item.unread, .notif-item.is-unread, .unread').forEach(el => {
        el.classList.remove('unread', 'is-unread');
      });

      // Swap filled bell → outline
      document.querySelectorAll('.cmd-icon-btn i.bi-bell-fill, .floating-btn i.bi-bell-fill').forEach(i => {
        i.classList.remove('bi-bell-fill');
        i.classList.add('bi-bell');
      });
    }
  };

  /* ==========================================================================
     5. SKELETON LOADERS
     ========================================================================== */
  const skeleton = {
    card(count = 1) {
      return Array(count).fill(`
        <div class="card-surface p-4 mb-3">
          <div class="skeleton skeleton-circle mb-3" style="width: 48px; height: 48px;"></div>
          <div class="skeleton skeleton-text" style="width: 70%;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </div>
      `).join('');
    }
  };

  /* ==========================================================================
     EXPOSE TO window.ITSA
     ========================================================================== */
  window.ITSA.toast = toast;
  window.ITSA.palette = palette;
  window.ITSA.optimistic = optimistic;
  window.ITSA.copy = copy;
  window.ITSA.confetti = confetti;
  window.ITSA.notifications = notifications;
  window.ITSA.skeleton = skeleton;

  /* ==========================================================================
     GLOBAL INITIALIZATION ON DOM READY
     ========================================================================== */
  document.addEventListener('DOMContentLoaded', () => {
    toast.init();

    /* --- Wire command palette trigger buttons (search bar, etc.) --- */
    document.querySelectorAll('[data-cmd-palette-open], .cmd-search').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        palette.open();
      });
    });

    /* --- Wire "Mark all read" buttons --- */
    document.querySelectorAll('[data-mark-all-read], .mark-all-read-btn, #mark-all-read, [data-notif-mark-all]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        notifications.markAllRead(btn);
      });
    });

    /* --- Wire chat floating button to chatbot page --- */
    document.querySelectorAll('[data-itsa-chat], .floating-btn[aria-label="Chat"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        // Only intercept if it's a <button>, not an <a>
        if (btn.tagName === 'BUTTON') {
          e.preventDefault();
          window.location.href = '/chatbot';
        }
      });
    });

    /* --- Wire notification floating button --- */
    document.querySelectorAll('[data-itsa-notifications]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (btn.tagName === 'BUTTON') {
          e.preventDefault();
          window.location.href = '/notifications';
        }
      });
    });

    /* --- Wire create button --- */
    document.querySelectorAll('[data-itsa-create]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/events';
      });
    });

    /* --- Auto-dismiss alert boxes --- */
    setTimeout(() => {
      document.querySelectorAll('.alert-auto-dismiss').forEach(el => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
      });
    }, 5000);

    /* --- Data-copy click binding --- */
    document.querySelectorAll('[data-copy]').forEach(el => {
      el.addEventListener('click', () => {
        copy(el.getAttribute('data-copy') || el.textContent);
      });
    });

    /* --- Page loaded class for transitions --- */
    document.body.classList.add('page-loaded');
  });

})();