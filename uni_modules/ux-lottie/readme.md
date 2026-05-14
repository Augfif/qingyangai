
<p align="center">
    <img alt="logo" src="https://www.uxframe.cn/logo/logo.png" width="120" height="120" style="margin-bottom: 10px;">
</p>
<h3 align="center" style="margin: 30px 0 30px;font-weight: bold;font-size:40px;">UxFrame Lottie动画组件 1.0.4</h3>

## 特别说明

如果您已经购买了[UxFrame 低代码高性能UI框架](https://ext.dcloud.net.cn/plugin?id=16148), 则无需再次购买本插件，请点击上方`进入交流群`联系我免费获取离线版插件！

### 使用方式

``` html
<template>
	<view>
		<view class="logo">
			<ux-lottie style="flex: 1;" ref="uxLottieRef" :loop="true" src="/static/refresh.json"></ux-lottie>
		</view>
		
		<button @click="play">播放</button>
		<button @click="pause">暂停</button>
		<button @click="stop">停止</button>
		<button @click="resume">重新播放</button>
		<button @click="destroy">销毁</button>
	</view>
</template>
```

``` js
<script setup>
	const uxLottieRef = ref<UxLottieComponentPublicInstance | null>(null)
	
	function play() {
		uxLottieRef.value?.$callMethod('play')
	}
	
	function pause() {
		uxLottieRef.value?.$callMethod('pause')
	}
	
	function stop() {
		uxLottieRef.value?.$callMethod('stop')
	}
	
	function resume() {
		uxLottieRef.value?.$callMethod('resume')
	}
	
	function destroy() {
		uxLottieRef.value?.$callMethod('destroy')
	}
</script>

```

## 文档教程 ⬇️

[https://www.uxframe.cn](https://www.uxframe.cn)
