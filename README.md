# tianyancha
天眼查滑动验证码

先输入账户名&密码触发出滑动验证码；

天眼查验证码触发出来后就是完整的直接截图就可以，要抓取到带缺口的就需要点击一下滑动按钮；

判断滑块与缺口的距离-->根据完整图片与带缺口图片之间的像素值计算需要滑动的距离；

每次根据像素值求出的偏移量都会过大，所以写使用for循环来循环（判断一个匹配错误状态，<拖动滑块>出现就'减值'已达到正确匹对，同时抓取一个<怪物>错误状态--->
此网站的<怪物>状态出现后会刷新一次滑动验证码图片，所以需要重新调用，判断滑块到缺口距离的函数以及本函数自身；

