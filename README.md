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

修改 `config.py` 中的配置项，fakeopen 的接口可能关闭，如无自行部署 [pandora-next](https://github.com/pandora-next/deploy) ，可以使用 `https://shared.3211000.xyz/proxy` 作为 `BASE_URL` 。


### 2.3. 运行

```shell
python main.py
```

### 2.4. token定时刷新

`crontab` 配置定时任务
    
```shell
0 12 * * * cd /path/to/your/project && /path/to/your/project/.venv/bin/python /path/to/your/project/refresh.py
```

> `refresh.py` 需要直连 `openai` ，也可参考 [fakeopen提供接口](https://github.com/zhile-io/pandora/blob/master/doc/fakeopen.md#3-authrefresh) 自行更改。

### 部分脚本作用

- `refresh.py`：定时刷新 token ，且校验密码是否更改
- `gen_share_token.py`：生成 share_token & pool_token ，且校验账号是否有效
- `redis_cache.py`：redis 缓存相关，可获取指定要求 token ，例如未改密码，账号有效等
- `pool_token.py`：基于存活的 share_token 快速生成 pool_token
- `other.py`：其他脚本，例如批量检测是否4，是否存在订阅分享等

## 3. TODO

TODO but not to do, just for summary.

- [ ] 消费者生产者模型出于练手的角度写的，结果生产者能力远大于消费者，而消费者因为 api 本身的限制，无法并发，导致生产者和消费者均只能单线程运行，毫无意义。

    **理论上可以通过控制生产者消费者的线程数达到平衡的效果，结果消费者的能力有限，生产者的能力过强，退化成了先生成后消费的模型。**

- [ ] 之前考虑 redis 相关的操作都放在 `redis_cache.py` 中，但是后来发现 `redis_cache.py` 中的方法太多过于冗余，且部分操作仅仅是一行代码，所以部分代码直接引用了 `redis` 模块直接操作 redis ，代码不够统一。

- [ ] 配置文件逻辑似乎有问题，导致每次添加新的配置项，即使只需要用到默认项，也需要在配置文件中添加，否则会报错。

    下次考虑使用 `settings.yaml` ，`config.py` 配置默认项，`settings.yaml` 通过配置项覆盖默认项。

- [ ] redis 中的数据结构设成 `str json` 的格式似乎是一个很大的问题，导致每次仅更新单个字段或新增字段，都需要 `dumps` 一次，然后 `loads` 一次，且部分代码更新字段时是覆盖式的更新，还会导致其他字段丢失。

    下次考虑使用 `hash` 。

- [ ] 理论上隐私数据最佳实践可能是使用环境变量，但是代码结构已经一团糟了，还是统一到配置文件中。

- [ ] 本来是练手的小脚本，结果随着需求的增加，代码越来越乱，fakeopen 的接口关闭，以前的硬编码需要手动更新，改的实在是痛苦， GG。

## 4. 参考

1. [如何获取access token](https://zhile.io/2023/05/19/how-to-get-chatgpt-access-token-via-pkce.html)
2. [已提供的简单接口](https://github.com/zhile-io/pandora/blob/master/doc/fakeopen.md#2-authlogin)