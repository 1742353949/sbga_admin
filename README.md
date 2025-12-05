
#### 项目根目录创建虚拟环境venv
python -m venv venv
#### 激活虚拟环境
venv/Scripts/activate

#### 项目依赖:写入/更新
pip freeze > requirements.txt
#### 项目依赖：安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#### 运行
python run.py

#### 项目目录结构
app📁 项目根目录/
├── 📁 docs/          # 项目文档
│   ├── 📄 README.md   # 项目说明（核心）
│   ├── 📄 版本日志.md # 版本更新日志
│   ├── 📄 API.md      # 接口文档（如有）
│   └── 📄 部署说明.md  # 环境部署/运行说明
├── 📁 controllers/           # 逻辑处理控制器
│   ├── 📁 Admin/     #后台管理控制器
│   ├── 📁 LFZZ/    # 联防智治控制器
│   ├── 📁 /    # 
│   └── 📄 MainController.py  # 主控制器
├── 📁 test/          # 测试用例目录
│   ├── 📁 unit/       # 单元测试
│   └── 📁 e2e/        # 端到端测试
├── 📁 config/        # 配置文件目录
│   ├── 📄 dev.config.js # 开发环境配置
│   └── 📄 prod.config.js # 生产环境配置
├── 📁 assets/        # 静态资源（图片/字体/数据等）
├── 📁 scripts/       # 脚本文件（构建/部署/自动化脚本）
├── 📁 logs/          # 日志文件（运行时生成）
├── 📄 .gitignore     # Git 忽略规则
├── 📄 package.json   # 依赖管理（前端/Node.js）/ requirements.txt（Python）
└── 📄 LICENSE        # 开源许可证（如有）

（实现自动遍历文件夹，并生成目录结构、api接口文档、文档说明-读取每个文件第一行注释，并在后台管理页面添加目录展示即可修改功能；）