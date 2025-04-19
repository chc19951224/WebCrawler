# ===自定義文件===#
from PageTraverse import StartPage, SubHref, SubPage
from EventHandler import DriverManager, SoupManager
# ===功能模組===#
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from io import StringIO
import pandas as pd
import os

# ==================== 爬蟲任務 ====================
class Scrape:
    def __init__(self):
        self.driver = DriverManager.get_driver()
        self.table = None
        self.item_name = None
        self.data_frame = None

    def scrape_name(self):
        # 定位到<h2>標簽
        h2_tag = self.driver.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div/div[2]/h2")
        self.item_name = h2_tag.text  # 獲取型號名稱

    def scrape_table(self):
        # 定位到<table>的父容器
        parent = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "table-scrollable")))
        # 定位並等待<table>標簽出現
        table = WebDriverWait(self.driver, 10).until(lambda driver: parent.find_element(By.TAG_NAME, "table"))
        self.table = table

        # 獲取<table>的HTML
        table_html = self.table.get_attribute("outerHTML")
        # 先將臨時文件寫進内存緩衝區，再解析成DataFrame
        self.data_frame = pd.read_html(StringIO(table_html))[0]

    def scrape_img(self):
        # 定位到所有的<img>標簽
        img_tags = self.table.find_elements(By.TAG_NAME, "img")
        for row in img_tags:
            img_urls = row.get_attribute("data-src")
            self.data_frame["圖片"] = img_urls

    def data_cleaning(self):
        self.data_frame.rename(columns={"Color": "顔色",
                                        "Element": "型號",
                                        "From": "起始年份",
                                        "To": "終止年份",
                                        "Avg Price": "平均價格"}, inplace=True)

        # 彈出"ImgUrls"欄位的對象
        img_urls_series = self.data_frame.pop("圖片")
        # 在最前面欄位索引的位置，插入欄位
        self.data_frame.insert(0, "圖片", img_urls_series)
        # 在原dataframe中,刪除指定欄位
        self.data_frame.drop(columns=["Unnamed: 0",
                                      "Set Parts",
                                      "Sets",
                                      "MOC Parts",
                                      "MOCs",
                                      "Owned"], inplace=True)
        try:
            """=== 取得文件串列 ==="""
            make_folder = Folder()  # 實例化
            make_folder.folder_generate()  # 生成文件夾
            category_folders = make_folder.get_folder_list()  # 取得文件夾串列
            """=== 控制存放路徑 ==="""
            folder_index = 0  # 初始存放文件夾的索引值
            update_index = GlobalVar.section  # 取得章節訪問次數，作爲進入下一類別文件夾的依據
            # (章節爬蟲次數 > 文件夾串列[0])，説明第1章節已經爬取結束，需要到下一個文件夾
            if folder_index < update_index:
                folder_index = update_index

            # 拼接csv文件路徑
            save_to_url = category_folders[folder_index] + "/" + self.item_name + ".csv"
            # 將csv文件存檔到子文件夾，去除索引值，設置為中文編碼
            self.data_frame.to_csv(save_to_url, index=False, encoding="utf-8-sig")
            print(f"{self.item_name}.csv文件成功保存到{category_folders[folder_index]}~")

        except Exception as e:
            print(f"{self.item_name}.csv文件下載失敗！原因：", e)

