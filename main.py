# 설정 파일을 불러오기
from CrawlingConfig import *

import requests
from bs4 import BeautifulSoup as bs
import re
import time
import pandas as pd

TX_List = []
TX_Status_List = []
From_List = []
From_Tag_List = []
To_List = []
To_Tag_List = []

base_Url = "https://etherscan.io/txs"
index = 1
max_Index = 4


class First_Row(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Empty_Data(Exception):
    def __init(self, msg):
        self.msg = msg

    def __str(self):
        return self.msg


# 이모지 제거함수
def remove_emoji(inputData):
    return inputData.encode('utf-8', 'ignore').decode('utf-8')


def refine_crawling_data(page):
    i = 0
    soup = bs(page, "html.parser")
    # tr Tag는 Etherscan에서 표 하나의 열을 나타낸다.
    tr_list = soup.select('tr')[1:]
    for tr in tr_list:
        # Debugging
        i += 1

        try:
            # tx_data = re.search(
            #     r'(<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s)?<span class="hash-tag text-truncate">\s?<a class=[\w\s!@#$%%^&*()_,.>/\"\'+:;=-]*<\/a>',
            #     page_text)
            # 만약에 표의 구성 정보가 들어왔다면 건너뛰는 연산을 진행한다.
            # 그러나 실제 동작하지 않을 것이지만 예방 차원에서 확인
            first_row_checker = tr.find('td')
            if first_row_checker is None:
                raise First_Row("페이지의 데이터 표의 첫번째 행입니다.")

            # 데이터가 있는 행일 경우
            else:
                print(tr)
                print("tr 끝")
                # TX Address (정규표현식 --> bs4)
                # tx_address = re.search(r'tx[\w/]*', tx_data.group()).group().replace('tx/', '')
                tx_address = tr.find('a').text
                if tx_address is None:
                    raise Empty_Data(tr + "에서 TX Address를 찾지 못했습니다.")
                print(tx_address)

                # Status Data를 확인하기 위한 정규 표현식
                # check_status = re.search(r'<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s', tx_data.group())
                check_status = tr.find('span', {'class': 'text-danger'})
                if check_status is None or check_status['data-bs-title'] is None:
                    refine_check_status = "None"
                else:
                    refine_check_status = check_status['data-bs-title']

                print(refine_check_status)
                continue

                # From, To Address
                # address_iter = re.finditer(r'<a href="\/address[\w/]*"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/a>', page_text)
                # address_from = address_iter.__next__()
                # address_to = address_iter.__next__()
                address_list = tr.find('a', {'class': 'js-clipboard link-secondary'})['data-bs-title']

                if address_from or address_to is None:
                    raise Empty_Data(tx_address+"의 From, To address가 정상적으로 인식되지 않았습니다")

                refine_address_from =  re.search(r'address[\w/]*', address_from.group()).group().replace('address/', '')
                check_address_from_tag = re.search(r'data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*', address_from.group())\
                    .group().replace('data-bs-title="', '')
                refine_address_from_tag = ""

                refine_address_to =  re.search(r'address[\w/]*', address_to.group()).group().replace('address/', '')
                check_address_to_tag = re.search(r'data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*',
                                                   address_to.group()) \
                    .group().replace('data-bs-title="', '')
                refine_address_to_tag = ""

                if check_address_from_tag != refine_address_from:
                    refine_address_from_tag.join(check_address_from_tag)
                else:
                    refine_address_from_tag.join("Nope")

                if check_address_to_tag != refine_address_to:
                    refine_address_to_tag.join(check_address_to_tag)
                else:
                    refine_address_to_tag.join("Nope")

                TX_List.append(tx_address)
                TX_Status_List.append()
                From_List.append(refine_address_from)
                From_Tag_List.append(refine_address_from_tag)
                To_List.append(refine_address_to)
                To_Tag_List.append(refine_address_to_tag)
                print("데이터 저장완료")

        except First_Row as FR:
            print(FR)
            continue

        except Empty_Data as ED:
            print(ED)
            continue


if __name__ == "__main__":
    # 원하는 페이지까지 데이터를 받기
    for page in range(1):
        # Base_Url에서 Data수와 page 갯수를 넘겨주기 위한 파라미터
        params = \
            {
                'ps': '100',
                'p': index,
            }

        try:
            # response = requests.get(base_Url, params=params, cookies=cookies, headers=headers, data=data)
            # text = remove_emoji(response.text)
            #
            # # Debugging
            # test_html = open("index.html", "w", encoding='utf8')
            # test_html.write(text)
            # test_html.close()
            text = open("TXntest.html","r")

            refine_crawling_data(text)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting : ", err)
            time.sleep(20)
            continue

        # 3페이지 이후 5초 휴식
        # if page % 3 == 0:
        #     time.sleep(5)
        #     print("Sleep 5 sec")
        # print("Current Page is " + str(page) + " Done")
        index += 1

    Ethereum_CSV = pd.DataFrame(
        {
            'TXN': TX_List,
            'TX_STATUS': TX_Status_List,
            'From': From_List,
            'From_TAG': From_Tag_List,
            'To': To_List,
            'TO_TAG': To_Tag_List
        }
    )
    Ethereum_CSV.to_csv('./Ethereum_Transaction.csv', index=True)



