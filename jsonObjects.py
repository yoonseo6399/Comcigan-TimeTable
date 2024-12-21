import base64
import json
from math import floor
from typing import List, TypeVar, Union, TypeAlias, Dict
from xmlrpc.client import DateTime

import requests
from pydantic import Field, BaseModel, PrivateAttr

# 서버가 이따구로 보내주는걸 어떡해.
ClassInfo : TypeAlias = List[List[List[List[int] | int] | int] | int]
ClassInfostr : TypeAlias = List[List[List[List[int | str] | int | str] | int | str] | int | str]

# 교시
class ClassPeriod:
    def __init__(self,modified : bool,teacher : str,subject : str,room : str):
        self.subject = subject
        self.modified = modified
        self.teacher = teacher
        self.room = room

class TimeTable:
    def __init__(self,oneday : List[ClassPeriod]):
        self.oneday = oneday
        ...




#            function teacher(mm, m2) {
#                if (m2 == 100) { 64007
#                    return Math.floor(mm / m2);
#                }
#                return mm % m2;
#            }
#            function subject(mm, m2) {
#                if (m2 == 100) {
#                    return mm % m2;
#                }
#                return Math.floor(mm / m2);
#            }

#[학년][반][요일][교시] 모두 1부터 시작
class WeeklyTimeTable:
    def __init__(self,lists : List[TimeTable]):
        self.lists = lists
    def print(self):
        print([d.oneday[0].subject for d in self.lists])

class ClassInfoInterpreter:
    def __init__(self,ordinary : ClassInfo, now : ClassInfo,room : ClassInfostr, subjects : List[str] ,teachers : List[str], periods : List[List[int]]):
        self.periods = periods
        self.teachers = teachers
        self.subjects = subjects
        self.room = room
        self.now = now
        self.ordinary = ordinary
    #1교시, 2교시... / 해석
    def _interpret_gcdp(self, grade, class_num, day, period) -> ClassPeriod:
        oneday_oldinfo = self.ordinary[grade][class_num][day][period]
        if self.now[grade][class_num][day][0] >= period:
            oneday_newinfo = self.now[grade][class_num][day][period]
        else:
            oneday_newinfo = oneday_oldinfo
        room_info = ""
        if self.room[grade][class_num][day][0] >= period:
            room_info = self.room[grade][class_num][day][period]
        room = ""
        # room is there?
        if room_info != "":
            room = room_info.split("_")[1]

        modified = oneday_oldinfo != oneday_newinfo
        #포맷이 이럼.
        subject = self.subjects[floor(oneday_newinfo / 1000)]
        teacher = self.teachers[oneday_newinfo % 1000][:2]
        return ClassPeriod(modified, teacher, subject, room)

    def _interpret_gc(self,grade,class_num) -> WeeklyTimeTable:
        week_time_table = WeeklyTimeTable([])
        for day in range(1, 6):
            # 가독성 ㅈㅅ ㅋㅋㅋ 해보고싶었음
            week_time_table.lists.append(
                TimeTable(
                    [self._interpret_gcdp(grade, class_num, day, period) for period in range(1, self.periods[grade][day])]
                )
            )
        return week_time_table
    #전체 테이블 해석
    def interpret(self) -> Dict[int,Dict[int,WeeklyTimeTable]]:
        result : Dict[int,Dict[int,WeeklyTimeTable]] = {}
        for grade in range(1, self.ordinary[0]):
            for class_num in range(1, self.ordinary[grade][0]):
                if not result.keys().__contains__(grade):
                    result[grade] = {}
                result[grade][class_num] = self._interpret_gc(grade, class_num)
        return result



class SchoolInfo(BaseModel):
    teachers : List[str] = Field(alias="자료446")
    periods : List[List[int]] = Field(alias="요일별시수")
    sessionPeriods : List[str] = Field(alias="일과시간")
    subjects : List[str | int] = Field(alias="자료492")
    room : ClassInfostr = Field(alias="자료245")
    a : ClassInfo = Field(alias="자료481")
    b : ClassInfo = Field(alias="자료147")

    def get_time_table(self) -> Dict[int,Dict[int,WeeklyTimeTable]]:
        return ClassInfoInterpreter(self.a, self.b, self.room, self.subjects, self.teachers,self.periods).interpret()

def get_school_info() -> SchoolInfo:
    url = "http://comci.net:4082/"
    schoolCode = 36179 # 신원고등학교 코드
    payload = f'73629_30837_2024-12-1 09:28:46_1'
    baseByte = payload.encode("utf-8")
    base64Str = base64.b64encode(baseByte).decode()
    requestURL = f'{url}{schoolCode}?{base64Str}'

    response = requests.get(requestURL)
    response.encoding = 'ko-KR'
    raw = response.text[:response.text.rfind('}')+1]
    dic = json.loads(raw)

    return SchoolInfo(**dic)