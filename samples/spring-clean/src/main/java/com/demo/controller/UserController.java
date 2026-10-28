package com.demo.controller;

import com.demo.service.UserService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
@Validated
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    public Map<String, Object> create(@RequestBody @Validated Map<String, String> body) {
        String name = body.get("name");
        String email = body.get("email");
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name required");
        }
        return userService.createUser(name.toLowerCase(), email);
    }
}
