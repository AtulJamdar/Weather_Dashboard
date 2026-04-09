package com.example.weatherdashboard;

import java.util.Map;
import java.util.HashMap;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

// This allows your Vercel frontend to access this API
@CrossOrigin(origins = "*") 
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
            String encodedCity = URLEncoder.encode(city.trim(), StandardCharsets.UTF_8);
            // Calling your LIVE Python Backend
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
            String encodedCity = URLEncoder.encode(city.trim(), StandardCharsets.UTF_8);
            // Fixed: Changed from localhost to your live Python Render URL
            String url = "https://weather-dashboard-iidt.onrender.com/history/" + encodedCity;
            return restTemplate.getForObject(url, Object.class);
        } catch (Exception e) {
            return Map.of("error", "Failed to fetch history: " + e.getMessage());
        }
    }
}