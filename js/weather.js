/**
 * Live Kalamazoo Weather Service
 * Uses Open-Meteo API (No API key needed, highly reliable, CORS friendly)
 * Target Coordinates: WMU Parkview Campus / Kalamazoo (42.2576° N, 85.6433° W)
 */

class WeatherService {
  constructor(options = {}) {
    this.lat = options.lat || 42.2576;
    this.lon = options.lon || -85.6433;
    this.refreshIntervalMinutes = options.refreshIntervalMinutes || 15;
    this.tempElement = document.getElementById('weatherTemp');
    this.descElement = document.getElementById('weatherDesc');
    this.iconElement = document.getElementById('weatherIcon');
    this.cachedData = null;
    this.timer = null;
  }

  init() {
    this.fetchWeather();
    this.timer = setInterval(() => this.fetchWeather(), this.refreshIntervalMinutes * 60 * 1000);
  }

  async fetchWeather() {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${this.lat}&longitude=${this.lon}&current_weather=true&temperature_unit=fahrenheit&windspeed_unit=mph`;

    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Weather HTTP error: ${response.status}`);
      const data = await response.json();
      
      if (data && data.current_weather) {
        this.cachedData = data.current_weather;
        this.render(data.current_weather);
      }
    } catch (err) {
      console.warn('Live weather fetch failed, utilizing cached or fallback weather:', err.message);
      if (this.cachedData) {
        this.render(this.cachedData);
      } else {
        // Sensible fallback for Kalamazoo
        this.render({ temperature: 72, weathercode: 1 });
      }
    }
  }

  getWeatherCondition(code) {
    // WMO Weather interpretation codes (WW)
    const codeMap = {
      0: { desc: 'Clear Sky', icon: '☀️' },
      1: { desc: 'Mainly Clear', icon: '🌤️' },
      2: { desc: 'Partly Cloudy', icon: '⛅' },
      3: { desc: 'Overcast', icon: '☁️' },
      45: { desc: 'Foggy', icon: '🌫️' },
      48: { desc: 'Depositing Rime Fog', icon: '🌫️' },
      51: { desc: 'Light Drizzle', icon: '🌦️' },
      53: { desc: 'Moderate Drizzle', icon: '🌧️' },
      55: { desc: 'Dense Drizzle', icon: '🌧️' },
      61: { desc: 'Slight Rain', icon: '🌦️' },
      63: { desc: 'Moderate Rain', icon: '🌧️' },
      65: { desc: 'Heavy Rain', icon: '🌧️' },
      71: { desc: 'Slight Snow', icon: '🌨️' },
      73: { desc: 'Moderate Snow', icon: '❄️' },
      75: { desc: 'Heavy Snow', icon: '❄️' },
      80: { desc: 'Rain Showers', icon: '🌦️' },
      81: { desc: 'Moderate Showers', icon: '🌧️' },
      82: { desc: 'Violent Showers', icon: '⛈️' },
      85: { desc: 'Snow Showers', icon: '🌨️' },
      86: { desc: 'Heavy Snow Showers', icon: '❄️' },
      95: { desc: 'Thunderstorm', icon: '⛈️' },
      96: { desc: 'Thunderstorm with Hail', icon: '⛈️' },
      99: { desc: 'Severe Thunderstorm', icon: '⛈️' }
    };

    return codeMap[code] || { desc: 'Kalamazoo, MI', icon: '🌤️' };
  }

  render(current) {
    const temp = Math.round(current.temperature);
    const { desc, icon } = this.getWeatherCondition(current.weathercode);

    if (this.tempElement) this.tempElement.textContent = `${temp}°F`;
    if (this.descElement) this.descElement.textContent = desc;
    if (this.iconElement) this.iconElement.textContent = icon;
  }
}

window.WeatherService = WeatherService;
