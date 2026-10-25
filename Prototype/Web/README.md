# 웹 프로토타입 빌드

claude.ai 아티팩트로 만든 웹 프로토타입의 HTML 원본입니다. 파일을 브라우저로 열면 바로 실행됩니다(three.js와 글꼴은 CDN에서 불러오므로 인터넷 연결 필요).

- 빌드 버전은 **제목 뒤에** 붙입니다(V0.01부터, 고칠 때마다 0.01씩, 완성되면 V1.0). 파일 이름은 바꾸지 않고, 이전 버전은 Git 기록으로 봅니다.
- 아티팩트를 고치면 이 폴더의 파일도 같은 내용으로 바꿔 커밋합니다. 아티팩트는 비공개라 링크는 소유자만 열 수 있습니다.

| 파일 | 내용 | 빌드 버전 | 아티팩트 |
| --- | --- | --- | --- |
| [escape.html](escape.html) | 탈출 방(감방·구덩이·단상). 총·경비·제압·던지기·명중 예측. A안(손의 힘 3초 뒤)·B안(손의 힘 즉시, 시야 창) 전환 | V0.01 (2026-10-25) | [링크](https://claude.ai/artifact/9yk2t6TGWsFJLXtRt3HRCR) |
| [throw_sandbox.html](throw_sandbox.html) | 던지기 샌드박스. 손을 떠난 물체가 3초 멈췄다 날아감, 멈춘 물체 밟기·치기 | 버전 표기 전 실험 | [링크](https://claude.ai/artifact/Y82bcBZsSGuMfKCMD6QeQv) |
| [fuse_puzzle_2d.html](fuse_puzzle_2d.html) | 초기 컨셉: 도화선 연쇄 퍼즐(2D). 누른 행동이 1.5초 뒤에 일어남 | 버전 표기 전 실험 | [링크](https://claude.ai/artifact/99dz98oTHXcNfSBLWiyVN8) |
| [fuse_puzzle_3d.html](fuse_puzzle_3d.html) | 초기 컨셉: 도화선 연쇄 퍼즐(3D) | 버전 표기 전 실험 | [링크](https://claude.ai/artifact/MTY2KaR4rwdjd1f31fdmLc) |

각 파일 안의 `window.AfterSecondsEscape` · `window.AfterSeconds` 객체로 입력 없이 시뮬레이션을 돌려 볼 수 있습니다(검수용).
