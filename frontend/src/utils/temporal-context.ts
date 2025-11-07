/**
 * Seasonal & Temporal Context
 * Phase 1: Quick Wins - Auto-inject timely relevance
 */

export interface Season {
  name: string;
  months: number[];
  mood: string;
  colors: string[];
  themes: string[];
  visualElements: string[];
}

export interface TemporalContext {
  season: Season;
  currentMonth: string;
  upcomingHolidays: string[];
  seasonalMood: string;
  suggestedThemes: string[];
}

const SEASONS: Record<string, Season> = {
  spring: {
    name: 'Spring',
    months: [3, 4, 5], // March, April, May
    mood: 'Fresh, renewing, optimistic, vibrant',
    colors: ['#FFB6C1', '#98FB98', '#87CEEB', '#FFFACD'],
    themes: ['growth', 'renewal', 'fresh starts', 'blossoming', 'vitality'],
    visualElements: ['flowers', 'bright colors', 'outdoor scenes', 'fresh greenery', 'sunlight']
  },
  summer: {
    name: 'Summer',
    months: [6, 7, 8], // June, July, August
    mood: 'Energetic, bright, adventurous, carefree',
    colors: ['#FFD700', '#FF6347', '#87CEEB', '#32CD32'],
    themes: ['adventure', 'freedom', 'energy', 'vacation', 'outdoors'],
    visualElements: ['sunshine', 'beaches', 'vibrant colors', 'outdoor activities', 'blue skies']
  },
  autumn: {
    name: 'Autumn',
    months: [9, 10, 11], // September, October, November
    mood: 'Warm, cozy, reflective, harvest',
    colors: ['#D2691E', '#FF8C00', '#8B4513', '#DAA520'],
    themes: ['harvest', 'coziness', 'transition', 'gratitude', 'preparation'],
    visualElements: ['fall foliage', 'warm tones', 'cozy settings', 'natural textures']
  },
  winter: {
    name: 'Winter',
    months: [12, 1, 2], // December, January, February
    mood: 'Cozy, festive, reflective, calm',
    colors: ['#4682B4', '#FFFFFF', '#C0C0C0', '#DC143C'],
    themes: ['celebration', 'togetherness', 'reflection', 'renewal', 'warmth'],
    visualElements: ['snow', 'warm lights', 'indoor coziness', 'celebrations', 'cool tones']
  }
};

const HOLIDAYS: Record<number, { month: number; day: number; name: string; themes: string[] }[]> = {
  1: [
    { month: 1, day: 1, name: 'New Year', themes: ['fresh start', 'goals', 'celebration'] }
  ],
  2: [
    { month: 2, day: 14, name: 'Valentine\'s Day', themes: ['love', 'romance', 'connection'] }
  ],
  3: [
    { month: 3, day: 17, name: 'St. Patrick\'s Day', themes: ['luck', 'celebration', 'green'] }
  ],
  4: [
    { month: 4, day: 22, name: 'Earth Day', themes: ['sustainability', 'environment', 'nature'] }
  ],
  5: [
    { month: 5, day: 12, name: 'Mother\'s Day', themes: ['appreciation', 'family', 'love'] }
  ],
  6: [
    { month: 6, day: 16, name: 'Father\'s Day', themes: ['appreciation', 'family', 'gratitude'] }
  ],
  7: [
    { month: 7, day: 4, name: 'Independence Day (US)', themes: ['freedom', 'celebration', 'patriotism'] }
  ],
  9: [
    { month: 9, day: 4, name: 'Labor Day', themes: ['work', 'achievement', 'rest'] }
  ],
  10: [
    { month: 10, day: 31, name: 'Halloween', themes: ['fun', 'creativity', 'mystery'] }
  ],
  11: [
    { month: 11, day: 22, name: 'Thanksgiving', themes: ['gratitude', 'family', 'abundance'] },
    { month: 11, day: 29, name: 'Black Friday', themes: ['deals', 'shopping', 'urgency'] }
  ],
  12: [
    { month: 12, day: 25, name: 'Christmas', themes: ['giving', 'celebration', 'joy', 'family'] },
    { month: 12, day: 31, name: 'New Year\'s Eve', themes: ['celebration', 'reflection', 'anticipation'] }
  ]
};

// Get current season based on month
export function getCurrentSeason(date: Date = new Date()): Season {
  const month = date.getMonth() + 1; // getMonth() returns 0-11
  
  for (const season of Object.values(SEASONS)) {
    if (season.months.includes(month)) {
      return season;
    }
  }
  
  return SEASONS.winter; // Default fallback
}

// Get upcoming holidays (within next 30 days)
export function getUpcomingHolidays(date: Date = new Date(), daysAhead: number = 30): string[] {
  const currentMonth = date.getMonth() + 1;
  const currentDay = date.getDate();
  const upcoming: string[] = [];
  
  // Check current month
  const currentMonthHolidays = HOLIDAYS[currentMonth] || [];
  for (const holiday of currentMonthHolidays) {
    const daysUntil = holiday.day - currentDay;
    if (daysUntil >= 0 && daysUntil <= daysAhead) {
      upcoming.push(`${holiday.name} in ${daysUntil} days`);
    }
  }
  
  // Check next month
  const nextMonth = currentMonth === 12 ? 1 : currentMonth + 1;
  const nextMonthHolidays = HOLIDAYS[nextMonth] || [];
  for (const holiday of nextMonthHolidays) {
    // Simplified calculation - just check if next month is within range
    upcoming.push(`${holiday.name} next month`);
  }
  
  return upcoming.slice(0, 3); // Return max 3 upcoming holidays
}

// Get month name
export function getMonthName(date: Date = new Date()): string {
  return date.toLocaleString('en-US', { month: 'long' });
}

// Get full temporal context
export function getTemporalContext(date: Date = new Date()): TemporalContext {
  const season = getCurrentSeason(date);
  const upcomingHolidays = getUpcomingHolidays(date);
  
  return {
    season,
    currentMonth: getMonthName(date),
    upcomingHolidays,
    seasonalMood: season.mood,
    suggestedThemes: season.themes
  };
}

// Enrich prompt with temporal context
export function enrichPromptWithTemporal(basePrompt: string, date: Date = new Date()): string {
  const context = getTemporalContext(date);
  
  const temporalEnrichment = `
TEMPORAL CONTEXT:
- Season: ${context.season.name} (${context.currentMonth})
- Seasonal Mood: ${context.seasonalMood}
- Seasonal Themes: ${context.suggestedThemes.join(', ')}
- Color Palette: ${context.season.colors.join(', ')}
- Visual Elements: ${context.season.visualElements.join(', ')}
${context.upcomingHolidays.length > 0 ? `- Upcoming Events: ${context.upcomingHolidays.join(', ')}` : ''}

Consider incorporating seasonal elements that resonate with the current time of year to make the content more timely and relevant.
`;

  return `${basePrompt}\n\n${temporalEnrichment}`;
}

// Get holiday themes for a specific date
export function getHolidayThemes(date: Date = new Date()): string[] {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const monthHolidays = HOLIDAYS[month] || [];
  
  for (const holiday of monthHolidays) {
    // Check if within 7 days of holiday
    const daysUntil = Math.abs(holiday.day - day);
    if (daysUntil <= 7) {
      return holiday.themes;
    }
  }
  
  return [];
}
