#!/bin/bash

# --- 配置参数 ---
# 1. 要处理的被试ID范围 (使用数字，用于循环)
#    例如: start_subject_id=1, end_subject_id=3 表示处理 sub-01 到 sub-03。
start_subject_id=1 # <-- 根据您的需要修改起始被试ID
end_subject_id=10   # <-- 根据您的需要修改结束被试ID

# 2. 要处理的会话ID范围 (使用数字，用于循环)
#    这些会话ID应该与原始数据目录中的 ses-XX 文件夹名称相匹配。
start_session_id=1 # <-- 根据您的需要修改起始会话ID
end_session_id=3   # <-- 根据您的需要修改结束会话ID

# 3. 宿主机上日志文件的存储目录
#    日志文件会在此目录下生成，请确保此目录存在或脚本有权限创建。
LOG_DIR="/media/xue/xue/data/heudiconv_logs" # <-- 请确保此目录存在或修改为您的路径

# --- 脚本开始 ---

echo "--- HeuDiConv 批量转换脚本启动 ---"
echo "被试ID范围: ${start_subject_id} 到 ${end_subject_id}"
echo "会话ID范围: ${start_session_id} 到 ${end_session_id}"
echo "日志目录: ${LOG_DIR}"
echo "---"

# 确保日志目录存在
mkdir -p "${LOG_DIR}"

# 遍历每个被试
for sub_raw_id in $(seq ${start_subject_id} ${end_subject_id}); do
    # 格式化被试 ID 为两位数字 (例如 sub-01, sub-02, ...)
    # 这个标签会作为 -s 参数的值传入 HeuDiConv。
    subject_label="sub-$(printf "%02d" ${sub_raw_id})"
    
    echo "处理被试: ${subject_label}"

    # 遍历每个会话
    for ses_raw_id in $(seq ${start_session_id} ${end_session_id}); do
        # 格式化会话 ID 为两位数字 (例如 ses-01, ses-02, ...)
        # 这个标签会作为 -ss 参数的值传入 HeuDiConv。
        session_label="ses-$(printf "%02d" ${ses_raw_id})"
        
        echo "  处理会话: ${session_label}"

        # 构造日志文件名
        LOG_FILE="${LOG_DIR}/${subject_label}_${session_label}_heudiconv.log"
        
        echo "    日志文件: ${LOG_FILE}"

        # 执行 HeuDiConv 命令
        # 仅 -s 和 -ss 参数会动态替换。
        # 其他所有参数和路径，包括 -d /base/dataset/{subject}/{session}/*/*.dcm 和 --overwrite 保持原样。
        docker run --rm -it -v ${PWD}:/base nipy/heudiconv:latest \
        -d /base/dataset/{subject}/{session}/*/*.dcm \
        -o /base/outBIDS/ \
        -f convertall \
        -s "${subject_label}" \
        -ss "${session_label}" \
        -c none \
        -b --minmeta \
        --overwrite \
        2>&1 | tee -a "${LOG_FILE}"

        # 检查 HeuDiConv 命令的退出状态。
        if [ $? -eq 0 ]; then
            echo "  会话 ${session_label} 处理成功。" >> "${LOG_FILE}"
            echo "  会话 ${session_label} 处理成功。"
        else
            echo "  会话 ${session_label} 处理失败，请检查 ${LOG_FILE}。" >> "${LOG_FILE}"
            echo "  会话 ${session_label} 处理失败，请检查 ${LOG_FILE}。"
            # 如果需要，可以在这里添加退出或更详细的错误处理逻辑。
        fi
        echo "" # 空行，用于分隔不同会话的输出

    done
done

echo "--- HeuDiConv 批量转换脚本完成 ---"
