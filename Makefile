.PHONY: help up down restart logs build clean

# 기본 명령어 (make 입력시 도움말 표시)
help:
	@echo "사용 가능한 명령어:"
	@echo "  make up       - 컨테이너 시작"
	@echo "  make down     - 컨테이너 종료"
	@echo "  make restart  - 컨테이너 재시작"
	@echo "  make logs     - 로그 보기"
	@echo "  make build    - 이미지 새로 빌드"
	@echo "  make clean    - 컨테이너 및 이미지 전부 삭제"

# 컨테이너 시작
up:
	docker-compose up -d
	@echo "✅ 컨테이너가 시작되었습니다. http://localhost:8000/api/v1"

# 컨테이너 종료
down:
	docker-compose down
	@echo "✅ 컨테이너가 종료되었습니다."

# 컨테이너 재시작
restart:
	docker-compose restart
	@echo "✅ 컨테이너가 재시작되었습니다."

# 로그 보기 (실시간)
logs:
	docker-compose logs -f

# 이미지 새로 빌드
build:
	docker-compose build
	@echo "✅ 이미지 빌드가 완료되었습니다."

# 전부 삭제 (컨테이너, 이미지, 볼륨)
clean:
	docker-compose down -v --rmi all
	@echo "✅ 모든 컨테이너와 이미지가 삭제되었습니다."
