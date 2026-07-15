@echo off
chcp 65001 >nul
echo ==========================================
echo  HPMS - 家庭采购决策系统 启动脚本
echo ==========================================
echo.

if not exist .env (
   echo [INFO] 未发现 .env 文件，正在从 .env.example 创建...
   copy .env.example .env
   echo [WARN] 请编辑 .env 文件修改 SECRET_KEY 和数据库密码
)

echo [Step 1/3] 检查 Docker 运行状态...
docker info >nul 2>&1
if %errorlevel% neq 0 (
   echo [ERROR] Docker Desktop 未运行！请先启动 Docker Desktop
   pause
   exit /b 1
)
echo [OK] Docker 运行正常

echo [Step 2/3] 构建镜像...
docker compose build
if %errorlevel% neq 0 (
   echo [ERROR] 构建失败，请检查错误信息
   pause
   exit /b 1
)

echo [Step 3/3] 启动所有服务...
docker compose up -d
if %errorlevel% neq 0 (
   echo [ERROR] 启动失败
   pause
   exit /b 1
)

echo.
echo ==========================================
echo  ✅ 启动成功！
echo.
echo  前端页面：  http://localhost
echo  API文档：   http://localhost/docs
echo  健康检查：  http://localhost/health
echo.
echo  管理命令：
echo   查看日志   docker compose logs -f
echo   停止服务   docker compose down
echo   重新启动   docker compose restart
echo ==========================================
pause
