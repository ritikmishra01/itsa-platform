/* ==========================================================================
   ITSA PLATFORM — ADMIN EVENTS PAGE BEHAVIORS
   Assign Coordinators · Edit Event · Cancel Event · Search
   ========================================================================== */
(function () {
  'use strict';

  window.ITSA = window.ITSA || {};

  const toast = window.ITSA.toast || {
    success: (t, m) => console.log('✓', t, m),
    error:   (t, m) => console.error('✗', t, m),
    info:    (t, m) => console.log('ℹ', t, m)
  };

  /* ============================================================
     1. SEARCH BOX
     ============================================================ */
  const searchInput = document.getElementById('adminEventSearch');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim().toLowerCase();
      document.querySelectorAll('.admin-table tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = q && !text.includes(q) ? 'none' : '';
      });
    });
  }

  /* ============================================================
     2. DELEGATED CLICK HANDLERS
     ============================================================ */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    e.preventDefault();
    const action  = btn.dataset.action;
    const eventId = btn.dataset.eventId;
    const title   = btn.dataset.eventTitle || 'this event';

    if (action === 'cancel-event') {
      confirmCancelEvent(btn, eventId, title);
    } else if (action === 'edit-event') {
      openEditModal(eventId, title, btn);
    } else if (action === 'assign-coordinator') {
      openAssignModal(eventId, title);
    }
  });

  /* ============================================================
     3. CANCEL EVENT (soft delete via status)
     ============================================================ */
  function confirmCancelEvent(btn, eventId, title) {
    let modal = document.getElementById('cancelEventModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'cancelEventModal';
      modal.className = 'delete-modal-backdrop';
      modal.innerHTML = `
        <div class="delete-modal">
          <div class="delete-modal-icon">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>
          <h3 class="delete-modal-title">Cancel Event?</h3>
          <p class="delete-modal-text">
            Are you sure you want to cancel <strong id="cancelEventName"></strong>?
            All registrations will remain, but the event will be marked as cancelled.
          </p>
          <div class="delete-modal-actions">
            <button type="button" class="delete-modal-btn delete-modal-cancel">Keep Event</button>
            <button type="button" class="delete-modal-btn delete-modal-confirm">
              <i class="bi bi-x-circle"></i> Cancel Event
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('open');
      });
      modal.querySelector('.delete-modal-cancel').addEventListener('click', () => {
        modal.classList.remove('open');
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') modal.classList.remove('open');
      });
    }

    modal.querySelector('#cancelEventName').textContent = title;

    const confirmBtn = modal.querySelector('.delete-modal-confirm');
    const newBtn = confirmBtn.cloneNode(true);
    confirmBtn.replaceWith(newBtn);

    newBtn.addEventListener('click', async () => {
      newBtn.disabled = true;
      newBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Cancelling...';

      try {
        const res = await fetch(`/api/v1/events/${eventId}/status`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          },
          credentials: 'same-origin',
          body: JSON.stringify({ status: 'CANCELLED' })
        });

        const data = await res.json().catch(() => ({}));

        if (res.ok && (data.success !== false)) {
          toast.success('Event Cancelled', `"${title}" has been cancelled.`);

          const row = btn.closest('tr');
          if (row) {
            const statusCell = row.querySelector('.admin-col-status');
            if (statusCell) {
              statusCell.innerHTML = `
                <span class="admin-status-chip admin-status-cancelled">
                  <span class="admin-status-dot"></span>
                  Cancelled
                </span>
              `;
            }
          }
          modal.classList.remove('open');
        } else {
          toast.error('Failed', data.error?.message || data.message || `HTTP ${res.status}`);
          newBtn.disabled = false;
          newBtn.innerHTML = '<i class="bi bi-x-circle"></i> Cancel Event';
        }
      } catch (err) {
        console.error('Cancel error:', err);
        toast.error('Network error', 'Could not cancel the event.');
        newBtn.disabled = false;
        newBtn.innerHTML = '<i class="bi bi-x-circle"></i> Cancel Event';
      }
    });

    modal.classList.add('open');
  }

  /* ============================================================
     4. EDIT EVENT MODAL
     ============================================================ */
  async function openEditModal(eventId, title, btn) {
    let eventData = null;
    try {
      const res = await fetch(`/api/v1/events/${eventId}`, {
        headers: { 'Accept': 'application/json' },
        credentials: 'same-origin'
      });
      if (res.ok) {
        const payload = await res.json();
        eventData = payload.data || payload;
      }
    } catch (err) {
      console.error('Fetch event error:', err);
    }

    let modal = document.getElementById('editEventModal');
    if (modal) modal.remove();

    const fmtDt = (dt) => {
      if (!dt) return '';
      try {
        return new Date(dt).toISOString().slice(0, 16);
      } catch (e) {
        return '';
      }
    };

    modal = document.createElement('div');
    modal.id = 'editEventModal';
    modal.className = 'delete-modal-backdrop';
    modal.innerHTML = `
      <div class="edit-modal">
        <div class="edit-modal-header">
          <h3>Edit Event</h3>
          <button type="button" class="edit-modal-close"><i class="bi bi-x-lg"></i></button>
        </div>
        <form id="editEventForm" class="edit-modal-body">
          <div class="edit-field">
            <label>Event Title</label>
            <input type="text" name="title" value="${eventData?.title || title}" required>
          </div>
          <div class="edit-field-row">
            <div class="edit-field">
              <label>Start Date & Time</label>
              <input type="datetime-local" name="start_datetime" value="${fmtDt(eventData?.start_datetime)}">
            </div>
            <div class="edit-field">
              <label>End Date & Time</label>
              <input type="datetime-local" name="end_datetime" value="${fmtDt(eventData?.end_datetime)}">
            </div>
          </div>
          <div class="edit-field">
            <label>Description</label>
            <textarea name="description" rows="3">${eventData?.description || ''}</textarea>
          </div>
          <div class="edit-field-row">
            <div class="edit-field">
              <label>Max Participants</label>
              <input type="number" name="max_participants" value="${eventData?.max_participants || ''}" min="1">
            </div>
            <div class="edit-field">
              <label>Status</label>
              <select name="status">
                <option value="DRAFT" ${eventData?.status === 'DRAFT' ? 'selected' : ''}>Draft</option>
                <option value="PUBLISHED" ${eventData?.status === 'PUBLISHED' ? 'selected' : ''}>Published</option>
                <option value="REGISTRATION_OPEN" ${eventData?.status === 'REGISTRATION_OPEN' ? 'selected' : ''}>Registration Open</option>
                <option value="REGISTRATION_CLOSED" ${eventData?.status === 'REGISTRATION_CLOSED' ? 'selected' : ''}>Registration Closed</option>
                <option value="ONGOING" ${eventData?.status === 'ONGOING' ? 'selected' : ''}>Ongoing</option>
                <option value="COMPLETED" ${eventData?.status === 'COMPLETED' ? 'selected' : ''}>Completed</option>
                <option value="CANCELLED" ${eventData?.status === 'CANCELLED' ? 'selected' : ''}>Cancelled</option>
              </select>
            </div>
          </div>
          <div class="edit-modal-footer">
            <button type="button" class="admin-btn admin-btn-ghost edit-modal-cancel">Cancel</button>
            <button type="submit" class="admin-btn admin-btn-primary">
              <i class="bi bi-check-lg"></i> Save Changes
            </button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(modal);

    const closeModal = () => modal.classList.remove('open');
    modal.querySelector('.edit-modal-close').addEventListener('click', closeModal);
    modal.querySelector('.edit-modal-cancel').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

    modal.querySelector('#editEventForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const payload = Object.fromEntries(formData.entries());

      const submitBtn = e.target.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Saving...';

      try {
        const res = await fetch(`/api/v1/events/${eventId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          },
          credentials: 'same-origin',
          body: JSON.stringify(payload)
        });

        const data = await res.json().catch(() => ({}));

        if (res.ok && (data.success !== false)) {
          toast.success('Saved', `"${payload.title}" updated successfully.`);
          setTimeout(() => window.location.reload(), 600);
        } else {
          toast.error('Failed', data.error?.message || data.message || `HTTP ${res.status}`);
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> Save Changes';
        }
      } catch (err) {
        console.error('Save error:', err);
        toast.error('Network error', 'Could not save changes.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> Save Changes';
      }
    });

    modal.classList.add('open');
  }

  /* ============================================================
     5. ASSIGN COORDINATORS MODAL
     ============================================================ */
  function openAssignModal(eventId, title) {
    // Read coordinators from the embedded JSON
    let coordinators = [];
    try {
      const el = document.getElementById('admin-coordinators-full');
      if (el) {
        coordinators = JSON.parse(el.textContent.trim());
      }
    } catch (err) {
      console.warn('Could not parse coordinators data:', err);
    }

    let modal = document.getElementById('assignCoordModal');
    if (modal) modal.remove();

    const coordOptions = coordinators.length
      ? coordinators.map(c => `
          <label class="assign-item">
            <input type="checkbox" name="coordinator_ids" value="${c.id}">
            <div class="assign-avatar">${(c.full_name || 'U')[0].toUpperCase()}</div>
            <div class="assign-info">
              <div class="assign-name">${c.full_name || 'Unknown'}</div>
              <div class="assign-email">${c.email || ''}</div>
            </div>
          </label>
        `).join('')
      : '<div class="assign-empty">No coordinators available. Create one first.</div>';

    modal = document.createElement('div');
    modal.id = 'assignCoordModal';
    modal.className = 'delete-modal-backdrop';
    modal.innerHTML = `
      <div class="edit-modal">
        <div class="edit-modal-header">
          <h3>Assign Coordinators</h3>
          <button type="button" class="edit-modal-close"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="edit-modal-body">
          <p class="assign-subtitle">Select coordinators for <strong>${title}</strong></p>
          <div class="assign-list">${coordOptions}</div>
        </div>
        <div class="edit-modal-footer">
          <button type="button" class="admin-btn admin-btn-ghost edit-modal-cancel">Cancel</button>
          <button type="button" class="admin-btn admin-btn-primary assign-save">
            <i class="bi bi-check-lg"></i> Assign Selected
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const closeModal = () => modal.classList.remove('open');
    modal.querySelector('.edit-modal-close').addEventListener('click', closeModal);
    modal.querySelector('.edit-modal-cancel').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

    modal.querySelector('.assign-save').addEventListener('click', async () => {
      const checked = Array.from(modal.querySelectorAll('input[name="coordinator_ids"]:checked'))
                          .map(cb => parseInt(cb.value, 10));

      if (!checked.length) {
        toast.info('No selection', 'Please select at least one coordinator.');
        return;
      }

      const saveBtn = modal.querySelector('.assign-save');
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Assigning...';

      try {
        const res = await fetch(`/api/v1/events/${eventId}/coordinators`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          },
          credentials: 'same-origin',
          body: JSON.stringify({ coordinator_ids: checked })
        });

        const data = await res.json().catch(() => ({}));

        if (res.ok && (data.success !== false)) {
          toast.success('Assigned', `${checked.length} coordinator(s) assigned.`);
          modal.classList.remove('open');
        } else {
          toast.error('Failed', data.error?.message || data.message || `HTTP ${res.status}`);
          saveBtn.disabled = false;
          saveBtn.innerHTML = '<i class="bi bi-check-lg"></i> Assign Selected';
        }
      } catch (err) {
        console.error('Assign error:', err);
        toast.error('Network error', 'Could not assign coordinators.');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-check-lg"></i> Assign Selected';
      }
    });

    modal.classList.add('open');
  }

  console.log('✅ admin-events.js loaded');
})();