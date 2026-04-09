package com.example.weatherdashboard;

import java.util.Map;
import java.util.HashMap;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@CrossOrigin(origins = "http://localhost:5173")
@RestController
@RequestMapping("/api")
public class WeatherController {

    private final RestTemplate restTemplate = new RestTemplate();
    private final Map<String, Object> cache = new HashMap<>();

    @GetMapping("/weather/{city}")
    public Map<String, Object> getWeather(@PathVariable String city) {
        if (cache.containsKey(city)) {
            return (Map<String, Object>) cache.get(city);
        }

        try {
            // Properly URL-encode the city name to handle special characters
            String encodedCity = URLEncoder.encode(city.trim(), StandardCharsets.UTF_8);
            String url = "https://weather-dashboard-iidt.onrender.com/weather/" + encodedCity;

            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            if (response == null) {
                return Map.of("status", "error", "message", "No response from Python service");
            }

            cache.put(city, response);
            return response;

        } catch (Exception e) {
            return Map.of(
                "status", "error",
                "message", "Failed to fetch weather data",
                "details", e.getMessage()
            );
        }
    }

    @GetMapping("/history/{city}")
    public Object getHistory(@PathVariable String city) {
        try {
            // Properly URL-encode the city name
            String encodedCity = URLEncoder.encode(city.trim(), StandardCharsets.UTF_8);
            String url = "http://127.0.0.1:8000/history/" + encodedCity;
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            return Map.of("error", "Failed to fetch history: " + e.getMessage());
        }
    }
}