package com.example.weatherdashboard;

import java.util.Map;
import java.util.HashMap;

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

        String url = "http://127.0.0.1:8000/weather/" + city;

        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            if (response == null) {
                return Map.of("error", "No response from Python service");
            }

            cache.put(city, response);
            return response; // don't remap keys unnecessarily

        } catch (Exception e) {
            return Map.of(
                "error", "Failed to call Python API",
                "details", e.getMessage()
            );
        }
    }

    @GetMapping("/history/{city}")
    public Object getHistory(@PathVariable String city) {
        String url = "http://127.0.0.1:8000/history/" + city;
        return restTemplate.getForObject(url, Object.class);
    }
}