'use strict';

/**
 * User Storage
 * Persists user preferences and booking history to ~/.openclaw/data/planit/users/{userId}.json
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const BASE_DIR = path.join(os.homedir(), '.openclaw', 'data', 'planit', 'users');

function getUserFilePath(userId) {
  return path.join(BASE_DIR, `${userId}.json`);
}

function ensureDir() {
  if (!fs.existsSync(BASE_DIR)) {
    fs.mkdirSync(BASE_DIR, { recursive: true });
  }
}

/**
 * Load user data. Returns default structure if not found.
 */
function loadUser(userId) {
  ensureDir();
  const filePath = getUserFilePath(userId);
  if (!fs.existsSync(filePath)) {
    return {
      userId,
      preferences: {
        budget: null,       // 'budget' | 'mid' | 'luxury'
        group: null,        // 'elderly' | 'family_kids' | etc.
        originCity: '上海',
      },
      history: [],          // array of booking records
      hotelBookings: {},    // destinationCity -> [hotelId, ...]
    };
  }
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return {
      userId,
      preferences: { budget: null, group: null, originCity: '上海' },
      history: [],
      hotelBookings: {},
    };
  }
}

/**
 * Save user data to disk.
 */
function saveUser(userId, data) {
  ensureDir();
  const filePath = getUserFilePath(userId);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

/**
 * Record a hotel booking for a user.
 * @param {string} userId
 * @param {string} destination - City name
 * @param {string} hotelId
 * @param {object} bookingDetails - { date, duration, group, budget }
 */
function recordHotelBooking(userId, destination, hotelId, bookingDetails = {}) {
  const user = loadUser(userId);

  // Update hotelBookings map
  if (!user.hotelBookings[destination]) {
    user.hotelBookings[destination] = [];
  }
  // Move to front if already exists, else prepend
  user.hotelBookings[destination] = [
    hotelId,
    ...user.hotelBookings[destination].filter((id) => id !== hotelId),
  ];

  // Append to history
  user.history.push({
    type: 'hotel_booking',
    destination,
    hotelId,
    ...bookingDetails,
    timestamp: new Date().toISOString(),
  });

  // Update preferences if provided
  if (bookingDetails.budget) user.preferences.budget = bookingDetails.budget;
  if (bookingDetails.group) user.preferences.group = bookingDetails.group;

  saveUser(userId, user);
  return user;
}

/**
 * Get previously booked hotel IDs for a destination, in preference order (most recent first).
 */
function getPreviousHotelBookings(userId, destination) {
  const user = loadUser(userId);
  return user.hotelBookings[destination] || [];
}

/**
 * Update user preferences.
 */
function updatePreferences(userId, prefs) {
  const user = loadUser(userId);
  Object.assign(user.preferences, prefs);
  saveUser(userId, user);
  return user;
}

/**
 * Get user preferences.
 */
function getPreferences(userId) {
  const user = loadUser(userId);
  return user.preferences;
}

/**
 * Get booking history (most recent first).
 */
function getHistory(userId, limit = 20) {
  const user = loadUser(userId);
  return [...user.history].reverse().slice(0, limit);
}

module.exports = {
  loadUser,
  saveUser,
  recordHotelBooking,
  getPreviousHotelBookings,
  updatePreferences,
  getPreferences,
  getHistory,
};
