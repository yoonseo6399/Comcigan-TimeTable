import requests

# URL 설정
url = f'http://comci.net:4082/36179?NzM2MjlfMzA4MzdfMjAyNC0xMi0xIDA5OjI4OjQ2XzE='

# 요청 헤더 설정

# GET 요청 보내기
response = requests.get(url)

# 상태 코드 확인
print("Status Code:", response.status_code)

# 응답 출력
if response.status_code == 200:  # 요청 성공 시
    print("Response:")
    print(response.text)
else:  # 요청 실패 시
    print("Request failed with status code:", response.status_code)