# After Seconds — Codex 작업 안내 V0.06

이 저장소의 공통 작업 규칙은 [CLAUDE.md](CLAUDE.md)를 따릅니다. 작업 전에 해당 문서를 읽습니다.

에셋을 가져올 때는 `CLAUDE.md`의 **에셋 반입·정리** 규칙과 [Unity 프로젝트 안내의 폴더별 사용 기준](Unity/README.md#폴더별-사용-기준)을 읽고, 반입과 용도별 폴더 정리까지 수행합니다.

애니메이션과 Animator 구성 리소스는 `Assets/Afrer_Seconds/07.Animator/`에서 대상별로 관리합니다. `Player/Clips/`에는 애니메이션용 FBX·클립, `Player/Controllers/`에는 Controller·Override Controller, `Player/Masks/`에는 Avatar Mask를 둡니다. 경비 등 다른 대상도 같은 분류를 따르며 필요한 폴더만 만듭니다. 기준 리깅 모델은 `05.Model`, 완성 게임 프리팹은 `04.Prefabs`, 2D 이미지는 `03.Art`를 사용합니다.

모델 폴더는 `05.Model/{Player,Enemy,Props,Environment}` 네 분류를 사용합니다. Props·Environment만 층별 `B5/B4/B3/B2/B1/1F/Common`으로 나누며, 각 분류/층 폴더에는 모델·프리팹·메시를 바로 둡니다. 하위 폴더는 Materials·Textures만 사용하고, 제작/반입 기록은 06.Data/AssetSources에 둡니다. 공용 파일은 복제하지 않습니다. 동작/Animator 리소스는 기존 07.Animator 규칙을 유지합니다.

집에서 이어갈 때는 먼저 [2026-11-03 이어하기](Docs/이어하기_2026-11-03.md)를 읽습니다. 사용자가 뒤집은 천장 방향과 유리 돔은 참고 이미지까지만 만든 상태라는 점을 유지합니다.
