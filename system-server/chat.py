from http import HTTPStatus
from dashscope import ImageSynthesis
import requests
from openai import OpenAI
import config


def chat_bot(messages, bot):
    if bot == "reason":
        url = config.DEEPSEEK_API_URL
        payload = {
            "model": "Pro/deepseek-ai/DeepSeek-R1",
            "messages": messages,
            "max_tokens": 8192
        }
        headers = {
            "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.request("POST", url, json=payload, headers=headers)
            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            try:
                res = chat_bot(messages, "qwen-json")
                return res
            except Exception:
                return "default"
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return "Error in response"
    elif bot == "qwen-json":
        client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_BASE_URL
        )
        response = client.chat.completions.create(
            temperature=1.0,
            model="qwen-max",
            messages=messages,
            stream=False,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    elif bot == "qwen-max":
        client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_BASE_URL
        )
        response = client.chat.completions.create(
            temperature=1.0,
            model="qwen-max",
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content
    elif bot == "deepseek-v3":
        url = config.DEEPSEEK_API_URL
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": messages,
            "stream": False,
            "max_tokens": 512,
            "stop": ["null"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"},
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "description": "<string>",
                        "name": "<string>",
                        "parameters": {},
                        "strict": False
                    }
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.request("POST", url, json=payload, headers=headers)
            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return "Error in request"
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return "Error in response"
    else:
        return "Unsupported bot type"


def chat_bot_format(system, user, bot):
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return chat_bot(messages, bot)


def incorrect_str_detect(init_str):
    init_str = init_str.replace('<｜end▁of▁sentence｜>', '')
    init_str = init_str.replace("\"", '')
    init_str = init_str.replace("《", '')
    init_str = init_str.replace("》", '')
    init_str = init_str.replace(" ", "")
    return init_str


def generate_image(positive_prompt, negative_prompt, save_path, size=None):
    try:
        # 使用配置中的API密钥和模型
        api_key = config.IMAGE_API_KEY
        model = config.IMAGE_MODEL
        image_size = size if size else config.DEFAULT_IMAGE_SIZE
        # 调用绘图API
        rsp = ImageSynthesis.call(
            api_key=api_key,
            model=model,
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            n=1,
            size=image_size
        )
        if rsp.status_code == HTTPStatus.OK:
            # 下载并保存图片
            for result in rsp.output.results:
                image_data = requests.get(result.url)
                image_data.raise_for_status()  # 检查HTTP请求是否成功

                with open(save_path, 'wb+') as f:
                    f.write(image_data.content)
                return True
        else:
            print(f'API调用失败，状态码: {rsp.status_code}, 错误码: {rsp.code}, 信息: {rsp.message}')
            return False
    except requests.exceptions.RequestException as e:
        print(f"图片下载失败: {str(e)}")
    except IOError as e:
        print(f"文件保存失败: {str(e)}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
    return False

