function getStoredUsers(): UTSJSONObject[] {
	const data = uni.getStorageSync('mock_users') as string
	if (data === '' || data === null) return []
	try {
		return JSON.parse(data) as UTSJSONObject[]
	} catch {
		return []
	}
}

function saveUsers(users: UTSJSONObject[]): void {
	uni.setStorageSync('mock_users', JSON.stringify(users))
}

function mockRegister(username: string, password: string): Promise<any> {
	return new Promise((resolve, reject) => {
		setTimeout((): void => {
			const users = getStoredUsers()
			let exists = false
			for (let i = 0; i < users.length; i++) {
				const u = users[i] as UTSJSONObject
				if (u['username'] as string === username) {
					exists = true
					break
				}
			}
			if (exists) {
				console.log('[mock] 注册失败: 用户名已存在', username)
				const err = {} as UTSJSONObject
				err['message'] = '用户名已存在'
				reject(err)
				return
			}
			const newId = users.length + 1
			const newUser = {} as UTSJSONObject
			newUser['id'] = newId
			newUser['username'] = username
			newUser['password'] = password
			newUser['createdAt'] = new Date().toISOString()
			users.push(newUser)
			saveUsers(users)
			console.log('[mock] 注册成功:', username)
			const user = {} as UTSJSONObject
			user['id'] = newId
			user['username'] = username
			const result = {} as UTSJSONObject
			result['token'] = 'mock-token-' + Date.now()
			result['user'] = user
			resolve(result)
		}, 500)
	})
}

function mockLogin(username: string, password: string): Promise<any> {
	return new Promise((resolve, reject) => {
		setTimeout((): void => {
			const users = getStoredUsers()
			console.log('[mock] 登录尝试, 当前用户数:', users.length)
			let matched: UTSJSONObject | null = null
			for (let i = 0; i < users.length; i++) {
				const u = users[i] as UTSJSONObject
				if (u['username'] as string === username && u['password'] as string === password) {
					matched = users[i] as UTSJSONObject
					break
				}
			}
			if (matched !== null) {
				console.log('[mock] 登录成功:', username)
				const user = {} as UTSJSONObject
				user['id'] = matched['id'] as number
				user['username'] = matched['username'] as string
				const result = {} as UTSJSONObject
				result['token'] = 'mock-token-' + Date.now()
				result['user'] = user
				resolve(result)
			} else {
				console.log('[mock] 登录失败: 用户名或密码错误')
				const err = {} as UTSJSONObject
				err['message'] = '用户名或密码错误'
				reject(err)
			}
		}, 500)
	})
}

export { mockRegister, mockLogin, getStoredUsers }
