/* ==========================================================================
   ITSA PLATFORM — COMMAND BAR BEHAVIORS
   Scroll shadow · Command palette trigger · Mobile drawer · User menu
   ========================================================================== */
(function () {
  'use strict';

  /* ============================================================
     1. Scroll shadow on command bar
     ============================================================ */
  const cmdBar = document.getElementById('app-command-bar');
  if (cmdBar) {
    const onScroll = () => cmdBar.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ============================================================
     2. ⌘K / Ctrl+K → open command palette
     ============================================================ */
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      const trigger = document.querySelector('[data-cmd-palette-open]');
      if (trigger) trigger.click();
    }
  });

  /* ============================================================
     3. Mobile drawer
     ============================================================ */
  const toggle   = document.getElementById('mobile-menu-toggle');
  const close    = document.getElementById('mobile-menu-close');
  const drawer   = document.getElementById('mobile-nav-drawer');
  const backdrop = document.getElementById('mobile-nav-backdrop');

  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add('open');
    backdrop?.classList.add('open');
    document.body.classList.add('no-scroll');
  }

  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove('open');
    backdrop?.classList.remove('open');
    document.body.classList.remove('no-scroll');
  }

  toggle?.addEventListener('click', openDrawer);
  close?.addEventListener('click', closeDrawer);
  backdrop?.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawer();
  });

  /* ============================================================
     4. User menu dropdown (avatar click)
     ============================================================ */
  const userToggle   = document.getElementById('cmd-user-toggle');
  const userDropdown = document.getElementById('cmd-user-dropdown');

  if (userToggle && userDropdown) {
    // Toggle open/close on avatar click
    userToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('open');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!userDropdown.contains(e.target) && e.target !== userToggle && !userToggle.contains(e.target)) {
        userDropdown.classList.remove('open');
      }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        userDropdown.classList.remove('open');
      }
    });
  }

  /* ============================================================
     5. Expose for other scripts
     ============================================================ */
  window.ITSA = window.ITSA || {};
  window.ITSA.openMobileDrawer  = openDrawer;
  window.ITSA.closeMobileDrawer = closeDrawer;
})();