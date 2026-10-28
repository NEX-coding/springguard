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

    // BUG: raw fragment concatenated by caller — high injection risk if used with ${}
    @Select("${clause}")
    Map<String, Object> findByKeyword(@Param("clause") String clause);
}
