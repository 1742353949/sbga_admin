
#### 项目根目录创建虚拟环境venv
python -m venv venv
#### 激活虚拟环境
venv/bin/activate

#### 项目依赖:写入/更新
pip freeze > requirements.txt
#### 项目依赖：安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#### 运行
python run.py