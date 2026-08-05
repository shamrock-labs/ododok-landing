# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개요

Ododok(オディ) 앱의 **일본 시장 랜딩 페이지 A/B 실험** 저장소. 빌드 시스템·패키지 매니저·의존성이 전혀 없는 순수 정적 HTML이며, `CNAME`(`ododok.app`)을 통해 GitHub Pages(`shamrock-labs/ododok-landing`, `main` 브랜치)로 서빙된다. 저장소 루트에 `index.html`이 없으므로 실제 진입점은 `/jp/`뿐이다.

## 명령어

```bash
# 전체 테스트 (의존성 없음, Python 3 표준 라이브러리만 사용)
python3 -m unittest discover -s tests -v

# 단일 테스트
python3 -m unittest tests.test_jp_concept_pages.JapaneseConceptPagesTest.test_jp_root_is_a_stable_concept_router

# 로컬 확인 — 상대 경로(../assets/)와 라우터 리다이렉트 때문에 file:// 로는 정상 동작하지 않음
python3 -m http.server 8000   # → http://localhost:8000/jp/
```

린터·포매터·CI 워크플로는 없다. `main`에 푸시하면 곧바로 배포된다.

## 구조

```
jp/index.html          A/B 라우터 (실제 콘텐츠 없음, JS로 즉시 리다이렉트)
jp/health/index.html   컨셉 A "8c" — 咀嚼 기록/건강 소구
jp/point/index.html    컨셉 B "9a" — 현금 리워드 소구
jp/assets/*.png        두 페이지가 공유하는 이미지
tests/test_jp_concept_pages.py   두 페이지의 정적 계약(contract) 검증
```

각 랜딩 페이지는 **단일 파일 완결형**이다. 공유 CSS/JS 파일이 없고, 모든 스타일이 인라인 `style` 속성 + `<head>` 내 한 줄짜리 압축 `<style>` 블록에 들어 있다. 즉 두 페이지 사이의 공통 요소(모션 시스템, Airbridge 스니펫, 타이포그래피 클래스)는 **의도적으로 복제**되어 있으며, 한쪽을 수정하면 다른 쪽도 같이 수정해야 한다. 테스트가 이 동기화를 강제한다.

## 아키텍처상 알아야 할 것들

### 1. A/B 라우터 (`jp/index.html`)

`/jp/`는 사용자를 `health` 또는 `point`로 배정한다. 배정 우선순위는 **forced(`?variant=`) → stored(`localStorage["ododok:jp-concept:v1"]`) → random(`crypto.getRandomValues`)** 이며, 랜덤 배정 결과는 즉시 localStorage에 기록된다. 새로고침해도 재배정되지 않아야 한다는 것이 이 파일의 핵심 불변식이다.

리다이렉트 시 쿼리스트링을 재작성한다: `variant` 파라미터는 **삭제**하고(URL 공유 시 실험 오염 방지), `experiment_id` / `experiment_variant` / `assignment_source`를 **추가**한 뒤 기존 UTM 파라미터와 함께 목적지로 전달한다. 이동은 `location.replace()`로 하여 뒤로 가기 시 라우터로 되돌아오지 않게 한다.

localStorage 접근은 시크릿 모드·브라우저 정책 때문에 예외를 던질 수 있어 항상 `try/catch`로 감싸야 한다. JS 미지원 시 `<noscript>`의 수동 링크가 폴백이다.

### 2. 트래킹 — Airbridge + Meta 픽셀 (두 랜딩 페이지 공통)

#### Airbridge

- SDK는 `<script src>` 태그가 아니라 **인라인 부트스트랩 스니펫**으로 삽입된다. `createAirbridge` 정의가 `airbridge.init` 호출보다 먼저 와야 한다(테스트가 순서를 검증).
- 앱 `ododokdev`, `utmParsing:true`.
- 이벤트는 `jp_landing_viewed`(진입 시)와 `jp_line_cta_clicked`(CTA 클릭 시) 두 개. 모든 이벤트의 `customAttributes`에 `concept`, `page_path`, `cta_position`, 그리고 URL에서 파싱한 UTM 5종이 실린다.
- **CTA 클릭 처리는 의도적으로 복잡하다.** `preventDefault()`로 이동을 막고 → 이벤트 전송 → `airbridge.events.wait(1000, ...)`으로 전송 완료를 기다린 뒤 `location.assign()`. 여기에 1200ms `setTimeout` 폴백과 중복 이동 방지 플래그(`navigated`)가 붙는다. 이유는 iOS Safari에서 페이지 이탈 시 비콘이 유실되기 때문이며, 같은 이유로 `target="_blank"`를 **쓰면 안 된다**(테스트가 금지).

