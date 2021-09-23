#-*- coding:utf-8 -*-
import requests
import json
import re
import pandas as pd
import csv
import time

def get_comment(goods_id,user_id,rate_type):
    flag = True
    count = 0
    date_list = []
    page_num = 1
    rate_type = str(rate_type)
    while flag:
        page_num1 = str(page_num)
        count1 = 0
        url = "https://rate.taobao.com/feedRateList.htm"
        header = {
            "cookie": "thw=cn; enc=%2FhR6LaGTopajhjRumuLnQ%2BA2M9sGSjeaUfF3TwfaTIXutq2VAkhiOxQvRBJGik3dzHBii3wZm5bPAHRQW4oqrg%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; t=e0249eca07722feb6893d8a32d92cafe; cna=bgwIGNKZUg8CAcp4Cx7n53k0; lgc=%5Cu5C31%5Cu95EE%5Cu6B64%5Cu7528%5Cu6237%5Cu4E0D%5Cu5B58%5Cu5728; tracknick=%5Cu5C31%5Cu95EE%5Cu6B64%5Cu7528%5Cu6237%5Cu4E0D%5Cu5B58%5Cu5728; mt=ci=29_1; miid=45666379231058975; sgcookie=E100IS9DJGQqJXQUZlEcG8oyhkgl%2BA4ViaXLHdhln3iumn0hFGGxqUmDxwU1ZHDZUBc6mO7KPgSh1ZSOkmei6XsUXQ%3D%3D; uc3=lg2=U%2BGCWk%2F75gdr5Q%3D%3D&nk2=3ROjY2NkfSJ8pLdySKncDA%3D%3D&id2=UNQwV4ewn8fVhA%3D%3D&vt3=F8dCuASnFxOUAqZnsQ4%3D; uc4=nk4=0%4035hJNHHx6SrseIGutRSU1beazyXkPooMmSNG&id4=0%40UgP7gBoxVTyWojM58sO%2BGPE9zVq3; _cc_=WqG3DMC9EA%3D%3D; _m_h5_tk=f4cfc3a79b541983dec62e0dda9b0c6b_1613718326277; _m_h5_tk_enc=91c5029df05fa739190785b208731817; xlly_s=1; x5sec=7b22726174656d616e616765723b32223a223033333362646133663863366639373665653730323630383532613365626365434a654276594547454d547336376d597636442b5a7a435a78727042227d; uc1=cookie14=Uoe1gWCfJbG8Ig%3D%3D; _tb_token_=5189ee7eee13e; cookie2=169519500a88fcf43825a87b82f1b8cc; v=0; tfstk=cHndBNsG6CAH7Fet32LGNtTAjZqdZPILw9NV2KXv_Z7lulsRiromDveMR-eJtdC..; l=eBgo9ZMqjOBWzUFjBO5w-urza77tXIOf11PzaNbMiInca6afahP2RNCIxk72udtjgtfDXetrzoRtYReH88zLRqTjGO0qOC0eQoJ6-; isg=BG1tM1hV8ePakZWinzfUULgHfAnnyqGcYKqifa9z0IQ4Jo7YdxsRbAtwEPrAoblU",
            "referer": "https://item.taobao.com/item.htm",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
        }
        params = {  # 必带信息
            "auctionNumId": goods_id,  # 商品id
            "userNumId": user_id,  # 商店id
            "currentPageNum": page_num1,  # 页码
            "rateType": rate_type,  # 评论情况
            "callback": "jsonp_tbcrate_reviews_list",
        }
        page_num += 1
        response = requests.get(url, params, headers=header).content.decode('utf-8')
        print(response)
        response = response[29:-2]
        response = json.loads(response)
        comments = response["comments"]
        total_comment = int(response["total"])
        if comments == [] or total_comment == 0:
            break
        for comment in comments:
            content = comment["content"]
            if content == '评价方未及时做出评价,系统默认好评!' or content == '此用户没有填写评价。':
                count1 += 1
                continue
            count += 1
            date = comment["date"]
            date = re.sub('[年月日]', '', date)
            date = int(date[:8])
            date_list.append(date)
    return count, date_list


def store_csv(all_list):
    fp = open(r'C:\Users\10155\Desktop\goods_comment.csv', 'a', encoding='gbk', newline='')
    csv_writer = csv.writer(fp)
    csv_writer.writerow(all_list)
    fp.close()


def get_right(service):
    wuyou = 0
    tuihuo_7 = 0
    tuihuo_15 = 0
    insurance_dingdan = 0
    gongyi = 0
    insurance_yunfei = 0
    for i in range(len(service)):
        right = service[i]['title']
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
    print('商品权益')
    print(wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi, insurance_yunfei)
    return wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi, insurance_yunfei

