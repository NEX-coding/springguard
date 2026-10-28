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
        // BUG: transactional self-invocation — saveInternal via this.* won't start new proxy tx semantics as expected in some cases
        return this.saveInternal(name, email);
    }

    @Transactional
    public Map<String, Object> saveInternal(String name, String email) {
        int id = userMapper.insertUser(name, email);
        try {
            auditService.record("create", id);
        } catch (Exception e) {
            // BUG: swallow exception inside transaction
            System.out.println("audit failed: " + e.getMessage());
        }
        Map<String, Object> out = new HashMap<>();
        out.put("id", id);
        out.put("name", name);
        return out;
    }

    public Map<String, Object> search(String keyword) {
        // BUG: SQL injection via string concat passed to mapper
        return userMapper.findByKeyword("name LIKE '%" + keyword + "%'");
    }
}
