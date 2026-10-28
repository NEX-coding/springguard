package com.demo.mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.Map;

@Mapper
public interface UserMapper {

    @Insert("INSERT INTO users(name, email) VALUES(#{name}, #{email})")
    int insertUser(@Param("name") String name, @Param("email") String email);

    @Select("SELECT id, name, email FROM users WHERE name = #{name}")
    Map<String, Object> findByName(@Param("name") String name);
}
