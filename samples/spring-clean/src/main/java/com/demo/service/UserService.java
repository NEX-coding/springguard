package com.demo.service;

import com.demo.mapper.UserMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;

@Service
public class UserService {

    private final UserMapper userMapper;
    private final AuditService auditService;

    public UserService(UserMapper userMapper, AuditService auditService) {
        this.userMapper = userMapper;
        this.auditService = auditService;
    }

    @Transactional
    public Map<String, Object> createUser(String name, String email) {
        int id = userMapper.insertUser(name, email);
        try {
            auditService.record("create", id);
        } catch (Exception e) {
            throw new IllegalStateException("audit failed, rolling back", e);
        }
        Map<String, Object> out = new HashMap<>();
        out.put("id", id);
        out.put("name", name);
        return out;
    }

    public Map<String, Object> search(String keyword) {
        return userMapper.findByName(keyword);
    }
}
