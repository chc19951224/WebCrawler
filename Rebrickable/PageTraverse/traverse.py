# ===自定義文件===#
from EventHandler import DriverManager, SoupManager, SecondTabHandler, ThirdTabHandler
# ===功能模組===#
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time

# ==================== 控制登入 ====================
class StartPage:
    def __init__(self):
        """=== 構造函數 ==="""
        self.driver = DriverManager.get_driver()

    def load_page(self, url):
        """=== 加載第1頁 ==="""
        self.driver.get(url)
        self.driver.implicitly_wait(5)  # 智能等待5秒，若完成加載則立刻結束等待

    def login(self):
        """=== 動態控制 ==="""
        try:
            self.driver.maximize_window()  # 主窗口最大化
            time.sleep(2)  # 停止2秒

            # 定位到首頁登入的按鈕
            login = self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div/ul[1]/li[2]/a")
            login.click()  # 點選按鈕
            time.sleep(1)

            # 定位到賬號和密碼的輸入框
            username = self.driver.find_element(By.XPATH,
                                                "/html/body/div/div[3]/div/div/div/form/fieldset/div[1]/div/div/input")
            username.click()
            username.send_keys("pradochang")  # 輸入賬號
            time.sleep(1)
            password = self.driver.find_element(By.XPATH,
                                                "/html/body/div/div[3]/div/div/div/form/fieldset/div[2]/div/div/input")
            password.click()
            password.send_keys("Zjzxd@3202")  # 輸入密碼
            time.sleep(1)

            enter = self.driver.find_element(By.XPATH, "/html/body/div/div[3]/div/div/div/form/footer/button")
            enter.click()
            time.sleep(1)

            # 定位到過濾器
            web_filter = self.driver.find_element(By.XPATH,
                                                  "/html/body/div/div[3]/div[2]/div[4]/div/div[2]/div[1]/span[6]")
            web_filter.click()
            time.sleep(2)

            # 滑鼠滾輪向下移動
            self.driver.execute_script("window.scrollTo(0,500)")
            time.sleep(2)

        except Exception as e:
            print("登入失敗！原因：", e)
        finally:
            print("網頁訪問結束~")

# ==================== 獲取網址 ====================
class SubHref:
    def __init__(self):
        """=== 構造函數 ==="""
        self.driver = DriverManager.get_driver()
        self.soup = SoupManager.get_soup()
        self.subpage_list = []

    def find_urls(self):
        """=== 取得第2頁網址 ==="""
        # 定位到<a>標簽的父容器
        a_container = self.driver.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div[4]/div/div[2]/div[2]")
        a_tags = a_container.find_elements(By.TAG_NAME, "a")  # 定位到所有<a>標簽

        try:
            for row in a_tags:  # 遍歷所有的<a>標簽
                href = row.get_attribute("href")  # 從"href"屬性中，獲取網址
                self.subpage_list.append(href)  # 將第2頁網址加入串列
        except Exception as e:
            print("第 2 頁網址獲取失敗！原因：", e)

    def get_urls(self):
        """=== 返回第2頁網址 ==="""
        return self.subpage_list

# ==================== 銜接跳轉 ====================
class SubPage:
    def __init__(self, page2_urls):  # 收第2頁網址
        """=== 構造函數 ===="""
        self.driver = DriverManager.get_driver()
        self.page2_urls = page2_urls

    def start(self):
        """=== 加載第2頁 ==="""
        for url in self.page2_urls[:]:  # 遍歷訪問第2頁
            SecondTabHandler.open_tab(self.driver, url)  # 打開第2頁
            # --- 找網址 ---#
            third_href = ThirdHref()
            third_href.start()  # 啓動
            SecondTabHandler.close_tab(self.driver)  # 關閉第2頁

            """=== 重置作業 ==="""
            from main import Counter
            Counter.reset_download()
            Counter.reset_page()
            Counter.add_section()

