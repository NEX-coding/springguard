package com.demo.controller;

import com.demo.service.UserService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // BUG: missing @Valid on request body
    @PostMapping
    public Map<String, Object> create(@RequestBody Map<String, String> body) {
        String name = body.get("name");
        String email = body.get("email");
        // BUG: business logic + NPE risk in controller
        return userService.createUser(name.toLowerCase(), email);
    }
}
