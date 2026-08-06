(function initializeOdodokAmplitude(window, document) {
  "use strict";

  // Amplitude browser ingestion keys are public project identifiers.
  const API_KEY = "2dd1bb5ab69073d8eeb3148d389b18a6";
  const SDK_URL = `https://cdn.amplitude.com/script/${API_KEY}.js`;
  const LOAD_TIMEOUT_MS = 3000;
  let sdkPromise;

  function startLoading() {
    sdkPromise = new Promise((resolve) => {
      const script = document.createElement("script");

      script.src = SDK_URL;
      script.onload = () => {
        try {
          if (!window.amplitude) {
            resolve(false);
            return;
          }

          if (window.sessionReplay && typeof window.sessionReplay.plugin === "function") {
            window.amplitude.add(window.sessionReplay.plugin({ sampleRate: 1 }));
          }

          window.amplitude.init(API_KEY, {
            serverZone: "US",
            fetchRemoteConfig: true,
            trackingOptions: { ipAddress: false },
            autocapture: {
              attribution: true,
              fileDownloads: false,
              formInteractions: false,
              pageViews: false,
              sessions: true,
              elementInteractions: true,
              networkTracking: false,
              webVitals: true,
              frustrationInteractions: true,
            },
          });

          resolve(true);
        } catch (_error) {
          resolve(false);
        }
      };
      script.onerror = () => {
        resolve(false);
      };

      document.head.appendChild(script);
    });

    return sdkPromise;
  }

  function load() {
    const readiness = sdkPromise || startLoading();

    return new Promise((resolve) => {
      const timeout = window.setTimeout(() => resolve(false), LOAD_TIMEOUT_MS);
      readiness.then((enabled) => {
        window.clearTimeout(timeout);
        resolve(enabled);
      });
    });
  }

  function track(eventName, eventProperties, useBeacon) {
    return load()
      .then((enabled) => {
        if (!enabled || !window.amplitude) return { code: 0 };
        if (useBeacon) window.amplitude.setTransport("beacon");
        const result = window.amplitude.track(eventName, eventProperties);
        return result && result.promise ? result.promise : result;
      })
      .catch(() => ({ code: 0 }));
  }

  function flush(useBeacon) {
    return load()
      .then((enabled) => {
        if (!enabled || !window.amplitude) return { code: 0 };
        if (useBeacon) window.amplitude.setTransport("beacon");
        const result = window.amplitude.flush();
        return result && result.promise ? result.promise : result;
      })
      .catch(() => ({ code: 0 }));
  }

  window.addEventListener("pagehide", () => {
    if (!window.amplitude) return;
    try {
      window.amplitude.setTransport("beacon");
      window.amplitude.flush();
    } catch (_error) {
      // Analytics must never block navigation.
    }
  });

  window.ododokAmplitude = { load, track, flush };
})(window, document);
