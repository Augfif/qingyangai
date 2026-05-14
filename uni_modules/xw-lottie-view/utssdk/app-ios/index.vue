<template>
	<view class="defaultStyles"></view>
</template>
<script lang="uts">
	import {
		LottieAnimationView,
		LottieAnimation,
		LottieLoopMode
	} from 'Lottie'
	import {
		URL
	} from 'Foundation'
	import {
		UTSiOS
	} from "DCloudUTSFoundation"

	export default {
		name: "xw-lottie-view",
		emits: ['bindended'],
		props: {
			/**
			 * 动画资源地址，支持远程 URL 地址和本地绝对路径
			 */
			"url": {
				type: String,
				default: ""
			},
			/**
			 * 动画是否自动播放
			 */
			"autoplay": {
				type: Boolean,
				default: false
			},
			/**
			 * 动画是否循环播放
			 */
			"loop": {
				type: Boolean,
				default: false
			},
			/**
			 * 是否隐藏动画
			 */
			"hidden": {
				type: Boolean,
				default: false
			},
			/**
			 * 动画操作，可取值 play、pause、stop
			 */
			"action": {
				type: String,
				default: "stop"
			},
			/**
			 * 动画速度 设置的是倍速
			 */
			"speed":{
				type: Number,
				default: 1
			},
			/**
			 * 动画重复次数 默认0次 ，-1为无限循环
			 */
			"loopCount":{
				type: Number,
				default: 0
			},
			/**
			 * 动画进度  取值范围0.0 ~ 1.0
			 */
			"progressVal":{
				type: Number,
				default: 0.0
			}

		},
		watch: {
			"url": {
				handler(newValue: string, oldValue: string) {
					if (this.autoplay) {
						this.playAnimation()
					}
				},
				immediate: false 
			},
			
			"loopCount":{
				handler(newValue: number) {
					if(this.$el != null){
						if(newValue===0){
							this.$el!.repeatCount = 0;
						}else if(newValue>0){
							const setValue=newValue.toInt();
							this.$el!.setRepeatCount(setValue);
						}else{
							this.$el!.repeatCount = Int.MAX_VALUE;
						}
						
						if(this.autoplay){
							this.playAnimation()
						}
					}
				},
				immediate: false
			},
			"loop": {
				handler(newValue: boolean, oldValue: boolean) {
					if (newValue) {
						this.$el.loopMode = LottieLoopMode.loop
					} else {
						this.$el.loopMode = LottieLoopMode.playOnce
					}
				},
				immediate: false
			},
			"autoplay": {
				handler(newValue: boolean, oldValue: boolean) {
					if (newValue) {
						this.playAnimation()
					}
				},
				immediate: false
			},
			"action": {
				handler(newAction: string, oldValue: string) {
					if (newAction == "play") {
					    this.$el!.playAnimation();
					} else if (newAction == "pause") {
					    this.$el.pause()
					} else if (newAction == "stop") {
					    this.$el.stop()
					}
				},
				immediate: false  
			},
			
			"progressVal":{
				handler(newV:number){
					if(this.$el != null){
						this.$el!.setProgress(newV.toFloat());
					}
				},
			    immediate: false
			},
			
			"speed":{
				handler(newValue:number){
					this.setAnimSpeed(newValue);
				},
				immediate: true
			},

			"hidden": {
				handler(newValue: boolean, oldValue: boolean) {
					this.$el.isHidden = this.hidden
				},
				immediate: false 
			},

		},
		expose: ['setRepeatMode','play','pause','setAnimSpeed'],
		methods: {
			play(){
				if(this.$el != null){
					this.playAnimation()
				}
			},
			pause(){
				if(this.$el != null){
					this.$el!.pause();
				}
			},
			setRepeatMode(repeatMode: string) {
				if (repeatMode == "RESTART") {
					if (this.loop) {
						this.$el.loopMode = LottieLoopMode.loop
					} else {
						this.$el.loopMode = LottieLoopMode.playOnce
					}
				} else if (repeatMode == "REVERSE") {
					if (this.loop) {
						this.$el.loopMode = LottieLoopMode.autoReverse
					} else {
						this.$el.loopMode = LottieLoopMode.repeatBackwards(1)
					}
				}
			},
			
			setAnimSpeed(val:number){
				if(val*1===0||val*1>10){
					console.log('设置的speed值太大了=');
				}else{
					if(this.$el != null){
						let defaultVal=this.$el!.getSpeed() * val;
						this.$el!.setSpeed(defaultVal.toFloat());
					}
				}
			},
			playAnimation() {
				// 构建动画资源 url
				var animationUrl: URL | null

				if (this.url.startsWith("http")) {
					animationUrl = new URL(string = this.url)
				} else {
					const filePath = UTSiOS.getResourcePath(this.url)
					animationUrl = new URL(fileURLWithPath = filePath)
				}

				if (animationUrl != null) {
					// 加载动画 LottieAnimation
					LottieAnimation.loadedFrom(url = animationUrl!, closure = (animation: LottieAnimation | null):
						void => {
							if (animation != null) {
								// 加载成功开始播放
								this.$el.animation = animation
								this.$el.play(completion = (isFinish: boolean): void => {
									if (isFinish) {
										// 播放完成回调事件
										this.fireEvent("bindended")
									}
								})
							}
						})
				}
			}
		},
		NVBeforeLoad() {
		},
		NVLoad(): LottieAnimationView {
			// 初始化 Lottie$el
			const animationView = new LottieAnimationView()
			// 默认只播放一次动画
			animationView.loopMode = LottieLoopMode.playOnce
			return animationView
		},
		NVLoaded() { //原生View已创建  
			if (this.loop) {
				this.$el.loopMode = LottieLoopMode.loop
			}

			this.$el.isHidden = this.hidden

			if (this.autoplay) {
				this.playAnimation()
			}
		},

		NVLayouted() { //原生View布局完成  
			//可选实现，这里可以做布局后续操作  
		},

		NVBeforeUnload() { //原生View将释放  
			//可选实现，这里可以做释放View之前的操作  
		},
		NVUnloaded() { //原生View已释放  
			//可选实现，这里可以做释放View之后的操作  
		}
	}
</script>
<style>
	//定义默认样式值, 组件使用者没有配置时使用  
	.defaultStyles {
		width: 750rpx;
		height: 240rpx;
	}
</style>