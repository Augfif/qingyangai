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
				reject({ message: '用户名已存在' })
				return
			}
			const newId = users.length + 1
			const now = new Date().toISOString()
			const newUser: UTSJSONObject = {
				id: newId,
				username: username,
				password: password,
				createdAt: now
			}
			users.push(newUser)
			saveUsers(users)
			resolve({
				token: 'mock-token-' + Date.now(),
				user: { id: newId, username: username }
			})
		}, 500)
	})
}

function mockLogin(username: string, password: string): Promise<any> {
	return new Promise((resolve, reject) => {
		setTimeout((): void => {
			const users = getStoredUsers()
			let matched: UTSJSONObject | null = null
			for (let i = 0; i < users.length; i++) {
				const u = users[i] as UTSJSONObject
				if (u['username'] as string === username && u['password'] as string === password) {
					matched = users[i] as UTSJSONObject
					break
				}
			}
			if (matched !== null) {
				resolve({
					token: 'mock-token-' + Date.now(),
					user: { id: matched['id'] as number, username: matched['username'] as string }
				})
			} else {
				reject({ message: '用户名或密码错误' })
			}
		}, 500)
	})
}

export { mockRegister, mockLogin, getStoredUsers }
