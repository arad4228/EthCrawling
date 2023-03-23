# 표의 첫번째 행에 대한 예외처리
class First_Row(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# 크롤링한 데이터가 비어있을 경우에 대한 예외처리
class Empty_Data(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# 지속적인 요청으로 인해 페이지 다운이 거졀됬을 경우에 대한 예외처리
class Refused_Connection(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


