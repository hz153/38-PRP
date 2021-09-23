from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
import re
import time
import csv
import pandas as pd
global items_url
global reviews
reviews = []
items_url='https://item.taobao.com/'
market_list=[]


def get_page(baseurl, product_list, type, date, num, watch):
    shop_id = baseurl[12:-11]
    driver.get(baseurl)
    time.sleep(2)
    try:
        close_brand()
    except:
        print('没有休息了页面')
    try:
        link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#hd div.all-cats-trigger.popup-trigger a')))
        url_all = link.get_attribute('href')
    except:
        print('进入全部商品错误')
    driver.get(url_all)
    for i in range(len(product_list)):
        find_product(shop_id, product_list[i], type[i], date[i], num[i], watch[i])
        driver.get(url_all)


def find_product(shop_id, product, type, date, num, watch):
    time.sleep(2)
    try:
        close_brand()
    except:
        print('没有休息了提示')
    input_place = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#shop-search-list div.search-form li.keyword input')))
    input_place.click()
    input_place.send_keys(product)
    button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#shop-search-list div.search-form li.submit button')))
    button.click()
    time.sleep(2)
    try:
        close_brand()
    except:
        print('没有休息了提示')
    get_product(shop_id, product, type, date, num, watch)


def same_name(name,product):
    for i in range(len(product)):
        if name[i]==product[i]:
            flag=True
        else:
            flag=False
        if flag==False:
            return False
    return True


def get_product(shop_id, product, type, date, num, watch):
    flag = True
    flag1 = True
    product_list = []
    while flag==True:
        time.sleep(3)
        html = driver.page_source
        doc = pq(html)
        divs = doc('#J_ShopSearchResult div.item3line1').items()  # 遍历所有的块，一行一个块
        for div in divs:
            dls = div('dl').items()  # 在每个块中取出产品
            for dl in dls:
                name = dl.find('dd.detail a').text()
                if same_name(name, product):
                    goods_url = dl.find('dd.detail a').attr('href')
                    goods_url = "https:" + goods_url
                    product_list.append(goods_url)
                    product_list.append(shop_id)
                    good_name = name
                    product_list.append(good_name)
                    goods_id = dl.attr('data-id')
                    product_list.append(goods_id)
                    cprice = dl.find('dd.detail div.cprice-area').text()
                    cprice = float(cprice[1:])
                    product_list.append(cprice)
                    try:
                        sprice = dl.find('dd.detail div.sprice-area').text()
                        sprice = float(sprice[1:])
                    except:
                        print('没有原价格')
                        sprice = 0
                    product_list.append(sprice)
                    product_list.append(type)
                    product_list.append(date)
                    product_list.append(num)
                    product_list.append(watch)
                    flag1 = False
                    break
        if flag1 == False:
            break
        else:
            try:
                next_url = doc('#J_ShopSearchResult div.pagination a.next').attr('href')
            except:
                next_url = None
            if next_url != None:
                driver.get(next_url)
                try:
                    close_brand()
                except:
                    print('没有休息了提示')
            else:
                flag = False
    print(product_list)
    right(product_list)


def close_brand():
    close_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#sufei-dialog-close')))
    close_button.click()


def right(product_list):
    wuyou = 0
    tuihuo_7 = 0
    tuihuo_15 = 0
    insurance_dingdan = 0
    gongyi = 0
    insurance_yunfei = 0
    goods_url = product_list[0]
    driver.get(goods_url)
    try:
        close_brand()
    except:
        print('没有休息了提示')
    html1 = driver.page_source
    doc1 = pq(html1)
    right_html = doc1('#J_tbExtra dl:nth-child(1) dd a').items()
    for i in right_html:
        right = i.text()
        if right == '无忧退货':
            wuyou = 1
        elif right == '15天退货':
            tuihuo_15 = 1
        elif right == '7天无理由':
            tuihuo_7 = 1
        elif right == '运费险':
            insurance_yunfei = 1
        elif right == '订单险':
            insurance_dingdan = 1
        elif right == '公益宝贝':
            gongyi = 1
        else:
            pass
    all_list = [product_list[1], product_list[2], product_list[3], product_list[4], product_list[5], product_list[6],
                product_list[7], product_list[8], product_list[9], wuyou, tuihuo_7, tuihuo_15, insurance_yunfei,
                insurance_dingdan, gongyi]
    print(all_list)
    store_csv(all_list)


def store_csv(all_list):
    fp = open('goods.csv', 'a', encoding='utf-8', newline='')
    csv_writer = csv.writer(fp)
    csv_writer.writerow(all_list)
    fp.close()


def same_shop(goodslist):
    flag = True
    count1 = 0
    length = len(goodslist)
    for i in range(0, length):
        if i+1 < length:
            if goodslist[i][1] != goodslist[i+1][1]:
                count1 = i
                break
        elif i+1 >= length:
            flag = False
            count1 = i
    return count1, flag


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    wait = WebDriverWait(driver, 10)
    upload_url = 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d92T0fwa&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
    driver.get(upload_url)
    time.sleep(13)
    # 扫码登录10秒内完成
    # 写一个从shop里面获取url的函数，再写一个从shop去直播数据配对的函数
    fp = open(r'C:\Users\deep dark\Desktop\goods.csv', 'a', encoding='utf-8', newline='')
    csv_writer = csv.writer(fp)
    csv_writer.writerow(['店铺id', '商品名称', '商品id', '优惠价格', '原价格', '商品类型', '开始直播时间', '同场直播商品', '观看人数',
                         '无忧退货', '7天无理由', '15天退货', '运费险', '订单险', '公益宝贝'])
    fp.close()
    df = pd.read_csv(r'C:\Users\deep dark\Desktop\shop.csv', encoding='gbk')
    full_shoplist = df.values.tolist()
    df = pd.read_csv(r'C:\Users\deep dark\Desktop\middle_goods.csv', encoding='gbk')
    full_goodslist = df.values.tolist()
    length1 = 0
    count = 0
    length_span, flag = same_shop(full_goodslist[length1:])
    while flag == True:
        baseurl = full_shoplist[count][1]
        count += 1
        goods_name = []
        goods_type = []
        goods_num = []
        goods_watch = []
        goods_date = []
        length_span += 1
        length2 = length_span + length1
        goods_list = full_goodslist[length1:length2]
        length1 = length2
        length_span, flag = same_shop(full_goodslist[length1:])
        for goods in goods_list:
            goods_name.append(goods[1])
            goods_type.append(goods[2])
            goods_date.append(goods[3])
            goods_num.append(goods[4])
            goods_watch.append(goods[5])
        print(baseurl, goods_name)
        get_page(baseurl, goods_name, goods_type, goods_date, goods_num, goods_watch)

