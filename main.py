# 설정 파일을 불러오기
from CrawlingConfig import cookies
from CrawlingConfig import headers
from CrawlingConfig import params
from CrawlingConfig import data

import pandas as pd
import requests
import re
import time

From_List = []
From_Tag_List = []
To_List = []
To_Tag_List = []

base_Url = "https://etherscan.io/txs"
index = 1
max_Index = 10000

# 50 to 100 Crawling
response = requests.get(base_Url, params=params, cookies=cookies, headers=headers, data=data)

for page in range(1):
    # html 파일 받기
    response = requests.get(base_Url, params=params, cookies=cookies, headers=headers)
    text = response.text

    # 파일 단위 저장기능(for Debug)
    # test_html = open("index.html","w", encoding='utf8')
    # test_html.write(text)
    # test_html.close()

    # 정규식
    # <a href="\/address\/[\w]*\" class=\"[\w\s-]*" [\w\s-=":]*(<br\/>)?(\([\w]*\))?">[\s\w:.?!@#$%^&*()_+=+/*-]*
    # <a href="\/address[\w/]*" class="[[\w\s-]*]?" [\w\s=":-]*(<br\/>\([\w]*\))?">
    # 최종: <a href="\/address[\w/]*" class="(hash-tag text-truncate)?"[\s\w=:"!@#$%^&*_=+~`.()-]*(<br\/>\(\w*\)")?>
    # 최종: <a href="\/address[\w/]*" class="(hash-tag text-truncate)?"[\s\w=:"!@#$%^&*_=+~`.()-]*(<br\/>\(\w*\)")?
    # 위 정규식의 문제점은 내부의 하나만 문제가 발생해도 안긁힘.(수정이 필요하다.)
    # 현재 적용: <a href="\/address[\w/]*"[\w\s!@#$%%^&*()_,.<>/"'+:;=-]*<\/a>
    address_List = re.finditer(
        r'<a href="\/address[\w/]*"[\w\s!@#$%%^&*()_,.<>/\"\'+:;=-]*<\/a>',
        text)

    element = 0

    for address in address_List:
        # group을 통해서 찾은 결과 접근
        matched_str = address.group()
        print("num: " + str(element) + " find: " + matched_str)

        find_address = re.search(r'address[\w/]*', matched_str).group().replace('address/', '')
        # 최종: data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*
        check_tag = re.search(r'data-bs-title="(Public Tag: )?[\w\s.:!@#$%^&_=+,/?-]*', matched_str).group().replace('data-bs-title="', '')

        # From
        if element % 2 == 0:
            From_List.append(find_address)

            if check_tag != find_address:
                From_Tag_List.append(check_tag)
            else:
                From_Tag_List.append('None')
        # To
        elif element % 2 == 1:
            To_List.append(find_address)

            if check_tag != find_address:
                To_Tag_List.append(check_tag)
            else:
                To_Tag_List.append('None')
        element = element + 1

    # 10초간 휴식
    time.sleep(10)


Ethereum_CSV = pd.DataFrame (
    {
        'From': From_List,
        'From_TAG': From_Tag_List,
        'To': To_List,
        'TO_TAG': To_Tag_List
    }
)
Ethereum_CSV.to_csv('./Ethereum_Transaction.csv', index=True)