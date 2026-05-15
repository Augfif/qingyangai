import { ref } from 'vue'

export const username = ref('')
export const isLoggedIn = ref(false)

export function login(user: string, token: string) {
	username.value = user
	isLoggedIn.value = true
	uni.setStorageSync('token', token)
	if (user !== '') {
		uni.setStorageSync('saved_user', user)
	}
}

export function logout() {
	username.value = ''
	isLoggedIn.value = false
	uni.removeStorageSync('token')
	uni.removeStorageSync('saved_user')
}

export function initAuth() {
	const token = uni.getStorageSync('token') as string
	if (token !== '') {
		isLoggedIn.value = true
		const saved = uni.getStorageSync('saved_user') as string
		if (saved !== '') {
			username.value = saved
		}
	}
}
