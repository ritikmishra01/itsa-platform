/*!
 * ITSA Platform — Theme Manager
 * Part B, File 4 of the Modern SaaS UI Redesign
 *
 * Handles light/dark mode with:
 *   • FOUC prevention (runs before first paint via IIFE)
 *   • System preference detection & live sync
 *   • Smooth CSS transitions added AFTER first paint
 *   • Persistent user preference via localStorage
 *   • Custom `themechange` event for downstream consumers
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * REQUIRED CSS (add to your stylesheet, e.g. theme.css or _variables.css):
 *
 *   html.theme-transitioning * {
 *     transition:
 *       background-color var(--dur-base) var(--ease-smooth),
 *       color            var(--dur-base) var(--ease-smooth),
 *       border-color     var(--dur-base) var(--ease-smooth) !important;
 *   }
 *
 * The `.theme-transitioning` class is added to <html> AFTER the initial paint
 * so the very first render has no transition flash. It is removed and re-added
 * around every subsequent theme switch to keep animations clean.
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * EXPECTED TOGGLE BUTTON MARKUP:
 *
 *   <button
 *     data-theme-toggle
 *     class="btn btn-icon"
 *     aria-label="Switch to dark mode"
 *   >
 *     <i class="bi bi-moon-stars"></i>
 *   </button>
 *
 *   • The button uses the `data-theme-toggle` attribute (no value needed).
 *   • The inner <i> element carries the Bootstrap Icon class.
 *   • Light mode  → icon: bi-moon-stars  | aria-label: "Switch to dark mode"
 *   • Dark  mode  → icon: bi-sun         | aria-label: "Switch to light mode"
 *   • Multiple toggle buttons are supported simultaneously (e.g. navbar + sidebar).
 * ─────────────────────────────────────────────────────────────────────────────
 */

/* ============================================================================
   1. IIFE — Anti-FOUC block
      Runs synchronously, before any paint, to stamp data-bs-theme on <html>.
      Priority: saved user preference → OS preference → default 'light'
   ============================================================================ */
(function () {
  'use strict';

  var STORAGE_KEY = 'itsa-theme';
  var saved = null;

  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch (_) {
    /* localStorage unavailable (private browsing, security policy, etc.) */
  }

  var theme =
    saved === 'light' || saved === 'dark'
      ? saved
      : window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';

  document.documentElement.setAttribute('data-bs-theme', theme);
})();

/* ============================================================================
   2. ThemeManager
      Public API exposed at window.ITSA.theme
   ============================================================================ */
