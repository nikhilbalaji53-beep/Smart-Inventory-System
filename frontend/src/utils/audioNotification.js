// Audio Notification Utility
// Creates and plays alert sounds for critical notifications

export const playAlertSound = (type = 'critical') => {
  try {
    // Create audio context
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    if (type === 'critical') {
      // Critical alert: High-pitched warning beep (3 rapid beeps)
      playCriticalAlert(audioContext);
    } else if (type === 'warning') {
      // Warning alert: Medium-pitched beep (2 beeps)
      playWarningAlert(audioContext);
    } else if (type === 'info') {
      // Info alert: Soft beep (1 beep)
      playInfoAlert(audioContext);
    }
  } catch (error) {
    console.error('Error playing notification sound:', error);
  }
};

const playCriticalAlert = (audioContext) => {
  const now = audioContext.currentTime;
  const duration = 0.15;
  
  // 3 rapid beeps at 1000 Hz
  for (let i = 0; i < 3; i++) {
    playBeep(audioContext, 1000, now + i * 0.25, duration);
  }
};

const playWarningAlert = (audioContext) => {
  const now = audioContext.currentTime;
  const duration = 0.2;
  
  // 2 beeps at 750 Hz
  playBeep(audioContext, 750, now, duration);
  playBeep(audioContext, 750, now + 0.35, duration);
};

const playInfoAlert = (audioContext) => {
  const now = audioContext.currentTime;
  
  // 1 soft beep at 500 Hz
  playBeep(audioContext, 500, now, 0.25);
};

const playBeep = (audioContext, frequency, startTime, duration) => {
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);
  
  oscillator.frequency.value = frequency;
  oscillator.type = 'sine';
  
  // Smooth volume envelope (attack and release)
  gainNode.gain.setValueAtTime(0, startTime);
  gainNode.gain.linearRampToValueAtTime(0.3, startTime + 0.01);
  gainNode.gain.linearRampToValueAtTime(0, startTime + duration);
  
  oscillator.start(startTime);
  oscillator.stop(startTime + duration);
};

// Browser notification API for desktop notifications
export const showDesktopNotification = (title, options = {}) => {
  if ('Notification' in window) {
    // Request permission if not already granted
    if (Notification.permission === 'granted') {
      new Notification(title, {
        icon: '📦',
        badge: '🔴',
        ...options
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, {
            icon: '📦',
            badge: '🔴',
            ...options
          });
        }
      });
    }
  }
};

// Request notification permissions on page load
export const requestNotificationPermissions = () => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
};
