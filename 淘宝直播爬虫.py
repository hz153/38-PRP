# -*- coding:utf-8 -*-
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
import re
import csv
import pandas as pd
from itertools import chain
from enum import Enum

"""
存放全局变量
desired_caps：Appium客户端参数
server：Appium服务器环境，本地端口号4723
过程函数调用结果枚举类
"""
desired_caps = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '7.1.2',  # 手机安卓版本
    'deviceName': 'xxx',  # 设备名，安卓手机可以随意填写
    'appPackage': 'com.taobao.taobao',  # 启动APP Package名称
    'appActivity': 'com.taobao.tao.TBMainActivity',  # 启动Activity名称
    'unicodeKeyboard': False,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,  # 不要重置App
    'newCommandTimeout': 6000,
    'automationName': 'UiAutomator2'
}
server = 'http://localhost:4723/wd/hub'
# TODO:修改文件地址
store_path = r'C:\Users\deep dark\Desktop\living_data_store.csv.csv'
success_path = r'C:\Users\deep dark\Desktop\success_shop.txt'
error_path = r'C:\Users\deep dark\Desktop\error_shop.txt'
source_data_path = r'C:\Users\deep dark\Desktop\livestreaming.csv'
living_button = None
current_view = None
goods_btn = None
watch_num = None
driver = None
cursor = None
wait = None


class Result(Enum):
    success = 1
    error = 2


def conn_Appinum():
    """
    连接Appium客户端
    返回Appium客户端的驱动、等待时间和调用结果
    """
    try:
        app_driver = webdriver.Remote(server, desired_caps)
        # 设置缺省等待时间
        app_wait = WebDriverWait(app_driver, 20)
        return_result = Result.success
        return app_driver, app_wait, return_result
    except Exception as e:
        # 如果访问错误则返回空值
        print("访问Appium客户端出错：", e)
        print("请查看是否被封号，并重启模拟器和Appium客户端")
        app_driver = None
        app_wait = None
        return_result = Result.error
        return app_driver, app_wait, return_result


def call_Appinum():
    """
    错误重拨Appinum，若重播超过三次则退出系统
    """
    call_result = Result.error
    retry_time = 0
    while call_result == Result.error:
        app_driver, app_wait, call_result = conn_Appinum()
        if call_resultt == Result.error:
            print("Appium客户端连接错误,重新连接")
            retry_time += 1
            if retry_time == 3:
                print("尝试过多，退出程序")
                return app_driver, app_wait, call_result
        else:
            return app_driver, app_wait, call_result


def enter_search_view():
    """
    跳转至搜索页面，打开搜索窗
    """
    # 点击微淘按钮
    weitao_xpath = '//android.widget.FrameLayout[@content-desc="微淘"]/android.widget.ImageView'
    search_xpath = '//android.widget.TextView[@content-desc="끽"]'
    try:
        # 如果获取按钮失败，则直接返回信息
        weitao_button = wait.until(EC.presence_of_element_located((By.XPATH, weitao_xpath)))
        weitao_button.click()
    except Exception as e:
        print("微淘按钮点击失败:", e)
        return Result.error
    try:
        search_button = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
        search_button.click()
    except Exception as e:
        print("搜索按钮点击失败:", e)
        return Result.error
    return Result.success


def init_csv(store_csv_path, error_csv_path):
    """
    初始化存储爬取数据的csv以及爬取错误的店铺
    """
    global cursor
    cursor = open(store_csv_path, 'a', encoding='gbk', newline='')
    csv_writer = csv.writer(cursor)
    csv_writer.writerow(['店铺名', '粉丝数', '直播时间', '直播标题', '观看人数', '直播商品数', '直播商品'])
    cursor.close()
    cursor = open(error_csv_path, 'a', encoding='gbk', newline='')
    csv_writer = csv.writer(cursor)
    csv_writer.writerow(['淘宝店铺名称'])
    fp.close()


