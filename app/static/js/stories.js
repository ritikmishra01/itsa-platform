/**
 * ITSA Platform - Instagram-Style Stories
 * Horizontal Stories Tray · Auto-advancing Player · View Tracker · Author Viewer List
 */
(function() {
  'use strict';

  // Global State
  let storyGroups = [];
  let currentUserGroupIndex = -1;
  let currentStoryIndex = -1;
  let progressTimer = null;
  let progressStartTime = 0;
  let progressElapsedTime = 0;
  let isPaused = false;
  const STORY_DURATION_MS = 5000;

  // DOM Elements
  const trayContainer = document.getElementById('storiesTrayList');
  const viewerModal = document.getElementById('storyViewerModal');
  const progressBarContainer = document.getElementById('storyProgressBarContainer');
  const storyAuthorAvatar = document.getElementById('storyAuthorAvatar');
  const storyAuthorName = document.getElementById('storyAuthorName');
  const storyTimeAgo = document.getElementById('storyTimeAgo');
  const storyMediaDisplay = document.getElementById('storyMediaDisplay');
  const storyCaption = document.getElementById('storyCaption');
  const storyAuthorControls = document.getElementById('storyAuthorControls');
  const storyViewsPill = document.getElementById('storyViewsPill');
  const storyViewsCount = document.getElementById('storyViewsCount');
  const storyDeleteBtn = document.getElementById('storyDeleteBtn');
  const closeViewerBtn = document.getElementById('closeStoryViewerBtn');
  const tapZoneLeft = document.getElementById('storyTapZoneLeft');
  const tapZoneRight = document.getElementById('storyTapZoneRight');

  // Create Story Modal Elements
  const createStoryModal = document.getElementById('createStoryModal');
  const createStoryForm = document.getElementById('createStoryForm');
  const storyFileInput = document.getElementById('storyFileInput');
  const storyFilePreview = document.getElementById('storyFilePreview');
  const storyTextarea = document.getElementById('storyTextarea');
  const textStoryPreviewCard = document.getElementById('textStoryPreviewCard');

  // Viewers Modal
  const storyViewersModal = document.getElementById('storyViewersModal');
  const storyViewersList = document.getElementById('storyViewersList');
  const storyViewersTotal = document.getElementById('storyViewersTotal');

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    initStoriesTray();
    bindViewerEvents();
    bindCreatorEvents();
  });

  /**
   * 1. LOAD & RENDER STORIES TRAY
   */
  async function initStoriesTray() {
    if (!trayContainer) return;
    try {
      const res = await fetch('/api/v1/stories', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const data = await res.json();
      if (data && data.success && data.data) {
        storyGroups = data.data.user_groups || [];
        renderStoriesTray(storyGroups, data.data.my_stories || []);
      }
    } catch (err) {
      console.error('Failed to load stories:', err);
    }
  }

  function renderStoriesTray(groups, myStories) {
    trayContainer.innerHTML = '';

    // 1. "Add Story / My Story" Item
    const currentUserName = window.ITSA_CURRENT_USER?.full_name || 'You';
    const currentUserInitial = currentUserName.charAt(0).toUpperCase();
    const hasMyStories = myStories && myStories.length > 0;

    const myItem = document.createElement('div');
    myItem.className = 'story-item';
    myItem.innerHTML = `
      <div class="story-ring ${hasMyStories ? 'unseen' : 'add-story'}" id="btnMyStoryRing">
        <div class="story-avatar-inner">
          ${currentUserInitial}
        </div>
        <div class="story-plus-badge">
          <i class="bi bi-plus-lg"></i>
        </div>
      </div>
      <div class="story-username">${hasMyStories ? 'Your Story' : 'Add Story'}</div>
    `;

    myItem.addEventListener('click', () => {
      if (hasMyStories) {
        // Find own group index
        const ownIndex = groups.findIndex(g => g.is_own);
        if (ownIndex !== -1) {
          openStoryViewer(ownIndex, 0);
          return;
        }
      }
      // Otherwise open creator modal
      if (window.bootstrap && createStoryModal) {
        const modal = bootstrap.Modal.getOrCreateInstance(createStoryModal);
        modal.show();
      }
    });
    trayContainer.appendChild(myItem);

    // 2. Render Other Users' Stories
    groups.forEach((group, gIdx) => {
      if (group.is_own) return; // Already handled in My Story slot
      if (!group.stories || group.stories.length === 0) return;

      const ringClass = group.has_unseen ? 'unseen' : 'seen';
      const initial = group.user_name.charAt(0).toUpperCase();

      const item = document.createElement('div');
      item.className = 'story-item';
      item.innerHTML = `
        <div class="story-ring ${ringClass}">
          <div class="story-avatar-inner">
            ${group.user_avatar ? `<img src="${group.user_avatar}" alt="${group.user_name}">` : initial}
          </div>
        </div>
        <div class="story-username" title="${group.user_name}">${group.user_name.split(' ')[0]}</div>
      `;

      item.addEventListener('click', () => {
        // Open at first unseen story, or story 0
        let firstUnseenIdx = group.stories.findIndex(s => !s.has_viewed);
        if (firstUnseenIdx === -1) firstUnseenIdx = 0;
        openStoryViewer(gIdx, firstUnseenIdx);
      });

      trayContainer.appendChild(item);
    });
  }

  /**
   * 2. STORY VIEWER PLAYER
   */
  function openStoryViewer(groupIndex, storyIndex) {
    if (!viewerModal) return;
    currentUserGroupIndex = groupIndex;
    currentStoryIndex = storyIndex;

    viewerModal.classList.add('active');
    document.body.style.overflow = 'hidden';

    renderCurrentStory();
  }

  function closeStoryViewer() {
    if (!viewerModal) return;
    clearTimer();
    viewerModal.classList.remove('active');
    document.body.style.overflow = '';
    // Refresh tray to update seen borders
    initStoriesTray();
  }

  function renderCurrentStory() {
    clearTimer();
    const group = storyGroups[currentUserGroupIndex];
    if (!group || !group.stories || !group.stories[currentStoryIndex]) {
      closeStoryViewer();
      return;
    }

    const story = group.stories[currentStoryIndex];

    // Build Progress Bar Segments
    progressBarContainer.innerHTML = '';
    group.stories.forEach((s, idx) => {
      const seg = document.createElement('div');
      seg.className = 'story-progress-segment';
      const fill = document.createElement('div');
      fill.className = 'story-progress-fill';
      if (idx < currentStoryIndex) {
        fill.classList.add('completed');
      }
      seg.appendChild(fill);
      progressBarContainer.appendChild(seg);
    });

    // Author Info Header
    storyAuthorAvatar.innerHTML = group.user_avatar
      ? `<img src="${group.user_avatar}">`
      : group.user_name.charAt(0).toUpperCase();
    storyAuthorName.textContent = group.user_name;
    storyTimeAgo.textContent = formatTimeAgo(story.created_at);

    // Media Display Content
    storyMediaDisplay.innerHTML = '';
    if (story.media_type === 'IMAGE') {
      const img = document.createElement('img');
      img.className = 'story-media-image';
      img.src = story.media_url;
      img.alt = 'Story';
      storyMediaDisplay.appendChild(img);
    } else if (story.media_type === 'VIDEO') {
      const vid = document.createElement('video');
      vid.className = 'story-media-video';
      vid.src = story.media_url;
      vid.autoplay = true;
      vid.playsInline = true;
      vid.muted = false;
      storyMediaDisplay.appendChild(vid);
    } else {
      // TEXT Story
      const textWrap = document.createElement('div');
      textWrap.className = 'story-text-container';
      textWrap.style.background = story.background_style || 'linear-gradient(135deg, #6366f1, #a855f7)';
      textWrap.textContent = story.text_content;
      storyMediaDisplay.appendChild(textWrap);
    }

    // Caption
    if (story.caption) {
      storyCaption.style.display = 'block';
      storyCaption.textContent = story.caption;
    } else {
      storyCaption.style.display = 'none';
    }

    // Author Controls (Views Pill & Delete Button)
    if (group.is_own || window.ITSA_CURRENT_USER?.role === 'ADMIN') {
      storyAuthorControls.style.display = 'flex';
      storyViewsCount.textContent = story.view_count || 0;
    } else {
      storyAuthorControls.style.display = 'none';
    }

    // Record view in backend
    recordView(story.id);

    // Start Progress Bar Timer
    startProgressTimer();
  }

  function startProgressTimer() {
    clearTimer();
    progressStartTime = Date.now();
    progressElapsedTime = 0;
    isPaused = false;

    const currentFill = progressBarContainer.children[currentStoryIndex]?.querySelector('.story-progress-fill');

    progressTimer = setInterval(() => {
      if (isPaused) return;

      progressElapsedTime = Date.now() - progressStartTime;
      const progressPercent = Math.min((progressElapsedTime / STORY_DURATION_MS) * 100, 100);

      if (currentFill) {
        currentFill.style.width = `${progressPercent}%`;
      }

      if (progressElapsedTime >= STORY_DURATION_MS) {
        clearTimer();
        if (currentFill) currentFill.classList.add('completed');
        goToNextStory();
      }
    }, 40);
  }

  function clearTimer() {
    if (progressTimer) {
      clearInterval(progressTimer);
      progressTimer = null;
    }
  }

  function pauseProgress() {
    if (!isPaused) {
      isPaused = true;
      clearTimer();
    }
  }

  function resumeProgress() {
    if (isPaused) {
      isPaused = false;
      progressStartTime = Date.now() - progressElapsedTime;
      const currentFill = progressBarContainer.children[currentStoryIndex]?.querySelector('.story-progress-fill');

      progressTimer = setInterval(() => {
        if (isPaused) return;
        progressElapsedTime = Date.now() - progressStartTime;
        const progressPercent = Math.min((progressElapsedTime / STORY_DURATION_MS) * 100, 100);

        if (currentFill) {
          currentFill.style.width = `${progressPercent}%`;
        }

        if (progressElapsedTime >= STORY_DURATION_MS) {
          clearTimer();
          if (currentFill) currentFill.classList.add('completed');
          goToNextStory();
        }
      }, 40);
    }
  }

  function goToNextStory() {
    const group = storyGroups[currentUserGroupIndex];
    if (!group) return;

    if (currentStoryIndex < group.stories.length - 1) {
      currentStoryIndex++;
      renderCurrentStory();
    } else {
      // Advance to next user's stories
      if (currentUserGroupIndex < storyGroups.length - 1) {
        currentUserGroupIndex++;
        currentStoryIndex = 0;
        renderCurrentStory();
      } else {
        closeStoryViewer();
      }
    }
  }

  function goToPreviousStory() {
    if (currentStoryIndex > 0) {
      currentStoryIndex--;
      renderCurrentStory();
    } else {
      // Move to previous user's last story
      if (currentUserGroupIndex > 0) {
        currentUserGroupIndex--;
        const prevGroup = storyGroups[currentUserGroupIndex];
        currentStoryIndex = prevGroup.stories.length - 1;
        renderCurrentStory();
      }
    }
  }

  async function recordView(storyId) {
    try {
      const res = await fetch(`/api/v1/stories/${storyId}/view`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
      const data = await res.json();
      if (data && data.success && data.data) {
        // Update local state
        const group = storyGroups[currentUserGroupIndex];
        if (group && group.stories[currentStoryIndex]) {
          group.stories[currentStoryIndex].has_viewed = true;
          group.stories[currentStoryIndex].view_count = data.data.view_count;
        }
      }
    } catch (e) {
      // Ignore background view tracking failure
    }
  }

  /**
   * 3. STORY VIEWER INTERACTIONS & CONTROLS
   */
  function bindViewerEvents() {
    if (!viewerModal) return;

    // Navigation tap zones
    tapZoneLeft?.addEventListener('click', (e) => {
      e.stopPropagation();
      goToPreviousStory();
    });

    tapZoneRight?.addEventListener('click', (e) => {
      e.stopPropagation();
      goToNextStory();
    });

    // Hold to pause
    storyMediaDisplay?.addEventListener('mousedown', pauseProgress);
    storyMediaDisplay?.addEventListener('mouseup', resumeProgress);
    storyMediaDisplay?.addEventListener('touchstart', pauseProgress, { passive: true });
    storyMediaDisplay?.addEventListener('touchend', resumeProgress);

    // Close button
    closeViewerBtn?.addEventListener('click', closeStoryViewer);

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      if (!viewerModal.classList.contains('active')) return;
      if (e.key === 'Escape') closeStoryViewer();
      if (e.key === 'ArrowRight') goToNextStory();
      if (e.key === 'ArrowLeft') goToPreviousStory();
      if (e.key === ' ') {
        isPaused ? resumeProgress() : pauseProgress();
      }
    });

    // Viewers List Pill
    storyViewsPill?.addEventListener('click', async (e) => {
      e.stopPropagation();
      pauseProgress();
      const group = storyGroups[currentUserGroupIndex];
      const story = group?.stories[currentStoryIndex];
      if (!story) return;

      try {
        const res = await fetch(`/api/v1/stories/${story.id}/viewers`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data && data.success) {
          renderStoryViewersModal(data.data.viewers || []);
        }
      } catch (err) {
        console.error('Failed to load viewers:', err);
      }
    });

    // Delete Story Button
    storyDeleteBtn?.addEventListener('click', async (e) => {
      e.stopPropagation();
      pauseProgress();
      const group = storyGroups[currentUserGroupIndex];
      const story = group?.stories[currentStoryIndex];
      if (!story) return;

      if (!confirm('Are you sure you want to delete this story?')) {
        resumeProgress();
        return;
      }

      try {
        const res = await fetch(`/api/v1/stories/${story.id}`, {
          method: 'DELETE',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data && data.success) {
          if (window.showToast) window.showToast('Story deleted', 'info');
          closeStoryViewer();
        } else {
          alert(data.message || 'Could not delete story');
          resumeProgress();
        }
      } catch (err) {
        alert('Network error while deleting story');
        resumeProgress();
      }
    });
  }

  function renderStoryViewersModal(viewers) {
    if (!storyViewersModal || !storyViewersList) return;
    storyViewersTotal.textContent = viewers.length;
    storyViewersList.innerHTML = '';

    if (viewers.length === 0) {
      storyViewersList.innerHTML = `
        <div class="text-center py-4 text-muted small">
          <i class="bi bi-eye-slash fs-3 d-block mb-2"></i>
          No views recorded yet.
        </div>
      `;
    } else {
      viewers.forEach(v => {
        const item = document.createElement('div');
        item.className = 'd-flex align-items-center justify-content-between py-2 border-bottom';
        item.innerHTML = `
          <div class="d-flex align-items-center gap-2">
            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center fw-bold" style="width: 32px; height: 32px; font-size: 0.8125rem;">
              ${v.user_name ? v.user_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <div class="fw-semibold small">${v.user_name}</div>
              <div class="text-muted" style="font-size: 0.75rem;">${v.user_email || ''}</div>
            </div>
          </div>
          <span class="text-muted" style="font-size: 0.75rem;">${formatTimeAgo(v.viewed_at)}</span>
        `;
        storyViewersList.appendChild(item);
      });
    }

    if (window.bootstrap) {
      const modal = bootstrap.Modal.getOrCreateInstance(storyViewersModal);
      modal.show();
      storyViewersModal.addEventListener('hidden.bs.modal', () => {
        resumeProgress();
      }, { once: true });
    }
  }

  /**
   * 4. STORY CREATOR MODAL
   */
  function bindCreatorEvents() {
    if (!createStoryForm) return;

    // Gradient Presets for Text Stories
    let selectedGradient = 'linear-gradient(135deg, #6366f1, #a855f7)';
    document.querySelectorAll('.gradient-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.gradient-preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedGradient = btn.dataset.gradient;
        if (textStoryPreviewCard) {
          textStoryPreviewCard.style.background = selectedGradient;
        }
      });
    });

    // Text story live preview
    storyTextarea?.addEventListener('input', () => {
      if (textStoryPreviewCard) {
        textStoryPreviewCard.textContent = storyTextarea.value || 'Type your message…';
      }
    });

    // File input preview
    storyFileInput?.addEventListener('change', () => {
      const file = storyFileInput.files[0];
      if (file && storyFilePreview) {
        const url = URL.createObjectURL(file);
        if (file.type.startsWith('video/')) {
          storyFilePreview.innerHTML = `<video src="${url}" controls style="max-height: 220px; width: 100%; object-fit: contain; border-radius: 8px;"></video>`;
        } else {
          storyFilePreview.innerHTML = `<img src="${url}" style="max-height: 220px; width: 100%; object-fit: contain; border-radius: 8px;">`;
        }
        storyFilePreview.style.display = 'block';
      }
    });

    // Form submission
    createStoryForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btnSubmitStory');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Sharing…';
      }

      try {
        const formData = new FormData(createStoryForm);
        formData.append('background_style', selectedGradient);

        const res = await fetch('/api/v1/stories', {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: formData
        });

        const data = await res.json();
        if (res.ok && data.success) {
          if (window.showToast) window.showToast('Story shared! Visible for 24 hours.', 'success');
          if (window.bootstrap && createStoryModal) {
            bootstrap.Modal.getInstance(createStoryModal)?.hide();
          }
          createStoryForm.reset();
          if (storyFilePreview) storyFilePreview.style.display = 'none';
          initStoriesTray();
        } else {
          alert(data.message || 'Failed to post story');
        }
      } catch (err) {
        alert('Network error while posting story');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> Share to Story';
        }
      }
    });
  }

  function formatTimeAgo(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);
    if (diffSec < 60) return 'Just now';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  }
})();
