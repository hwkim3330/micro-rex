# MICRO REX

**Microduck의 제어 구조를 유지하는 티렉스형 로봇 외장 설계 프로젝트.**

![Micro Rex CAD rendering](artifacts/micro_rex_hero.png)

[3D 모델 돌려보기](https://hwkim3330.github.io/micro-rex/) · [도면 PDF](drawings/Micro_Rex_Drawings.pdf) · [STEP 조립 파일](models/micro_rex_retrofit.step) · [GLB 전체 모델](models/micro_rex.glb) · [출력 STL](models/print/) · [검증 보고서](artifacts/validation.json)

현재 릴리스는 **Rev A 설계 프로토타입**입니다. 실물 장착, 보행 정책, 강도 및 제조 공차는 검증되지 않았습니다. `호환`은 아래에서 실제 검사한 제어 인터페이스 범위를 뜻합니다. 완성된 양산 로봇이나 검증된 보행 업그레이드로 소개하지 않습니다.

## 무엇을 만들었나

- 카메라 앞을 개방한 두개골 외장, 별도 이빨·눈썹, 위쪽 조립 브리지.
- 작은 앞발과 장착 브래킷, 속이 빈 분할 꼬리와 스트랩 장착판.
- 수정 가능한 CadQuery 원본, 개별 STEP/STL, 16개 부품의 출력 방향 정리본.
- 전체 로봇 GLB, 외장 STEP 조립 파일, MuJoCo 모델 및 지면이 포함된 장면.
- 실제 형상에서 생성한 17쪽 치수 참고 도면과 부품 목록.
- PC·모바일 브라우저에서 회전·확대·분해 보기 및 원본 부품 표시 전환.

기존 Microduck보다 개선하려는 항목은 외장 수정/교체의 용이성, 출력 파일·도면 제공, 추적 가능한 호환성 검사입니다. 속도·안정성·배터리 수명 향상은 아직 입증하지 않았습니다.

## 호환성 확인 범위

| 항목 | 결과 |
|---|---|
| 원본 정책 제어 관절 | **14개**, 이름·순서 유지 |
| 관절 축·위치·가동 범위 | 원본과 배열 비교 통과 |
| 액추에이터 연결·제어 범위·힘 제한 | 원본과 배열 비교 통과 |
| 센서 종류·차원·연결 ID | 원본과 배열 비교 통과 |
| 원본 모델 질량 | 737.24 g |
| Micro Rex 모델 질량 | 784.93 g |
| 예상 외장 추가 질량 | 47.68 g, PLA 실체적 환산 |
| 새 출력 STL | 16개, 폐곡면 및 양의 체적 검사 통과 |
| 단순 PD 자세 유지 | **원본과 Micro Rex 모두 3초 직립 실패**; 정책 평가가 아님 |
| 실물 조립 / 보행 정책 / sim-to-real | **미검증** |

원본 로봇의 입 모터는 14차원 보행 정책과 별도입니다. 이 패키지는 입 모터 제어를 추가하거나 15차원 정책으로 바꾸지 않습니다. 꼬리·앞발은 정적 외장입니다. 추가 질량과 관성은 모델에 반영했으며, 기존 보행 정책을 그대로 쓰면 동일 성능이 나온다고 보장하지 않습니다.

## 원본 자료도 함께 받기

공식 제어 소프트웨어, 공식 RL/메시, 공식 Robot HAT 회로도, 커뮤니티 역설계 도면을 서로 구분해 고정 커밋으로 연결합니다.

```bash
git clone --recurse-submodules https://github.com/hwkim3330/micro-rex.git
cd micro-rex
```

이미 클론했다면 `git submodule update --init --recursive`를 실행합니다. 모든 출처와 커밋은 [upstream.lock.json](upstream.lock.json), 자료별 상태는 [출처 기록](docs/SOURCES.md)에 있습니다. 커뮤니티 역설계 자료는 공식 공장 도면으로 취급하지 않습니다.

## 모델 재생성

Python 3.11 이상, Linux 기준입니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python cad/build.py
python tools/print_parts.py
python tools/tail_continuous.py
python tools/validate.py
MUJOCO_GL=egl python tools/render.py  # EGL 환경 필요; 정적 렌더는 이미 포함
python tools/drawings.py
```

`models/parts/`는 조립 기준 좌표, `models/print/`는 중심 정렬 및 출력면을 맞춘 파일입니다. 원본 로봇의 STL은 `vendor/microduck/assets/`에 있습니다. 전체 조립 STEP은 **새 외장**만 정확한 CAD 솔리드로 담고, 원본 전체 로봇 형상은 GLB와 upstream STL/MJCF로 제공합니다.

```bash
python -m http.server 5190
# http://127.0.0.1:5190/web/
```

뷰어 라이브러리도 저장소 안에 있으므로 외부 CDN이 필요 없습니다. 모델을 MuJoCo에서 열려면 `models/scene.xml`을 사용합니다.

개발자 브라우저 검사: `npm ci --ignore-scripts && npm run test:viewer`. 설치된 Chrome 경로는 `CHROME_PATH`로 지정할 수 있습니다.

## 제작 전 확인

[조립 및 검증 항목](docs/ASSEMBLY.md)을 먼저 확인하세요. 현재 꼬리 조인트, 스트랩 고정, 나사 체결 길이와 가동 중 간섭은 실물 확인 대상입니다. 도면은 프로토타입 치수 참고용이며 공장 제작 승인도면이 아닙니다.

## 라이선스

독립 프로젝트이며 Pollen Robotics 또는 Hugging Face의 공식 제품이 아닙니다.

- 새 코드: Apache-2.0.
- 원본 하드웨어 모델: upstream의 **CC BY-SA-NC** 표기 유지.
- 새 외장 및 파생 모델·도면: **CC BY-NC-SA 4.0**, 원본 하드웨어 조건도 적용.
- Three.js: MIT.

[자세한 출처·라이선스](licenses/HARDWARE.md). 상업 사용을 허용하는 하드웨어 패키지가 아닙니다.
