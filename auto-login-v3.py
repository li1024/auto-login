import datetime
import traceback
import sys
import threading
import os
import tkinter as tk
from tkinter import font
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from win10toast import ToastNotifier

# 函数用于创建并运行窗口
def create_window():
    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #ico_path = os.path.join(current_dir, "123.ico")
    # 创建主窗口
    root = tk.Tk()
    root.title("一键登录程序")
    # 设置窗口图标
    #root.iconbitmap(ico_path)
    # 设置窗口大小为宽400像素，高300像素
    root.geometry("400x300")
    # 创建自定义字体
    custom_font1 = font.Font(family="Helvetica", size=16)
    custom_font2 = font.Font(family="Arial", size=20)
    custom_font3 = font.Font(family="Arial", size=20)
    # 创建Label并设置字体大小和换行
    label_text1 = "程序正在运行       "
    label_text2 = "关闭程序可自动关闭浏览器"
    label_text3 = "打不开页面请联系作者"
    label1 = tk.Label(root, text=label_text1, font=custom_font1, wraplength=150)
    label1.pack()
    # 创建空的标签作为间隔
    spacer = tk.Label(root, text="", height=1)
    spacer.pack()
    label2 = tk.Label(root, text=label_text2, font=custom_font2, fg="blue")
    label2.pack()
    spacer = tk.Label(root, text="", height=1)
    spacer.pack()
    label3 = tk.Label(root, text=label_text3, font=custom_font3)
    label3.pack()
    # 添加按钮
    #button = tk.Button(root, text="点击这里", command=lambda: print("按钮被点击了"))
    #button.pack()
    # 定义关闭窗口时执行的函数
    def on_closing():
        root.destroy()  # 关闭窗口
        root.quit()     # 停止mainloop()
        driver.quit()
        sys.exit()      # 终止脚本进程
    # 绑定关闭窗口事件
    root.protocol("WM_DELETE_WINDOW", on_closing)
    # 运行窗口
    root.mainloop()

# 为了提高安全性，从文件读取用户名和密码
def read_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "info.txt")
    with open(file_path, 'r') as file:
        # 读取第一行赋给username
        username = file.readline().strip()
        # 读取第二行赋给password
        password = file.readline().strip()
        # 读取url
        url = file.readline().strip()
    return username, password, url

# 初始化Edge选项
edge_options = Options()

# 添加配置项以排除日志输出
edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 初始化 Edge 浏览器
driver = webdriver.Edge(options=edge_options)

def input_credentials(username, password):
    """输入用户名和密码"""
    message = "无法定位用户名或密码输入框标签"
    try:
        username_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "inputEmail3"))
        )
        password_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "inputPassword3"))
        )
        username_element.send_keys(username)
        password_element.send_keys(password)
    except Exception as e:
        log_exception(e)
        show_error_notification(message)
        driver.quit()  # 在异常发生时关闭浏览器
        sys.exit(1)  # 传入一个非零的退出码，表示异常终止

def handle_captcha():
    """处理验证码"""
    message = "无法定位验证码标签或输入框"
    try:
        # 这里假设我们可以通过某种方式（比如自动化点击）来触发验证码刷新
        # 并且假设getElementById返回的元素包含了验证码文本
        captcha_element = driver.execute_script("return document.getElementById('checkCode')")
        captcha_text = captcha_element.text
        captcha_input = driver.find_element(By.ID, "checkCodeInput")
        captcha_input.send_keys(captcha_text)
    except Exception as e:
        log_exception(e)
        show_error_notification(message)
        driver.quit()  # 在异常发生时关闭浏览器
        sys.exit(1)  # 传入一个非零的退出码，表示异常终止

def submit_form():
    """提交表单"""
    message = "无法定位确定按钮"
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login_button"))
        )
        submit_button.click()
    except Exception as e:
        log_exception(e)
        show_error_notification(message)
        driver.quit()  # 在异常发生时关闭浏览器
        sys.exit(1)  # 传入一个非零的退出码，表示异常终止

def show_error_notification(message):
    """显示错误通知到Windows桌面,并引导查看日志"""
    error_message = f"请查看错误日志了解详细信息: {message}"
    toaster = ToastNotifier()
    toaster.show_toast(
        "程序异常",
        f"发生错误: {error_message}",
        duration=30,  # 通知持续时间，默认10秒
        icon_path=None  # 可以指定图标路径
    )

def log_exception(exception):
    """记录异常到日志文件"""
    with open("error_log.txt", "a") as log_file:
        log_file.write("Error occurred at {}\n".format(datetime.datetime.now()))
        log_file.write("Exception details:\n")
        log_file.write(str(exception))
        log_file.write("\nTraceback:\n")
        log_file.write(traceback.format_exc())
        log_file.write("\n-------------------------\n")

# 调用函数以执行相应操作
def main():
    # 创建并启动窗口线程
    window_thread = threading.Thread(target=create_window)
    window_thread.start()
    username, password, url = read_config()
    # 打开网站
    driver.get(url)
    # 将浏览器窗口最大化
    driver.maximize_window()
    input_credentials(username, password)
    handle_captcha()
    submit_form()
    #input("按任意键退出...")

if __name__ == "__main__":
    main()
