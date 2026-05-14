## 使用说明

* ### app端(<font color="red"> 注：需要打包自定义基座运行，只能在nvue页面使用</font>)

 组件参数:
 
|参数   |类型   |默认值   |可选值  |必填  |说明  |
|:-----:|:-----:|:----:|:----:|:----:|:----:|
|url|string|-|-|Y|url地址，支持远程和本地json|
|autoplay|boolean|false|true/false|N|是否自动播放|
|action|string|stop|play/pause/stop|N|动作|
|speed|number|1|-|N|动画播放速度|
|loopCount|number|0|大于0的数字|N|动画循环的次数|
|progressVal|number|0.0|0.0~1.0|N|播放进度|


* 方法

 > * play  动画播放
 > * pause  动画暂停
 > * setRepeatMode  设置动画的正反序播放，可选值"RESTART/REVERSE"
 > * setAnimSpeed  设置动画的速度,参数与组件参数一致


 <font color="red"> 使用方式：</font>

 
 ```html
<template>
	<view class="content">
		<xw-lottie-view 
		ref='lottieWrap'
		:autoplay="autoplay" 
		:url="url" 
		:loopCount="loopCount"
		:action="action"
		:style="{width:'750rpx',height:'300px'}"
		></xw-lottie-view>
		<view class="btn-wrap">
			<button class="btn" @tap="play">开始播放</button>
			<button class="btn" @tap="pause">暂停播放</button>
			<button class="btn" @tap="changeSpeed">动画加速</button>
		</view>
	</view>
</template>
<script setup lang="ts">
	import {ref}from 'vue';
	let url=ref("/static/Ani_02.json");
	const autoplay=ref(false);
	const loopCount=ref(0);
	const action=ref('stop');
	const lottieWrap=ref();

	const changeSpeed=()=>{
		lottieWrap.value.setAnimSpeed(1.1);
	}
	const play=()=>{
		 lottieWrap.value.play();
	}
	const pause=()=>{
		lottieWrap.value.pause();
	}
</script>
 ```
 
 * ### H5端

 参数说明:
 
|参数   |类型   |默认值   |可选值  |必填  |说明  |
|:-----:|:-----:|:----:|:----:|:----:|:----:|
|path|string|-|-|Y|path地址，只支持远程json|
|autoplay|boolean|false|true/false|N|是否自动播放|
|loop|number|false|true/false|N|是否循环播放|
 
 <font color="red"> 使用方式：</font>
 
 说明：需要创建一个ID为lottie的标签，然后直接引入方法调用会返回一个动画实例，可通过实例调用内部方法
 ```html
 <template>
 	<view class="wrap">
 		<view id='lottie' class="lottie"></view>
 		<button type="default" @click="paly">播放</button>
 		<button type="default" @click="pause">暂停</button>
 		<button type="default" @click="setSeed">加速</button>
 	</view>
 	
 </template>
 
 <script setup lang="ts">
 	import {ref}from 'vue';
 	import {loadLottieHandle} from '../../uni_modules/xw-lottie-view'; //引入
 	
 	let lottieInstance=loadLottieHandle({
 		path:"https://b.bdstatic.com/miniapp/images/lottie_example_one.json",
 		autoplay:false,
 		loaded:()=>{
 			console.log('加载成功回调')
 		}
 	});
 	
	//播放动画
 	const paly=()=>{
 		lottieInstance.play();
 	};
 	
	//暂停动画
 	const pause=()=>{
 		lottieInstance.pause();
 	};
 	
	//设置速度
 	const setSeed=()=>{
 		lottieInstance.setSeed(2);
 	}

 	
 </script>
 ```
 