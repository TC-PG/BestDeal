# chmod +x chromedriver
# sudo apt-get install -f
# sudo dpkg -i google-chrome-stable_current_amd64.deb

import os
import time
from cs50 import SQL
from flask import Flask, render_template, redirect, jsonify, request, flash, session
from flask_session import Session
from tempfile import mkdtemp
from flask_bcrypt import Bcrypt
from helpers import login_required

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import requests
import json

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(16)
db = SQL("sqlite:///final.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['JSON_AS_ASCII'] = False

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

errorMessage = {
    "message": None
}

successMessage = {
    "message": None
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    account = request.form.get("account")
    password = request.form.get("password")

    if not account or not password:
        flash('請輸入帳號密碼')
        return render_template("index.html")

    user = db.execute("select * from user where account= :account", account = account)

    if not user:
        flash('帳號或密碼錯誤')
        return render_template("index.html")
    else:
        hashPwd = user[0]['password']
        try:
            pwdCheck = bcrypt.check_password_hash(hashPwd, password)
        except ValueError:
            flash('發生錯誤')
            return render_template("index.html")

    if not pwdCheck:
        flash('帳號或密碼錯誤')
        return render_template("index.html")

    session['user'] = account
    session['user_id'] = user[0]['id']
    return redirect("/")


@app.route("/signup", methods=["post"])
def register():
    account = request.form.get("account")
    password = request.form.get("password")
    if not account or not password:
        flash('請輸入帳號密碼')
        return render_template("index.html")

    hashPwd = bcrypt.generate_password_hash(password).decode('utf-8')
    user = db.execute("select * from user where account= :account", account = account)
    if not user:
        user_id = db.execute("insert into user(account, password) values(:account,:password)", account = account, password = hashPwd)
        session['user'] = account
        session['user_id'] = user_id
    else:
        flash('用戶已存在')
        return render_template("index.html")


    return redirect("/")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    return redirect("/")


@app.route("/search")
def search():

    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking");
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("window-size=1024,768")
    # Add sandbox mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')

    products = []
    name = request.args.get("product")
    if name == "":
        errorMessage["message"] = "無法查詢，請輸入商品名稱"
        return jsonify(errorMessage), 500

    select = request.args.get("select")

    if select == "Shopee":
        with webdriver.Chrome("./chromedriver", chrome_options=chrome_options) as driver:
            print('begin web crawling')
            driver.get("https://shopee.tw/search?keyword=" + name)
            # sleep 3s for page loading
            time.sleep(3)
          # Scroll few times to load all items
            for x in range(5):
                driver.execute_script("window.scrollBy(0,300)")
                time.sleep(0.1)

            # Get all links (without clicking)
            all_links = driver.find_elements_by_xpath('//a[@data-sqe="link"]')
            for item in all_links:
                url = item.get_attribute('href')
                productNameElement = item.find_element_by_class_name('_1NoI8_')
                img = item.find_element_by_tag_name('img')
                imgsrc = img.get_attribute('src')
                price = item.find_elements_by_class_name('_341bF0')
                productName = productNameElement.text
                if len(price) == 2:
                    productPrice = "${} - ${}".format(price[0].text,price[1].text)
                else:
                    productPrice = "${}".format(price[0].text)

                products.append(
                        {
                            "name":productName,
                            "url":url,
                            "src":imgsrc,
                            "price":productPrice
                        }
                    )

    elif select == "PCHome":
        url = "https://ecshwebc.pchome.com.tw/search/v3.3/all/results?q={}&page=1&sort=sale/dc".format(name)
        response = requests.get(url)
        data = json.loads(response.text)
        prods = data["prods"]
        for product in prods:
            url = "https://24h.pchome.com.tw/prod/{}".format(product["Id"])
            imgsrc = "https://b.ecimg.tw/{}".format(product["picB"])
            productName = product["name"]
            productPrice = "${}".format(product["price"])
            products.append(
                    {
                        "name":productName,
                        "url":url,
                        "src":imgsrc,
                        "price":productPrice
                    }
                )
    else:
        errorMessage["message"] = "無法查詢"
        return jsonify(errorMessage), 500


    return jsonify(products), 200



@app.route("/save", methods=["post"])
@login_required
def save():
    data = request.get_json()

    if data:
        db.execute("insert into favorites(image, productName, price, url, user_id) values(:image, :productName, :price, :url, :user_id)", image = data['src'], productName = data['productName'], price = data['price'], url = data['url'], user_id= session['user_id'])
        successMessage["message"] = '儲存成功'
        return jsonify(successMessage), 200

    errorMessage["message"] = '發生錯誤，無法儲存'
    return jsonify(errorMessage), 500


@app.route("/favorites")
def getFavorites():
    if not session:
        return redirect("/")

    rows = db.execute("select * from favorites where user_id = :user_id", user_id = session["user_id"])

    items = []
    for row in rows:
        items.append(
                {
                    "id": row["id"],
                    "image": row["image"],
                    "productName": row["productName"],
                    "price": row["price"],
                    "url": row["url"]
                }

            )

    return render_template("favorites.html", favorites = items)

@app.route("/delete", methods=["post"])
@login_required
def delete():
    id = request.get_json()

    if not id:
        errorMessage["message"] = "發生錯誤，id未知"
        return jsonify(errorMessage),500

    db.execute("delete from favorites where id=:id", id= id)

    successMessage["message"] = "刪除成功"
    return jsonify(successMessage),200