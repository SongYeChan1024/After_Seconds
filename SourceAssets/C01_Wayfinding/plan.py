"""바닥 업무 동선. 좌표는 실험동 중심 기준 Unity X/Z. 작성자: 송예찬."""
from pathlib import Path
import json,math
H=Path(__file__).resolve().parent
def arc(radius,start,end,step=2):
    n=math.ceil(abs(end-start)/step)
    return [[radius*math.cos(math.radians(start+(end-start)*i/n)),radius*math.sin(math.radians(start+(end-start)*i/n))] for i in range(n+1)]
def polar(r,a):return [r*math.cos(math.radians(a)),r*math.sin(math.radians(a))]
# R1의 기존 출발점 (-0.2, 5.6)에 정확히 합류. 직원 이동을 T11 인계부까지 연장한다.
def bezier(a,b,c,d,n=20):
    return [[(1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(2)] for t in [i/n for i in range(1,n+1)]]
r1arc=arc(5.35,192.144,110)
r1=[polar(10.5,192.144),polar(6.1,192.144)]+r1arc+bezier(r1arc[-1],[-1.0,5.33],[-.010263,5.03079],[-.174702,5.524105])+[[-.2,5.6]]
# 시료 이송은 포드 북동쪽을 돌아 T03 문 중앙으로 이어진다.
s1=arc(5.6,89,18)+[polar(6.35,5.356),polar(10.5,5.356)]
# 정비 표식은 유일한 활성 점검함 전면의 접근 공간에만 둔다. 층 전체 정비 노선이 아니다.
m1=[polar(6.2,152),polar(7.35,152)]
plan=dict(version='V0.01',author='송예찬',scope='C01 + T01/T03/T11 doorway thresholds',origin=[-15,-82,-10],
    routes=[dict(id='R1',kind='double',width=.05,offset=.12,color='#DEE6E9',points=r1),dict(id='S1',kind='single',width=.09,color='#5E9C9A',points=s1),dict(id='M1',kind='dashed',width=.075,color='#BC9B5A',points=m1)],
    labels=[dict(code='R1',position=polar(7.5,192.144),forward=polar(1,12.144),side=-.60),dict(code='R1',position=[-.7,7.1],forward=[-.2425356,.9701425],side=.62),dict(code='S1',position=polar(7.5,5.356),forward=polar(1,5.356),side=.60),dict(code='S1',position=polar(5.6,48),forward=polar(1,-42),side=.62),dict(code='M1',position=polar(6.45,152),forward=polar(1,152),side=.85)],
    doors=[dict(id='Door_B5-T01_0',code='R1'),dict(id='Door_B5-T03_4',code='S1'),dict(id='Door_B5-T11_q',code='R1')],
    rules=['R1 기존 메시·재질·다른 공동 경로 유지','M1은 점검함 앞 국소 접근/비움 표시만','과도한 발광/큰 방 이름/탈출 정답 표지 없음','신규 Collider·게임 C# 없음','B5 전체 완성 후 조명·색감 최종 조정'])
(H/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('Plan:',[(r['id'],len(r['points'])) for r in plan['routes']])
