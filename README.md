## 环境配置

- 安装 `funcsigs` 库和 `pip` 工具

        sudo dnf install -y python2-funcsigs python-pip

- 安装 `openstacksdk` 库（依赖 `funcsigs`）

        sudo pip install openstacksdk

### TODO:

用部署工具自动配置环境。

## 程序配置

- 将 `etc/foldex.conf` 中的参数修改为合适值，复制到 `/etc/foldex/`下。
