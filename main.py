# 설정 파일을 불러오기
from CrawlingConfig import *
from EthExceptions import *

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
max_Index = 5000


# error가 발생하는 데이터만 저장하는 함수
def sava_error_data(error_data):
    test_html = open("error.html", "a", encoding='utf8')
    test_html.write(error_data)
    test_html.close()


def print_all_data_count():
    print("TXN: " + str(len(TX_List)) + " TX_Status: " + str(len(TX_Status_List)) + " From: " + str(len(From_List)) + " From_Tags: " + str(len(From_Tag_List)) + " To: " + str(len(To_List)) + " To_Tags: " + str(len(To_Tag_List)))

# 이모지 제거함수
def remove_emoji(inputData):
    return inputData.encode('utf-8', 'ignore').decode('utf-8')


def refine_crawling_data(page):
    global refine_address_from, refine_address_from_tag, refine_address_to, refine_address_to_tag

    soup = bs(page, "html.parser")
    # tr Tag는 Etherscan에서 표 하나의 열을 나타낸다.
    tr_list = soup.select('tr')[1:]

    for tr in tr_list:
        try:
            # 만약에 표의 구성 정보가 들어왔다면 건너뛰는 연산을 진행한다.
            # 그러나 실제 동작하지 않을 것이지만 예방 차원에서 확인
            first_row_checker = tr.find('td')
            if first_row_checker is None:
                raise First_Row("페이지의 데이터 표의 첫번째 행입니다.")

            # 데이터가 있는 행일 경우
            else:
                # TX Address
                tx_address = tr.find('a').text
                if tx_address is None:
                    raise Empty_Data(tr + "에서 TX Address를 찾지 못했습니다.")

                check_status = tr.find('span', {'class': 'text-danger'})
                if check_status is None or check_status['data-bs-title'] is None:
                    refine_check_status = "None"
                else:
                    refine_check_status = check_status['data-bs-title']

                # From, To Address
                address_list = tr.find_all('a', {'data-bs-html': 'true'})

                if len(address_list) != 2:
                    sava_error_data(str(tr))
                    raise Empty_Data(tx_address +"에 대한 From, To address를 긁지 못했습니다.")

                for address in address_list:
                    # From
                    if address_list.index(address) == 0:
                        refine_address_from = address['href'].replace('/address/','')
                        address_from_tag = address['data-bs-title']
                        refine_address_from_tag = re.sub(r'(<br\/>)?\([\w]*\)','', address_from_tag)
                        if refine_address_from_tag == refine_address_from:
                            refine_address_from_tag = "None"
                    # To
                    else:
                        refine_address_to = address['href'].replace('/address/', '')
                        address_to_tag = address['data-bs-title']
                        refine_address_to_tag = re.sub(r'(<br\/>)?\([\w]*\)','', address_to_tag)
                        if refine_address_to_tag == refine_address_to:
                            refine_address_to_tag = "None"

                TX_List.append(tx_address)
                TX_Status_List.append(refine_check_status)
                From_List.append(refine_address_from)
                From_Tag_List.append(refine_address_from_tag)
                To_List.append(refine_address_to)
                To_Tag_List.append(refine_address_to_tag)

        except First_Row as FR:
            print(FR)
            continue

        except Empty_Data as ED:
            print(ED)
            continue


if __name__ == "__main__":
    # 원하는 페이지까지 데이터를 받기
    for page in range(max_Index):
        before_count = [len(TX_List), len(TX_Status_List), len(From_List), len(From_Tag_List), len(To_List), len(To_Tag_List)]

        # Base_Url에서 Data수와 page 갯수를 넘겨주기 위한 파라미터
        params = \
            {
                'ps': '100',
                'p': index,
            }

        try:
            response = requests.get(base_Url, params=params, cookies=cookies, headers=headers, data=data)
            text = remove_emoji(response.text)

            # # Debugging
            # test_html = open("index.html", "w", encoding='utf8')
            # test_html.write(text)
            # test_html.close()
            refine_crawling_data(text)
            print(str(page)+" page가 완료되었습니다.")
            print_all_data_count()
            after_count = [len(TX_List), len(TX_Status_List), len(From_List), len(From_Tag_List), len(To_List), len(To_Tag_List)]
            if before_count == after_count:
                raise Refused_Connection("지나친 요청으로 인해 " + str(page)+" 페이지에 대한 요청이 거절되었습니다.")

        except requests.exceptions.ConnectionError as err:
            print("Error Connecting : ", err)
            time.sleep(10)
            continue
        except Refused_Connection as RC:
            print(RC)
            time.sleep(10)
            continue
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



