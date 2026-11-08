/* ==========================================================================
   ITSA PLATFORM — COMMUNITY FEED BEHAVIORS
   Post creation · Reactions · Comments · Media picker
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
     1. POST COMPOSER
     ============================================================ */
  const composer = document.getElementById('postForm');
  const composerTextarea = composer?.querySelector('textarea[name="content"]');
  const composerPhotoBtn = document.querySelector('[data-feed-action="photos"]');
  const composerVideoBtn = document.querySelector('[data-feed-action="video"]');
  const composerPhotoInput = document.getElementById('feed-photo-input');
  const composerVideoInput = document.getElementById('feed-video-input');
  const composerPreview = document.getElementById('feed-media-preview');

  let selectedFile = null;

  if (composer && composerTextarea) {
    composer.addEventListener('submit', async (e) => {
      e.preventDefault();

      const content = composerTextarea.value.trim();
      if (!content && !selectedFile) {
        toast.error('Empty post', 'Please write something or attach a photo/video.');
        return;
      }

      const submitBtn = composer.querySelector('button[type="submit"]');
      const originalHtml = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Posting…';

      try {
        const formData = new FormData();
        formData.append('content', content);
        if (selectedFile) {
          formData.append('media', selectedFile);
        }

        const res = await fetch('/api/v1/posts', {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: formData,
          credentials: 'same-origin'
        });

        const data = await res.json().catch(() => ({}));

        if (res.ok) {
          toast.success('Posted!', 'Your post is live. +2 points earned.');
          composerTextarea.value = '';
          selectedFile = null;
          if (composerPreview) {
            composerPreview.innerHTML = '';
            composerPreview.style.display = 'none';
          }
          setTimeout(() => window.location.reload(), 600);
        } else {
          let errMsg = `HTTP ${res.status}`;
          if (data.error) {
            errMsg = data.error.message || data.error.code || errMsg;
          } else if (data.message) {
            errMsg = data.message;
          }
          toast.error('Failed', errMsg);
        }
      } catch (err) {
        console.error('Post error:', err);
        toast.error('Network error', 'Could not reach the server.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalHtml;
      }
    });

    composerTextarea.addEventListener('input', () => {
      composerTextarea.style.height = 'auto';
      composerTextarea.style.height = Math.min(composerTextarea.scrollHeight, 300) + 'px';
    });
  }

  /* ============================================================
     2. MEDIA PICKER
     ============================================================ */
  if (composerPhotoBtn && composerPhotoInput) {
    composerPhotoBtn.addEventListener('click', (e) => {
      e.preventDefault();
      composerPhotoInput.click();
    });

    composerPhotoInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      selectedFile = file;
      showPreview(file, 'image');
    });
  }

  if (composerVideoBtn && composerVideoInput) {
    composerVideoBtn.addEventListener('click', (e) => {
      e.preventDefault();
      composerVideoInput.click();
    });

    composerVideoInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      selectedFile = file;
      showPreview(file, 'video');
    });
  }

  function showPreview(file, type) {
    if (!composerPreview) return;
    const url = URL.createObjectURL(file);

    composerPreview.style.display = 'block';
    composerPreview.innerHTML = `
      <div class="feed-preview-item">
        ${type === 'image'
          ? `<img src="${url}" alt="Preview">`
          : `<video src="${url}" controls></video>`}
        <button type="button" class="feed-preview-remove" aria-label="Remove">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    `;

    composerPreview.querySelector('.feed-preview-remove').addEventListener('click', () => {
      selectedFile = null;
      composerPreview.innerHTML = '';
      composerPreview.style.display = 'none';
      if (composerPhotoInput) composerPhotoInput.value = '';
      if (composerVideoInput) composerVideoInput.value = '';
    });
  }

  /* ============================================================
     3. REACTIONS
     ============================================================ */
  document.querySelectorAll('[data-reaction]').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();

      const postId = btn.dataset.postId;
      const reaction = btn.dataset.reaction;

      console.log(`🖱️ Reaction clicked: ${reaction} on post ${postId}`);

      const wasActive = btn.classList.contains('active');

      const post = btn.closest('.social-post');
      const actionBar = post?.querySelector('.social-post-actions');

      actionBar?.querySelectorAll('[data-reaction]').forEach(b => {
        b.classList.remove('active');
        const icon = b.querySelector('i');
        if (icon) {
          icon.classList.remove('bi-hand-thumbs-up-fill', 'bi-heart-fill');
        }
      });

      if (!wasActive) {
        btn.classList.add('active');
        const icon = btn.querySelector('i');
        if (icon) {
          if (reaction === 'LIKE') icon.classList.add('bi-hand-thumbs-up-fill');
          if (reaction === 'LOVE') icon.classList.add('bi-heart-fill');
        }
      }

      try {
        const res = await fetch(`/api/v1/posts/${postId}/react`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify({ reaction_type: reaction })
        });

        console.log(`📡 API response status: ${res.status}`);

        const data = await res.json().catch(() => ({}));
        console.log('📦 API response data:', data);

        if (res.ok && data.success !== false) {
          const reactionText = reaction.toLowerCase();
          toast.success('Reaction saved', `You reacted with ${reactionText}.`);
          console.log(`✅ Reaction ${reaction} saved successfully`);
        } else {
          btn.classList.remove('active');
          const icon = btn.querySelector('i');
          if (icon) {
            icon.classList.remove('bi-hand-thumbs-up-fill', 'bi-heart-fill');
          }
          const errMsg = data.error?.message || data.message || `HTTP ${res.status}`;
          toast.error('Failed', errMsg);
        }
      } catch (err) {
        console.error('❌ Reaction error:', err);
        btn.classList.remove('active');
        const icon = btn.querySelector('i');
        if (icon) {
          icon.classList.remove('bi-hand-thumbs-up-fill', 'bi-heart-fill');
        }
        toast.error('Network error', err.message || 'Could not save reaction.');
      }
    });
  });

  /* ============================================================
     4. INLINE COMMENTS
     ============================================================ */
  document.querySelectorAll('.social-comment-input').forEach(input => {
    const postId = input.dataset.postId;

    const submit = async () => {
      const text = input.value.trim();
      if (!text) return;

      const sendBtn = input.parentElement.querySelector('.social-send-btn');
      if (sendBtn) sendBtn.disabled = true;

      console.log(`💬 Posting comment on post ${postId}: "${text}"`);

      try {
        const res = await fetch(`/api/v1/comments/post/${postId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify({ content: text })
        });

        console.log(`📡 Comment API status: ${res.status}`);
        const data = await res.json().catch(() => ({}));
        console.log('📦 Comment response:', data);

        if (res.ok && data.success !== false) {
          input.value = '';
          toast.success('Comment added', 'Your comment is now visible.');
          setTimeout(() => window.location.reload(), 600);
        } else {
          const errMsg = data.error?.message || data.message || `HTTP ${res.status}`;
          toast.error('Failed', errMsg);
        }
      } catch (err) {
        console.error('Comment error:', err);
        toast.error('Network error', 'Could not save comment.');
      } finally {
        if (sendBtn) sendBtn.disabled = false;
      }
    };

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    });

    const btn = input.parentElement.querySelector('.social-send-btn');
    btn?.addEventListener('click', (e) => {
      e.preventDefault();
      submit();
    });
  });

  /* ============================================================
     5. COMMENT BUTTON — focus the input
     ============================================================ */
  document.querySelectorAll('.social-action-comment').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const post = btn.closest('.social-post');
      post?.querySelector('.social-comment-input')?.focus();
    });
  });

  /* ============================================================
     6. VIEW MORE COMMENTS
     ============================================================ */
  document.querySelectorAll('.social-view-more').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.reload();
    });
  });

  console.log('✅ feed.js loaded');
})();