#### Meta 픽셀

**단일 픽셀 ID를 두 페이지가 공유**한다. 컨셉별 성과는 픽셀을 나누지 않고 Meta Ads Manager의 맞춤 전환에서 URL(`/jp/point/` vs `/jp/health/`)로 분리한다.

- **PageView** — `<head>` base code가 자동 발동.
- **Lead** — LINE CTA 클릭 시. 기존 Airbridge 클릭 핸들러 **안에서** 발동하며, 이미 존재하는 1000ms 대기창을 재사용하므로 추가 지연이 없다. 별도 리스너를 만들면 이동 레이스가 생기니 절대 분리하지 말 것.
- `fbq` 호출은 `try/catch`로 감싼다. 광고 차단기 환경에서 예외가 나도 LINE 이동이 막히면 안 되기 때문이다. `setTimeout(navigate,1200)` 폴백이 **픽셀 호출보다 먼저** 걸려 있어야 하며 테스트가 이 순서를 강제한다.
- 같은 `eventId`(UUID)를 Meta의 `eventID`와 Airbridge의 `event_id`에 **동시에** 싣는다. 두 계측을 사후 대조하기 위한 것이고, 나중에 CAPI를 붙이면 그대로 중복 제거 키가 된다.

픽셀 ID는 파일당 2곳(`fbq('init',...)`, `<noscript>` 폴백 img), 총 4곳에 중복된다. 정적 HTML이라 단일 상수로 뺄 수 없으므로 **테스트가 4곳의 동일성과 형식(15~16자리 숫자)을 강제**한다.

**라우터(`jp/index.html`)에는 픽셀을 넣지 않는다.** 즉시 리다이렉트하므로 PageView가 이중 계상되고 리다이렉트가 느려진다. 테스트가 차단한다. `fbclid`는 라우터가 쿼리스트링을 통째로 넘기며 보존하므로 `_fbc` 귀속은 정상 동작한다.

**측정 한계** — LINE 친구추가는 오프사이트에서 완료되므로 픽셀은 "CTA를 눌렀다"까지만 본다. `Lead`는 전환이 아니라 **의도 신호**다. Meta의 Lead 수와 Airbridge에 잡히는 실제 친구추가·설치 수의 비율을 상시 대조해야 하며, 이 비율이 무너지면 최적화 타겟을 바꿔야 한다는 신호다.

### 3. LINE CTA 링크는 컨셉별로 다르다

| 컨셉 | 딥링크 |
|---|---|
| point | `https://go.ododok.app/ekfx7o` |
| health | `https://go.ododok.app/7ueukr` |

전환이 컨셉별로 귀속되어야 하므로 두 링크가 섞이면 안 된다. 테스트가 각 페이지에 자기 CTA만 2개 이상 존재하고 상대 CTA는 0개임을 검증한다.

### 4. 모션 시스템

`data-reveal="1"` 요소를 IntersectionObserver로 관찰해 `.motion-ready`(`opacity:.15`, `translateY(22px)`) → `.motion-visible`(1400ms cubic-bezier) 전환. 관찰 파라미터(`threshold:.08`, `rootMargin:'0px 0px -4% 0px'`)와 히어로 float(7s)·CTA breathe(5s) 애니메이션 타이밍까지 테스트에 하드코딩되어 있다.

주의할 세 가지: (a) 첫 화면 요소는 `requestAnimationFrame` 이중 중첩으로 즉시 노출시켜 초기 빈 화면을 막는다, (b) `prefers-reduced-motion:reduce`에서 모든 모션이 완전히 비활성화되어야 한다, (c) `transition:all`은 금지(테스트가 차단) — 모바일 성능 때문에 속성을 명시해야 한다.

### 5. 일본어 조판

일본어는 자동 줄바꿈이 어색해지기 쉬워 별도 장치를 쓴다.

