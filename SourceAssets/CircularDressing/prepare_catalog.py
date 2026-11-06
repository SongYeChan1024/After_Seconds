from pathlib import Path
import json,math
H=Path(__file__).resolve().parent;R=H.parents[1]
d=json.loads((R/'Docs/도면/원형공동/facility_layout.json').read_text('utf-8'))
E=[]
def env(code,name,dims,floors,method,notes,model='',stage='후속 제작'):
 E.append(dict(code=code,name=name,category='환경 모듈',priority='P1' if stage!='후속 제작' else 'P2',w=dims[0],d=dims[1],h=dims[2],floors=floors,method=method,notes=notes,model=model,stage=stage))
env('E01','반원 터널 외피',(4.2,4,3.4),'지하 공통','Blender','유효폭4.2m·최고3.4m. 기존 CF 외피 유지. 연결부 실제 개구부','CF_B5_Core','기존 구조 재사용')
env('E02','반구 공동 외피',(20,20,10),'지하 공통','Blender','방별 반지름을 따름. 내부 칸막이는 별도','CF_B5_Core','기존 구조 재사용')
env('E03','터널 보강 리브',(4.2,.18,3.4),'지하 공통','Blender','바닥 기단·분절 조인트·볼트 포함. 내부 돌출90mm 이하','CFD_TunnelRib','1차 제작')
env('E04','곡면 벽 하부 보호판',(1.1,.05,1.1),'지하 공통','Blender','C01 반지름10m용 곡면. 바닥과 벽 접점 밀착, 4가지 불규칙 마모','CFD_CovePanel','1차 제작')
env('E05','곡면 맞춤 설비 받침',(1.25,.32,1.9),'B5/B4','Blender','반구 벽 뒤쪽으로 물러나는 형상에 맞춰 설비를 고정','CFD_ServiceBackplate','1차 제작')
env('E06','밀폐형 벽·천장 작업등',(1.2,.18,.10),'지하 공통','Blender','프레임·확산판·나사·고정 브래킷. 발광만으로 방을 밝히지 않음','CFD_SealedLight','1차 제작')
env('E07','환기 루버와 필터 덮개',(.65,.12,.45),'지하 공통','Blender','루버 날개·내부 어둠·체결부, 먼지는 흡입부 주변','CFD_Vent','1차 제작')
env('E08','케이블 트레이 직선',(0.3,2,.14),'지하 공통','Blender','실제 측판·가로대·행거, 머리 위 유효높이 확보','CFD_CableTray','1차 제작')
env('E09','배관 벽 고정 클램프',(.32,.25,.32),'B2/B5','Blender','관을 감싸는 밴드·벽 받침·볼트 포함','CFD_PipeClamp','1차 제작')
env('E10','벽면 점검함',(.55,.15,.75),'지하 공통','Blender','힌지·손잡이·도어 틈·매입 나사. 금속도와 거칠기 분리','CFD_InspectionBox','1차 제작')
env('E11','터널·공동 접합 칼라',(4.5,.4,3.6),'지하 공통','Blender','문 포켓과 충돌하지 않는 단면. 연결마다 각도 정합')
env('E12','T·Y 교차 터널',(8,8,3.4),'지하 공통','Blender','실제 분기 개구부. 리브 중복과 막힌 충돌체 제거')
env('E13','곡선·경사 터널',(4.2,6,3.4),'지하 공통','Blender','곡률·경사 가안. 직선 모듈 비균일 스케일 금지')
env('E14','2.4m 문틀·수납 포켓',(5.24,.48,3.08),'지하 공통','Blender','P40 문에 포함. 열린 문짝이 포켓 밖으로 나오지 않음','CF_PocketDoor_240','기존 구조 재사용')
env('E15','문 하부 레일·씰',(2.4,.4,.024),'지하 공통','Blender','P40 문에 포함, 통행 단차 최소화','CF_PocketDoor_240','기존 포함')
env('E16','관찰창·매입 프레임',(2.4,.2,1.5),'B4/B5','Blender','실제 뒤쪽 관찰실 필요. 유리·프레임·씰 분리')
env('E17','생활 구획 칸막이',(2,.12,2.4),'B5/B1','Blender','곡면 외피 안의 개별 생활 구획. 중앙 통로 차폐벽으로 쓰지 않음')
env('E18','바닥 배수 채널',(.15,2,.025),'B5/B4/B3','Blender','표면과 평탄한 격자·받이. 젖은 구역에 한정')
env('E19','벽·바닥 안내선 세트',(0.14,2,.002),'전층 공통','Blender/텍스처','R1 흰 이중선, S1 청록 사각, M1 황토 점선. 탈출 정답을 직접 표시하지 않음')
env('E20','점등 스위치·회로함',(.3,.12,.45),'B3 중심','Blender','13회로, 보관5구역 기본 소등. 비상·작업등 분리. 동작은 사용자 구현')
env('E21','비상 보조등',(.35,.15,.16),'지하 공통','Blender','안전 이동용 저휘도. B2 상시 적색과 경보 상태 구별')
env('E22','스틸 그레이팅 데크',(1.22,1.1,.08),'B2','Blender','실제 구멍. C02 높이3.6m와 상하 관찰 동선','CF_B2_Mezzanine','기존 구조 재사용')
env('E23','메자닌 기둥·보·접합',(0.25,2.4,3.6),'B2','Blender','베이스 플레이트·볼트·보 접합 포함','CF_B2_Mezzanine','기존 포함')
env('E24','메자닌 계단·난간',(1.4,5.6,3.6),'B2','Blender','20단·단높이.18m·디딤.28m. 두 계단과 순환 데크','CF_B2_Mezzanine','기존 포함')
env('E25','불투명 정비 작업 발판',(2.2,1.6,.08),'B2','Blender','격자 관찰과 엄폐를 함께 제공','CF_B2_Mezzanine','기존 포함')
env('E26','배관 직선·엘보·플랜지',(.3,2,.3),'B2/B5','Blender','실제 연결부·볼트·용접부·관 지지. 직선관 처짐 금지','CF_B2_ProcessPipework','기존 구조 재사용')
env('E27','계기·밸브·배관 분기',(.4,.4,.5),'B2/B5','VARCO 후 Blender','회전축과 분리 피벗 준비. 단열·유체별 분기 구분')
env('E28','층간 계단·참·방화 구획',(4.2,8,16),'지하 공통','Blender','층간 높이는 도면 개별값. 문 뒤 실제 공간과 층 연결 필요')
env('E29','화물 리프트·승강로',(4,4,17),'B3/B2/1F','Blender','상하 출입구·피트·문 수납 공간. 승강 동작은 사용자 구현')
env('E30','시료 랙 통로 바닥·충격 보호',(2,.15,.4),'B3','Blender','운반차 접촉 높이에 국소 마모. 랙 사이 시야와 교행 폭 검수')
env('E31','폐공장 외벽·창·셔터',(4,.3,4),'1F','Blender','지상은 평지붕. 지하 청정 마감과 다른 풍화·부분 보수')
env('E32','벽·바닥 생활 흔적 재질',(2,2,0),'전층 공통','PBR 제작','불규칙 먼지·닦임·손때. 조명에 맞게 층별 바탕색 조절, 반복 도형 금지')

