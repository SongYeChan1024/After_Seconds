# After Seconds VARCO 에셋 후보 반입 V0.04

2026-10-28 · 작성자 송예찬

[After_Seconds 플로우](https://3d.varco.ai/flow/b7248081-b012-4913-87ba-4b056a7381ea)에서 첫 교환 테스트에 사용할 후보 3종을 가져왔다. AS02 관제 콘솔, AS03 원심분리기, AS04 문짝은 후속 레벨 작업 때 검수한다.

| ID | 후보 | 삼각형 수 | 배치용 높이 | 충돌체 |
| --- | --- | --- | --- | --- |
| AS01 | 시료 궤짝 | 8,000 | 💡 1.0m | BoxCollider |
| AS05 | 회색 플레이어 더미 | 8,000 | 💡 1.8m | CapsuleCollider |
| AS06 | 주황색 경비 더미 | 8,000 | 💡 1.8m | CapsuleCollider |

## Unity에서 확인하기

사용자는 에셋을 가져온 뒤 Plane과 레벨을 직접 배치한다. 자동으로 만든 검수 씬과 검수용 바닥·기준 큐브·카메라·조명·표기는 정리했다. 현재 기존 SampleScene으로 돌아왔으며, 씬 배치는 사용자가 진행한다.

사용자가 정리한 현재 모델 위치는 다음과 같다.

| 후보 | 현재 위치 |
| --- | --- |
| AS01 궤짝 | `Assets/Afrer_Seconds/05.Model/Props/Props_Crate_V0.1.prefab` |
| AS05 플레이어 | `Assets/Afrer_Seconds/05.Model/Player/Player_Dummy_V0.1.prefab` |
| AS06 경비 | `Assets/Afrer_Seconds/05.Model/Enemy/Enemy_Guard_V0.1.prefab` |

`05.Model`은 반입한 모델과 조립 중인 외형을 관리한다. 현재 파일도 `.prefab` 형식이지만 이 단계에 해당한다. `04.Prefabs`에는 스크립트와 결합해 기능이 완성된 게임 에셋만 보관하며, 현재는 비어 있다. 환경 모델은 `05.Model/Environment`에 분류한다.

각 모델의 루트에는 단순 충돌체가 있고 `VisualRoot` 아래에 가져온 메쉬가 있다. 정규화한 높이와 바닥 맞춤은 `VisualRoot`에만 적용했다. 실제 레벨 치수와 캐릭터 충돌체 치수는 플레이 테스트로 정한다.

Unity Project 창에서 `05.Model/Player`, `Enemy`, `Props`의 모델을 사용자가 만든 Scene에 직접 배치한다. 앞으로 반입하는 모델도 `05.Model`의 해당 분류에 정리한다. 원본 모델부터 직접 설정하려면 이 README가 있는 `03.Art/Candidates/VARCO/` 아래 각 후보의 `Models/`에 있는 FBX를 사용한다.

원본 FBX는 각 후보의 `Models/`에 보존했다. `Textures/`에는 추출한 색상·노멀 텍스처가, `Materials/`에는 URP/Lit 재질이 있다. 실제 추출 크기는 색상 1024×1024, 노멀 2048×2048이다. 노멀은 NormalMap 형식으로 가져왔으며 색상과 함께 프리팹 재질에 연결했다. 메탈릭·매끄러움은 검수용 가안이다.

## 캐릭터 후보의 현재 상태

AS05와 AS06은 정적 T포즈 메쉬다. Unity에서 두 모델 모두 SkinnedMeshRenderer·뼈대·바인드 포즈·애니메이션 클립·유효 Humanoid Avatar가 없는 것을 확인했다. 지금은 크기·색 구분·위치 교환의 외형으로 사용할 수 있으며, 신체 동작에는 별도 리깅과 애니메이션이 필요하다.

두 캐릭터는 별도로 생성한 메쉬여서 동일한 토폴로지와 비례를 보장하지 않는다. 회색 더미 가슴의 불필요한 문자 흔적 등 생성 결과의 정리는 최종 캐릭터 작업에서 검토한다. 현재 SampleScene에서는 플레이어 이동과 1인칭 시야 회전을 연결했다. 모델 프리팹에는 Motor·Presenter 등이 일부 연결되어 있으나 CameraRoot·PlayerLook은 씬에 추가한 구성이므로, 독립 실행되는 완성 플레이어 프리팹은 아직 아니다. 사격과 경비 행동도 후속 작업이다.

## 출처와 검수 기록

- `source_manifest.json`: 원본 다운로드 이름·출처 플로우·파일 크기·SHA-256. FBX 내보내기에서 바닥 피벗 옵션을 사용했다.
- `varco-import-facts.json`: 반입 당시 Unity 실측 경계·메쉬 수·삼각형 수·재질 및 텍스처 경로·리깅 상태. 모델 이동 전 경로도 포함하므로 현재 모델 위치는 위 표를 기준으로 한다.
- 이전 검수 이미지: 저장소 `Docs/도면/연구소_전체_시안/05_VARCO_Unity_반입검수.png`. 이 이미지의 자동 배치는 현재 씬에 적용되어 있지 않다.

반입 당시 브릿지는 Unity 6000.4.0f1에서 정상 동작하는 상태를 확인했다. 이번 후보는 FBX 다운로드로 확보했으며, 브릿지를 통한 중복 전송은 하지 않았다. 반입에 사용한 임시 Editor 스크립트는 제거했다. 에셋 반입 작업 자체에서는 게임 스크립트와 AD를 추가하거나 변경하지 않았다.

현재 브릿지는 기본 패키지 의존성에 포함하지 않는 선택 설치다. 기존 FBX·텍스처·재질과 현재 씬은 학원 PC의 브릿지 폴더 없이 사용할 수 있다. 웹 전송이 필요하면 집 PC에서 브릿지의 `package.json`을 `Install package from disk`로 선택하며, 설치로 생긴 PC별 절대 `file:` 경로는 공용 저장소에 다시 커밋하지 않는다.
