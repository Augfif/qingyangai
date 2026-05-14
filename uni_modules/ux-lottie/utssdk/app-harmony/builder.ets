import lottie, { AnimationItem, AnimationDirection } from '@ohos/lottie';

@Component
struct LottieComponent {
  @Prop src: string = ""
  @Prop loop: boolean = true
  @Prop autoplay: boolean = true
  @Prop animDirection: number = 1
  @Prop @Watch('onCommandChange') command: string = '' // 指令
  
  private renderingSettings: RenderingContextSettings = new RenderingContextSettings(true);
  private canvasRenderingContext: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.renderingSettings);
  private animateItem: AnimationItem | null = null;
  private animateName: string = 'animation';

  aboutToDisappear(): void {
    lottie.destroy(this.animateName);
    this.animateItem = null;
  }
  
  onCommandChange() {
	  let command = this.command.split('-')[0]
      if (command == 'play') {
		this.loadAnimation();
		this.animateItem?.setDirection(this.animDirection as AnimationDirection)
        this.animateItem?.play();
      } else if (command == 'pause') {
        this.animateItem?.pause();
      } else if (command == 'stop') {
        this.animateItem?.stop();
      } else if (command == 'resume') {
        this.animateItem?.stop();
		this.animateItem?.play();
      } else if (command == 'destroy') {
        lottie.destroy(this.animateName);
        this.animateItem = null;
      }
   }

  loadAnimation() {
	if(this.animateItem != null) {
		return
	}
	
	if(this.src == '') {
	  return
	}
	  
	let uri = ''
	let path = ''
	let animationData: Object | null = null
	if(this.src.startsWith("http://") || this.src.startsWith("https://")) {
		uri = this.src
	} else {
		if(this.src.startsWith("{")) {
			animationData = JSON.parse(this.src)
		} else {
			path = this.src
		}
	}
	
	this.animateItem = lottie.loadAnimation({
	  container: this.canvasRenderingContext,
	  renderer: 'canvas',
	  loop: this.loop,
	  autoplay: true,
	  name: this.animateName,
	  contentMode: 'Contain',
	  path: path,
	  uri: uri,
	  animationData: animationData,
	})
	
	this.animateItem?.setDirection(this.animDirection as AnimationDirection)
  }

  build() {
    Canvas(this.canvasRenderingContext)
      .width('100%')
      .height('100%')
      .onReady(() => {
        // 加载动画
        if (this.animateItem != null) {
          // 可在此生命回调周期中加载动画，可以保证动画尺寸正确
          this.animateItem?.resize();
        } else {
          // 抗锯齿的设置
          this.canvasRenderingContext.imageSmoothingEnabled = true;
          this.canvasRenderingContext.imageSmoothingQuality = 'medium';
          this.loadAnimation();
        }
      })
  }
}

@Builder
export function LottieView(params: ESObject) {
	Row() {
		if(params.src) {
			LottieComponent({src: params.src, loop: params.loop, autoplay: params.autoplay, animDirection: params.direction, command: params.command})
				.width('100%')
				.height('100%')
		}
	}
	.width('100%')
	.height('100%')
	.attributeModifier(params.attributeUpdater)
}