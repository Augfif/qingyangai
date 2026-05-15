import { ref } from 'vue'

const username = ref('')
const isLoggedIn = ref(false)

const login = (user: string, token: string) => {
	username.value = user
	isLoggedIn.value = true
	uni.setStorageSync('token', token)
	if (user !== '') {
		uni.setStorageSync('saved_user', user)
	}
}

const logout = () => {
	username.value = ''
	isLoggedIn.value = false
	uni.removeStorageSync('token')
	uni.removeStorageSync('saved_user')
}

const initAuth = () => {
	const token = uni.getStorageSync('token') as string
	if (token !== '') {
		isLoggedIn.value = true
		const saved = uni.getStorageSync('saved_user') as string
		if (saved !== '') {
			username.value = saved
		}
	}
}

function useUserStore() {
	return {
		username: username,
		isLoggedIn: isLoggedIn,
		login: login,
		logout: logout,
		initAuth: initAuth
	}
}

export { useUserStore }
