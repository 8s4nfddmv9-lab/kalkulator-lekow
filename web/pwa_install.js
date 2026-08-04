(() => {
  'use strict';

  let deferredPrompt = null;
  let installedInThisSession = false;
  let nextSubscriptionId = 1;
  const subscribers = new Map();
  const displayModeQuery = window.matchMedia('(display-mode: standalone)');

  function isIos() {
    const userAgent = navigator.userAgent || '';
    return /iPad|iPhone|iPod/i.test(userAgent) ||
      (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function isAndroid() {
    return /Android/i.test(navigator.userAgent || '');
  }

  function browserFamily() {
    const userAgent = navigator.userAgent || '';
    if (
      isIos() &&
      /Safari/i.test(userAgent) &&
      !/(CriOS|FxiOS|EdgiOS|OPiOS|DuckDuckGo)/i.test(userAgent)
    ) {
      return 'safari';
    }
    if (/(Chrome|Chromium|CriOS|EdgA|EdgiOS|SamsungBrowser)/i.test(userAgent)) {
      return 'chromium';
    }
    return 'other';
  }

  function isStandalone() {
    return installedInThisSession ||
      displayModeQuery.matches ||
      navigator.standalone === true;
  }

  function currentState() {
    return {
      platform: isIos() ? 'ios' : (isAndroid() ? 'android' : 'other'),
      browser: browserFamily(),
      standalone: isStandalone(),
      canPrompt: deferredPrompt !== null,
    };
  }

  function serializedState() {
    return JSON.stringify(currentState());
  }

  function notifySubscribers() {
    const value = serializedState();
    subscribers.forEach((callback) => {
      try {
        callback(value);
      } catch (error) {
        console.error('Nie udało się zaktualizować stanu instalacji PWA.', error);
      }
    });
  }

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredPrompt = event;
    notifySubscribers();
  });

  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    installedInThisSession = true;
    notifySubscribers();
  });

  if (typeof displayModeQuery.addEventListener === 'function') {
    displayModeQuery.addEventListener('change', notifySubscribers);
  } else if (typeof displayModeQuery.addListener === 'function') {
    displayModeQuery.addListener(notifySubscribers);
  }

  window.infusionCalcPwaGetState = () => serializedState();

  window.infusionCalcPwaPrompt = async () => {
    if (deferredPrompt === null) {
      return 'unavailable';
    }

    const promptEvent = deferredPrompt;
    deferredPrompt = null;
    notifySubscribers();

    try {
      await promptEvent.prompt();
      const choice = await promptEvent.userChoice;
      if (choice && choice.outcome === 'accepted') {
        return 'accepted';
      }
      if (choice && choice.outcome === 'dismissed') {
        return 'dismissed';
      }
      return 'unavailable';
    } catch (error) {
      console.error('Nie udało się otworzyć systemowego promptu instalacji PWA.', error);
      return 'unavailable';
    }
  };

  window.infusionCalcPwaSubscribe = (callback) => {
    const token = String(nextSubscriptionId++);
    subscribers.set(token, callback);
    callback(serializedState());
    return token;
  };

  window.infusionCalcPwaUnsubscribe = (token) => {
    subscribers.delete(String(token));
  };
})();
