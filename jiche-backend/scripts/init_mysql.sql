-- 极车 MySQL 生产库初始化（认证模块）
-- 用法: mysql -u root -p < scripts/init_mysql.sql
-- 或在 setup_mysql.sh 中自动执行

CREATE DATABASE IF NOT EXISTS `jiche`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `jiche`;

-- 说明：业务表由 Django migrate 自动创建（user、auth_login_ticket 等）
-- 若需手动核对，可执行: python manage.py sqlmigrate accounts 0001
