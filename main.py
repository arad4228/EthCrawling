# 설정 파일을 불러오기
from CrawlingConfig import cookies
from CrawlingConfig import headers
from CrawlingConfig import params
from CrawlingConfig import data

import pandas as pd
import requests
import re
import time


TX_List = []
TX_Status_List = []
From_List = []
From_Tag_List = []
To_List = []
To_Tag_List = []

base_Url = "https://etherscan.io/txs"
index = 1
max_Index = 5000

# 50 to 100 Crawling
response = requests.get(base_Url, params=params, cookies=cookies, headers=headers, data=data)

for page in range(5):
    # html 파일 받기
    response = requests.get(base_Url, params=params, cookies=cookies, headers=headers)
    text = response.text.replace('​','')

    # 파일 단위 저장기능(for Debug)
    # test_html = open("index.html","w", encoding='utf8')
    # test_html.write(text)
    # test_html.close()

    element = 0

    # 정규식
    # 최초: (<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s)?<span class="hash-tag text-truncate">\s<a href="\/tx[\w/]*"[\w\s!@#$%%^&*()_,.>/\"\'+:;=-]*<\/a>
    # 수정: (<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s)?<span class="hash-tag text-truncate">\s+<a href="\/tx[\w/]*"[\w\s!@#$%%^&*()_,.>/\"\'+:;=-]*<\/a>
    tx_List = re.finditer(
        r'(<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s)?<span class="hash-tag text-truncate">\s+<a href="\/tx[\w/]*"[\w\s!@#$%%^&*()_,.>/\"\'+:;=-]*<\/a>',
    text)

    # TX
    for tx in tx_List:
        # group를 통해서 찾은 결과 접근
        matched_Str = tx.group()
        #  + " find: " + matched_Str
        print("num: " + str(element))

        find_TxAddress = re.search(r'tx[\w/]*', matched_Str).group().replace('tx/','')
        check_Status = re.search(r'<span class="text-danger"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/span>\s', matched_Str)

        TX_List.append(find_TxAddress)

        if check_Status is None:
            TX_Status_List.append("None")
        # 정규식
        # data-bs-title="[\w\s!@#$%%^&*()_,.<>/\'+:;=-]*" : 에러 문구 추출
        else:
            refine_Str = re.search(r'data-bs-title="[\w\s!@#$%%^&*()_,.<>/\'+:;=-]*"', check_Status.group()).group().replace('data-bs-title="','')
            refine_Str = refine_Str.replace('"','')
            TX_Status_List.append(refine_Str)
        element = element + 1


    # 정규식
    # <a href="\/address\/[\w]*\" class=\"[\w\s-]*" [\w\s-=":]*(<br\/>)?(\([\w]*\))?">[\s\w:.?!@#$%^&*()_+=+/*-]*
    # <a href="\/address[\w/]*" class="[[\w\s-]*]?" [\w\s=":-]*(<br\/>\([\w]*\))?">
    # 최종: <a href="\/address[\w/]*" class="(hash-tag text-truncate)?"[\s\w=:"!@#$%^&*_=+~`.()-]*(<br\/>\(\w*\)")?>
    # 최종: <a href="\/address[\w/]*" class="(hash-tag text-truncate)?"[\s\w=:"!@#$%^&*_=+~`.()-]*(<br\/>\(\w*\)")?
    # 위 정규식의 문제점은 내부의 하나만 문제가 발생해도 안긁힘.(수정이 필요하다.)
    # 현재 적용: <a href="\/address[\w/]*"[\w\s!@#$%%^&*()_,.<>/"'+:;=-]*<\/a>
    # From, To Address 추출
    address_List = re.finditer(
        r'<a href="\/address[\w/]*"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/a>',
        text)

    element = 0

    # From, To Address
    for address in address_List:
        matched_Str = address.group()
        #  + " find: " + matched_Str
        print("num: " + str(element))

        find_Address = re.search(r'address[\w/]*', matched_Str).group().replace('address/', '')
        # 최종: data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*
        check_tag = re.search(r'data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*', matched_Str).group().replace('data-bs-title="', '')

        # From
        if element % 2 == 0:
            From_List.append(find_Address)

            if check_tag != find_Address:
                From_Tag_List.append(check_tag)
            else:
                From_Tag_List.append('None')
        # To
        elif element % 2 == 1:
            To_List.append(find_Address)

            if check_tag != find_Address:
                To_Tag_List.append(check_tag)
            else:
                To_Tag_List.append('None')
        element = element + 1

    # 3페이지 이후 5초 휴식
    if page % 3 == 0:
        time.sleep(5)
        print("Sleep 5 sec")
    print("Current Page is " + str(page) + " Done")

Ethereum_CSV = pd.DataFrame (
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