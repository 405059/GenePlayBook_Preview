import oss2

# Alibaba Cloud OSS service configuration
OSS_ACCESS_KEY_ID = 'Replace_with_your_OSS_ACCESS_KEY_ID'      # Replace with your API Key
OSS_ACCESS_KEY_SECRET = 'Replace_with_your_OSS_ACCESS_KEY_SECRET'  # Replace with your API Key
OSS_ENDPOINT = 'Replace_with_your_OSS_endpoint'  # OSS endpoint
OSS_BUCKET_NAME = 'Replace_with_your_OSS_BUCKET_NAME'  # Replace with your OSS Bucket Name

# AI API key configuration
QWEN_API_KEY = "Replace_with_your_QWEN_API_KEY"  # Replace with your API Key
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # Qwen API Base URL

DEEPSEEK_API_KEY = "Replace_with_your_DEEPSEEK_API_KEY"  # Replace with your API Key
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # DeepSeek API URL

# Image generation API configuration
IMAGE_API_KEY = "Replace_with_your_IMAGE_API_KEY"  # Replace with your API Key
IMAGE_MODEL = "wanx2.1-t2i-turbo"  # Default image model
DEFAULT_IMAGE_SIZE = "1440*768"  # Default image size

# Application configuration
secret_key = "Replace_with_your_secret_key"  # User's name or unique identifier
enable_cloud_services = True
game_id = 0

# Initialize OSS authentication and bucket
auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

speaker_identifier = "Speaker 2"