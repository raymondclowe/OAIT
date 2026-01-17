# OAIT PWA (Progressive Web App) Features

## Overview

OAIT now includes Progressive Web App (PWA) support, enabling:
- **Install on mobile devices** (Android, iOS)
- **Install on desktop** (Windows, Mac, Linux)
- **Offline UI support** (via service worker caching)
- **App-like experience** (no browser chrome when installed)

## Files Added

### 1. Web App Manifest (`manifest.json`)
Defines the app metadata for installation:
- App name, description, colors
- Icons (192x192 and 512x512)
- Display mode (standalone)
- Categories and screenshots

### 2. Service Worker (`sw.js`)
Provides offline support:
- Caches static assets for offline access
- Network-first strategy for API calls
- Graceful degradation when offline
- Automatic cache updates

### 3. App Icons
SVG-based icons for various screen sizes:
- `icons/icon-192.png` - 192x192 icon
- `icons/icon-512.png` - 512x512 icon
- Gradient design with brain/AI + book imagery
- OAIT branding

## How to Use

### Installing on Mobile (Android)

1. Open Chrome/Edge on Android
2. Navigate to `https://your-server:7860`
3. Tap the menu (⋮) → "Install app" or "Add to Home screen"
4. Confirm installation
5. App icon appears on home screen

### Installing on Desktop

1. Open Chrome/Edge on desktop
2. Navigate to `https://your-server:7860`
3. Click the install icon (⊕) in the address bar
4. Or: Menu → "Install OAIT"
5. App opens in standalone window

### Installing on iOS

1. Open Safari on iOS
2. Navigate to `https://your-server:7860`
3. Tap the Share button (⬆)
4. Select "Add to Home Screen"
5. Confirm and app appears on home screen

## Offline Capabilities

The service worker caches:
- Static HTML pages
- CSS and JavaScript (future)
- App manifest
- Icons

**Note**: WebSocket connections require network connectivity. The offline mode provides access to the UI, but live tutoring requires an active connection.

## Testing PWA Features

### Check PWA Status

1. Open DevTools (F12)
2. Go to Application tab
3. Check "Manifest" section
4. Check "Service Workers" section

### Lighthouse PWA Audit

```bash
# Install Lighthouse
npm install -g lighthouse

# Run PWA audit
lighthouse https://your-server:7860 --only-categories=pwa
```

## Configuration

### Update Manifest (`manifest.json`)

- **name**: Full app name
- **short_name**: Short name for home screen
- **start_url**: Initial URL when app opens
- **theme_color**: Browser UI color
- **background_color**: Splash screen color

### Update Service Worker (`sw.js`)

- **CACHE_NAME**: Update version when deploying
- **STATIC_ASSETS**: Add/remove cached files
- Caching strategy can be modified as needed

## Browser Support

| Browser | PWA Install | Service Worker | Offline Support |
|---------|-------------|----------------|-----------------|
| Chrome (Android) | ✅ | ✅ | ✅ |
| Chrome (Desktop) | ✅ | ✅ | ✅ |
| Edge (Desktop) | ✅ | ✅ | ✅ |
| Safari (iOS 14+) | ✅ | ⚠️ Limited | ⚠️ Limited |
| Firefox | ⚠️ Partial | ✅ | ✅ |

## Security Considerations

- **HTTPS Required**: PWAs require HTTPS in production
- **localhost Exception**: Works on localhost for development
- **Service Worker Scope**: Limited to same origin
- **Cache Management**: Old caches are automatically deleted

## Future Enhancements

1. **Offline Queue**: Queue actions when offline, sync when online
2. **Push Notifications**: Notify students of session reminders
3. **Background Sync**: Sync session data in background
4. **Shortcuts**: Quick actions from app icon
5. **Share Target**: Allow sharing problems directly to OAIT

## Troubleshooting

### Service Worker Not Registering

- Check console for errors
- Verify HTTPS or localhost
- Clear browser cache
- Check service worker scope

### Icons Not Showing

- Verify icon paths in manifest.json
- Check icon file sizes match manifest
- Clear app data and reinstall

### Offline Mode Not Working

- Verify service worker is active
- Check network tab for cache hits
- Ensure static assets are in STATIC_ASSETS array

## Resources

- [PWA Documentation](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Workbox](https://developers.google.com/web/tools/workbox) - Advanced service worker library

---

**Last Updated**: 2026-01-17
