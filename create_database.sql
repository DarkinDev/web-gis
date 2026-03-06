-- Script tạo database bus_gis với PostGIS extension
-- Chạy lệnh này trong PostgreSQL

-- Tạo database
CREATE DATABASE bus_gis;

-- Kết nối vào database (chạy trong psql hoặc pgAdmin Query Tool)
\c bus_gis

-- Bật extension PostGIS (quan trọng cho GIS)
CREATE EXTENSION postgis;

-- Kiểm tra PostGIS đã được cài đặt chưa
SELECT PostGIS_version();
