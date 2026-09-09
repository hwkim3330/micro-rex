# Microduck weights compatibility / Rev C

사용자 요청에 따라 Microduck 원본 기구를 유지하는 Micro Rex 호환 개발을 재개했습니다. 판매용 독립 기구 Micro X와 달리, 이 저장소는 원본 하드웨어의 비상업 조건을 유지합니다.

## 실제로 사용한 자료

- 원본 모델과 추론 코드: `upstream.lock.json`의 Microduck RL 커밋. 관절 14개와 관절·몸체 배치, 센서 순서를 유지합니다.
- [공식 정책 저장소](https://huggingface.co/pollen-robotics/microduck-policies/tree/088524a64e2557dc453256b6071dbb9d23888802): `alpha_walking.onnx`를 변경하거나 재학습하지 않았습니다. 다운로드 URL과 SHA256은 `artifacts/policy_source.json`에 고정합니다. 모델 카드의 가중치 라이선스는 Apache-2.0입니다. 이는 하드웨어의 상업 이용 허가가 아닙니다.
- 관측 61개, 행동 14개, 50 Hz. upstream 추론 코드의 HOME 기준 자세, 투영 중력, 관절 상대 위치·속도, 이전 행동과 명령 배열을 사용합니다.
- BAM M6 XL330 모터 모델, 7.4 V, firmware kp 200, 전압 강하 gain 0.1. MuJoCo는 원본 추론 코드가 사용하는 3.10.0을 별도 환경에 설치했습니다. CAD 검사 환경은 3.4.0입니다.

## 비교 결과

평평한 바닥에서 정지, 0.1 m/s 전진, 0.3 m/s 전진, 0.3 rad/s 회전 명령 각각 초기 관절 잡음 seed 3개를 사용해 10초씩 평가했습니다. 원본 12회와 외장 포함 12회에서 정한 넘어짐 기준(몸통 기울기 45° 초과 또는 높이 65 mm 미만)에 도달하지 않았습니다.

외장 모델의 0.3 m/s 명령 시험에서 X 이동은 1.009–1.064 m, Y 이동은 −0.340–−0.202 m였습니다. 속도 및 직진 추종이 명령과 일치하지 않습니다. 0.1 m/s 명령에서는 거의 전진하지 않았고 회전 명령 추종도 작았습니다. 원본에서도 같은 종류의 문제가 나타났습니다. **가중치 로딩·추론·짧은 평지 동작을 확인했지만, 모든 기능의 호환이나 실물 보행을 검증한 것은 아닙니다.**

외장은 46.53 g의 추정 질량과 관성을 더합니다. 추가 나사·와셔·스트랩의 실측 질량은 포함 전입니다. 외장 충돌은 보수적 단순 형상으로 근사하며 실물 간섭이나 강도 검증을 대체하지 않습니다. 상세 수치는 `artifacts/policy_evaluation.json`을 따릅니다.

별도로 공식 `alpha_stand.onnx`를 그대로 사용해 머리 pitch 명령 −0.25/0/+0.25 rad, seed 0으로 두 모델을 각 3회 시험했습니다. 10초 동안 넘어짐 기준에는 도달하지 않았습니다. 이 시험도 명령 추종 정확도나 장기 신뢰성의 합격 판정은 아닙니다.

## 재현

```sh
git submodule update --init upstream/microduck_rl
python3 -m venv .venv-policy
.venv-policy/bin/python -m pip install -r requirements-policy.txt
.venv-policy/bin/python tools/fetch_policy.py
.venv-policy/bin/python tools/evaluate_policy.py
```

가중치는 `.cache/policies`에 저장하며 이 저장소에서 다시 배포하지 않습니다. 다운로드는 고정 리비전을 사용하고 평가 전에 SHA256을 대조합니다. walking 비교 24회와 standing/head 비교 6회를 수행합니다. 가상 환경과 모델 가중치는 git에서 제외합니다.

웹의 기록 재생은 이 평가에서 저장한 실제 관절·몸체 좌표를 사용합니다. ONNX를 브라우저에서 실행하거나 실제 로봇을 연결하는 기능은 아닙니다. 현재 기록은 전진 0.3 m/s, seed 0 시험입니다.

## 외장 변경

원본 머리와 다리 구조를 유지하고 옆 볼을 곡선으로 다듬고 주둥이 길이를 줄였습니다. 기존 `brow_*` 부품 ID는 큰 볼록 눈 부품으로 변경했습니다. 눈동자는 도색 의도이며 MuJoCo의 검은 표시는 시각 근사입니다. 실제 눈 부품 고정, 커버와 원본 하우징 간 공차 및 카메라 시야 확인은 남아 있습니다.