def trans_date(ret):
    """将文本日期转换为数字日期"""
    mon = ret[5:8]
    if mon == 'Jan':
        mon = '01'
    elif mon == 'Feb':
        mon = '02'
    elif mon == 'Mar':
        mon = '03'
    elif mon == 'Apr':
        mon = '04'
    elif mon == 'May':
        mon = '05'
    elif mon == 'Jun':
        mon = '06'
    elif mon == 'Jul':
        mon = '07'
    elif mon == 'Aug':
        mon = '08'
    elif mon == 'Sep':
        mon = '09'
    elif mon == 'Oct':
        mon = '10'
    elif mon == 'Nov':
        mon = '11'
    elif mon == 'Dec':
        mon = '12'
    else:
        print('error')
    temp = ret[0:4]
    temp = temp + mon
    temp = temp + ret[9:11]
    temp = int(temp)
    return temp


def extract_data_page1(shop_data_list):
    """
    正则提取直播日期、标题、阅读量
    返回直播块间的日期、直播名称以及直播块的日期list
    """
    date_pat = r'周(一|二|三|四|五|六|日)\s.*'
    name_pat = r'\s{1,10}.*'
    butten_pat = r'(\d{1,2}月\d{1,2}日 .*)'
    date_list = []
    title_list = []
    butten_list = []

    for shop_data in shop_data_list:
        ret1 = re.match(butten_pat, shop_data)
        ret2 = re.match(date_pat, shop_data)
        ret3 = re.match(name_pat, shop_data)
        try:
            butten_list.append(ret1.group())
        except Exception as e:
            print("按钮日期提取错误：", e)
            pass
        try:
            ret2 = str(ret2.group())
            ret2 = ret2[3:]
            date = trans_date(ret2)
            date_list.append(date)
        except Exception as e:
            print("日期列表提取错误：", e)
            pass
        try:
            title = ret3.group()
            count = 0
            for ch in title:
                if ch == ' ':
                    count += 1
            title = title[count:]
            title_list.append(title)
        except Exception as e:
            print("直播标题提取错误：", e)
            pass
    return date_list, title_list, butten_list


def save2csv(store_data, living_date, title_name, watch_num1, goods_number, goods_list):
    """
    将数据存储至CSV

    :param store_data: 店铺名称和店铺关注人数
    :param living_date: 直播日期
    :param title_name: 直播场次名称
    :param watch_num1: 观看人数
    :param goods_number: 商品数量
    :param goods_list: 商品名称列表
    """
    global cursor
    try:
        cursor = open(r'C:\Users\deep dark\Desktop\淘宝直播数据.csv', 'a', encoding='gbk', newline='')
        csv_writer = csv.writer(cursor)
        row_list = [store_data[0], store_data[1], living_date, title_name, watch_num1, goods_number, goods_list]
        csv_writer.writerow(row_list)
        print("存储成功")
    except Exception as e:
        print("存储出错,错误：", e)
    finally:
        cursor.close()


def scroll_func():
    """
    滑动直播商品栏->固定滑动参数：
    1.滑动商品栏，检查是否成功
    2.记录滑动了几次，作为返回结果
    """
    scroll_num = 0
    for i in range(0, 3):
        try:
            driver.swipe(start_x=540, start_y=1800, end_x=540, end_y=1323, duration=2700)
            scroll_num += 1
        except Exception as e:
            print('商品页面滑动错误,错误：', e)
        time.sleep(1)
    return scroll_num


def scroll_func2(distance):
    """
    滑动直播列表->需要给定滑动参数
    """
    distance = 1500 - distance
    scroll_flag = True
    scroll_count = 0
    while scroll_flag:
        try:
            driver.swipe(start_x=540, start_y=1500, end_x=540, end_y=distance, duration=2700)
            scroll_flag = False
            return Result.success
        except Exception as e:
            print("滑动直播列表失败，错误：", e)
            print("正在重试，剩余重试次数：", str(3 - scroll_count))
            scroll_count += 1
            if scroll_count >= 3:
                print('尝试次数用尽，即将退出程序')
                return Result.error
        time.sleep(1)


