from waitress import serve
from app import create_app
import os


if __name__ == '__main__':
    print("app运行中。。。")
    app = create_app()

    host = '127.0.0.1'
    port = 5004
    #debug模式下运行
    # app.run(debug=True,host='0.0.0.0',port=5005)
    print(f"app运行在{host}:{port}")
    #生产模式下运行
    serve(app,host=host,port=port)