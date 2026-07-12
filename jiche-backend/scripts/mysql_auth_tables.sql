-- 极车认证模块 MySQL 建表参考（由 Django migration accounts.0001 生成）
-- 生产环境推荐: python manage.py migrate
-- 本文件仅供 DBA 审阅，字段以 Django Model 为准

CREATE TABLE IF NOT EXISTS `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `internal_username` varchar(64) NOT NULL,
  `unionid` varchar(64) DEFAULT NULL,
  `mp_openid` varchar(64) DEFAULT NULL,
  `web_openid` varchar(64) DEFAULT NULL,
  `nickname` varchar(64) NOT NULL DEFAULT '',
  `phone` varchar(11) DEFAULT NULL,
  `avatar` varchar(512) DEFAULT NULL,
  `is_staff` tinyint(1) NOT NULL DEFAULT 0,
  `is_super_staff` tinyint(1) NOT NULL DEFAULT 0,
  `staff_granted_at` datetime(6) DEFAULT NULL,
  `shop_status` smallint NOT NULL DEFAULT 0,
  `shop_id` bigint DEFAULT NULL,
  `last_login_at` datetime(6) DEFAULT NULL,
  `last_login_platform` varchar(16) NOT NULL DEFAULT '',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `staff_granted_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_username` (`internal_username`),
  UNIQUE KEY `unionid` (`unionid`),
  UNIQUE KEY `mp_openid` (`mp_openid`),
  UNIQUE KEY `web_openid` (`web_openid`),
  KEY `user_shop_st_9f3150_idx` (`shop_status`),
  KEY `user_shop_id_c5f340_idx` (`shop_id`),
  KEY `user_is_staf_3c0a45_idx` (`is_staff`),
  KEY `user_staff_granted_by_id_fk` (`staff_granted_by_id`),
  CONSTRAINT `user_staff_granted_by_id_fk`
    FOREIGN KEY (`staff_granted_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `auth_login_ticket` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ticket` varchar(64) NOT NULL,
  `status` smallint NOT NULL DEFAULT 0,
  `scan_openid` varchar(64) DEFAULT NULL,
  `scan_unionid` varchar(64) DEFAULT NULL,
  `redirect_path` varchar(256) DEFAULT NULL,
  `client_ip` char(39) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `confirmed_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket` (`ticket`),
  KEY `auth_login__status_9c6113_idx` (`status`, `expires_at`),
  KEY `auth_login_ticket_user_id_fk` (`user_id`),
  CONSTRAINT `auth_login_ticket_user_id_fk`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
