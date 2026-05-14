<template>
    <view class="defaultStyles"></view>
</template>
<script lang="uts">
    import Animator from 'android.animation.Animator'
    import TextUtils from 'android.text.TextUtils'
    import View from 'android.view.View'
    import LottieAnimationView from 'com.airbnb.lottie.LottieAnimationView'
    import LottieDrawable from 'com.airbnb.lottie.LottieDrawable'
	import FileInputStream from 'java.io.FileInputStream'
	import { UTSAndroid } from "io.dcloud.uts";

    class CustomAnimListener extends Animator.AnimatorListener {

        comp: UTSComponent < LottieAnimationView >
            constructor(com: UTSComponent < LottieAnimationView > ) {
                super();
                this.comp = com
            }

        override onAnimationStart(animation: Animator):void {
			console.log('动画开始了===');
		}
		
		override onAnimationStart(animation:Animator, isReverse:boolean):void {
            console.log('动画开始播放===');
        }

        override onAnimationEnd(animation: Animator, isReverse: boolean):void {
            this.comp.$emit("finished");
        }
		
        override onAnimationEnd(animation: Animator):void {
			console.log('动画结束===');
		}
		
		override onAnimationCancel(animation: Animator):void {
			this.comp.$emit("cancel")
		}

        override onAnimationRepeat(animation: Animator):void {}
    }

    export default {
        name: "xw-lottie-view",
        emits: ['finished','cancel'],
        props: {
            /**
             * 动画资源地址，支持本地资源绝对路径或远程地址
             */
            "url": {
                type: String,
                default: ""
            },
            /**
             * 动画自动播放
             */
            "autoplay": {
                type: Boolean,
                default: false
            },
            /**
             * 动画可见性
             */
            "visible": {
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
                handler(newPath: string) {
					if(this.$el != null){
						let lottieAnimationView = this.$el!;
						if (!TextUtils.isEmpty(newPath)) {
						    if (newPath.startsWith("http://") || newPath.startsWith("https://")) {
						        lottieAnimationView.setAnimationFromUrl(newPath)
						    } else {
								let realJsonPath = UTSAndroid.getResourcePath(newPath)
						        lottieAnimationView.setAnimation(new FileInputStream(realJsonPath),newPath)
						    }
						}
						
						if(this.autoplay){
							lottieAnimationView.playAnimation();
						}
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
							this.$el!.playAnimation();
						}
					}
				},
				immediate: false
			},

            "autoplay": {
                handler(newValue: boolean) {
					if(this.$el != null){
						if (newValue) {
						    this.$el!.playAnimation();
						}
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

            "action": {
                handler(newAction: string) {
                    if(this.$el != null){
                    	if (newAction == "play") {
                    	    this.$el!.playAnimation();
                    	} else if (newAction == "pause") {
                    	    this.$el!.pauseAnimation();
                    	} else if (newAction == "stop") {
                    	    this.$el!.cancelAnimation();
                    	}
                    }
                },
                immediate: false
            },

            "visible": {
                handler(newValue: boolean) {
					if(this.$el != null){
						this.$el!.visibility = newValue?View.GONE:View.VISIBLE;
					}
                },
                immediate: false
            },
			
			"speed":{
				handler(newValue:number){
					this.setAnimSpeed(newValue);
				},
				immediate: true
			}

        },
		expose: ['play','pause','reset','setRepeatMode','setAnimSpeed'],
        methods: {
			play(){
				if(this.$el != null){
					this.$el!.playAnimation();
				}
			},
			pause(){
				if(this.$el != null){
					this.$el!.pauseAnimation();
				}
			},
			reset(){
				if(this.$el != null){
					this.$el!.cancelAnimation();
				}
			},
			resumePlay(){
				if(this.$el != null){
					this.$el!.resumeAnimation();
				}
			},
            setRepeatMode(repeat: string) {
				if(this.$el != null){
					if ("RESTART" == repeat) {
					    this.$el!.repeatMode = LottieDrawable.RESTART
					} else if ("REVERSE" == repeat) {
					    this.$el!.repeatMode = LottieDrawable.REVERSE
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
			}
        },
        
        NVLoad(): LottieAnimationView { 
            let lottieAnimationView = new LottieAnimationView($androidContext);
            return lottieAnimationView
        },
		
        NVLoaded() { 
			if(this.$el != null){
				this.$el!.repeatMode = LottieDrawable.RESTART;
				this.$el!.visibility = View.VISIBLE;
				this.$el!.repeatCount = 0;
				this.$el!.addAnimatorListener(new CustomAnimListener(this));
				// console.log('el=====',this!.$el);
			}
        }
        
    }
</script>
<style>
</style>
