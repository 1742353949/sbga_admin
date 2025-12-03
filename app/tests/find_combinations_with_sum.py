import random
from typing import List, Optional, Tuple
from itertools import combinations
import os
# 添加openpyxl导入
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
# 添加多线程相关导入
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

def random_combination_with_sum(target_sum: int, count: int) -> Optional[List[int]]:
    """
    生成指定数量的随机数，使其总和等于目标值
    
    Args:
        target_sum (int): 目标和
        count (int): 需要生成的数字个数
    
    Returns:
        Optional[List[int]]: 包含随机数的列表，如果无法生成则返回None
    """
    # 参数校验
    if count <= 0:
        raise ValueError("count must be positive")
    
    if count == 1:
        return [target_sum]
    
    # 生成前count-1个随机数
    result = []
    remaining_sum = target_sum
    
    for i in range(count - 1):
        # 为了保证最后一个数不会过大或过小，我们需要限制当前数的范围
        # 最小值为0，最大值为剩余和减去后面每个数至少为1的情况
        max_value = remaining_sum - (count - i - 1)
        if max_value < 0:
            return None
            
        # 生成随机数
        current_value = random.randint(0, max_value)
        result.append(current_value)
        remaining_sum -= current_value
    
    # 最后一个数即为剩余的值
    result.append(remaining_sum)
    
    return result

def random_combination_with_sum_positive(target_sum: int, count: int) -> Optional[List[int]]:
    """
    生成指定数量的正整数随机数，使其总和等于目标值
    
    Args:
        target_sum (int): 目标和（必须大于等于count）
        count (int): 需要生成的数字个数
    
    Returns:
        Optional[List[int]]: 包含正整数随机数的列表，如果无法生成则返回None
    """
    # 参数校验
    if count <= 0:
        raise ValueError("count must be positive")
    
    if target_sum < count:
        return None  # 无法生成全为正整数的组合
    
    if count == 1:
        return [target_sum]
    
    # 使用"星棒法"生成正整数随机组合
    # 先给每个位置分配1，然后将剩余的部分随机分配
    result = [1] * count
    remaining = target_sum - count
    
    # 将剩余值随机分配给各个位置
    for _ in range(remaining):
        index = random.randint(0, count - 1)
        result[index] += 1
    
    # 打乱顺序使分布更均匀
    random.shuffle(result)
    
    return result

def random_combination_with_sum_flexible(target_sum: int, count: int, min_val: int = 0) -> Optional[List[int]]:
    """
    生成指定数量的随机数，使其总和等于目标值，可以指定最小值
    
    Args:
        target_sum (int): 目标和
        count (int): 需要生成的数字个数
        min_val (int): 每个数字的最小值，默认为0
    
    Returns:
        Optional[List[int]]: 包含随机数的列表，如果无法生成则返回None
    """
    if count <= 0:
        raise ValueError("count must be positive")
    
    # 调整目标和，先减去所有数字的最小值部分
    adjusted_sum = target_sum - (min_val * count)
    
    if adjusted_sum < 0:
        return None
    
    # 生成非负数组合
    combination = random_combination_with_sum(adjusted_sum, count)
    
    if combination is None:
        return None
    
    # 加上最小值
    result = [x + min_val for x in combination]
    
    return result

