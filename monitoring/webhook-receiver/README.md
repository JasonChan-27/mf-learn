Webhook Receiver

说明：此目录包含一个最小的 Express webhook 接收器示例，会把 Alertmanager 的 POST 请求转发为 GitHub `repository_dispatch` 事件，从而触发可配置的 GitHub Actions（例如回滚 workflow）。

部署前准备：

- 设置环境变量 `GITHUB_TOKEN`（具有 repo:dispatch 权限）、`REPO_OWNER`、`REPO_NAME`。
- 可选：设置 `SECRET` 并让 Alertmanager 在 `x-alert-secret` header 中带上该值。

示例：在 Alertmanager 中配置 webhook：

```yaml
receivers:
	- name: 'mf-webhook'
		webhook_configs:
			- url: 'https://your-webhook-host/webhook'
				send_resolved: true
				http_config: {}
				# 或者使用 header 传递简易 secret
				headers:
					- 'x-alert-secret: my-secret-value'
```

运行：

```
node receiver.js
```

安全注意：真实环境请放在受限网络、使用 HTTPS 和鉴权代理后面。
