# 部署文档

本目录存放GreenDataCenter系统的部署相关文档。

## 文档列表

- [安装指南](installation.md) - 系统安装指南
- [配置说明](configuration.md) - 系统配置说明
- [运维指南](operations.md) - 系统运维指南

## 安装指南

### 环境要求

#### 最低配置

| 组件 | 最低配置 | 说明 |
|------|----------|------|
| CPU | 4核 | 支持多线程 |
| 内存 | 8GB | 推荐16GB |
| 存储 | 50GB | 系统数据 |
| 网络 | 100Mbps | 互联网连接 |
| Python | 3.10+ | 运行环境 |

#### 推荐配置

| 组件 | 推荐配置 | 说明 |
|------|----------|------|
| CPU | 8核+ | 提高处理速度 |
| 内存 | 16GB+ | 多并发处理 |
| 存储 | 200GB+ | 日志和数据存储 |
| 网络 | 1Gbps+ | 高并发支持 |

### 软件依赖

```bash
# Python依赖
Python 3.10+
uv
```

### 系统依赖

```bash
# 数据库（未来）
PostgreSQL 14+ 或 MySQL 8.0+

# 缓存（未来）
Redis 7.0+ 或 Memcached

# 监控
Prometheus + Grafana
```

### 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/GreenDataCenter.git
cd GreenDataCenter
```

#### 2. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

#### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加API密钥
nano .env
```

`.env` 文件示例：

```env
# DeepSeek API Key
LLM_API_KEY=sk-your-api-key-here

# 可选：Tavily API Key
TAVILY_API_KEY=your-tavily-api-key-here

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=./logs
```

#### 4. 初始化数据库（未来）

```bash
# PostgreSQL
createdb greendatacenter
psql -c "CREATE TABLE users (...);"

# MySQL
mysql -u root -p <database> < database_name> < schema.sql
```

#### 5. 创建必要目录

```bash
# 创建日志目录
mkdir -p logs

# 创建数据目录
mkdir -p data

# 创建缓存目录
mkdir -p cache
```

#### 6. 运行测试

```bash
# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 运行基础测试
python tests/test_simple.py
python tests/test_coordinator.py

# 运行API测试
python tests/test_api.py
```

### 生产部署

#### 1. 使用systemd服务（Linux）

```bash
# 创建服务文件
sudo nano /etc/systemd/greendatacenter.service
```

`/etc/systemd/greendatacenter.service` 文件内容：

```ini
[Unit]
Description=GreenDataCenter AI Service
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/greendatacenter
Environment="PATH=/opt/venv/bin"
ExecStart=/opt/venv/bin/python -m uvicorn greendatacenter.cli:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 启用服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl enable greendatacenter

# 启动服务
sudo systemctl start greendatacenter

# 查看服务状态
sudo systemctl status greendatacenter

# 查看服务日志
sudo journalctl -u greendatacenter -f
```

#### 3. 使用PM2进程管理

```bash
# 使用PM2管理进程
pip install pm2

# 启动应用
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs --lines 100
```

#### 4. 使用Supervisor管理进程

```bash
# 安装supervisor
apt-get install supervisor

# 创建配置文件
sudo nano /etc/supervisor/conf.d/greendatacenter.conf
```

`/etc/supervisor/conf.d/greendatacenter.conf` 文件内容：

```ini
[program:greendatacenter]
command=/opt/venv/bin/python -m uvicorn greendatacenter.cli:app --host 0.0.0.0
directory=/opt/greendatacenter
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/greendatacenter.err.log
stdout_logfile=/var/log/greendatacenter.out.log
```

启动supervisor：

```bash
# 更新配置
sudo supervisorctl reread

# 启动服务
sudo supervisorctl start greendatacenter

# 查看状态
sudo supervisorctl status greendatacenter
```

### Docker部署

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
COPY --from=builder /root/.cargo/bin/uv /usr/local/bin/uv

# 安装项目依赖
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync

# 复制应用代码
COPY src/ /app/src
COPY data/ /app/data

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 启动命令
CMD ["uv", "run", "python", "-m", "greendatacenter.cli:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
```

部署命令：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down

# 重启服务
docker-compose restart api
```

## 配置说明

### 环境变量配置

#### 开发环境配置

```env
# 开发环境
DEBUG=True
LOG_LEVEL=DEBUG

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME=greendatacenter_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
```

#### 生产环境配置

```env
# 生产环境
DEBUG=False
LOG_LEVEL=INFO

# 数据库
DB_HOST=prod-db.example.com
DB_PORT=5432
DB_NAME=greendatacenter
DB_USER=prod_user
DB_PASSWORD=secure_password_here
```

### 日志配置

#### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| DEBUG | 详细调试信息 | 开发环境、问题排查 |
| INFO | 一般信息 | 生产环境正常运行 |
| WARNING | 警告信息 | 需要关注但不影响运行 |
| ERROR | 错误信息 | 需要立即处理 |
| CRITICAL | 严重错误 | 系统可能无法运行 |

#### 日志轮转

```python
import logging
from logging.handlers import RotatingFileHandler

# 创建日志轮转处理器
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
    encoding='utf-8'
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 运维指南

### 监控指标

#### 核心指标

| 指标 | 监控方式 | 告警阈值 | 说明 |
|------|----------|----------|----------|
| API响应时间 | APM工具 | > 3秒 | 性能下降 |
| API成功率 | 监控系统 | < 95% | 服务异常 |
| 内存使用率 | 系统监控 | > 80% | 需要扩容 |
| CPU使用率 | 系统监控 | > 80% | 需要扩容 |
| 磁盘使用率 | 系统监控 | > 85% | 需要清理 |

### 日志分析

#### 日志查看

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看API错误
grep "API Error" logs/app.log

# 统计错误数量
grep -c "ERROR" logs/app.log
```

#### 日志管理

```bash
# 日志轮转配置
find logs/ -name "*.log" -type f -mtime +7 -delete

# 压缩旧日志
find logs/ -name "*.log" -type f -mtime +30 -gzip
```

### 备份策略

#### 数据备份

```bash
# 备份数据库
mysqldump -u root -p<database> <database_name> > backup_$(date +%Y%m%d).sql

# 备份应用数据
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env *.json
```

#### 备份频率

- 数据库：每日备份
- 配置文件：每周备份
- 应用数据：每周备份
- 日志文件：每日轮转，保留30天

### 故障处理

#### 常见故障

| 故障类型 | 常见原因 | 解决方法 | 预防措施 |
|------|----------|----------|----------|
| API无响应 | DeepSeek API服务异常 | 检查API密钥和额度 | 实现重试机制 |
| 内存溢出 | 数据处理量过大 | 优化数据处理逻辑 | 增加内存限制 |
| 磁盘满 | 日志或数据占用过多 | 定期清理 | 实施日志轮转 |
| 数据库连接失败 | 数据库服务异常 | 检查数据库状态 | 实现连接池 |
| 依赖缺失 | Python包未安装 | 运行uv sync | 使用requirements.txt固定版本 |

#### 故障恢复流程

1. 检测故障（监控系统告警）
2. 通知相关人员（邮件、短信）
3. 尝试自动恢复
4. 如无法恢复，切换到备用服务
5. 记录故障和恢复过程
6. 进行事后分析，改进预防措施

### 安全加固

#### API安全

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer

# API密钥验证
async def verify_api_key(x_api_key: str = Header(..., ...)):
    if not validate_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return True

# 应用验证中间件
app.add_middleware(APIKeyHeader(verify_api_key))
```

#### 访问控制

```python
from slowapi import Request, HTTPException

# IP白名单
ALLOWED_IPS = ["192.168.1.0", "192.168.1.100"]

async def check_ip_whitelist(request: Request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403,
            detail="IP not allowed"
        )
```

#### 速率限制

```python
from slowapi import Request, HTTPException
from slowapi_limiter import Limiter

# 设置速率限制
limiter = Limiter(key="api", default_limits="100/minute")

async def rate_limited(request: Request):
    return {"message": "Rate limit exceeded"}
```

### 性能优化

#### 缓存策略

- 使用Redis缓存频繁请求结果
- 缓存专家分析结果（30分钟）
- 缓存系统状态（1分钟）
- 缓存常见查询（10分钟）

#### 代码优化

- 避免N+1查询（使用JOIN）
- 使用批量操作减少数据库访问
- 优化JSON序列化
- 异步处理长时间任务

## 更新部署

### 回滚计划

- 保留最近3个版本
- 使用Git标签管理版本
- 回滚脚本

### 更新流程

```bash
# 1. 备份当前版本
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz . env data/

# 2. 拉取新版本
git pull origin main

# 3. 安装依赖
uv sync

# 4. 数据库迁移（如有）
python scripts/migrate_database.py

# 5. 更新配置
cp .env.example .env
nano .env

# 6. 重启服务
sudo systemctl restart greendatacenter

# 7. 验证服务
curl http://localhost:8000/status

# 8. 监控日志
tail -f /var/log/greendatacenter/app.log
```

### 蓝绿部署

- 开发环境 → 测试环境 → 预发布 → 生产环境
- 每个阶段都要进行充分测试
- 使用CI/CD自动化部署流程