def handle_page3_data(data_list):
    """
    第三页的数据处理，并返回数据(含有中文的判断方法)
    1.shop_price_list  商品价格列表
    2.shop_title 商品标题列表
    """
    while None in data_list:
        data_list.remove(None)
    while '马上抢' in data_list:
        data_list.remove('马上抢')
    # shop_price_list = []
    # shop_price_pat = '(¥\xa0.*)'
    goods_title_list = []
    good_title_pat = r'(.+\…)'

    # for i in range(len(data_list)):
    #     try:
    #         ret = re.match(shop_price_pat, data_list[i])
    #         price = ret.group()
    #         price = float(price[2:])
    #         shop_price_list.append(price)
    #     except:
    #         pass

    for i in range(len(data_list)):
        try:
            ret = re.match(good_title_pat, data_list[i])
            title = ret.group()
            while '\u3000' in title:
                title.remove('\u3000')
            title = title[:-1]
            goods_title_list.append(title)
        except Exception as e:
            print("解析错误，错误：", e)
            pass
    return goods_title_list


# 2021/9/15已修改，删除了冗余的代码段，并规定最后三个商品不获取
def handle_page3(goods_num):
    """
    :param goods_num: 该场直播的商品数量
    :return: 商品信息列表

    进入第三个界面的任务：
    1.进入第三个界面->直播商品栏
    2.获取直播商品信息
    3.滚动商品栏获取更多的商品信息
    4.退出商品栏
    """
    print("*" * 30)
    print("进入第三个界面")
    print("*" * 30)
    # 全局变量
    global current_view
    # 还剩最后一个或者两个商品就结束，避免重复
    goods_list = []
    view_content_list = []
    while goods_num > 5:
        try:
            current_view = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'android.view.View')))
        except Exception as e:
            current_view = None
            print("商品栏页面抓取出现错误,错误：", e)
            return goods_list
        for element in current_view:
            goods_desc = element.get_attribute('content-desc')
            view_content_list.append(goods_desc)
        current_goods_list = handle_page3_data(view_content_list)
        for current_goods in current_goods_list:
            goods_list.append(current_goods)
        time.sleep(2)
        scroll_num = scroll_func()
        goods_num -= scroll_num
    current_view = None
    print("商品栏数据获取结束，正在跳转至上一页面...")
    return goods_list