def read_excel_column(file_path: str, column_name: str = 'A', decimal_places: int = 2) -> List[float]:
    """
    读取Excel表格中第一列的所有数值
    
    Args:
        file_path (str): Excel文件路径
        column_name (str): 列名参数（此参数不再使用，仅为兼容性保留）
        decimal_places (int): 保留的小数位数，默认为2位小数
    
    Returns:
        List[float]: 包含该列所有数值的列表
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return []
        
        # 使用openpyxl直接读取Excel文件
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        worksheet = workbook.active
        
        # 读取第一列数据
        values = []
        for row in worksheet.iter_rows(min_col=1, max_col=1, values_only=True):
            cell_value = row[0]
            if cell_value is not None:
                values.append(cell_value)
        
        # 输出第一列第一行数据
        if len(values) > 0:
            print(f"第一列第一行数据: {values[0]}")
        
        # 过滤掉非数值数据，只保留可以转换为float的数值，并保留指定小数位数
        numeric_values = []
        for value in values:
            try:
                numeric_value = round(float(value), decimal_places)
                numeric_values.append(numeric_value)
            except (ValueError, TypeError):
                # 跳过无法转换为数值的数据（如文本）
                print(f"无法转换为数值: {value}")
                continue
        
        return numeric_values
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return []
    except ImportError as e:
        print(f"缺少必要的依赖库: {e}")
        print("\n解决方法:")
        print("1. 尝试使用以下命令安装openpyxl:")
        print("   pip install openpyxl")
        print("2. 如果上述命令失败，请尝试:")
        print("   python -m pip install openpyxl")
        print("3. 如果仍然失败，请检查您的Python环境是否正确设置")
        print("   或尝试重新创建虚拟环境")
        return []
    except Exception as e:
        if "File contains no valid workbook part" in str(e):
            print(f"Excel文件格式错误: {file_path}")
            print("可能的原因:")
            print("1. 文件已损坏")
            print("2. 文件不是有效的Excel格式(.xlsx或.xls)")
            print("3. 文件是空文件或内容已被破坏")
            print("\n解决方法:")
            print("1. 检查文件扩展名是否正确(.xlsx推荐)")
            print("2. 尝试用Excel打开该文件确认是否能正常打开")
            print("3. 如果能打开，请另存为新的.xlsx文件再试")
            print("4. 确认文件路径没有特殊字符或中文")
        else:
            print(f"读取Excel文件时发生错误: {e}")
        return []

# 修改 find_combinations_with_sum 函数以支持多线程处理
def find_combinations_with_sum(numbers: List[int], target_sum: int, combination_size: int = None, 
                              max_combination_size: int = 7, early_exit: bool = False, tolerance: float = 0.001) -> List[Tuple[int, ...]]:
    """
    在给定数组中查找和等于目标值的所有组合
    
    Args:
        numbers (List[int]): 数值列表
        target_sum (int): 目标和
        combination_size (int, optional): 组合大小，如果不指定则查找所有可能大小的组合
        max_combination_size (int): 最大组合数，默认为7
        early_exit (bool): 是否在找到第一个符合条件的组合后退出，默认为False
        tolerance (float): 浮点数比较的容差值，默认为0.001
    
    Returns:
        List[Tuple[int, ...]]: 所有满足条件的组合列表
    """
    print("开始查找组合...")
    # 如果指定了组合大小
    if combination_size is not None:
        # 使用多线程处理大组合
        result = _find_combinations_parallel(numbers, target_sum, combination_size, early_exit, tolerance)
        print(f"完成查找大小为 {combination_size} 的组合")
        return result
    else:
        # 查找所有可能大小的组合，但不超过max_combination_size
        result = []
        print(f"共有 {len(numbers)} 个数字，将查找组合数不大于 {max_combination_size} 的所有可能大小的组合...")
        for size in range(1, min(len(numbers) + 1, max_combination_size + 1)):
            print(f"正在查找大小为 {size} 的组合...")
            size_results = _find_combinations_parallel(numbers, target_sum, size, early_exit, tolerance)
            result.extend(size_results)
            print(f"已完成大小为 {size} 的组合查找，找到 {len(size_results)} 个符合条件的组合")
            # 如果启用了early_exit并且找到了结果，则直接返回
            if early_exit and len(size_results) > 0:
                print(f"找到第一个符合条件的组合，提前退出")
                return result
        print("完成所有组合查找")
        return result

def _find_combinations_parallel(numbers: List[int], target_sum: int, combination_size: int, early_exit: bool = False, tolerance: float = 0.001) -> List[Tuple[int, ...]]:
    """
    使用多线程并行查找指定大小的组合
    
    Args:
        numbers (List[int]): 数值列表
        target_sum (int): 目标和
        combination_size (int): 组合大小
        early_exit (bool): 是否在找到第一个符合条件的组合后退出
        tolerance (float): 浮点数比较的容差值
    
    Returns:
        List[Tuple[int, ...]]: 所有满足条件的组合列表
    """
    result = []
    
    # 计算组合总数
    total_combinations = math.comb(len(numbers), combination_size)
    print(f"大小为 {combination_size} 的组合总数: {total_combinations}")
    
    # 如果组合数较少，直接处理
    if total_combinations < 10000:
        print(f"组合数较少，直接处理...")
        count = 0
        for combo in combinations(numbers, combination_size):
            # 修改为使用自定义容差值
            if math.isclose(sum(combo), target_sum, abs_tol=tolerance):
                result.append(combo)
                # 如果启用了early_exit，找到一个就退出
                if early_exit:
                    print(f"找到符合条件的组合，提前退出")
                    return result
            count += 1
            if count % 1000 == 0:
                print(f"已处理 {count}/{total_combinations} 个组合...")
        print(f"处理完成，共找到 {len(result)} 个符合条件的组合")
        return result
    
    # 对于大量组合，使用多线程处理
    print("组合数较多，使用多线程处理...")
    # 将组合分块处理
    chunk_size = max(1000, total_combinations // 4)  # 每个线程处理的组合数
    chunks = []
    
    # 创建组合迭代器
    combo_iter = combinations(numbers, combination_size)
    
    # 分块处理组合
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(combo_iter))
            chunks.append(chunk)
        except StopIteration:
            if chunk:
                chunks.append(chunk)
            break
    
    print(f"共分为 {len(chunks)} 个任务块，每块约 {chunk_size} 个组合")
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 提交任务
        future_to_chunk = {
            executor.submit(_process_chunk, chunk, target_sum, early_exit, tolerance): (i, len(chunk)) 
            for i, chunk in enumerate(chunks)
        }
        
        completed_tasks = 0
        # 收集结果
        for future in as_completed(future_to_chunk):
            chunk_index, chunk_size = future_to_chunk[future]
            print(f"任务块 {chunk_index+1}/{len(chunks)} 处理完成")
            chunk_result = future.result()
            result.extend(chunk_result)
            completed_tasks += 1
            print(f"已完成 {completed_tasks}/{len(chunks)} 个任务块")
            # 如果启用了early_exit并且找到了结果，则直接返回
            if early_exit and len(chunk_result) > 0:
                print(f"找到符合条件的组合，提前退出")
                return result
    
    print(f"多线程处理完成，共找到 {len(result)} 个符合条件的组合")
    return result

def _process_chunk(chunk: List[Tuple], target_sum: int, early_exit: bool = False, tolerance: float = 0.001) -> List[Tuple[int, ...]]:
    """
    处理组合块，找出符合目标和的组合
    
    Args:
        chunk (List[Tuple]): 组合块
        target_sum (int): 目标和
        early_exit (bool): 是否在找到第一个符合条件的组合后退出
        tolerance (float): 浮点数比较的容差值
    
    Returns:
        List[Tuple[int, ...]]: 符合条件的组合列表
    """
    local_result = []
    for combo in chunk:
        # 使用自定义容差值
        if math.isclose(sum(combo), target_sum, abs_tol=tolerance):
            local_result.append(combo)
            # 如果启用了early_exit，找到一个就退出
            if early_exit:
                break
    return local_result

# 主程序
if __name__ == "__main__":
    # 读取Excel并查找组合
    # 修改为不指定列名，让函数读取第一列
    print("开始读取Excel文件...")
    excel_data = read_excel_column(f'D:/A_zzy/test/test3.xlsx')
    print(f"读取完成，共读取到 {len(excel_data)} 个数据")
    print(excel_data)


    target = -135907.59 #-8944.9
    tolerance = 30
    print(f"目标和: {target}")
    
    # 查找所有组合（不限制组合大小，但不超过7个元素，找到一个就退出）
    print("开始查找组合...")
    combinations_result = find_combinations_with_sum(excel_data, target, max_combination_size=7, early_exit=False, tolerance=tolerance)
    
    print(f"在Excel A列中找到和为 {target} ,误差在 {tolerance} 以内的任意数组合:")
    if combinations_result:
        for i, combo in enumerate(combinations_result, 1):
            print(f"组合{i}: {combo}")
            # 实现将组合中的值相加并输出和 与 目标值相减 的值
            combo_sum = sum(combo)
            difference = target - combo_sum
            print(f"  组合{i}的和: {combo_sum}, 目标值：{target}  差: {difference}")
        print(f"\n总共找到 {len(combinations_result)} 个组合")
    else:
        print("未找到满足条件的组合")
    print("程序执行完毕")