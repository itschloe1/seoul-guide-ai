# Seoul Guide AI - Discord Channel Full History
**Channel:** #seoul-guide-ai (`1490538996663582760`)
**Period:** 2026-04-06 ~ 2026-04-10
**Saved:** 2026-04-10

---

## Session 1: 2026-04-06 (Project Kickoff & Code Consolidation)

### Project Status Check
- context-library 12개 문서 완성 (~5,800줄), 실제 bot 코드는 PM-OS 쪽에만 있었음
- PM-OS/seoul-guide-ai/ 에서 텔레그램 봇 MVP 개발 완료 (Haiku 모델)
- 기능: 텍스트 Q&A + 사진 Vision + /start, /reset

### Code Consolidation
- PM-OS에서 Seoul-Guide-AI 레포로 코드 통합 (commit `f2c32ef`)
- bot.py, system_prompt.md, requirements.txt, .env.example 이동
- 이후 이 레포가 single source of truth

### Reddit/Marketing Discussion
- Reddit 주요 서브레딧들 셀프 프로모션 금지 확인
- 대안 채널: Facebook expat 그룹, TikTok, Reddit organic seeding
- 유저가 선호하는 방향: 입소문 + 커뮤니티 + 집단지성 knowledge base 업데이트

### Community Strategy (Phase Plan)
- **Phase 1**: /feedback 커맨드 + 그룹 채팅 지원 + share links
- **Phase 2**: 그룹에서 좋은 답변 → knowledge base 반영
- **Phase 3**: 봇이 모르는 질문 자동 수집 → 커뮤니티가 gap 채움
- Phase 1 코드 구현 완료 (commit `f516dcf`)

### Bot Rebranding
- 이름 "서울메이트(Seoulmate)"로 변경
- username 변경 시도 → BotFather에서 /setusername 불가
- 새 봇 만들기 or 유지 논의 (결론 미정)

---

## Session 2: 2026-04-09 (Deployment Prep)

### Status Recheck
- 봇이 로컬에서만 돌고 있어서 서버 꺼지면 응답 불가 확인
- Railway 배포 결정

### Separate Repo Created
- `itschloe1/seoulmate-bot` GitHub repo 별도 생성 (PM-OS에서 분리)
- 이 레포(Seoul-Guide-AI)에도 동일 코드 존재

### Telegram Setup
- 새 봇 username: `@livinginkorea_bot`
- Display name 추천: "Living in Korea AI"
- About/Description 텍스트 생성 (사진 과도 강조 피드백 반영)

### Key Feedback from User
- **봇은 사진 번역 봇이 아님** — 한국 생활 전반 AI 어시스턴트
- 약국, 렌트, 비자, 은행, 교통 등 범용 질문 커버
- 포지셔닝: "한국 사는 외국인의 카톡 한국인 친구"

### MVP Validation Plan
- 배포 → 본인 테스트 → 지인 5-10명 → 반응 보고 확장
- 커뮨니티/채널은 유저가 생긴 후

---

## Session 3: 2026-04-10 (Railway Deploy)

### Railway Deployment
- Procfile 생성 (`worker: python bot.py`)
- GitHub push 완료 (commit `94cefb6`)
- Railway에서 GitHub repo 연결 + 환경변수 설정
- **배포 성공! 봇 라이브 확인**

### Environment Variables
- 필수: `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`
- 선택: `ADMIN_CHAT_ID` (@userinfobot으로 확인), `COMMUNITY_GROUP_LINK` (미설정)

### Notes
- Railway ephemeral filesystem → feedback JSON 재배포 시 소실 (나중에 DB 필요)
- Railway 무료 플랜 월 $5 크레딧 (이 봇이면 충분)

---

## Decisions & Direction

| Decision | Date | Detail |
|----------|------|--------|
| 코드 통합 | 04-06 | PM-OS → Seoul-Guide-AI 레포로 |
| 별도 repo | 04-09 | seoulmate-bot repo 별도 생성 (Railway용) |
| 봇 포지셔닝 | 04-09 | 사진 번역기 X, 한국생활 전반 AI 친구 |
| 커뮤니티 전략 | 04-06 | 입소문 + 집단지성 → Phase별 확장 |
| 배포 | 04-10 | Railway 배포 완료, 라이브 |

## Next Steps (as of 2026-04-10)

1. 본인 테스트 — 외국인 입장에서 다양한 질문 던져보기
2. 지인 5-10명 테스트 배포
3. system prompt 품질 개선 (테스트 결과 기반)
4. feedback DB 연동 (Railway PostgreSQL)
5. 커뮤니티 그룹 생성 (유저 확보 후)
6. 홍보 시작 (Facebook expat 그룹 등)