# 2021/9/15 已修改，调整了异常控制程序，统一了变量名，并且增加了更多注释和提示
def handle_page2(store_data, living_date, title_name, button_content):
    """
    :param store_data: 店铺名称和关注人数
    :param living_date:  直播日期
    :param title_name:  直播名称
    :param button_content:  直播按钮的内容
    :return: 结果->error或success

    进入第二个界面的任务：
    1.进入第二个界面->直播内容界面
    2.获取观看人数和商品数量
    3.点击进入第三个界面->直播商品栏界面
    """
    print("*" * 30)
    print("进入第二个界面->直播内容界面")
    print("当前的店铺信息：", store_data)
    print("当前的直播日期：", living_date)
    print("当前的直播名字：", title_name)
    print("*" * 30)
    selector_content = 'new UiSelector().className("android.view.View").description("{}")'.format(button_content)
    # 全局变量
    global goods_btn, watch_num
    # 初始化参数
    btn_click_flag = True
    btn_click_count = 0
    # 尝试点击进入直播的按钮，尝试三次，如果失败则返回错误信息
    while btn_click_flag:
        try:
            button = driver.find_element_by_android_uiautomator(selector_content)
            button.click()
            btn_click_flag = False
        except Exception as e:
            btn_click_count += 1
            print('进入直播间错误,错误为：', e)
            print('等待一秒后再试，尝试剩余次数：', str(3 - btn_click_count))
            time.sleep(1)
            btn_click_flag = True
            if btn_click_count >= 3:
                print('尝试次数用尽，即将退出程序')
                return Result.error
    btn_click_flag = True
    btn_click_count = 0
    time.sleep(5)
    # 进入直播，点击暂停
    pause_btn_id = 'com.taobao.taobao:id/taolive_video_enter_btn'
    pause_btn_id1 = 'com.taobao.taobao:id/video_controller_play_btn'
    while btn_click_flag and btn_click_count < 3:
        try:
            pause_button = wait.until(EC.presence_of_element_located((By.ID, pause_btn_id)))
            pause_button.click()
            btn_click_flag = False
        except:
            try:
                pause_button = wait.until(EC.presence_of_element_located((By.ID, pause_btn_id1)))
                pause_button.click()
                TouchAction(driver).wait(3000).tap(x=900, y=1500, count=1).perform()
                btn_click_flag = False
            except Exception as e:
                btn_click_count += 1
                print('暂停错误,错误：', e)
                print('剩余尝试次数：', str(3 - btn_click_count))
    goods_btn_id = 'com.taobao.taobao:id/taolive_product_switch_btn'
    try:
        goods_btn = wait.until(EC.presence_of_element_located((By.ID, goods_btn_id)))
    except Exception as e:
        print("商品按钮寻找错误，错误：", e)
        return Result.error
    if re.match('[0-9]*', goods_btn.text) is not None:
        goods_number = int(goods_btn.text)
    else:
        goods_number = ''
    print('当前直播上线的商品数量：', str(goods_number))
    # 确定是否获取商品信息
    if goods_number == '' or goods_number < 6:
        print('这场直播没有商品,即将返回上一页面')
        return Result.success
    else:
        watch_num_id = 'com.taobao.taobao:id/taolive_topbar_watch_num'
        # 获取观看人数
        try:
            # 找到观看人数的框，并获取其中的观看人数
            watch_block = wait.until(EC.presence_of_element_located((By.ID, watch_num_id)))
            watch_num = watch_block.text
            watch_num = int(watch[:-3])
        except Exception as e:
            print('观看人数获取错误,错误：', e)
            watch_num = 0
        # try:
        #     ID_ele = wait.until(EC.presence_of_element_located((By.ID, 'com.taobao.taobao:id/taolive_room_num')))
        #     ID = ID_ele.text
        #     ID = ID[3:]
        # except:
        #     print('淘宝直播间ID获取错误')
        # 获取直播的商品数量
        # 获取淘宝直播间ID
        btn_click_flag = True
        btn_click_count = 0
        print('正在点击商品按钮，请稍等...')
        while btn_click_flag:
            try:
                goods_btn.click()
                btn_click_flag = False
            except Exception as e:
                btn_click_count += 1
                print('进入商品页面错误,错误：', e)
                print('等待一秒后再试，尝试剩余次数：', str(3 - btn_click_count))
                if btn_click_count >= 3:
                    print('尝试次数用尽，即将退出程序')
                    return Result.error
        time.sleep(3)
        # 2021/9/15 14:26修改
        # 进入商品栏界面
        goods_list = handle_page3(goods_number)
        # 存储信息
        save2csv(store_data, living_date, title_name, watch_num, goods_number, goods_list)
        # 返回第二个页面，模拟keyboard的返回键
        try:
            driver.press_keycode(4)
        except Exception as e:
            print('返回上一页面错误，即将退出程序，错误：', e)
            return Result.error
    return Result.success


def isnot_end():
    """查看是否到底了"""
    global current_view
    end_flag = True
    recall_times = 0
    check_result = Result.error
    current_view_class = 'android.view.View'
    while check_result == Result.error:
        try:
            current_view = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, current_view_class)))
            check_result = Result.success
        except Exception as e:
            recall_times += 1
            print('未能获取当前页面信息,错误：', e)
            print('剩余尝试次数：', str(3 - recall_times))
            if recall_times > 3:
                print('尝试次数用尽，即将退出程序')
                current_view = None
                return end_flag, Result.error
    temp_data = []
    for element in current_view:
        temp_data.append(element.get_attribute('content-desc'))
    for char in temp_data:
        if char == '到底了':
            print('到底了')
            end_flag = False
    current_view = None
    return end_flag, Result.success


