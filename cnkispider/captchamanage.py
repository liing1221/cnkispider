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
# import tesserocr
import pytesseract
from PIL import Image
from PIL import ImageOps

class CaptchaManager:
    """
    验证码处理模块：文字图片验证码
    """
    # 验证码请求的url
    url = 'http://kns.cnki.net/kns/brief/vericode.aspx?rurl=%2fkns%2fbrief%2fbrief.aspx%3fcurpage%3d16%26RecordsPerPage%3d20%26QueryID%3d0%26ID%3d%26turnpage%3d1%26tpagemode%3dL%26dbPrefix%3dSCDB%26Fields%3d%26DisplayMode%3dlistmode%26PageName%3dASP.brief_default_result_aspx%26isinEn%3d1#J_ORDER&'
    # 验证码图片的url，t参数仅起随机数防止浏览器使用缓存的作用：JS中Math.random() 返回0.0 ~ 1.0 之间的一个伪随机数。
    COUNT = 0

    def __init__(self):
        """
        初始化验证码请求头
        """
        self.headers = {

        }
        self.threshold = 160
        self.url = 'http://kns.cnki.net/kns/brief/vericode.aspx?rurl=%2fkns%2fbrief%2fbrief.aspx%3fcurpage%3d16%26RecordsPerPage%3d20%26QueryID%3d0%26ID%3d%26turnpage%3d1%26tpagemode%3dL%26dbPrefix%3dSCDB%26Fields%3d%26DisplayMode%3dlistmode%26PageName%3dASP.brief_default_result_aspx%26isinEn%3d1#J_ORDER&'
        t = round(random.random(), 15)    # 可用round（数值， 位数）四舍五入，控制位数
        self.img_url = 'http://kns.cnki.net/kns/checkcode.aspx?t=%27' + str(t)

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

    def img_process(self, filename):
        """
        传入图片进行二值化处理: 返回处理后的图片
        :param filename:
        :return:
        """
        image = Image.open(filename).convert('L')    # 转换为灰度图
        image.show()
        # 灰度图二值化处理
        table = []
        for i in range(256):
            if i < self.threshold:
                table.append(0)
            else:
                table.append(1)
        img_binary = image.point(table, '1')
        img_binary.show()
        img_binary = img_binary.convert('L')
        img_invert = ImageOps.invert(img_binary)
        img_invert.save(filename.split('.')[0] + '.jpg', 'jpeg')
        self.auto_captcha_identify(img_invert)
        # 图片去噪

        return image

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
        处理验证码
        :return:
        """
        url = self.url

        image_file = self.get_img()
        img = self.img_process(image_file)
        result = self.auto_captcha_identify(img)



if __name__ == "__main__":
    captchamanager = CaptchaManager()
    captchamanager.do_verify()