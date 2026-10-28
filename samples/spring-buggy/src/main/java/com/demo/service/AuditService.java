package com.demo.service;

import org.springframework.stereotype.Service;

@Service
public class AuditService {
    public void record(String action, int id) {
        if (action.equals("boom")) {
            throw new IllegalStateException("audit down");
        }
        System.out.println(action + ":" + id);
    }
}