# def isnot_zhibo():
#     flag = True
#     time.sleep(5)
#     try:
#         eles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'android.view.View')))
#     except:
#         try:
#             eles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'android.view.View')))
#         except:
#             print('直播数据错误')
#     temp_data = []
#     for ele in eles:
#         temp_data.append(ele.get_attribute('content-desc'))
#     for char in temp_data:
#         if char == '直播':
#             print('到顶了')
#             flag = False
#     return flag


def fans_num_trans(fans_num):
    fans_num = fans_num[3:]
    if fans_num[-1] == '万':
        fans_num = fans_num[:-1]
        fans_num = float(fans_num)
        fans_num = fans_num * 10000
    fans_num = int(fans_num)
    return fans_num


def position_list(position):
    temp = []
    position = re.findall(r"\d+", position)
    for num in position:
        num = int(num)
        temp.append(num)
    return temp


def set_scroll_params(gap_date_list, button_date_list):
    """
    设置对每个直播块的滑动距离参数
    :param button_date_list: 在直播块间的时间内容
    :param gap_date_list: 在直播板上的时间内容:
    :return: 滑动距离参数
    """
    # 获取当前直播的直播块间和直播板上的时间内容
    gap_date = gap_date_list[0]
    button_date = button_date_list[0]
    # TODO: 修改起始日期设定
    time_diff = gap_date - 20210101
    # 根据与设定时间的差距，判断是否选择该场直播
    if time_diff > 0:
        click_flag = False
    else:
        click_flag = True
    if button_date[-3:] == '小时前':
        scroll_param = 568
    else:
        gap_date = str(gap_date)
        gap_date = gap_date[4:]
        button_date = re.sub('[年月日]', '', button_date)
        if len(button_date) == 10:
            button_date = button_date[:4]
        else:
            button_date = button_date[4:8]
        # 如果是一天一场，那么要多滑动一些
        if gap_date == button_date:
            scroll_param = 568
        else:
            scroll_param = 480
    return scroll_param, click_flag


