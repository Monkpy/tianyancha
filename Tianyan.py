# -*- coding: utf-8 -*-
import random
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains


class Tyc(object):

    def __init__(self):
        Url = 'https://www.tianyancha.com/'
        chrome_path = 'C:\Program Files (x86)\chromedriver\chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_path)
        self.driver.get(Url)
        self.driver.maximize_window()

    def __del__(self):
        self.driver.close()

    def show_element(self, element):  # 让验证码图片迅速还原成完整图片
        self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: block;")

    def hide_element(self, element):  # 暂不知用处
        self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: none;")

    def open_login(self):
        try:
            t = random.uniform(0.5, 1)
            time.sleep(t)
            login_button = self.driver.find_element_by_xpath('//a[@onclick="header.loginLink(event)"]')
            login_button.click()
            time.sleep(2)
            pwd_button = self.driver.find_element_by_xpath('//div[@active-tab="1"]')
            pwd_button.click()
            time.sleep(1)
            username = self.driver.find_element_by_xpath('//div[@class="pb24 position-rel"]/div[1]/input[@id="mobile"]')
            username.send_keys('账户')
            time.sleep(t)
            password = self.driver.find_element_by_xpath('//div[@class="input-warp -block"]/input[@id="password"]')
            password.send_keys('密码')
            time.sleep(1)
            click_button = self.driver.find_element_by_xpath('//div[@onclick="loginObj.loginByPhone(event);"]')
            click_button.click()
            time.sleep(2)

        except Exception as e:
            print(e)

    def get_image_location(self):
        # 获取验证码图片路径--->调用get_images截取图片
        fullbg = self.driver.find_element_by_xpath('//a[@class="gt_fullbg gt_show"]')
        self.hide_element(fullbg)
        self.show_element(fullbg)
        # 获取完整图片
        self.get_images(fullbg, 'tyc_full.png')
        # 点击一下滑动按钮触发出来带缺口的图片
        self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]').click()
        time.sleep(2)
        # 获取带缺口的图片
        bg = self.driver.find_element_by_xpath('//div[@class="gt_cut_fullbg gt_show"]')
        self.show_element(bg)
        self.get_images(bg, 'tyc_bg.png')

    def get_images(self, img, name):
        # 截图整个网页
        self.driver.save_screenshot(r'./Images/Tyc.png')
        # 验证码路径
        location = img.location
        # 验证码尺寸
        size = img.size
        # top, bottom, left, right = location['y']+3, location['y'] + size['height'], location['x']-325, location['x'] + size['width']-328
        # 加入代码self.driver.maximize_window()使浏览器全屏后就不需要修改位置参数了,mac上不知道什么原因需要修改位置
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        picture = Image.open(r'./Images/Tyc.png')
        picture = picture.crop((left, top, right, bottom))
        picture.save(r'./Images/%s' % name)
        time.sleep(0.5)

    def is_pixel_equal(self, tyc_bg, tyc_full, x, y):
        """
        :param tyc_bg: 带缺口图片
        :param tyc_full: 完整图片
        :param x: (Int) x位置
        :param y: (Int) y位置
        :return: (Boolean) 像素是否相同
        """
        # 获取缺口图片的像素点（按RGE格式）
        bg_pixel = tyc_bg.load()[x, y]
        # 获取完整图片的像素点（按RGB格式）
        full_pixel = tyc_full.load()[x, y]
        threshold = 60
        if (abs(full_pixel[0] - bg_pixel[0] < threshold) and abs(full_pixel[1] - bg_pixel[1] < threshold) and abs(
                full_pixel[2] - bg_pixel[2] < threshold)):
            # 如果差值在判断值之内，返回是相同像素
            return True

    def get_distance(self, tyc_bg, tyc_full):
        """
        :param tyc_bg: 带缺口图片
        :param tyc_full: 完整图片
        :return: (Int) 滑块与缺口的距离
        """
        # 滑块位置初始设置为 60 (这个是去掉开始的一部分)
        left_dist = 60
        # 遍历像素点横坐标
        for i in range(left_dist, tyc_full.size[0]):
            # 遍历像素点纵坐标
            for j in range(tyc_full.size[1]):
                if not self.is_pixel_equal(tyc_bg, tyc_full, i, j):
                    # 返回此时横轴坐标就是滑块需要移动的距离
                    return i

    def get_trace(self, distance):
        """
        :param distrance: (Int)缺口与滑块之间的距离
        :return: (List)移动轨迹
        """
        # 创建存放轨迹信息的列表
        trace = []
        # 设置加速的距离
        faster_distance = distance * 1.5
        # 设置初始位置、初始速度、时间间隔
        start, v0, t = 0, 0, 0.1
        # 当尚未移动到终点时
        while start < distance:
            # 如果处于加速阶段
            if start < faster_distance:
                # 设置加速度为2
                a = 12
            # 如果处于减速阶段
            else:
                # 设置加速度为-3
                a = -4
            # 移动的距离公式
            move = v0 * t + 1 / 2 * a * t * t
            # 此刻速度
            v = v0 + a * t
            # 重置初速度
            v0 = v
            # 重置起点
            start += move
            # 将移动的距离加入轨迹列表
            trace.append(round(move))
        # 返回轨迹信息
        return trace

    def move_to_gap(self, trace):
        t = random.uniform(0, 0.5)
        # 得到滑块标签
        slider = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in trace:
            # 使用move_by_offset()方法拖动滑块，perform()方法用于执行
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        # 模拟人类对准时间
        time.sleep(t)
        # 释放滑块
        ActionChains(self.driver).release().perform()

    def slice(self):
        bg_image = Image.open(r'./Images/tyc_bg.png')
        full_image = Image.open(r'./Images/tyc_full.png')
        try:
            # 计算位置距离
            distance = self.get_distance(bg_image, full_image)
            print('计算偏移量为：%s Px' % distance)
            # 位移算法
            trace = self.get_trace(int(distance))  # 拖动过来可以上来先做减值
            print(trace)
            # 移动滑块
            self.move_to_gap(trace)
            time.sleep(0.5)
            while True:
                for i in range(9, 12):
                    try:
                        mspan = self.driver.find_element_by_xpath('//div[@class="gt_info_text"]/span[2]').text
                        print(mspan)
                        if '拖动滑块' in mspan:
                            time.sleep(1)
                            distance = self.get_distance(bg_image, full_image)
                            print('计算偏移量为：%s Px' % distance)
                            trace = self.get_trace(int(distance)-int(i))
                            print('减值%s' % i)
                            print(trace)
                            # 移动滑块
                            self.move_to_gap(trace)
                            time.sleep(0.5)
                        else:  # 请关闭验证重试
                            if '怪物' in mspan:
                                time.sleep(5)
                                self.get_image_location()
                                self.slice()
                            else:
                                break
                    except Exception as e:
                        if '//div[@class="gt_info_text"]/span[2]' in str(e):
                            pass
                        else:
                            print(e)
                break
        except Exception as e:
            if '//span[@class="gt_info_content"]' in str(e):
                pass
            else:
                print(e)

    def get_cookie(self):
        time.sleep(3)
        try:
            login_name = self.driver.find_element_by_xpath('//div[@nav-type="user"]/a').get_attribute("text")
            print(login_name)
            time.sleep(3)
            cookie = {}
            cookies = self.driver.get_cookies()
            for i in cookies:
                a = i['name']
                b = i['value']
                cookie[a] = b
            self.cookie_to_redis(cookie)
        except Exception as e:
            print(e)

    def cookie_to_redis(self, cookie):
        # 连接数据库
        from redis import StrictRedis, ConnectionPool
        # 使用连接池
        pool = ConnectionPool(host='localhost', port=6379, db=0)
        rds = StrictRedis(connection_pool=pool)
        rds.set('ck', '%s' % cookie)
        # 然后将其获取并打印
        print(rds.get('ck'))

    def entrace(self):
        self.open_login()
        self.get_image_location()
        self.slice()
        self.get_cookie()


if __name__ == '__main__':
    tyc = Tyc()
    tyc.entrace()



   