# ==================== 頁碼判斷，爬蟲任務 ====================
class ThirdHref:
    def __init__(self):
        """=== 構造函數 ==="""
        self.driver = DriverManager.get_driver()
        self.sub_url = None  # 第2頁完整url，初始值設空，等待拼接
        self.prefix_url = self.driver.current_url  # 第2頁url前綴，是第2頁串列的網址
        self.page3_urls = []

    def start(self):
        """=== 開始 ==="""
        from main import GlobalVar, Counter
        from main import Scrape
        from main import Value
        scraper = Scrape()
        value = Value()
        """=== 清空串列 ==="""
        self.page3_urls.clear()  # 每進入下一次分類前，需要清空串列

        """=== 計算頁數，最小數量&最小數量 ==="""
        min_value = value.min_value(self.driver)  # 找到最小數量
        max_value = value.max_value(self.driver)  # 找到最大數量
        print(min_value, " / ", max_value)
        pagination = value.calculate_pagination(min_value, max_value)  # 判斷類別對應的頁碼
        print(f"===== 這個類別的總頁數是 {pagination} 頁! =====")

        """=== 單頁結構 ==="""
        self.append_urls()
        for url in self.page3_urls[:]:
            ThirdTabHandler.open_tab(self.driver, url)  # 打開第3頁
            # --- 爬數據 ---#
            scraper.scrape_name()
            scraper.scrape_table()
            scraper.scrape_img()
            time.sleep(1)
            scraper.data_cleaning()
            ThirdTabHandler.close_tab(self.driver)  # 關閉第3頁

            Counter.add_download()  # ===下載次數 +1===#
            print("目前下載次數：", GlobalVar.download)
        self.page3_urls.clear()  # 下載完一頁后清空

        """=== 多頁結構 ==="""
        # 如果(下載次數 <= 最大數量)
        while (GlobalVar.download < max_value) and (pagination > 1):
            # 如果(下載次數 % 100) == 1，説明達到翻頁的條件
            if GlobalVar.download % 100 == 1:
                Counter.add_page()  # ===頁碼+1===#
                print(f"===== 目前正在下載第{GlobalVar.page_url}頁 / 總共是 {pagination} 頁！！！ =====")
                self.load_next()  # 翻到下一頁

                self.append_urls()
                for url in self.page3_urls[:]:
                    ThirdTabHandler.open_tab(self.driver, url)  # 打開第3頁
                    # --- 爬數據 ---#
                    scraper.scrape_name()
                    scraper.scrape_table()
                    scraper.scrape_img()
                    time.sleep(1)
                    scraper.data_cleaning()
                    ThirdTabHandler.close_tab(self.driver)  # 關閉第3頁

                    Counter.add_download()  # ===下載次數 +1===#
                    print("目前下載次數：", GlobalVar.download)
                self.page3_urls.clear()  # 下載完一頁后清空

                # 如果(下載次數 % 100) == 最大數量，説明是最後一頁
                if GlobalVar.download == max_value:
                    Counter.reset_download()  # 重置下載數量
                    print("此類下載完畢~")
            else:
                self.append_urls()
                for url in self.page3_urls[:]:
                    ThirdTabHandler.open_tab(self.driver, url)  # 打開第3頁
                    # --- 爬數據 ---#
                    scraper.scrape_name()
                    scraper.scrape_table()
                    scraper.scrape_img()
                    time.sleep(1)
                    scraper.data_cleaning()
                    ThirdTabHandler.close_tab(self.driver)  # 關閉第3頁

                    Counter.add_download()  # ===下載次數 +1===#
                    print("目前下載次數：", GlobalVar.download)
                self.page3_urls.clear()  # 下載完一頁后清空

                # 如果(下載次數 % 100) == 最大數量，説明是最後一頁
                if GlobalVar.download == max_value:
                    Counter.reset_download()  # 重置下載數量
                    print("此類下載完畢~")

    def get_page3_urls(self):
        """=== 返回第3頁網址 ==="""
        return self.page3_urls

    def load_next(self):
        from main import GlobalVar
        self.sub_url = urljoin(self.prefix_url, f"?page={GlobalVar.page_url}")
        self.driver.get(self.sub_url)  # 加載下一頁
        self.driver.implicitly_wait(5)

    def append_urls(self):
        container = self.driver.find_element(By.XPATH,
                                             "/html/body/div/div[3]/div[2]/div[4]/div/div[2]/div/div[4]")
        a_tags = container.find_elements(By.TAG_NAME, "a")
        for row in a_tags:
            href = row.get_attribute("href")
            self.page3_urls.append(href)
