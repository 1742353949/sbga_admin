from datetime import timedelta

# # 通用构造（参数均为可选，默认值 0，支持整数/浮点数）
# delta = timedelta(    
#     minutes=15+5    
    
# )
# print(delta)

from datetime import datetime, timedelta

end_time = datetime.now() + timedelta(minutes=10 + 5) 
end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

print(end_time_str)  # 输出示例：2025-11-28 15:42:36     

print('=== 时间范围 ===', end_time)      
    
now = datetime.now()
print(isinstance(now, datetime))  # True
print(isinstance(now, timedelta)) # False