newprops=[dict(code='P146',name='급식 전달 캐비닛',category='생활·지원',priority='P1',w=.9,d=.55,h=1.25,floors='B5',method='VARCO 후 Blender',notes='P82 소형 전달함과 구분되는 바닥형 보급장. 기준 구간용 추가 가안',model='CFD_TransferCabinet',stage='생성 중'),dict(code='P147',name='응급 보급장',category='생활·지원',priority='P1',w=.75,d=.45,h=1.4,floors='B5/B4',method='VARCO 후 Blender',notes='P89 소형 응급용품함과 구분되는 비품 보관장. 기준 구간용 추가 가안',model='CFD_EmergencyCabinet',stage='생성 중')]
placements=[]
def place(code,model,x,v,y=0,yaw=0,room='C01',variant=0):
 placements.append(dict(id=f'CD-{len(placements)+1:03}',code=code,model=model,floor='B5',room=room,x=x,v=v,y=y,yaw=yaw,variant=variant))
t=d['floors'][0]['tunnels'][0];p=t['p'];q=t['q'];dx=q[0]-p[0];dv=q[1]-p[1];L=math.hypot(dx,dv);ux=dx/L;uv=dv/L;rx=-uv;rv=ux;yaw=math.degrees(math.atan2(ux,-uv))
for s in [2.3,5.25,8.2,11.15]:
 place('E03','CFD_TunnelRib',p[0]+ux*s,p[1]+uv*s,yaw=yaw,room='T01')
 place('E06','CFD_SealedLight',p[0]+ux*s,p[1]+uv*s,3.19,yaw,room='T01')
for s in [3.1,5.1,7.1,9.1,11.1]:place('E08','CFD_CableTray',p[0]+ux*s+rx*.95,p[1]+uv*s+rv*.95,2.91,yaw,room='T01')
# Arc around the C01 south-west living wall, clear of north/east doors.
for i,angle in enumerate([55,64,73,82,91,100,109,118,127,136,145,154]):
 a=math.radians(angle);place('E04','CFD_CovePanel',-15+math.cos(a)*9.91,10+math.sin(a)*9.91,0,math.degrees(math.atan2(-math.cos(a),math.sin(a))),variant=(i*7+3)%4)
for angle in [30,160]:
 a=math.radians(angle);x=-15+math.cos(a)*9.5;v=10+math.sin(a)*9.5;rot=math.degrees(math.atan2(-math.cos(a),math.sin(a)))
 place('E05','CFD_ServiceBackplate',x,v,0,rot);place('E07','CFD_Vent',x,v,1.42,rot);place('E10','CFD_InspectionBox',x,v,.4,rot)
for s in [4,7,10]:
 place('E09','CFD_PipeClamp',p[0]+ux*s+rx*1.62,p[1]+uv*s+rv*1.62,2.35,yaw,room='T01')
 place('E26','CFD_ServicePipe',p[0]+ux*s+rx*1.62,p[1]+uv*s+rv*1.62,2.35,yaw,room='T01')
place('P146','CFD_TransferCabinet',-21.8,12.6,0,70)
place('P128','CFD_LinenHamper',-21.4,14.1,0,60)
place('P147','CFD_EmergencyCabinet',-22.5,10.5,0,85)
for s,label in [(2.5,'Start'),(11.5,'End')]:place('E26','CFD_PipeReturn'+label,p[0]+ux*s+rx*1.62,p[1]+uv*s+rv*1.62,2.35,yaw,room='T01')
out=dict(version='V0.03',environment=E,newprops=newprops,placements=placements,floor_art=d['floor_art_direction'],source='원형 공동 제작 설계 V0.03 + 2026-11-06 사용자 요청',scope='B5 C01 및 T01 기준 구간 1차 제작. 전층 배치 수량은 미확정.')
(H/'production_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('ENV',len(E),'PLACEMENTS',len(placements))
