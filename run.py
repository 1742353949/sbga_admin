from waitress import serve
from app import create_app
import os


if __name__ == '__main__':
    print("app运行中。。。")
    app = create_app()
    app.run(debug=True,host='0.0.0.0',port=5004)
    # serve(app,host='0.0.0.0',port=5003)