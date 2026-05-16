/**
 * utils/request.ts
 * 全局网络请求工具 — 基于 uni.request 封装的 Promise 调用
 *
 * 设计要点：
 * - BASE_URL 统一从 config 读取，避免页面中散落硬编码地址
 * - 使用位置参数而非 options 对象，避开 UTS 泛型推导失败
 * - 返回 UTSJSONObject，避免 as 自定义类型引发 ClassCastException
 */

import { BASE_URL } from '@/utils/config'

export const request = (
	url: string,
	method: "GET" | "POST",
	data: UTSJSONObject | null
): Promise<UTSJSONObject> => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + url,
			method: method,
			data: data,
			success: (res) => {
				resolve(res.data as UTSJSONObject)
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}
