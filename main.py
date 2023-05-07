import os
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from dotenv import load_dotenv
import schedule
import time

disable_warnings(InsecureRequestWarning)


# LINEにバス時刻表のPDFのリンクを送信
def send_pdf_link(file_url, line_notify_token):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{file_url}'}
    # requests.post(line_notify_api, headers=headers, data=data)
    try:
        response = requests.post(line_notify_api, headers=headers, data=data)
        response.raise_for_status()
        # print(f"Sent PDF link to LINE: {file_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending PDF link to LINE: {str(e)}")


# シャトルバスの時刻表をダウンロード
def download_pdf_file(file_url, file_path, line_notify_token):
    try:
        send_pdf_link(file_url, line_notify_token)
        response = requests.get(file_url, verify=False)
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"Error downloading {os.path.basename(file_path)}: {str(e)}")
        return False


# downlaodディレクトリが存在しなかったら作成する
def download_dir_exit(download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)


def main():
    url = "https://www.chitose.ac.jp/info/access"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select('a[href*="/uploads/files/R5"]')

    # pdfのファイル名を変更 -> MMDD-MMDD.pdf
    pdf_files = [os.path.basename(link.get('href')).split('_')[-1].strip() for link in links]

    download_dir = "download"
    download_dir_exit(download_dir)
    
    load_dotenv()
    line_notify_token =  os.getenv('LINE_NOTIFY_TOKEN') 

    successful_downloads = 0
    for i, pdf_file in enumerate(pdf_files): 
        file_url = "https://www.chitose.ac.jp" + links[i].get('href')
        file_path = os.path.join(download_dir, pdf_file)
        if download_pdf_file(file_url, file_path, line_notify_token):
            successful_downloads += 1
    # print(f"{successful_downloads} PDF files downloaded successfully!")


if __name__ == '__main__':
    schedule.every().monday.at("10:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
#     main()