def get_info(shop_id, goods_id):
    url = "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm"
    header = {
        "cookie": "thw=cn; enc=%2FhR6LaGTopajhjRumuLnQ%2BA2M9sGSjeaUfF3TwfaTIXutq2VAkhiOxQvRBJGik3dzHBii3wZm5bPAHRQW4oqrg%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; ubn=p; ucn=center; t=e0249eca07722feb6893d8a32d92cafe; cna=bgwIGNKZUg8CAcp4Cx7n53k0; lgc=%5Cu5C31%5Cu95EE%5Cu6B64%5Cu7528%5Cu6237%5Cu4E0D%5Cu5B58%5Cu5728; tracknick=%5Cu5C31%5Cu95EE%5Cu6B64%5Cu7528%5Cu6237%5Cu4E0D%5Cu5B58%5Cu5728; mt=ci=29_1; miid=45666379231058975; sgcookie=E100IS9DJGQqJXQUZlEcG8oyhkgl%2BA4ViaXLHdhln3iumn0hFGGxqUmDxwU1ZHDZUBc6mO7KPgSh1ZSOkmei6XsUXQ%3D%3D; uc3=lg2=U%2BGCWk%2F75gdr5Q%3D%3D&nk2=3ROjY2NkfSJ8pLdySKncDA%3D%3D&id2=UNQwV4ewn8fVhA%3D%3D&vt3=F8dCuASnFxOUAqZnsQ4%3D; uc4=nk4=0%4035hJNHHx6SrseIGutRSU1beazyXkPooMmSNG&id4=0%40UgP7gBoxVTyWojM58sO%2BGPE9zVq3; _cc_=WqG3DMC9EA%3D%3D; _m_h5_tk=f4cfc3a79b541983dec62e0dda9b0c6b_1613718326277; _m_h5_tk_enc=91c5029df05fa739190785b208731817; cookie2=1af2fb47db16f6c606e44e5de824f59e; _tb_token_=e73a8b73893da; xlly_s=1; v=0; uc1=cookie14=Uoe1gWCfJCmToQ%3D%3D; isg=BOTkVL9YWHhECqyZLuDt-3lIteLWfQjngfU7Jv4EHq9aqYZzJoxed-7IaQGxdkA_; tfstk=cB-ABgquwbc0pI6JLE3u1JiP75dAaVEA6-1UXv2KpiXSMyrTfscexHpAEq6dBjDR.; l=eBgo9ZMqjOBWzYhxBO5Zlurza77OCIObz1PzaNbMiInca66h_ECMFNCIxxMy8dtjgt5xjetrzoRtYRU68xzLRPkDBeYIOC0eQT9w-e1..",
        "referer": "https://item.taobao.com/item.htm",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
    }
    params = {
        "itemId": goods_id,
        "sellerId": shop_id,
        "modules": "price,originalPrice,xmpPromotion,tradeContract",
        "callback": "onSibRequestSuccess",
    }
    response = requests.get(url, params, headers=header).content.decode('utf-8')
    response = response[22:-2]
    response = json.loads(response)
    print(response)
    service = response['data']['tradeContract']['service']
    wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi, insurance_yunfei = get_right(service)
    try:
        sprice = response['data']['originalPrice']['def']['price']
    except:
        sprice = 0
    try:
        cprice = response['data']['promotion']['promoData']['def'][0]['price']
    except:
        cprice = 0
    return sprice, cprice, wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi, insurance_yunfei


if __name__ == '__main__':
    fp = open(r'C:\Users\10155\Desktop\goods_comment.csv', 'a', encoding='gbk', newline='')
    csv_writer = csv.writer(fp)
    csv_writer.writerow(['淘宝店铺名称', '商品名称', '原价格', '优惠价格', '无忧退货', '7天无理由', '15天退货', '订单险', '公益商品',
                         '运费险', '好评数量', '好评时间', '中评数量', '中评时间', '差评数量', '差评时间', '商品类型', '开始直播时间',
                         '同场直播商品', '观看人数'])
    fp.close()
    df = pd.read_csv(r'C:\Users\10155\Desktop\goods.csv', encoding='gbk')
    full_goodlist = df.values.tolist()
    for good in full_goodlist:
        time.sleep(2)
        shop_id = str(int(good[0]))
        user_id = str(int(good[1]))
        goods_id = str(int(good[2]))
        type = int(good[5])
        time_ = good[6]
        goods_num = good[7]
        watch = good[8]
        print(shop_id, user_id, goods_id)
        sprice, cprice, wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi, insurance_yunfei = get_info(shop_id, goods_id)
        rate_type = 1
        print('开始爬好评')
        count_good, date_list_good = get_comment(goods_id, user_id, rate_type)
        rate_type = 0
        print('开始爬中评')
        count_middle, date_list_middle = get_comment(goods_id, user_id, rate_type)
        rate_type = -1
        print('开始爬差评')
        count_bad, date_list_bad = get_comment(goods_id, user_id, rate_type)
        all_list = [good[3], good[4], sprice, cprice, wuyou, tuihuo_7, tuihuo_15, insurance_dingdan, gongyi,
                    insurance_yunfei, count_good, date_list_good, count_middle, date_list_middle, count_bad, date_list_bad,
                    type, time_, goods_num, watch]
        print(all_list)
        store_csv(all_list)









