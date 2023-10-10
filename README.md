# 批量账号token获取

## 1. 说明

通过提取获得的批量账密，尝试获取 token ，存 redis 保存 access token 和 refresh token 。

## 2. 使用方法

### 2.1. 安装依赖

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2. 配置

```shell
cp config.py.example config.py
```

修改 `config.py` 中的配置项。

### 2.3. 运行

```shell
python main.py
```

### 2.4. token定时刷新

`crontab` 配置定时任务
    
```shell
0 12 * * * cd /path/to/your/project && source .venv/bin/activate && python refresh.py
```

> `refresh.py` 需要直连 `openai` ，也可参考 [fakeopen提供接口](https://github.com/zhile-io/pandora/blob/master/doc/fakeopen.md#3-authrefresh) 自行更改。

## 3. 参考

1. [如何获取access token](https://zhile.io/2023/05/19/how-to-get-chatgpt-access-token-via-pkce.html)
2. [已提供的简单接口](https://github.com/zhile-io/pandora/blob/master/doc/fakeopen.md#2-authlogin)