(() => {
  'use strict';

  const PRODUCTION_HOST = 'infusioncalc.eu';
  const MAX_QUEUE_SIZE = 32;
  const MAX_RETRY_ATTEMPTS = 40;
  const RETRY_DELAY_MS = 500;

  const ALLOWED_EVENTS = new Set([
    'app_open',
    'install_prompt_opened',
    'install_button_clicked',
    'pwa_installed',
    'warning_opened',
    'privacy_opened',
    'github_clicked',
    'contact_clicked',
  ]);

  const ALLOWED_INSTALL_METHODS = new Set([
    'ios_safari_instructions',
    'ios_open_safari',
    'android_native_prompt',
    'android_manual_instructions',
  ]);

  const queue = [];
  let retryAttempts = 0;
  let retryTimer = null;

  function isIos() {
    const userAgent = navigator.userAgent || '';
    return /iPad|iPhone|iPod/i.test(userAgent) ||
      (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function platform() {
    if (isIos()) return 'ios';
    if (/Android/i.test(navigator.userAgent || '')) return 'android';
    return 'other';
  }

  function displayMode() {
    return window.matchMedia('(display-mode: standalone)').matches ||
      navigator.standalone === true
      ? 'standalone'
      : 'browser';
  }

  function sanitizePayload(payload) {
    const result = {
      platform: platform(),
      display_mode: displayMode(),
    };

    const appVersion = typeof payload.app_version === 'string'
      ? payload.app_version.trim()
      : '';
    if (/^[0-9A-Za-z.+-]{1,48}$/.test(appVersion)) {
      result.app_version = appVersion;
    }

    const installMethod = typeof payload.install_method === 'string'
      ? payload.install_method.trim()
      : '';
    if (ALLOWED_INSTALL_METHODS.has(installMethod)) {
      result.install_method = installMethod;
    }

    return result;
  }

  function send(item) {
    if (window.location.hostname !== PRODUCTION_HOST) {
      return true;
    }
    if (!window.umami || typeof window.umami.track !== 'function') {
      return false;
    }

    try {
      window.umami.track(item.name, item.data);
      return true;
    } catch (_) {
      return false;
    }
  }

  function flushQueue() {
    retryTimer = null;
    while (queue.length > 0 && send(queue[0])) {
      queue.shift();
    }

    if (queue.length === 0 || retryAttempts >= MAX_RETRY_ATTEMPTS) {
      if (retryAttempts >= MAX_RETRY_ATTEMPTS) {
        queue.length = 0;
      }
      return;
    }

    retryAttempts += 1;
    retryTimer = window.setTimeout(flushQueue, RETRY_DELAY_MS);
  }

  function scheduleFlush() {
    if (retryTimer !== null || retryAttempts >= MAX_RETRY_ATTEMPTS) {
      return;
    }
    retryTimer = window.setTimeout(flushQueue, RETRY_DELAY_MS);
  }

  window.infusionCalcAnalyticsTrack = (eventName, payloadJson) => {
    if (!ALLOWED_EVENTS.has(eventName)) {
      return false;
    }

    let payload = {};
    try {
      const parsed = JSON.parse(payloadJson || '{}');
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        payload = parsed;
      }
    } catch (_) {
      payload = {};
    }

    const item = {
      name: eventName,
      data: sanitizePayload(payload),
    };

    if (send(item)) {
      return true;
    }

    if (queue.length < MAX_QUEUE_SIZE) {
      queue.push(item);
      scheduleFlush();
    }
    return true;
  };
})();