- `.semantic-line` — 의미 단위로 끊은 `display:block; white-space:nowrap` 스팬. 제목은 여기에 수동으로 줄을 나눠 넣는다.
- `.support-line`, `.token` — 끊기면 안 되는 구(句)·고유명사(`AirPods`, `オディ`, `どんぐり`) 보호.
- `.jp-copy` + `@supports(word-break:auto-phrase)` — 지원 브라우저에서 형태소 단위 줄바꿈.
- 폰트 크기는 `clamp()`로 뷰포트 대응. 기준 폭은 430px(모바일 전용 페이지이며 데스크톱 레이아웃은 없다).

`<html lang="ja">`여야 하고, **페이지 안에 한글이 단 한 글자도 남아 있으면 안 된다**(테스트가 정규식으로 검사). 카피 편집 시 한국어 원문이 섞여 들어가는 사고가 실제로 있었다.

알려진 불일치: `health/`만 Google Fonts에서 Noto Sans JP를 로드하고 `point/`는 시스템 폰트에 의존한다. 또 `health/`의 인라인 `font` 선언 일부는 아직 `Pretendard`(한국어 폰트) 이름을 참조한다.

### 6. 디자인 소스 마커

각 페이지 최상단 컨테이너에 `id="8c"` / `id="9a"`와 `data-source-section="..."`가 붙어 있고, 그 아래 배지 UI(`8c`, `コンセプトA · 確定案…`)가 원본 시안 번호를 표시한다. 이는 디자인 툴에서 내보낸 산출물의 출처 표시이며 테스트가 존재를 강제하므로 **정리한다고 지우면 안 된다**.

## 작업 규칙

- **테스트가 곧 스펙이다.** `tests/test_jp_concept_pages.py`는 문자열·CSS 값·DOM 구조를 리터럴로 검증한다. 카피, 모션 타이밍, 이벤트 이름, CTA 링크를 바꾸려면 테스트를 함께 갱신해야 하며, 테스트 실패는 대부분 "랜딩 계약이 깨졌다"는 신호다.
- 두 랜딩 페이지 중 하나만 고치는 변경은 의심하라. 모션·트래킹·타이포 관련 수정은 거의 항상 양쪽에 적용되어야 한다.
- 새 컨셉을 추가할 때는 (1) `jp/<concept>/index.html`, (2) `jp/index.html`의 `VARIANTS` 배열, (3) 테스트의 `CASES` 딕셔너리 세 곳을 모두 손봐야 한다.
- 이미지 참조는 `jp/<concept>/`에서 `../assets/`로 올라간다. 페이지를 다른 깊이로 옮기면 전부 깨진다(전용 테스트 있음).
- **메타 광고는 `/jp/point/`, `/jp/health/`에 직접 링크한다.** `/jp/`(랜덤 라우터)로 걸면 크리에이티브와 랜딩 메시지가 절반 확률로 어긋나 전환율과 실험 결과가 함께 오염된다.
- 커밋 메시지는 한글로 작성한다.

## 미완료 항목

- [x] **픽셀 ID 삽입** — `27445797488456045`, 4곳 모두 반영 완료.
- [ ] **도메인 인증 + AEM** — `ododok.app`을 Business Manager에서 인증하고 이벤트 우선순위 8개를 설정. 이 제품은 AirPods가 필수라 사용자층이 구조적으로 iOS에 쏠리므로, 미설정 시 iOS 전환이 거의 잡히지 않는다. 상위 2칸은 향후 실제 친구추가·결제 이벤트용으로 비워두고 `Lead`를 3순위에 둔다.
- [ ] **맞춤 전환 생성** — URL 기준으로 point/health 분리.
- [ ] **개인정보 고지** — 푸터의 「利用規約　プライバシーポリシー　お問い合わせ」가 링크 없는 평문이다. 픽셀을 붙인 상태이므로 일본 APPI 관점에서 공백이 있다. 실제 URL 연결과 쿠키 사용 고지 필요.
- [ ] **CAPI** — 정적 호스팅이라 서버가 없어 미적용. 브라우저 픽셀만으로는 신호가 20~40% 유실된다. `eventId`는 이미 심어두었으므로 Airbridge Meta 연동이나 서버리스 함수를 붙이면 중복 제거가 바로 동작한다.
