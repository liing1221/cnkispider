# -*- coding: utf-8 -*-
"""
    @Project     : cnkispider
    @File        : captchamanage.py
    @Create_Date : 2019-02-20 15:37
    @Update_Date : 2019-02-20 15:37
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
import os, re
import random
import requests
import pytesseract
from collections import defaultdict
from PIL import Image
from PIL import ImageOps
from aip import AipOcr

class CaptchaManager:
    """
    验证码处理模块：文字图片验证码
    """
    # 验证码请求的url
    # 验证码图片的url，t参数仅起随机数防止浏览器使用缓存的作用：JS中Math.random() 返回0.0 ~ 1.0 之间的一个伪随机数。
    COUNT = 0

    def __init__(self):
        """
        初始化验证码请求头
        """
        self.headers = {

        }
        self.url = 'http://kns.cnki.net/kns/brief/vericode.aspx?rurl=%2fkns%2fbrief%2fbrief.aspx%3fcurpage%3d16%26RecordsPerPage%3d20%26QueryID%3d0%26ID%3d%26turnpage%3d1%26tpagemode%3dL%26dbPrefix%3dSCDB%26Fields%3d%26DisplayMode%3dlistmode%26PageName%3dASP.brief_default_result_aspx%26isinEn%3d1#J_ORDER&'
        t = round(random.random(), 15)    # 可用round（数值， 位数）四舍五入，控制位数
        self.img_url = 'http://kns.cnki.net/kns/checkcode.aspx?t=%27' + str(t)
        print(self.img_url)

    def get_img(self, current_url=None, session=None, response=None, proxies=None, timeout=None):
        """
        获取验证码图片
        :param img_url: 验证码图片URL
        :return:
        """
        self.COUNT += 1
        if session:
            self.s = session   # 保持回话
        else:
            self.s = requests.Session()
        # 获取页面响应的验证码图片url
        if not response and not proxies:
            response = self.s.get(url=self.url, headers= self.headers, timeout=timeout)
        elif not response and proxies:
            response = self.s.get(url=self.url, headers=self.headers, proxies=proxies, timeout=timeout)
        else:
            response = response
        img_url_pattern = re.compile(r'.*?<img src="(.*?)".*?')
        img_url = re.search(img_url_pattern, response.text).group(1)
        img_url = 'http://kns.cnki.net' + img_url
        # 下载保存图片
        if proxies:
            img_response = self.s.get(img_url, headers=self.headers, proxies=proxies, timeout=timeout)
        else:
            img_response = self.s.get(img_url, headers=self.headers, timeout=timeout)
        if not os.path.exists('./img'):
            os.makedirs('./img')
        image_filename = 'D:/liing_code/spider_projects/cnkispider/img/captcha{}.png'.format(self.COUNT)
        with open(image_filename, 'wb') as f:
            f.write(img_response.content)
        return image_filename

    def img_threshold(self, image):
        """
        获取image文件像素值数量最多的像素点的像素值
        :param image: 验证码图片文件：流对象
        :return:
        """
        pixel_dict = defaultdict(int)    #　初始化一个像素点数量的字典,默认为int() —— 0
        w, h = image.size
        for i in range(w):
            for j in range(h):
                pixel = image.getpixel((i, j))
                pixel_dict[pixel] += 1
        max_pixel = max(pixel_dict.values())   # 像素值数量的最大值
        for k, v in pixel_dict.items():
            if v == max_pixel:
                threshold = k
                return threshold
            else:
                continue

    def img_bin_process(self, threshold):
        """
        根据阈值获取灰度图转为二值图的映射列表
        :param threshold: 灰度图像素阈值
        :return:
        """
        table = []
        for i in range(256):
            rate = 0.4  # 在threshold的适当范围内进行二值转化
            if threshold * (1 - rate) <= i <= threshold * (1 + rate):
                table.append(1)    # 在阈值附近的去除，其他保留
            else:
                table.append(0)
        return table

    def img_rid_noise(self, image):
        """
        去掉二值处理后图片的噪声点
        :param image: 二值处理后的图片流对象
        :return: 去除噪声后的图片
        """
        w, h = image.size
        noises = []    # 记录噪声点位置
        pixes = []
        for i in range(1, w - 1):
            for j in range(1, h - 1):   # 遍历图片中的点（去除边缘）
                pixel_b_counts = []     # 记录该点附近黑色像素的数量
                count = 0
                for m in range(i-1, i+2):
                    for n in range(j-1, j+2):   # 取该点为中心的九宫格遍历
                        pix = image.getpixel((m, n))
                        if pix != 1:    # 1为白色，0为黑色
                            count += 1
                            # pixel_b_counts.append(pix)
                if count <= 2:          # 该像素附近的黑色像素数量 <= 4， 则该像素为噪声
                    noises.append((i, j))
                if count >= 8:          # 该像素附近的黑色像素数量 >= 8, 则该像素不是噪声
                    pixes.append((i, j))
        for noise in noises:            # 噪声点像素设为1  白色， 去除噪声
            image.putpixel(noise, 1)
        for pix in pixes:
            image.putpixel(pix, 0)      # 非噪声点像素设为0  黑色， 修复图像
        return image

    def img_process(self, filename):
        """
        传入图片进行灰度、二值化、噪声处理
        :param filename: 图片文件
        :return: 处理后的图片对象
        """
        # 图片转化为灰度图
        image = Image.open(filename).convert('RGB')
        # image = Image.open(filename).convert('L')
        # # 灰度图二值化处理
        # threshold = self.img_threshold(image=image)  # 获取二值化阈值
        # threshold = 240
        # print("threshold >> ", threshold)
        # bin_table = self.img_bin_process(threshold=threshold)
        # img_bin = image.point(bin_table, '1')
        # # 二值化图噪声处理
        # img_rid_noise = self.img_rid_noise(img_bin)
        # # return img_rid_noise
        # img = img_rid_noise .convert('L')
        # img.show()
        img = image
        img_invert = ImageOps.invert(img)
        image_name = filename.split('.')[0] + '.jpg'
        img_invert.save(image_name, 'jpeg')
        # self.auto_captcha_identify(img_invert)
        # return image
        return image_name

    def auto_captcha_identify(self, img):
        """
        自动验证码识别
        :return:
        """
        result = pytesseract.image_to_string(img)
        print(result)
        return result

    def do_verify(self):
        """
        验证码识别
        :return:
        """
        url = self.url
        # 获取验证码图片
        image_file = self.get_img()
        # 验证码图片处理
        img = self.img_process(image_file)
        # 验证码图片识别
        result = self.auto_captcha_identify(img)
        print(result)
        # 结果处理：去除非字母数字的
        verify_code = []
        for i in result:
            if i.isalpha():
                verify_code.append(i.upper())
            if i.isdigit():
                verify_code.append(i)
        result = ''.join(verify_code)
        print(result)

    def baidu_verify(self):
        """
        通过百度AipOcr 进行智能识别
        :return:
        """
        APP_ID = '15606537'
        API_KEY = 'L4jATkRTkTucTwxwgrl0claa'
        SECRET_KEY = 'O7c20fZGp8yzGAMHm5K7A0oyynlsqdXx'
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        filename = self.get_img()   # 读取图片
        filename = self.img_process(filename)
        with open(filename, 'rb') as fp:
            image = fp.read()
        options = {}
        options["language_type"] = "ENG"
        result = client.basicGeneral(image, options=options)   # 调用通用文字识别, 图片参数为本地图片
        print(result)
        words = result['words_result'][0]['words']
        print(words)
        word = []
        for i in words:
            if i.isalpha():
                word.append(i.upper())
            if i.isdigit():
                word.append(i)
        words = ''.join(word)
        print(words)


if __name__ == "__main__":
    captchamanager = CaptchaManager()
    # captchamanager.do_verify()
    captchamanager.baidu_verify()