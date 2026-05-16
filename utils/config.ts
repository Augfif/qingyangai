/**
 * utils/config.ts
 * 前端全局配置 — 部署前替换为实际服务器地址
 *
 * 修改方式：
 * 1. 将 YOUR_SERVER_IP 替换为后端服务器的真实 IPv4 地址
 * 2. 如端口变更，同步修改 :8080
 */
const BASE_URL = 'http://YOUR_SERVER_IP:8080'

export { BASE_URL }
