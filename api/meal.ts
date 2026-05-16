/**
 * api/meal.ts
 * 三餐计划 API — 调用 POST /api/tasks/meal-plan 并安全解析响应
 */

import { request } from '@/utils/request'

// ==================== 类型定义 ====================

/** 后端返回的单餐结构 */
type BackendMealItem = {
	items: string[]
	ingredients?: string
	calories?: string
	tips?: string
}

/** 三餐计划 API 的完整响应 */
type MealPlanResponse = {
	date: string
	target: string
	breakfast: BackendMealItem
	lunch: BackendMealItem
	dinner: BackendMealItem
}

// ==================== API 函数 ====================

/**
 * 生成三餐计划
 * 将用户输入的自然语言目标发送给后端，返回结构化膳食计划
 *
 * @param prompt 用户的饮食目标字符串，如 "我想调理肠胃、不想节食"
 */
export const generateMealPlan = async (prompt: string): Promise<MealPlanResponse> => {
	// 显式创建 UTSJSONObject 并赋值，避免字面量强转丢失字段
	const body = {} as UTSJSONObject
	body["target"] = prompt

	// 直接按顺序传参，避开泛型推导报错
	const obj = await request('/api/tasks/meal-plan', 'POST', body)

	// 从 UTSJSONObject 逐字段安全提取，避免 as MealPlanResponse 的 ClassCastException
	const bf = obj["breakfast"] as UTSJSONObject
	const lu = obj["lunch"] as UTSJSONObject
	const dn = obj["dinner"] as UTSJSONObject

	return {
		date: obj["date"] as string,
		target: obj["target"] as string,
		breakfast: { items: bf["items"] as string[] },
		lunch:     { items: lu["items"] as string[] },
		dinner:    { items: dn["items"] as string[] }
	}
}

// ==================== 导出 ====================

export type { MealPlanResponse, BackendMealItem }