def shop_page_extract(shop_name):
    """
    1、进入店铺页面
    2、进入微淘直播
    3、返回第一张图的相关信息
    4、sum_pag1_data得到一个总的列表数据
    """
    # 函数变量
    global living_button, current_view
    search_block_xpath = '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.widget.EditText'
    search_button_xpath = '//android.view.View[@content-desc="搜索"]'
    weitao_button_xpath = '//android.view.View[@content-desc="店铺微淘"]'
    zhibo_button_xpath = '//android.view.View[@content-desc="直播"]'
    page1_data_list = []
    shop_data_list = [shop_name]
    # 点击搜索
    try:
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, search_block_xpath)))
        search_input.click()
    except Exception as e:
        print("点击搜索框错误,错误：", e)
        return Result.error
    shop_shell = "adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{}'".format(shop_name)
    os.system(shop_shell)
    # 点击搜索按钮，进入店铺详情页
    try:
        search_button = wait.until(EC.presence_of_element_located((By.XPATH, search_button_xpath)))
        search_button.click()
        TouchAction(driver).wait(1000).tap(x=281, y=573, count=1).perform()
    except:
        print("点击搜索按钮错误")
        return Result.error
    # 点击显示的第一个店铺，店铺页面，转到微淘直播
    time.sleep(7)
    try:
        code = 'new UiSelector().descriptionContains("粉丝数")'
        element = driver.find_element_by_android_uiautomator(code)
        fans_num = element.get_attribute('content-desc')
        fans_num = fans_num_trans(fans_num)
        shop_data_list.append(fans_num)
    except Exception as e:
        print('店铺粉丝数无法解析,错误:', e)
        return Result.error
    print(shop_data_list)
    try:
        weitao_button = wait.until(EC.presence_of_element_located((By.XPATH, weitao_button_xpath)))
        weitao_button.click()
    except Exception as e:
        print('微淘按钮点击失败,错误:', e)
        return Result.error
    try:
        living_button = wait.until(EC.presence_of_element_located((By.XPATH, zhibo_button_xpath)))
    except Exception as e:
        print('直播按钮可能在当前页面不存在，向下滑,错误：', e)
        # 使用直播的下边缘位置讲整个直播页面全部滑出来
        try:
            driver.swipe(start_x=176, start_y=650, end_x=176, end_y=240, duration=1700)
            living_button = wait.until(EC.presence_of_element_located((By.XPATH, zhibo_button_xpath)))
        except NoSuchElementException:
            print('直播按钮获取失败')
            return Result.error
    # 获取页面的长宽信息,返回的是字符串
    position = living_button.get_attribute('bounds')
    position = position_list(position)
    live_y = position[3] + 30
    try:
        living_button.click()
        time.sleep(2)
    except Exception as e:
        print('直播按钮点击失败,错误：', e)
        return Result.error
    # 向下滑动以显示三个直播页面，如果出现错误则手动调整
    try:
        driver.swipe(start_x=176, start_y=live_y, end_x=176, end_y=198, duration=5000)
    except:
        print("滑动操作错误，需要手动解决!")
        time.sleep(5)
    check_result, end_flag = isnot_end()
    if check_result == Result.error:
        return Result.error
    while end_flag:
        try:
            current_view = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'android.view.View')))
        except:
            current_view = None
            print("直播信息获取错误")
            continue
        for element in current_view:
            content = element.get_attribute('content-desc')
            if content != '':
                page1_data_list.append(content)
        gap_dates, title_names, button_dates = extract_data_page1(page1_data_list)
        current_view = None
        page1_data_list = []
        # button_dates为直播块的时间数据，gap_dates为直播块间的时间数据
        distance, click_flag = set_scroll_params(gap_dates, button_dates)
        # 获取直播时间
        living_date = gap_dates[0]
        if click_flag:
            time.sleep(2)
            click_result = handle_page2(data_shop_list, living_date, title_names[0], button_dates[0])
            # 如果成功完成直播页面数据的获取，则返回到上一页面，否则返回错误
            if click_result == Result.success:
                try:
                    driver.press_keycode(4)
                except Exception as e:
                    print('返回上一页面错误，错误：', e)
                    return Result.error
            else:
                return Result.error
            time.sleep(2)
            # 将直播列表对齐，以方便全部展示信息，滑动可以不返回错误，可以人工手动操作
            try:
                driver.swipe(start_x=176, start_y=700, end_x=176, end_y=445, duration=2300)
            except Exception as e:
                print('直播列表滑动错误，错误：', e)
                print('需要手动滑动')
            time.sleep(2)
        scroll_func2(distance)
        check_result, end_flag = isnot_end()
        if check_result == Result.error:
            return Result.error
    return Result.success


# 在main函数中的变量算是全局变量
if __name__ == '__main__':
    driver, wait, result = call_Appinum()
    if result != Result.error:
        # 初始化csv
        init_csv(store_path, error_path)
        # 获取店铺信息
        df = pd.read_csv(source_data_path, encoding='gbk')
        full_shop_list = df['淘宝店铺名称']
        full_shop_list = list(full_shop_list)
        for shop in full_shop_list:
            result = shop_page_extract(shop)
            if result == Result.success:
                with open(success_path, 'a', encoding='utf-8') as fp:
                    print(shop, '店铺直播信息获取成功')
                    fp.write(shop + '\n')
                    fp.close()
                search_flag = True
                retry_num = 0
                for a1 in range(0, 2):
                    try:
                        driver.press_keycode(4)
                        time.sleep(2)
                    except:
                        print('返回上一页错误')
                        search_flag = False
                        break
                while search_flag:
                    try:
                        search_element = wait.until(
                            EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@content-desc="끽"]')))
                        search_element.click()
                        search_flag = False
                    except:
                        retry_num += 1
                        print('剩余尝试次数：', str(3 - retry_num))
                        time.sleep(2)
                        if retry_num >= 3:
                            print('尝试次数已用尽，退出程序')
                            break
            else:
                print('')
                with open(error_path, 'a', encoding='utf-8') as fp:
                    print(shop, '店铺直播信息获取失败，准备退出程序')
                    fp.write(shop + '\n')
                    fp.close()
                break
