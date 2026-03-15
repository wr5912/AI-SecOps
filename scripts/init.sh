# AI-SecOps 开发环境初始化脚本

#!/bin/bash
set -e

echo "🚀 AI-SecOps 开发环境初始化"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python版本: $python_version"

# 检查Node.js版本
node_version=$(node --version 2>&1)
echo "📌 Node.js版本: $node_version"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装后端依赖
echo "📦 安装后端依赖..."
pip install --upgrade pip
pip install -e ".[all]"

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 复制环境变量模板
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
fi

# 启动Docker服务
echo "🐳 启动Docker服务..."
docker-compose -f docs/templates/docker-compose.dev.yml up -d

echo "✅ 初始化完成!"
echo ""
echo "📌 启动命令:"
echo "  后端: cd backend && uvicorn src.api.main:app --reload"
echo "  前端: cd frontend && npm run dev"
echo ""
echo "📌 访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  Neo4j: http://localhost:7474"