var ThemeManager = (function () {
  'use strict';

  /* ── Constants ─────────────────────────────────────────────────────────── */
  var STORAGE_KEY      = 'itsa-theme';
  var ATTR             = 'data-bs-theme';
  var TRANSITION_CLASS = 'theme-transitioning';
  var EVENT_NAME       = 'themechange';
  var TOGGLE_SELECTOR  = '[data-theme-toggle]';

  /* Icon / label maps ─────────────────────────────────────────────────────── */
  var ICON_MAP  = { light: 'bi-moon-stars', dark: 'bi-sun'              };
  var LABEL_MAP = { light: 'Switch to dark mode', dark: 'Switch to light mode' };

  /* ── Internal helpers ──────────────────────────────────────────────────── */

  /**
   * Safely read a value from localStorage.
   * Returns null when storage is unavailable.
   * @returns {string|null}
   */
  function _readStorage() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  /**
   * Safely write a value to localStorage.
   * Silently fails when storage is unavailable.
   * @param {string} value
   */
  function _writeStorage(value) {
    try {
      localStorage.setItem(STORAGE_KEY, value);
    } catch (_) {
      /* noop */
    }
  }

  /**
   * Resolve the theme that should currently be active.
   * Priority: saved user preference → OS preference → 'light'
   * @returns {'light'|'dark'}
   */
  function _resolveTheme() {
    var saved = _readStorage();
    if (saved === 'light' || saved === 'dark') return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Stamp data-bs-theme on <html> without triggering a CSS transition.
   * Used internally by set() which handles the transition class separately.
   * @param {'light'|'dark'} theme
   */
  function _applyAttr(theme) {
    document.documentElement.setAttribute(ATTR, theme);
  }

  /* ── Public API ────────────────────────────────────────────────────────── */

  var ThemeManager = {

    /**
     * init()
     * ──────
     * • Reads saved/system preference and stamps data-bs-theme on <html>
     *   (the IIFE above has already done this, but init() ensures the JS
     *    state is in sync after DOM is ready).
     * • Renders all toggle button states.
     * • Wires up the OS-preference listener so changes auto-propagate when
     *   the user has not set an explicit preference.
     */
    init: function () {
      var theme = _resolveTheme();
      _applyAttr(theme);
      this.updateButtons();

      /* Listen for OS preference changes.
         Only honour them when the user has NOT saved an explicit preference. */
      if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        var self = this;

        /* Use addEventListener when available; fall back to addListener
           (deprecated but required for Safari < 14). */
        var handler = function (e) {
          if (_readStorage()) return; /* user has an explicit preference – skip */
          self.set(e.matches ? 'dark' : 'light', /* persist= */ false);
        };

        if (typeof mq.addEventListener === 'function') {
          mq.addEventListener('change', handler);
        } else if (typeof mq.addListener === 'function') {
          mq.addListener(handler);
        }
      }
    },

    /**
     * get()
     * ─────
     * Returns the current active theme string.
     * @returns {'light'|'dark'}
     */
    get: function () {
      var attr = document.documentElement.getAttribute(ATTR);
      return attr === 'dark' ? 'dark' : 'light';
    },

    /**
     * set(theme [, persist])
     * ──────────────────────
     * • Applies the given theme to <html> via data-bs-theme.
     * • Persists to localStorage (unless persist === false).
     * • Wraps the DOM change in transition class removal/addition so the
     *   browser skips the transition on the very frame the attribute changes
     *   and then immediately re-enables it for future hover/focus effects.
     * • Updates all toggle buttons.
     * • Dispatches a custom `themechange` event on document.
     *
     * @param {'light'|'dark'} theme
     * @param {boolean} [persist=true]  Set false to skip localStorage write
     *                                  (used by the OS-preference listener).
     */
    set: function (theme, persist) {
      if (theme !== 'light' && theme !== 'dark') {
        console.warn('[ITSA.theme] Unknown theme "' + theme + '". Expected "light" or "dark".');
        return;
      }

      var html = document.documentElement;

      /* Remove transition class → change attribute → re-add transition class.
         This sequence runs in a single frame: the browser sees both the class
         removal and the attribute change together, so no transition fires.
         The class is restored on the next rAF so future transitions work. */
      html.classList.remove(TRANSITION_CLASS);
      _applyAttr(theme);

      /* Force a style recalculation so the browser picks up the attribute
         change without transition, then restore the transition class. */
      void html.offsetHeight; /* reflow trigger */
      html.classList.add(TRANSITION_CLASS);

      if (persist !== false) {
        _writeStorage(theme);
      }

      this.updateButtons();

      /* Dispatch custom event for other modules to react to theme changes */
      try {
        var event = new CustomEvent(EVENT_NAME, {
          detail:   { theme: theme },
          bubbles:  true,
          composed: true
        });
        document.dispatchEvent(event);
      } catch (_) {
        /* IE11 fallback (CustomEvent constructor not available) */
        var legacyEvent = document.createEvent('CustomEvent');
        legacyEvent.initCustomEvent(EVENT_NAME, true, false, { theme: theme });
        document.dispatchEvent(legacyEvent);
      }
    },

    /**
     * toggle()
     * ────────
     * Flips the active theme between 'light' and 'dark'.
     */
    toggle: function () {
      this.set(this.get() === 'dark' ? 'light' : 'dark');
    },

    /**
     * updateButtons()
     * ───────────────
     * Finds every [data-theme-toggle] element in the DOM and synchronises:
     *   • The <i> child class list  (Bootstrap Icon class)
     *   • The button aria-label     (accessibility label)
     *
     * Safe to call at any time; no-ops if no buttons are present.
     */
    updateButtons: function () {
      var theme   = this.get();
      var icon    = ICON_MAP[theme];
      var label   = LABEL_MAP[theme];
      var buttons = document.querySelectorAll(TOGGLE_SELECTOR);

      for (var i = 0; i < buttons.length; i++) {
        var btn    = buttons[i];
        var iconEl = btn.querySelector('i');

        /* Update aria-label on the button */
        btn.setAttribute('aria-label', label);

        /* Swap the Bootstrap Icon class on the <i> element */
        if (iconEl) {
          /* Remove both possible icon classes before adding the correct one */
          iconEl.classList.remove('bi-moon-stars', 'bi-sun');
          iconEl.classList.add(icon);
        }
      }
    }

  };

  return ThemeManager;
})();

/* ============================================================================
   3. Global namespace exposure
      window.ITSA.theme → ThemeManager
   ============================================================================ */
window.ITSA       = window.ITSA || {};
window.ITSA.theme = ThemeManager;

/* ============================================================================
   4. DOMContentLoaded bootstrap
      • Initialises ThemeManager (system listener, button state).
      • Delegates click events for all [data-theme-toggle] buttons
        (delegation handles buttons added after init, e.g. via AJAX).
      • Adds the .theme-transitioning class to <html> so that all future
        theme switches animate smoothly (but the very first paint does not).
   ============================================================================ */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  /* ── 4a. Initialise ──────────────────────────────────────────────────── */
  ThemeManager.init();

  /* ── 4b. Click delegation for toggle buttons ─────────────────────────── */
  /*
   * We attach a single listener on <body> rather than one per button so that
   * buttons rendered after DOMContentLoaded (modals, ajax-loaded sidebars,
   * etc.) work without extra wiring.
   */
  document.body.addEventListener('click', function (e) {
    /* Walk up from the click target to see if a [data-theme-toggle] was hit */
    var target = e.target;
    while (target && target !== document.body) {
      if (target.hasAttribute && target.hasAttribute('data-theme-toggle')) {
        e.preventDefault();
        ThemeManager.toggle();
        return;
      }
      target = target.parentElement;
    }
  });

  /* ── 4c. Enable smooth transitions AFTER initial paint ───────────────── */
  /*
   * requestAnimationFrame fires after the browser has painted the first
   * frame. Adding the class here guarantees the initial theme stamp (done
   * by the IIFE) never triggers a transition, preventing a white→dark flash.
   */
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      /* Double rAF ensures we are safely past the first paint commit. */
      document.documentElement.classList.add('theme-transitioning');
    });
  });

  /* ── 4d. OS preference listener ──────────────────────────────────────── */
  /*
   * NOTE: The live matchMedia listener is wired inside ThemeManager.init().
   * Nothing extra is needed here; this comment is kept for documentation
   * clarity so readers understand where each concern lives.
   *
   * Summary of listener behaviour (from ThemeManager.init):
   *   • Fires when the user changes OS dark/light mode at the system level.
   *   • Ignored when the user has set an explicit preference (localStorage).
   *   • When honoured, calls ThemeManager.set(theme, false) — no persistence.
   */

}); /* end DOMContentLoaded */
