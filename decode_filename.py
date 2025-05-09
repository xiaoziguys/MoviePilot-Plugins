# -*- coding: utf-8 -*-
import sys

def decode_filename(encoded_str):
    # 将转义字符转换为字节
    try:
        # 替换特殊字符为对应的转义序列
        encoded_str = encoded_str.replace('æ', '\xe6').replace('å', '\xe5').replace('ç', '\xe7').replace('è', '\xe8').replace('í', '\xed').replace('â', '\xe2').replace('ã', '\xe3').replace('ä', '\xe4')
        # 尝试将字符串中的转义序列解码为字节
        bytes_str = bytes(encoded_str, 'latin1')
        # 尝试以UTF-8解码字节
        decoded_str = bytes_str.decode('utf-8')
        return decoded_str
    except Exception as e:
        return f"解码失败: {str(e)}"

if __name__ == "__main__":
    # 用户提供的文件名
    filename = 'æ\x9c\x80å\x90\x8eç\x94\x9fè¿\x98è\x80\x85.The.Last.of.Us.S02E01.1080p.HDä¸\xadè\x8b±å\x8f\x8cå\xad\x97.mp4'
    result = decode_filename(filename)
    print(f"原始文件名: {filename}")
    print(f"解码后文件名: {result}")