# ==================== 文件夾生成 ====================
class Folder:
    def __init__(self):
        self.driver = DriverManager.get_driver()
        self.soup = SoupManager.get_soup()
        self.complete_dir = None
        self.suffix_dir = None
        self.prefix_dir = r"C:/Users/PradoChang/Desktop/LEGO"  # 主目錄路徑
        self.folder_list = []  # 創建串列，存放所有類別完整路徑的文件夾

    def folder_generate(self):
        """=== 創建文件夾 ==="""
        # 定位到<h5>標簽的父容器
        parent = self.soup.select_one("div", {"class": "row row-condensed"})
        # # 定位到所有的<h5>標簽
        h5_tags = parent.select("h5", {"class": "text-center"})

        # 取得第2頁的標題
        for row in h5_tags:
            sub_title = row.getText()  # 依序取得<h5>標簽中的標題文字
            # 將第2頁的標題，賦值爲文件夾的名稱，如果名稱含有“/”符號，則以“&”取代
            self.suffix_dir = sub_title.replace("/", "&")
            self.complete_dir = os.path.join(self.prefix_dir + "/" + self.suffix_dir)  # 拼接文件夾的完整路徑
            self.folder_list.append(self.complete_dir)  # 將所有完整文件夾路徑加入串列
        # 篩選元素
        self.folder_list = self.folder_list[6:]  # 刪除前6個元素
        # 創建文件夾
        for folder_name in self.folder_list:
            try:
                if not os.path.exists(folder_name):  # 如果文件夾不存在
                    os.mkdir(folder_name)  # 創建新的文件夾
            except Exception as e:
                print(f"{folder_name} 文件夾創建失敗！原因：", e)

    def get_folder_list(self):
        return self.folder_list

# ==================== 頁碼判斷 ====================
class Value:
    @staticmethod
    def min_value(driver):
        em_tag = driver.find_element(By.TAG_NAME, "em")
        min_value = int(em_tag.text.split(" ")[1])
        return min_value

    @staticmethod
    def max_value(driver):
        em_tag = driver.find_element(By.TAG_NAME, "em")  # 定位到<em>標簽
        # 從<em>標簽中，獲取字串，字串以空格進行分割；獲取第3個字串(索引值從0開始)
        max_value = em_tag.text.split(" ")[3]
        if max_value == "1,000":
            max_value = int(max_value.replace(',', ''))  # 移除逗號后轉爲整數
            return max_value
        return int(max_value)

    @staticmethod
    def calculate_pagination(min_value, max_value):
        if max_value == 1000:  # 如果總共是10頁
            pagination = (max_value // min_value)  # 除數 整除 被除數
            return pagination
        else:  # 如果總共不是10頁
            pagination = (max_value // min_value) + 1  # 除數 整除 被除數 +1
            return pagination

# ==================== 全局變量控制 ====================
class Counter:
    @staticmethod
    def add_download():
        GlobalVar.download += 1

    @staticmethod
    def add_page():
        """=== 增加頁碼 ==="""
        GlobalVar.page_url += 1

    @staticmethod
    def add_section():
        """=== 增加章節 ==="""
        GlobalVar.section += 1

    @staticmethod
    def reset_download():
        """=== 重置頁碼 ==="""
        GlobalVar.download = 1

    @staticmethod
    def reset_page():
        """=== 重置頁碼 ==="""
        GlobalVar.page_url = 1


# ==================== 全局變量宣告 ====================
class GlobalVar:
    section = 0  # 類別數量的起始值為0，因爲爬取第1個類別時，章節還未完成
    download = 1  # 下載次數起始值為1，因爲串列索引從0開始
    page_url = 1  # 頁碼的起始值為1，因爲網頁從第1頁開始


def main():
    # === 第1頁 ===#
    start_page = StartPage()
    start_page.load_page("https://rebrickable.com/parts/")
    start_page.login()

    # --- 找網址 ---#
    sub_href = SubHref()
    sub_href.find_urls()  # 找第 2 頁網址
    page2_urls = sub_href.get_urls()  # 取第 2 頁網址

    # === 第2頁 ===#
    subpage = SubPage(page2_urls)  # 丟第 2 頁網址
    subpage.start()

if __name__ == "__main__":
    main()

# [Hint]如果任務中斷，需要改變指定的代碼：

# 1、起始網址
# class Subpage -> for url in self.page2_url[n-1:]

# 2、文件路徑
# class Scrape -> folder_index = n-1
# class GlobalVar -> section = n-1
