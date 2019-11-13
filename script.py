from flask import Flask, request, render_template
import time
myWeb = Flask(__name__)

user_pwd = {}  # user-password dictionary
readin = open('user_pwd.txt', "r", encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split('\n')
del s[-1]
for line in s:
    l = line.split()
    user_pwd[l[0]] = l[1]


holding_pwd = ""  # password for check holding condition

readin = open('holding_pwd.txt', 'r', encoding="UTF-8")
s = readin.read()
readin.close()
holding_pwd = s

del_pwd = ""

readin = open('del_pwd.txt', 'r', encoding="UTF-8")
s = readin.read()
readin.close()
del_pwd = s

# print(del_pwd)

user_holding = {}  # cash, share 1, share 2 ... share 5
readin = open('user_holding.txt', 'r', encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split('\n')
del s[-1]
for line in s:
    l = line.split()
    user_holding[l[0]] = [float(l[1]), int(l[2]), int(
        l[3]), int(l[4]), int(l[5]), int(l[6])]


market_price = [0, 0, 0, 0, 0]  # 最近四十次成交的均价

readin = open('market_price.txt', 'r', encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split()
for i in range(len(market_price)):
    market_price[i] = float(s[i])


market_price_queue = {12: [], 13: [], 14: [],
                      15: [], 16: []}  # 5 * 40 * 2 [quant, total]
readin = open("market_price_queue.txt", 'r', encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split("\n\n")
del s[-1]

for d in s:
    d = d.split("\n")
    day = int(d[0])
    for o in d[1:]:
        l = o.split()
        market_price_queue[day].append([int(l[0]), float(l[1])])


def update_market_price(day):
    # day = 12 ~ 16
    global market_price
    global market_price_queue
    length = len(market_price_queue[day])
    if length > 40:
        del market_price_queue[day][0]
    share_sum = 0.0
    price_sum = 0.0
    for l in market_price_queue[day]:
        share_sum += l[0]
        price_sum += l[1]
    if share_sum == 0:
        market_price[day - 12] = 0
    else:
        market_price[day - 12] = round(price_sum / share_sum, 2)
    return


# order是2个40 * 6的list, orderID username Day quant price total
buy_order = []
readin = open("buy_order.txt", 'r', encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split('\n')
del s[len(s) - 1]
for line in s:
    l = line.split()
    if l == []:
        continue
    buy_order.append([int(l[0]), l[1], int(
        l[2]), int(l[3]), float(l[4]), float(l[5])])

sell_order = []
readin = open("sell_order.txt", 'r', encoding="UTF-8")
s = readin.read()
readin.close()
s = s.split('\n')
del s[len(s) - 1]
for line in s:
    l = line.split()
    if l == []:
        continue
    sell_order.append([int(l[0]), l[1], int(
        l[2]), int(l[3]), float(l[4]), float(l[5])])

order_cnt = 0
readin = open("order_cnt.txt", 'r', encoding="UTF-8")
s = readin.read()
readin.close()
order_cnt = int(s)


def del_order(ID, buy_sell):
    global buy_order
    global sell_order
    if buy_sell == "buy":
        for i in range(len(buy_order)):
            if buy_order[i][0] == ID:
                del buy_order[i]
                break
    else:
        for i in range(len(sell_order)):
            if sell_order[i][0] == ID:
                del sell_order[i]
                break
    return


def add_order(ID, user, day, quant, price, total, buy_sell):
    global buy_order
    global sell_order
    if buy_sell == "buy":
        buy_order.append([ID, user, day, quant, price, total])
        buy_order = sorted(buy_order, key=lambda x: x[0], reverse=True)
        if len(buy_order) > 40:
            del buy_order[len(buy_order) - 1]
    else:
        sell_order.append([ID, user, day, quant, price, total])
        sell_order = sorted(sell_order, key=lambda x: x[0], reverse=True)
        if len(sell_order) > 40:
            del sell_order[len(sell_order) - 1]
    return


@myWeb.route("/")  # 主页
def root():
    return render_template("login.html")

@myWeb.route("/delete_order_page")
def delete_order_page():
    return render_template("delete_order_page.html")

@myWeb.route("/holding_condition")
def holding_condition():
    return render_template("holding_condition.html")


@myWeb.route("/prof_delete_order_page")
def delete_order():
    return render_template("delete_order.html")

@myWeb.route("/change_password_page")
def change_password_page():
    return render_template("change_pwd.html")

@myWeb.route("/store_data")  # 存储数据
def store_data():
    # 把订单 市价 持仓情况全部写进不同的txt中
    global buy_order
    global sell_order
    global market_price
    global user_holding

    localtime = time.asctime(time.localtime(time.time()))

    output = open('buy_order_record.txt', 'a+', encoding='UTF-8')
    output.write(str(localtime) + '\n')
    for o in buy_order:
        rowtxt = "{}, {}, {}, {}, {}, {}".format(
            o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
        output.write('\n')
    output.write('\n')
    output.close()

    output = open('sell_order_record.txt', 'a+', encoding='UTF-8')
    output.write(str(localtime) + '\n')
    for o in sell_order:
        rowtxt = "{}, {}, {}, {}, {}, {}".format(
            o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
        output.write('\n')
    output.write('\n')
    output.close()

    output = open('market_price_record.txt', 'a+', encoding='UTF-8')
    output.write(str(localtime) + '\n')
    o = market_price
    rowtxt = "{}, {}, {}, {}, {}".format(o[0], o[1], o[2], o[3], o[4])
    output.write(rowtxt)
    output.write('\n\n')
    output.close()

    output = open('user_holding_record.txt', 'a+', encoding='UTF-8')
    output.write(str(localtime) + '\n')
    for name in user_holding:
        o = user_holding[name]
        rowtxt = "{}, {}, {}, {}, {}, {}, {}".format(
            name, o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
        output.write('\n')
    output.write('\n')
    output.close()

    # user_holding
    output = open('user_holding.txt', 'w+', encoding='UTF-8')
    for name in user_holding:
        o = user_holding[name]
        rowtxt = "{} {} {} {} {} {} {}".format(
            name, o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
        output.write('\n')
    output.close()
    # buy_order
    output = open('buy_order.txt', 'w+', encoding='UTF-8')
    for o in buy_order:
        rowtxt = "{} {} {} {} {} {}".format(o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
        output.write('\n')
    output.close()

    # sell_order
    output = open('sell_order.txt', 'w+', encoding='UTF-8')
    for o in sell_order:
        rowtxt = "{} {} {} {} {} {}\n".format(
            o[0], o[1], o[2], o[3], o[4], o[5])
        output.write(rowtxt)
    output.close()

    # order_cnt
    output = open("order_cnt.txt", 'w+', encoding='UTF-8')
    output.write(str(order_cnt))
    output.close()

    # market_price
    output = open("market_price.txt", 'w+', encoding="UTF-8")
    output.write("{} {} {} {} {}".format(
        market_price[0], market_price[1], market_price[2], market_price[3], market_price[4]))
    output.close()

    # market_price_queue
    output = open("market_price_queue.txt", 'w+', encoding="UTF-8")
    s = ""
    for name in market_price_queue:
        s += str(name) + '\n'
        ls = market_price_queue[name]
        for l in ls:
            s += "{} {}\n".format(l[0], l[1])
        s += '\n'
    output.write(s)
    output.close()

    return 'data stored successfully'


@myWeb.route("/check_user_pwd", methods=["post"])
def check_user_pwd():
    # 检查用户名和密码
    username = request.form["username"]
    password = request.form["password"]

    if username in user_pwd:
        if user_pwd[username] == password:

            return '1'
        else:
            return '0'
    else:
        return '0'
        # 若用户名密码均正确 返回1, 用户名正确密码错误返回0, 用户名错误返回-1
        # 并且如果用户名和密码正确，返回持仓情况


@myWeb.route("/check_holding_pwd", methods=["post"])
def check_holding_pwd():
    pwd = request.form["password"]
    if pwd == holding_pwd:
        return '1'
    else:
        return '0'


@myWeb.route("/check_del_ID_pwd", methods=["post"])
def check_del_ID_pwd():
    global del_pwd
    global buy_order
    global sell_order

    ID = request.form["orderID"]
    pwd = request.form["password"]
    odt = request.form["ordertype"]
    # print(ID, pwd, odt)
    if pwd == del_pwd:
        # print("valid del pwd")
        flag = False
        ls = []
        if odt == "buy":
            ls = buy_order
        else:
            ls = sell_order
        int_ID = int(ID)
        for o in ls:
            if o[0] == int_ID:
                flag = True
                break

        if not flag:
            return '0'
        else:
            return '1'

    else:
        # print("invalid del pwd")
        return '0'


@myWeb.route("/return_holding", methods=["post"])
def return_holding():
    username = request.form["username"]
    ls = user_holding[username].copy()
    ls[0] = round(ls[0], 4)
    return {username: ls}


@myWeb.route("/return_holding_str", methods=["post"])
def return_holding_str():
    global user_holding
    s = "<!doctype html><html><head><meta charset='UTF-8'></head><body>"
    s += "<table border=1><tr><th>user</th><th>cash</th><th>December 12</th><th>December 13</th><th>December 14</th><th>December 15</th><th>December 16</th></tr>"
    for name in user_holding:
        s += "<tr>"
        s += "<td>"
        s += name
        s += "</td>"
        hold = user_holding[name]
        for i in range(len(hold)):
            s += "<td>"
            tmp = hold[i]
            if i == 0:
                tmp = round(tmp, 4)
            s += str(tmp)
            s += "</td>"

        s += "</tr>"
    s += "</table></body>"

    return s


@myWeb.route("/return_price", methods=["post"])
def return_price():
    return {"price": market_price}


@myWeb.route("/return_order", methods=["post"])
def return_order():
    l1 = buy_order.copy()
    for o in l1:
        o[5] = round(o[5], 3)
    l2 = sell_order.copy()
    for o in l2:
        o[5] = round(o[5], 3)
    return {"buyorder": l1, "sellorder": l2}


@myWeb.route("/return_order_str", methods=["post"])
def return_order_str():
    table_type = request.form["type"]
    ls = []
    if table_type == "buy":
        ls = buy_order.copy()
    else:
        ls = sell_order.copy()

    lines = len(ls)

    s = ""
    for i in range(lines):
        s += "<tr>"
        for j in range(6):
            if j == 1:
                continue
            tmp = ls[i][j]
            if j == 5:
                tmp = round(tmp, 3)
            s += ("<td id='" + table_type + "_order" + str(i) +
                  str(j) + "'>" + str(tmp) + "</td>")
        s += "</tr>"
    for i in range(lines, 40):
        s += "<tr>"
        for j in range(6):
            if j == 1:
                continue
            s += ("<td id='" + table_type + "_order" + str(i) +
                  str(j) + "'>" + "____________" + "</td>")
        s += "</tr>"
    return s

@myWeb.route("/change_pwd", methods=["post"])
def change_pwd():
    global user_pwd
    # 检查用户名和密码
    username = request.form["username"]
    password = request.form["password"]
    n_password = request.form["new_password"]
    if username in user_pwd:
        if user_pwd[username] != password:
            print('a')
            return '0'
    else:
        print('b')
        return '0'
        # 若用户名密码有一个不正确 return 0
    if len(n_password) > 10:
        return '0'
    print("valid")
    user_pwd[username] = n_password
    output = open("user_pwd.txt", "w+", encoding="UTF-8")
    for name in user_pwd:
        output.write("{} {}\n".format(name, user_pwd[name]))
    output.close()
    return '1'


@myWeb.route("/handle_order", methods=["post"])
def handle_order():
    global user_pwd
    global user_holding
    global market_price
    global market_price_queue
    global buy_order
    global sell_order
    global order_cnt
    # user: username, pwd: password, quant: quantity, pri: price, odt: ordertype, Day : date
    username = request.form["user"]
    password = request.form["pwd"]

    # 防止有小伙子作弊
    if username in user_pwd:
        if user_pwd[username] != password:
            # 正确的用户名和错误的密码
            return '0'
    else:
        # 错误的用户名
        return '0'

    quantity = int(request.form["quant"])
    price = round(float(request.form["pri"]), 2)
    ordertype = request.form["odt"]  # "buy" or "sell"
    day = int(request.form["Day"])  # 12 13 14 15 16 17

    # 检查用户cash or 持仓
    if ordertype == "buy" and user_holding[username][0] < round(quantity * price, 3):
        return "-2"
    if ordertype == "sell" and user_holding[username][day - 12 + 1] < quantity:
        return "-2"

    # 检查同一用户订单数量
    ls = []
    if ordertype == "buy":
        ls = buy_order
    else:
        ls = sell_order
    
    cnt = 0
    for o in ls:
        if o[1] == username:
            cnt += 1
    if cnt >= 4:
        return '-1'


    order_cnt += 1  # 这个订单的编号
    # 确定是买还是卖

    if ordertype == "buy":
        if len(sell_order) != 0:
            # 如果是买，则把 该日 所有卖出订单价格由低到高排序
            ls_buy = []  # n * 6
            for o in sell_order:
                if o[2] == day:
                    ls_buy.append(o)
            ls_buy = sorted(ls_buy, key=lambda x: x[4])

            left_quant = quantity
            # orderID 0, username 1, day 2, quant 3, price 4, total 5
            # cash, share 1, share 2 ... share 5
            for i in range(len(ls_buy)):
                o = ls_buy[i]

                if price >= o[4]:  # 成交价为o[4]
                    actual_quant = min(left_quant, o[3])
                    # 实际成交额
                    actual_amount = round(actual_quant * o[4], 3)
                    # 检查双方股票和资金余额
                    if actual_quant <= user_holding[o[1]][day - 12 + 1] and user_holding[username][0] >= actual_amount:
                        
                        
                        # 处理订单余额
                        left_quant -= actual_quant
                        # 股票变动
                        user_holding[username][day - 12 + 1] += actual_quant
                        user_holding[o[1]][day - 12 + 1] -= actual_quant
                        # 资金变动
                        user_holding[username][0] -= actual_amount
                        user_holding[username][0] = round(user_holding[username][0], 4)
                        user_holding[o[1]][0] += actual_amount
                        user_holding[o[1]][0] = round(user_holding[o[1]][0], 4)
                        # 更新卖方订单
                        if actual_quant == o[3]:
                            del_order(o[0], "sell")
                        else:
                            o[3] -= actual_quant
                            o[5] = round(o[3] * o[4], 3)
                        

                        # 更新市场价格记录队列
                        if o[1] != username:
                            market_price_queue[day].append([actual_quant, actual_amount])
                        # 若全部买到了，则终止
                        if left_quant == 0:
                            break
                else:
                    break
            # 若有剩余，添加新订单
            if left_quant > 0:
                add_order(order_cnt, username, day, left_quant,
                          price, round(price * left_quant, 3), "buy")

            # 更新市场价格
            update_market_price(day)
        else:
            add_order(order_cnt, username, day, quantity,
                      price, round(price * quantity, 3), "buy")

        # 如果是卖，则所有买的订单价格由高到低排序
    else:
        if len(buy_order) != 0:
            # 遍历订单，每成交一单，则在 该日 的最近成交队列里加上一个订单，如果成交订单总数超过20个，则删掉旧订单
            ls_sell = []
            for o in buy_order:
                if o[2] == day:
                    ls_sell.append(o)
            ls_sell = sorted(ls_sell, key=lambda x: x[4], reverse=True)

            left_quant = quantity
            # orderID 0, username 1, day 2, quant 3, price 4, total 5
            # cash, share 1, share 2 ... share 5
            for i in range(len(ls_sell)):
                o = ls_sell[i]

                if price <= o[4]:  # 成交价为price
                    actual_quant = min(left_quant, o[3])
                    # 实际成交额
                    actual_amount = round(actual_quant * price, 3)

                    # 检查双方股票和资金余额
                    if actual_quant <= user_holding[username][day - 12 + 1] and user_holding[o[1]][0] >= actual_amount:
                        # 处理订单余额
                        left_quant -= actual_quant
                        # 股票变动
                        user_holding[username][day - 12 + 1] -= actual_quant                      
                        user_holding[o[1]][day - 12 + 1] += actual_quant
                        # 资金变动
                        user_holding[username][0] += actual_amount
                        user_holding[username][0] = round(user_holding[username][0], 4)
                        user_holding[o[1]][0] -= actual_amount
                        user_holding[o[1]][0] = round(user_holding[o[1]][0], 4)
                        # 更新买方订单
                        if actual_quant == o[3]:
                            del_order(o[0], "buy")
                        else:
                            o[3] -= actual_quant
                            o[5] = round(o[3] * o[4], 3)
                    

                        # 更新市场价格记录队列
                        if o[1] != username:
                            market_price_queue[day].append([actual_quant, actual_amount])
                        # 若全部买到了，则终止
                        if left_quant == 0:
                            break
                else:
                    break
            # 若有剩余，添加新订单
            if left_quant > 0:
                add_order(order_cnt, username, day, left_quant,
                          price, round(price * left_quant, 3), "sell")

            # 更新市场价格
            update_market_price(day)

        else:
            add_order(order_cnt, username, day, quantity,
                      price, round(price * quantity, 3), "sell")
    store_data()
    return '1'


@myWeb.route("/handle_delete", methods=["post"])
def handle_delete():
    global buy_order
    global sell_order
    ID = request.form["orderID"]
    odt = request.form["ordertype"]
    flag = False
    ls = []
    if odt == "buy":
        ls = buy_order
    else:
        ls = sell_order
    for o in ls:
        if o[0] == int(ID):
            flag = True
            break

    if not flag:
        return '0'
    del_order(int(ID), odt)
    store_data()
    return '1'


if __name__ == "__main__":
    myWeb.run(host="0.0.0.0", port=80, debug=True)
