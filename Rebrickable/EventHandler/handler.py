from selenium import webdriver
from bs4 import BeautifulSoup


class DriverManager:
    """單例模式，作爲全局唯一對象"""
    driver_instance = None  # 類變量，用來表示driver對象，默認為空值

    @classmethod  # 類方法，不允許傳遞參數
    def get_driver(cls):
        if cls.driver_instance is None:  # 若driver變量沒有對象時
            cls.driver_instance = webdriver.Chrome()  # 打開Chrome瀏覽器
        return cls.driver_instance  # 返回自身對象


class SoupManager:
    """單例模式，作爲全局唯一對象"""
    soup_instance = None  # 類變量，用來表示soup對象，默認為空值

    @classmethod  # 類方法，不允許傳遞參數
    def get_soup(cls):
        driver = DriverManager.get_driver()  # 調用driver對象
        if cls.soup_instance is None:  # 若soup變量沒有對象時
            cls.soup_instance = BeautifulSoup(driver.page_source, "lxml")  # 用LXML解析器解析網頁原始碼
        return cls.soup_instance  # 返回自身對象


class SecondTabHandler:
    @staticmethod
    def open_tab(driver, url):
        """=== 打開分頁 ==="""
        driver.execute_script("window.open('')")  # 打開第2頁
        driver.switch_to.window(driver.window_handles[-1])  # 切換到第2頁
        driver.get(url)  # 獲取網址
        driver.implicitly_wait(5)

    @staticmethod
    def close_tab(driver):
        """=== 關閉分頁 ==="""
        driver.close()  # 關閉第2頁
        driver.switch_to.window(driver.window_handles[0])  # 切換到第1頁


class ThirdTabHandler:
    @staticmethod
    def open_tab(driver, url):
        """=== 打開分頁 ==="""
        driver.execute_script("window.open('')")  # 打開第3頁
        driver.switch_to.window(driver.window_handles[-1])  # 切換到第3頁
        driver.get(url)  # 獲取網址
        driver.implicitly_wait(5)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")  # 滾動到底部

    @staticmethod
    def close_tab(driver):
        """=== 關閉分頁 ==="""
        driver.close()  # 關閉第3頁
        driver.switch_to.window(driver.window_handles[1])  # 切換到第2頁
